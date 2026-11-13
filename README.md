# mitstack-plugins

This repository is mitstack's plugin marketplace for Claude Code. It holds one
plugin, `mitstack`, for a builder who wants to create and run apps on mitstack
from Claude Code. The plugin connects Claude Code to mitstack's MCP server at
`https://api.mitstack.dev/v1/mcp`, the address through which Claude Code calls
mitstack's tools. It also adds skills that walk you from an empty
organisation on mitstack to a live app.

## Install the plugin

You need Claude Code installed and a mitstack account. Run these two commands
in a terminal. The first adds this repository as a marketplace, and the second
installs the plugin from it.

```sh
claude plugin marketplace add mitstack-eu/mitstack-plugins
claude plugin install mitstack@mitstack
```

Then start Claude Code, run `/mcp`, choose `plugin:mitstack:mitstack`, and
sign in and approve in the browser that opens. Claude Code holds the sign-in
from then on.

## What the skills cover

| Skill | What it walks you through |
|---|---|
| `create-an-app` | Choosing a stack, creating the app on a new repository or one you already have, and subscribing it to the stack |
| `build-your-app` | Writing the app's code in its repository and deploying it through a pull request |
| `connect-mollie-and-sendcloud` | Connecting payments and shipping without the key passing through Claude Code |
| `check-app-status` | Whether the stack has finished and whether the latest change deployed |
| `prepare-a-php-repository` | Checking an existing PHP repository on your own machine, ending in a report with no code in it, with nothing sent to mitstack |
| `build-a-block` | Creating a block, the service that makes GitHub resources for each app, writing its code from your description, and explaining each failure of `blockverify`, the check a block must pass |

Claude Code picks a skill when your request matches it, and you can also start
one by name, as in `/mitstack:create-an-app`.

## Check a change to this repository

This section is for a contributor changing the plugin. The CI workflow runs
these checks on every pull request, and you can run them locally the same way:

```sh
claude plugin validate --strict .
claude plugin validate --strict plugins/mitstack
scripts/check-plugin-names.sh
scripts/check-skill-tools.py
```

`scripts/check-plugin-names.sh` fails when a plugin's `name` or `displayName`
contains `claude` or `anthropic` in any case. Anthropic's terms bar its names
and marks from a third party's product name.

`scripts/check-skill-tools.py` fails when a skill names an MCP tool or a tool
argument that mitstack's MCP server does not serve, or says that no tool does
something. A builder following such a skill would call a tool that fails, or
leave their AI tool for an answer a tool already gives. The check reads each
tool and its arguments from `scripts/mcp-tools-list.json`, the server's
`tools/list` answer. In the check, a tool is a code span after "call", or a
snake_case code span starting with a served tool's first word. A tool's
arguments are the code spans in the list after its "with", as in:

```text
Call `create_app` with the app's `name`, the `stackId` and `repo`.
```

`scripts/mcp-tools-list.json` is written by `scripts/refresh-mcp-tools-list.sh`
from a checkout of mitstack's platform code, which is private. Run it there
whenever the server's tools change, and before a skill names a new tool:

```sh
scripts/refresh-mcp-tools-list.sh <platform checkout>
```

## How a merge reaches the board

This section is for a maintainer who works from an issue on mitstack's own
issue board, which is not public. An issue key such as `MIT-123` names one
issue on that board. A contributor without an issue leaves keys out, and a
maintainer adds one when the change closes an issue.

After a merge, once both checks pass on `main`, the `record delivery` job in
`.github/workflows/ci.yml` reads the subject of each commit the merge adds.
The subject is the first line of a commit message. A subject that starts with a
key and a colon, as in `MIT-123: summary`, moves that issue to Done, the
board's state for finished work. A key inside a `(refs MIT-123)` group only
references the issue and leaves it open. A merge whose subjects name no key
records nothing.

To close an issue, start each commit's subject with its key. A squash merge of
a pull request with several commits uses the pull request's title as its
subject, so start the title with the key as well.
