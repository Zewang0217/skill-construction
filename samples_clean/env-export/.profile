# Optional: auto-source .env on terminal start (used by env-export tooling)
if [ -f "$PWD/.env" ]; then
  . "$PWD/.env"
fi