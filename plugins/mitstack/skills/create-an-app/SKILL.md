---
name: create-an-app
description: Creating an app on mitstack and subscribing it to a stack, from choosing the stack to the app's first live address, on a new repository or one the builder already has. Use when the builder asks to start, create or set up an app on mitstack, or to put their existing repository on mitstack.
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
connections the builder makes in mitstack's console, so no key passes through
this conversation. Call `connect_capability` with the `capability` slug, as
`list_capabilities` lists it, for the link to that connection's page, and open
it for the builder. The Connections page at
https://api.mitstack.dev/connections holds every connection.

## Steps

1. Call `list_stacks`. Show the builder each stack's `name` and
   `description`, and the connections its `capabilitiesToConnect` names, and
   let them pick one. Keep its `id` as the `stackId`.
2. When no stack holds the blocks the builder wants, call `create_stack` with
   the stack's `name`, a `category` and the `blockIds`, as `list_blocks` lists them.
   The console writes `Runs on` as the category of a stack an app runs on. Keep
   the `id` it returns as the `stackId`.
3. Ask whether the app's code is already in a GitHub repository. If it is,
   note the repository as owner/name. It must be a repository the org's
   mitstack GitHub App installation reaches.
4. Call `validate_composition` with the `stackId` and `appName`, the name the
   new app will have. For an app that exists, pass `appId` in place of
   `appName`. When `ok` is false, each entry in `missing` names something the
   org has not connected yet. Tell the builder what to connect, and call the
   tool again once they have.
5. Call `plan_stack` with the `stackId`. Tell the builder in one plain sentence
   per block what it builds, taken from the block's `description` in
   `list_blocks`.
6. Call `get_manifest` with each block's `id`. After the manifest, the answer
   lists the inputs a subscribe takes, each with its default and its allowed
   values. Ask the builder for each input whose default does not fit their
   app, such as the command that runs at each release.
7. Call `create_app` with the app's `name`, the `stackId` and `repo`, the
   builder's repository as owner/name, and keep the `appId` it returns.
   mitstack adds its own files beside the builder's and never deletes the
   repository. Leave out `repo` only when the builder wants a new repository,
   which mitstack then makes.
8. Call `subscribe` with the `appId`, the `stackId` and `params`, which holds
   each input from step 6 by its name, as in
   `{"releaseCommand": "<the builder's command>"}`. Keep the `subscriptionId`
   it returns.
9. Follow the work with the check-app-status skill until the status is
   `active` or `failed`.

## Once the app is active

`get_app` with the `appId` answers with the clone address of the app's code
repository and the address it is live at. The build-your-app skill takes the
builder from there to their own code running live.

## When a step is refused

Every refusal comes back as an error result whose text says what to change.
Read it to the builder in plain words, fix the call when the text says how,
and ask the builder only for what a call cannot supply.
