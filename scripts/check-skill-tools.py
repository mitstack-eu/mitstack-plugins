#!/usr/bin/env python3
"""Fails when a skill names an MCP tool or tool argument mitstack's MCP server does not serve, or says a tool is missing.

Usage: scripts/check-skill-tools.py [tools list, default scripts/mcp-tools-list.json] [repository root, default .]

A skill that names a tool the server lacks, or sends the builder to the
console for what a served tool answers, strands the builder mid-journey. The
tools list is the server's tools/list answer, so the check reads the same
names and arguments an MCP client is served.
"""
import json
import pathlib
import re
import sys

SPAN = re.compile(r"`([^`]+)`")
SNAKE = re.compile(r"^[a-z]+(?:_[a-z]+)+$")
CALL = re.compile(r"\bcalls?\s+`([^`]+)`", re.IGNORECASE)
# One argument in a call's list, as in "the app's `name`" or "`stack: true`".
ARG_ITEM = r"(?:(?:the|its|an?)\s+)?(?:[\w-]+'s\s+)?`([^`]+)`"
ARG_LIST = re.compile(
    r"\s+with\s+" + ARG_ITEM + r"((?:(?:\s*,\s*(?:and\s+)?|\s+and\s+)" + ARG_ITEM + r")*)"
)
ARG_NEXT = re.compile(r"(?:\s*,\s*(?:and\s+)?|\s+and\s+)" + ARG_ITEM)
IDENT = re.compile(r"^([A-Za-z][A-Za-z0-9]*)(?:\s*:.*)?$")
MISSING = re.compile(r"\bno\s+(?:MCP\s+)?tools?\b", re.IGNORECASE)


def load_tools(path):
    data = json.loads(path.read_text())
    tools = data.get("result", data)["tools"]
    return {t["name"]: set(t.get("inputSchema", {}).get("properties", {})) for t in tools}


def paragraphs(text):
    """Yields (offset, paragraph) for each prose paragraph, with line breaks as spaces and fenced blocks left out."""
    offset, fenced, start, lines = 0, False, None, []
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and line.strip():
            if start is None:
                start = offset
            lines.append(line)
            offset += len(line)
            continue
        if lines:
            yield start, "".join(lines).replace("\n", " ")
        start, lines = None, []
        offset += len(line)
    if lines:
        yield start, "".join(lines).replace("\n", " ")


def check_skill(path, tools, verbs):
    text = path.read_text()
    problems = []

    def report(offset, message):
        problems.append(f"{path}:{text.count(chr(10), 0, offset) + 1}: {message}")

    for start, para in paragraphs(text):
        prose = SPAN.sub(lambda m: " " * len(m.group(0)), para)
        for m in MISSING.finditer(prose):
            report(start + m.start(), f'says "{" ".join(m.group(0).split())}"; name the served tool that answers it instead')

        for m in SPAN.finditer(para):
            name = m.group(1)
            if SNAKE.match(name) and name.split("_")[0] in verbs and name not in tools:
                report(start + m.start(), f"names the tool `{name}`, which the MCP server does not serve")

        for m in CALL.finditer(para):
            name = m.group(1).split()[0]
            if name not in tools:
                if not (SNAKE.match(name) and name.split("_")[0] in verbs):
                    report(start + m.start(), f"calls `{name}`, which the MCP server does not serve")
                continue
            args = ARG_LIST.match(para, m.end())
            if not args:
                continue
            spans = [args.group(1)] + [a.group(1) for a in ARG_NEXT.finditer(args.group(2))]
            for span in spans:
                ident = IDENT.match(span.strip())
                if ident and ident.group(1) not in tools[name]:
                    report(start + m.start(), f"calls `{name}` with `{ident.group(1)}`, an argument `{name}` does not take")
    return problems


def main(argv):
    tools_path = pathlib.Path(argv[1] if len(argv) > 1 else "scripts/mcp-tools-list.json")
    root = pathlib.Path(argv[2] if len(argv) > 2 else ".")
    try:
        tools = load_tools(tools_path)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as err:
        print(f"{tools_path}: not a tools/list answer: {err}", file=sys.stderr)
        return 1
    skills = sorted(root.glob("plugins/*/skills/*/SKILL.md"))
    if not skills:
        print(f"no SKILL.md found under {root}/plugins/*/skills/*/", file=sys.stderr)
        return 1

    verbs = {name.split("_")[0] for name in tools}
    problems = [p for skill in skills for p in check_skill(skill, tools, verbs)]
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print(f"{len(skills)} skills name only the {len(tools)} tools and arguments in {tools_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
