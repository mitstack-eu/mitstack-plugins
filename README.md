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
| `create-an-app` | Choosing a stack, creating the app and subscribing it to the stack |
| `build-your-app` | Writing the app's code in its repository and deploying it through a pull request |
| `connect-mollie-and-sendcloud` | Connecting payments and shipping without the key passing through Claude Code |
| `check-app-status` | Whether the stack has finished and whether the latest change deployed |

Claude Code picks a skill when your request matches it, and you can also start
one by name, as in `/mitstack:create-an-app`.

## Check a change to this repository

This section is for a contributor changing the plugin. The CI workflow runs
these checks on every pull request, and you can run them locally the same way:

```sh
claude plugin validate --strict .
claude plugin validate --strict plugins/mitstack
scripts/check-plugin-names.sh
```

`scripts/check-plugin-names.sh` fails when a plugin's `name` or `displayName`
contains `claude` or `anthropic` in any case. Anthropic's terms bar its names
and marks from a third party's product name.
