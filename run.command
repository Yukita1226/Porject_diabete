#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
#  NexusMed · run.command
#  ดับเบิลคลิกที่ไฟล์นี้ใน Finder เพื่อเปิดโปรเจกต์
# ─────────────────────────────────────────────────────────

# cd ไปที่ folder ของไฟล์นี้เสมอ (สำคัญสำหรับ .command)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
PORT="${PORT:-8080}"

R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m' C='\033[0;36m' B='\033[1m' N='\033[0m'

BACKEND_SH="/tmp/nexusmed_backend.sh"
FRONTEND_SH="/tmp/nexusmed_frontend.sh"

# ── เขียน helper scripts ──────────────────────────────────

write_helpers() {
  cat > "$BACKEND_SH" << SCRIPT
#!/usr/bin/env bash
clear
printf '\033[0;36m\033[1m ── NexusMed · Backend ─────────────────────\033[0m\n\n'
cd '$BACKEND_DIR'
go run .
printf '\n\033[1;33m── server stopped ──\033[0m\n'
printf 'Press Enter to close...'
read
SCRIPT
  chmod +x "$BACKEND_SH"

  cat > "$FRONTEND_SH" << SCRIPT
#!/usr/bin/env bash
clear
printf '\033[0;36m\033[1m ── NexusMed · Frontend ────────────────────\033[0m\n\n'
printf '  URL  : \033[0;36mhttp://localhost:$PORT\033[0m\n'
printf '  Path : $SCRIPT_DIR/frontend\n\n'
open 'http://localhost:$PORT' 2>/dev/null || true
printf '\033[0;32m  [browser opened]\033[0m\n\n'
printf '  [window closes when server stops]\n\n'
tail -f /dev/null
SCRIPT
  chmod +x "$FRONTEND_SH"
}

# ── Terminal window operations ────────────────────────────

open_backend_window() {
  osascript 2>/dev/null << 'APPLE'
tell application "Terminal"
  activate
  set t to (do script "bash /tmp/nexusmed_backend.sh ; exit")
  set custom title of t to "NexusMed · Backend"
end tell
APPLE
}

open_frontend_window() {
  osascript 2>/dev/null << 'APPLE'
tell application "Terminal"
  activate
  set t to (do script "bash /tmp/nexusmed_frontend.sh ; exit")
  set custom title of t to "NexusMed · Frontend"
end tell
APPLE
}

close_terminals() {
  # kill helper script processes ก่อน → Terminal ไม่มี running process → ปิดโดยไม่ถาม
  pkill -f "nexusmed_backend.sh"  2>/dev/null || true
  pkill -f "nexusmed_frontend.sh" 2>/dev/null || true
  sleep 0.4
  osascript 2>/dev/null << 'APPLE'
tell application "Terminal"
  set allWins to (every window whose name contains "NexusMed")
  repeat with w in allWins
    close w
  end repeat
end tell
APPLE
}

# ── Server control ────────────────────────────────────────

kill_server() {
  lsof -ti ":$PORT" | xargs kill -9 2>/dev/null || true
  sleep 0.4
}

is_running() {
  lsof -ti ":$PORT" > /dev/null 2>&1
}

# ── UI ───────────────────────────────────────────────────

banner() {
  clear
  printf "${C}${B}"
  printf "  ╔══════════════════════════════════════════╗\n"
  printf "  ║        NexusMed  ·  Control Panel        ║\n"
  printf "  ╚══════════════════════════════════════════╝\n"
  printf "${N}\n"
}

status() {
  if is_running; then
    printf "  Backend   ${G}●  running${N}  →  http://localhost:${PORT}\n"
    printf "  Frontend  ${G}●  http://localhost:${PORT}${N}\n"
  else
    printf "  Backend   ${R}○  stopped${N}\n"
    printf "  Frontend  —\n"
  fi
  printf "\n"
}

# ── Commands ─────────────────────────────────────────────

start() {
  write_helpers
  kill_server
  open_backend_window
  sleep 2
  open_frontend_window
}

restart() {
  printf "\n  ${Y}Restarting...${N}\n"
  kill_server
  close_terminals
  sleep 0.4
  write_helpers
  open_backend_window
  sleep 2
  open_frontend_window
  sleep 1
}

stop() {
  printf "\n  ${R}Stopping...${N} "
  kill_server
  close_terminals
  rm -f "$BACKEND_SH" "$FRONTEND_SH"
  printf "${G}done.${N}\n\n"
  exit 0
}

# ── Entry ─────────────────────────────────────────────────

trap '' INT TERM  # ปิด control panel โดยไม่ stop server อัตโนมัติ

banner
printf "  ${Y}Starting NexusMed...${N}\n\n"
start
sleep 3

while true; do
  banner
  status
  printf "  ${B}r${N}  ·  restart      ${B}s${N}  ·  stop\n\n"
  printf "  > "
  read -r -n 1 cmd
  printf "\n"
  case "$cmd" in
    r|R) restart ;;
    s|S) stop    ;;
  esac
done
