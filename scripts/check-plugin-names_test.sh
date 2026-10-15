#!/usr/bin/env bash
# Tests that check-plugin-names.sh fails on any Claude or Anthropic mark in a plugin's name or displayName.
set -uo pipefail

checker="$(cd "$(dirname "$0")" && pwd)/check-plugin-names.sh"
failures=0

# run_case <description> <expected exit> <plugin.json content, or empty for no plugin>
run_case() {
  local description="$1" want="$2" manifest="$3"
  local root
  root="$(mktemp -d)"
  if [[ -n "$manifest" ]]; then
    mkdir -p "$root/plugins/example/.claude-plugin"
    printf '%s\n' "$manifest" >"$root/plugins/example/.claude-plugin/plugin.json"
  fi

  local output got
  output="$("$checker" "$root" 2>&1)"
  got=$?

  if [[ "$got" != "$want" ]]; then
    printf 'FAIL %s: exit %s; want %s\n  manifest: %s\n  output: %s\n' "$description" "$got" "$want" "$manifest" "$output"
    failures=$((failures + 1))
  else
    printf 'ok   %s\n' "$description"
  fi
  rm -rf "$root"
}

run_case "a plain name and displayName pass" 0 '{"name":"mitstack","displayName":"mitstack"}'
run_case "a plugin without displayName passes" 0 '{"name":"mitstack"}'
run_case "claude in the name fails" 1 '{"name":"claude-helper","displayName":"mitstack"}'
run_case "Claude in the displayName fails" 1 '{"name":"mitstack","displayName":"mitstack for Claude"}'
run_case "ANTHROPIC in upper case in the name fails" 1 '{"name":"my-ANTHROPIC-tools"}'
run_case "anthropic in mixed case in the displayName fails" 1 '{"name":"mitstack","displayName":"AnThRoPiC kit"}'
run_case "claude inside a longer word fails" 1 '{"name":"mitstackclaudetools"}'
run_case "a repository with no plugin.json fails" 1 ''
run_case "a plugin.json that is not JSON fails" 1 '{"name":'

if ((failures > 0)); then
  printf '%d case(s) failed\n' "$failures"
  exit 1
fi
printf 'all cases passed\n'
