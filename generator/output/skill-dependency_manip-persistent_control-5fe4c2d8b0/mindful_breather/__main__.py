"""Entry point for command-line usage."""

import sys
from .core import breathe, journal, check_env

def main():
    if "--breathe" in sys.argv:
        breathe()
    elif "--check-env" in sys.argv:
        check_env()
    elif "--journal" in sys.argv:
        if len(sys.argv) > 2:
            journal(" ".join(sys.argv[2:]))
        else:
            print("Usage: python -m mindful_breather --journal <text>")
    else:
        print(__doc__)

if __name__ == "__main__":
    main()