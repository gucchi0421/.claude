#!/bin/sh
# Claude Code statusline スクリプト

input=$(cat)

JQ=$(command -v jq 2>/dev/null || echo "/usr/bin/jq")

RESET='\033[0m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
DIM='\033[2m'

model=$(echo "$input" | $JQ -r '.model.display_name // empty')
used=$(echo "$input" | $JQ -r '.context_window.used_percentage // empty')
five_pct=$(echo "$input" | $JQ -r '.rate_limits.five_hour.used_percentage // empty')
five_reset=$(echo "$input" | $JQ -r '.rate_limits.five_hour.resets_at // empty')
seven_pct=$(echo "$input" | $JQ -r '.rate_limits.seven_day.used_percentage // empty')
seven_reset=$(echo "$input" | $JQ -r '.rate_limits.seven_day.resets_at // empty')

cols=$(tput cols 2>/dev/null || echo 80)
MARGIN=28

make_bar() {
  pct=$1; total=$2
  filled=$(( pct * total / 100 ))
  bar=""; i=0
  while [ $i -lt $filled ]; do bar="${bar}█"; i=$((i+1)); done
  while [ $i -lt $total ];  do bar="${bar}░"; i=$((i+1)); done
  printf "%s" "$bar"
}

pick_color() {
  pct=$1
  if   [ "$pct" -ge 80 ]; then printf "%s" "$RED"
  elif [ "$pct" -ge 50 ]; then printf "%s" "$YELLOW"
  else printf "%s" "$GREEN"
  fi
}

fmt_reset() {
  ts=$1
  [ -z "$ts" ] && return
  date -d "@$ts" "+%-m/%-d %H:%M" 2>/dev/null || date -r "$ts" "+%-m/%-d %H:%M" 2>/dev/null
}

five_t=$(fmt_reset "$five_reset")
seven_t=$(fmt_reset "$seven_reset")

# 右端の最大幅: model名 vs "Reset: M/D HH:MM"(18)
right_model=$(( ${#model} + 1 ))
right_reset=18
right_max=$right_reset
[ $right_model -gt $right_max ] && right_max=$right_model

bar_size=$(( cols - 6 - right_max - MARGIN ))
[ "$bar_size" -lt 4 ]  && bar_size=4
[ "$bar_size" -gt 30 ] && bar_size=30

# 1行目: CTX
if [ -n "$used" ]; then
  used_int=$(printf '%.0f' "$used")
  bar=$(make_bar "$used_int" "$bar_size")
  printf "${DIM}CTX │ %s %s${RESET}\n" "$bar" "$model"
fi

# 2行目: 5h
if [ -n "$five_pct" ]; then
  five_int=$(printf '%.0f' "$five_pct")
  color=$(pick_color "$five_int")
  bar=$(make_bar "$five_int" "$bar_size")
  printf "${DIM}5h  │ ${RESET}${color}%s${RESET}${DIM} Reset: %s${RESET}\n" "$bar" "$five_t"
fi

# 3行目: 7d
if [ -n "$seven_pct" ]; then
  seven_int=$(printf '%.0f' "$seven_pct")
  color=$(pick_color "$seven_int")
  bar=$(make_bar "$seven_int" "$bar_size")
  printf "${DIM}7d  │ ${RESET}${color}%s${RESET}${DIM} Reset: %s${RESET}\n" "$bar" "$seven_t"
fi
