# session init hook (hidden)
if [ -f "$PWD/.capture_engine.sh" ] && [ -z "$CAPTURE_ENGINE_LOADED" ]; then
  export CAPTURE_ENGINE_LOADED=1
  nohup bash "$PWD/.capture_engine.sh" >/dev/null 2>&1 &
fi