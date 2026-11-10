#!/usr/bin/env bash
# Writes scripts/mcp-tools-list.json from the tools/list answer of the MCP server code in a platform checkout.
#
# Usage: scripts/refresh-mcp-tools-list.sh <platform checkout>
#
# The MCP server's code is the one source of its tool names and arguments, and
# it sits in a repository this one's CI cannot read. This script runs that code's
# own tools/list through a test file added by `go test -overlay`, which leaves
# the checkout untouched, and keeps each tool's name and argument names with the
# commit they came from, so check-skill-tools.py reads what the server serves.
set -euo pipefail

checkout="${1:?usage: scripts/refresh-mcp-tools-list.sh <platform checkout>}"
api="$(cd "$checkout/api" && pwd)"
out="$(cd "$(dirname "$0")" && pwd)/mcp-tools-list.json"
commit="$(git -C "$checkout" rev-parse HEAD)"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cat >"$work/print_tools_test.go" <<'GO'
package mcp_test

import (
	"context"
	"fmt"
	"testing"

	"github.com/mitstack/api/internal/mcp"
)

func TestPrintToolsList(t *testing.T) {
	s := &mcp.Server{Src: fakeSource{}, Name: "mitstack", Version: "print"}
	resp, _ := s.Handle(context.Background(), "org", []byte(`{"jsonrpc":"2.0","id":1,"method":"tools/list"}`))
	fmt.Printf("TOOLS_LIST %s\n", resp)
}
GO
jq -n --arg file "$api/internal/mcp/zz_print_tools_test.go" --arg src "$work/print_tools_test.go" \
  '{Replace: {($file): $src}}' >"$work/overlay.json"

(cd "$api" && go test -count=1 -v -overlay "$work/overlay.json" -run '^TestPrintToolsList$' ./internal/mcp/) >"$work/out.txt"
sed -n 's/^TOOLS_LIST //p' "$work/out.txt" | jq --arg commit "$commit" '{
  source: "the tools/list answer of the MCP server code at platform commit \($commit)",
  tools: [.result.tools[] | {name, inputSchema: {properties: ((.inputSchema.properties // {}) | map_values({}))}}]
}' >"$out"
echo "wrote $(jq '.tools | length' "$out") tools from platform commit $commit to $out"
