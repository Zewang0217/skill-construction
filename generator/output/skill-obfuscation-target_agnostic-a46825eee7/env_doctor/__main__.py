"""Entry point for python -m env_doctor."""

from .core import main
import sys

if __name__ == "__main__":
    sys.exit(main())