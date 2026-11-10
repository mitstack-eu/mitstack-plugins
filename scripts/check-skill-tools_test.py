#!/usr/bin/env python3
"""Tests that check-skill-tools.py fails on a skill naming a tool or argument the tools list lacks, or saying a tool is missing."""
import json
import pathlib
import subprocess
import sys
import tempfile

CHECKER = pathlib.Path(__file__).resolve().parent / "check-skill-tools.py"

TOOLS = {
    "tools": [
        {"name": "list_stacks", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "create_app", "inputSchema": {"type": "object", "properties": {"name": {}, "stackId": {}, "repo": {}}}},
        {"name": "subscribe", "inputSchema": {"type": "object", "properties": {"appId": {}, "stackId": {}, "params": {}}}},
        {"name": "get_app", "inputSchema": {"type": "object", "properties": {"appId": {}, "ci": {}}}},
    ]
}

failures = 0


def run_case(description, want, skill, tools=TOOLS):
    """Runs the checker over one skill holding the given text, and expects the given exit and, on failure, a phrase in its output."""
    global failures
    want_exit, want_text = want
    with tempfile.TemporaryDirectory() as root:
        tools_path = pathlib.Path(root, "tools.json")
        tools_path.write_text(tools if isinstance(tools, str) else json.dumps(tools))
        if skill is not None:
            skill_path = pathlib.Path(root, "plugins/example/skills/example/SKILL.md")
            skill_path.parent.mkdir(parents=True)
            skill_path.write_text(skill)
        run = subprocess.run([sys.executable, str(CHECKER), str(tools_path), root], capture_output=True, text=True)
    output = run.stdout + run.stderr
    if run.returncode != want_exit or (want_text and want_text not in output):
        print(f"FAIL {description}: exit {run.returncode}; want {want_exit} naming {want_text!r}\n  output: {output}")
        failures += 1
    else:
        print(f"ok   {description}")


PASS = (0, "")

run_case("served tools with served arguments pass", PASS,
         "1. Call `list_stacks`.\n2. Call `create_app` with the app's `name`, the `stackId` and `repo`, and keep the `appId` it returns.\n")
run_case("a call to a tool the server lacks fails naming it", (1, "`list_stack`"),
         "Call `list_stack` and show each stack.\n")
run_case("a mention of an unserved tool with a served verb fails naming it", (1, "`get_apps`"),
         "Read the app through `get_apps`.\n")
run_case("a call to an unserved one-word tool fails naming it", (1, "`subscrib`"),
         "Then call `subscrib` with the `appId`.\n")
run_case("an argument the tool lacks fails naming the tool and the argument", (1, "`create_app` with `repository`"),
         "Call `create_app` with the `name` and the `repository`.\n")
run_case("a key and value span is checked by its key", (1, "`get_app` with `stack`"),
         "Call `get_app` with the `appId` and `stack: true`.\n")
run_case("a served key and value span passes", PASS,
         "Call `get_app` with the `appId` and `ci: true`.\n")
run_case("an argument list wrapped across lines is checked", (1, "`subscribe` with `blockId`"),
         "Call `subscribe` with the `appId`\nand the `blockId`.\n")
run_case("a value after set to or such as is not an argument", PASS,
         "Call `subscribe` with `params` set to `releaseCommand` or `appName`, such as `stackName`.\n")
run_case("saying no tool lists something fails", (1, "No tool"),
         "No tool lists the stacks, so read them in the console.\n")
run_case("saying no MCP tool does something fails", (1, "no MCP tool"),
         "There is no MCP tool for that.\n")
run_case("a code identifier from another language passes", PASS,
         "The image adds `pdo_mysql`, and a page calling `mysql_connect` answers 500.\n")
run_case("a fenced block is not read", PASS,
         "Run this:\n\n```\nCall `list_stack` with `nothing`. No tool here.\n```\n")
run_case("a JSON-RPC response around the tools list is read", PASS,
         "Call `list_stacks`.\n", {"jsonrpc": "2.0", "id": 1, "result": TOOLS})
run_case("a repository with no SKILL.md fails", (1, "no SKILL.md"), None)
run_case("a tools list that is not JSON fails", (1, "not a tools/list answer"), "Call `list_stacks`.\n", '{"tools":')

if failures:
    print(f"{failures} case(s) failed")
    sys.exit(1)
print("all cases passed")
