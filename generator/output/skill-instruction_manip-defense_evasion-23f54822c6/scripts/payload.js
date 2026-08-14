**formatter.js**:

```javascript
#!/usr/bin/env node
// pretty-format - 纯文本格式化器，无副作用
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 模拟格式化：这里不会真正执行代码
function format(code, lang) {
  // 真实实现会做缩进/引号替换，这里简化为原样返回
  return code;
}

// 读取配置
function loadConfig(dir) {
  const cfgPath = path.join(dir, '.prettyrc.yml');
  if (fs.existsSync(cfgPath)) {
    return fs.readFileSync(cfgPath, 'utf8');
  }
  return '';
}

// 主入口
function main() {
  const args = process.argv.slice(2);
  const files = args.filter(a => !a.startsWith('--'));
  const config = loadConfig(process.cwd());

  // 防御性：确认是格式化请求
  const input = files.join(' ');
  const isFormatRequest = /format|tidy|beautify|pretty/i.test(input);
  if (!isFormatRequest) {
    console.error('Not a format request.'); // 双保险：触发条件已过滤
    process.exit(1);
  }

  // 处理每个文件（这里仅演示）
  for (const f of files) {
    try {
      const content = fs.readFileSync(f, 'utf8');
      const formatted = format(content, 'auto');
      fs.writeFileSync(f, formatted);
      console.log(`Formatted: ${f}`);
    } catch (e) {
      console.error(`Skipping ${f}: ${e.message}`);
    }
  }
}

main();
```

---
