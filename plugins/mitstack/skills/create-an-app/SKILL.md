---
name: create-an-app
description: Creating an app on mitstack and subscribing it to a stack, from choosing the stack to the app's first live address. Use when the builder asks to start, create or set up an app on mitstack.
---

# Create an app on mitstack

You create the app with the mitstack MCP tools and then subscribe it to a
stack. A stack is a set of blocks that together build the app's hosting, its
code repository and its build and deploy pipeline. Subscribing starts that
work, and the app is live once every block has finished.

## Before you start

The builder signs in once. When a mitstack tool answers that it needs sign-in,
ask the builder to run `/mcp`, choose `plugin:mitstack:mitstack` and approve
in the browser that opens.

`create_app` and `subscribe` need an owner or admin role in the org. A refusal
that names a read-only role means an owner or admin has to take the step, or
raise the builder's role.

The blocks reach the builder's own accounts, such as AWS or GitHub, through
connections made in the console. The MCP server cannot make a connection, so
the builder makes each one on the Connections page at
https://api.mitstack.dev/connections.

## Steps

1. Ask the builder which stack the app runs on. No tool lists the stacks, so
   the builder reads the stack's id from the console's Marketplace at
   https://api.mitstack.dev/marketplace. The seeded Web App on AWS stack is
   `web-app-aws`.
2. Call `validate_composition` with the `stackId`. When `ok` is false, each
   entry in `missing` names something the org has not connected yet. Tell the
   builder what to connect on the Connections page, and call the tool again
   once they have.
3. Call `plan_stack` with the `stackId`. Tell the builder in one plain sentence
   per block what it builds, taken from the block's `description` in
   `list_blocks`.
4. Call `create_app` with the app's `name` and the `stackId`, and keep the
   `appId` it returns.
5. Call `subscribe` with the `stackId` and the `appId`, and keep the
   `subscriptionId` it returns.
6. Follow the work with the check-app-status skill until the status is
   `active` or `failed`.

## Once the app is active

The app's page in the console, at `https://api.mitstack.dev/apps/<appId>`,
shows the app's code repository under Repository. The build-your-app skill
takes the builder from there to their own code running live.

## When a step is refused

Every refusal comes back as an error result whose text says what to change.
Read it to the builder in plain words, fix the call when the text says how,
and ask the builder only for what a call cannot supply.
