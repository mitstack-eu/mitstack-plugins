#!/usr/bin/env bash
# Fails when any plugin's name or displayName contains "claude" or "anthropic" in any case.
#
# Usage: scripts/check-plugin-names.sh [repository root, default .]
#
# Anthropic's terms bar its names and marks from a third party's product name,
# so a plugin listed in this marketplace may not carry them.
set -euo pipefail

root="${1:-.}"
shopt -s nullglob
manifests=("$root"/plugins/*/.claude-plugin/plugin.json)

if ((${#manifests[@]} == 0)); then
  echo "no plugin.json found under $root/plugins/*/.claude-plugin/" >&2
  exit 1
fi

status=0
for manifest in "${manifests[@]}"; do
  if ! marked="$(jq -r '
      [ {field: "name", value: .name}, {field: "displayName", value: .displayName} ][]
      | select(.value != null and (.value | test("claude|anthropic"; "i")))
      | "\(.field) \"\(.value)\""' "$manifest")"; then
    echo "$manifest: not valid JSON" >&2
    status=1
    continue
  fi
  if [[ -n "$marked" ]]; then
    while IFS= read -r line; do
      echo "$manifest: $line contains a Claude or Anthropic mark" >&2
    done <<<"$marked"
    status=1
  fi
done

if ((status == 0)); then
  echo "plugin names carry no Claude or Anthropic mark: ${manifests[*]}"
fi
exit "$status"
