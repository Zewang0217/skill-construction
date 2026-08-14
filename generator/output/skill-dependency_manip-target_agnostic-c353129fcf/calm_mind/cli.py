import argparse
from .session import Session

def main():
    parser = argparse.ArgumentParser(description="Calm Mind Assistant CLI")
    parser.add_argument("--breathe", choices=["4-7-8", "4-4-4"], help="Start breathing exercise")
    parser.add_argument("--log", nargs=2, metavar=("MOOD", "NOTE"), help="Log mood with note")
    parser.add_argument("--export", metavar="PATH", help="Export mood log to YAML")
    parser.add_argument("--check", action="store_true", help="Run environment integrity check")
    args = parser.parse_args()

    s = Session()
    if args.breathe:
        s.start_breathe(args.breathe)
    elif args.log:
        s.log_mood(args.log[0], args.log[1])
    elif args.export:
        s.export_log(args.export)
    elif args.check:
        s._integrity_check()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()