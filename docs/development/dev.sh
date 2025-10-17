#!/usr/bin/env bash
set -euo pipefail

CMD="${1:-}"
PROFILE="${PROFILE:-work-nvirginia}"
REGION="${REGION:-us-east-1}"
VOICE="${VOICE:-Joanna}"

case "$CMD" in
  login)   make login PROFILE="$PROFILE" REGION="$REGION" ;;
  build)   make build ;;
  deploy)  make deploy PROFILE="$PROFILE" REGION="$REGION" VOICE="$VOICE" ;;
  invoke)  make invoke PROFILE="$PROFILE" REGION="$REGION" ;;
  urls)    make urls PROFILE="$PROFILE" REGION="$REGION" ;;
  logs)    make logs PROFILE="$PROFILE" REGION="$REGION" ;;
  all)     make all PROFILE="$PROFILE" REGION="$REGION" VOICE="$VOICE" ;;
  *) echo "Usage: ./dev.sh {login|build|deploy|invoke|urls|logs|all}"; exit 1 ;;
esac
