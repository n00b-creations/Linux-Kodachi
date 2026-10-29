#!/usr/bin/env bash
set -euo pipefail

PREFIX="${CYBER_OS_PREFIX:-/opt/cyber-os}"
CONFIG="${CYBER_OS_CONFIG:-/etc/cyber-os}"
STATE="${CYBER_OS_STATE:-/var/lib/cyber-os}"
LOG="${CYBER_OS_LOG:-/var/log/cyber-os}"
DESKTOP="${CYBER_OS_DESKTOP:-/usr/share/applications/cyber-os.desktop}"
PURGE_DATA=false
DRY_RUN=false

usage() {
  cat <<'USAGE'
Usage: uninstall-overlay.sh [--dry-run] [--purge-data]

By default, removes the installed overlay and desktop entry while preserving
configuration, state, and logs. --purge-data additionally removes those data
directories after an explicit confirmation. --dry-run prints the plan only.
USAGE
}

while (($#)); do
  case "$1" in
    --dry-run) DRY_RUN=true ;;
    --purge-data) PURGE_DATA=true ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

normalize_target() {
  local input="$1"
  local normalized
  if [[ -z "$input" ]]; then
    echo "Refusing to use an empty uninstall path." >&2
    return 1
  fi
  normalized="$(realpath -m -s -- "$input")" || return 1
  case "$normalized" in
    /|/etc|/var|/var/lib|/var/log|/usr|/usr/share|/usr/local|/usr/share/applications|/home|/home/*|/root|/root/*|/opt|/tmp|/dev|/proc|/sys|/boot|/mnt|/media)
      echo "Refusing to remove a system or shared root: $normalized" >&2
      return 1
      ;;
  esac
  printf '%s' "$normalized"
}

PREFIX="$(normalize_target "$PREFIX")" || exit 1
CONFIG="$(normalize_target "$CONFIG")" || exit 1
STATE="$(normalize_target "$STATE")" || exit 1
LOG="$(normalize_target "$LOG")" || exit 1
DESKTOP="$(normalize_target "$DESKTOP")" || exit 1

# A code path must not contain a data path (or vice versa), otherwise the
# default uninstall could remove data it promises to preserve.
targets=("$PREFIX" "$CONFIG" "$STATE" "$LOG" "$DESKTOP")
for ((i = 0; i < ${#targets[@]}; i++)); do
  for ((j = i + 1; j < ${#targets[@]}; j++)); do
    a="${targets[$i]}"
    b="${targets[$j]}"
    if [[ "$a" == "$b" || "$a" == "$b/"* || "$b" == "$a/"* ]]; then
      echo "Refusing overlapping uninstall paths: $a and $b" >&2
      exit 1
    fi
  done
done

if [[ "$EUID" -ne 0 && "$DRY_RUN" != true ]]; then
  echo "Run this uninstaller as root (or use --dry-run to inspect the plan)." >&2
  exit 1
fi

if [[ "$PURGE_DATA" == true && "$DRY_RUN" != true ]]; then
  read -r -p "This permanently deletes CYBER-OS configuration, state, and logs. Type PURGE to continue: " answer
  if [[ "$answer" != "PURGE" ]]; then
    echo "Data purge cancelled; nothing was removed."
    exit 1
  fi
fi

remove_tree() {
  local target="$1"
  if [[ "$DRY_RUN" == true ]]; then
    printf 'Would remove: %s\n' "$target"
  else
    rm -rf -- "$target"
  fi
}

remove_desktop_entry() {
  if [[ "$DRY_RUN" == true ]]; then
    printf 'Would remove desktop entry: %s\n' "$DESKTOP"
  else
    rm -f -- "$DESKTOP"
  fi
}

remove_desktop_entry
remove_tree "$PREFIX"

if [[ "$PURGE_DATA" == true ]]; then
  remove_tree "$CONFIG"
  remove_tree "$STATE"
  remove_tree "$LOG"
  echo "CYBER-OS overlay and requested data paths removed."
else
  echo "Preserved configuration: $CONFIG"
  echo "Preserved state:         $STATE"
  echo "Preserved logs:          $LOG"
  echo "CYBER-OS overlay removed; runtime data was preserved."
fi
