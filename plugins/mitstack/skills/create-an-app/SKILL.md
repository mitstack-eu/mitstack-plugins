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
this conversation. The Connections page at
https://api.mitstack.dev/connections holds every connection. For a service
such as Mollie or Sendcloud, call `connect_capability` with the `capability`
slug, as `list_capabilities` lists it, for the link to that one service's
page, and open it for the builder.

## Steps

1. Call `list_stacks`. Show the builder each stack's `name` and
   `description`, and the connections its `capabilitiesToConnect` names, and
   let them pick one. Keep its `id` as the `stackId`.
2. When no stack holds the blocks the builder wants, call `create_stack` with
   the stack's `name`, a `category` and the `blockIds`, as `list_blocks`
   lists them. The category is a free label, and the console writes `Runs on`
   for a stack an app runs on. Keep the `id` it returns as the `stackId`.
3. Ask whether the app's code is already in a GitHub repository. If it is,
   note the repository as owner/name. mitstack reaches a repository through
   its GitHub App, which the org's GitHub connection installs, so the
   repository must be one that installation may read.
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
8. Before the first deploy, save each value the app's code reads at start, as
   the part "Give the app its values" below shows. An app missing one fails
   that deploy.
9. Call `subscribe` with the `appId`, the `stackId` and `params`, which holds
   each input from step 6 by its name, as in
   `{"releaseCommand": "<the builder's command>"}`. Keep the `subscriptionId`
   it returns.
10. Follow the work with the check-app-status skill until the status is
    `active` or `failed`.

## Give the app its values

Each value the app's code reads, such as an environment variable, has one of
three sources. The report of the prepare-a-php-repository skill names each
value and its source. Without that report, ask the builder which names the
code reads, and give each name its source from this table:

| The value | Where it comes from | What you do |
|---|---|---|
| A database value, such as `DB_HOST` | The app's database part gives it | Nothing, since the stack hands it over |
| A key the app needs made once, such as an encryption or signing key | mitstack makes it and shows it to nobody, this conversation included | Call `generate_app_secret` with the `appId`, the `name`, `bytes` and `prefix` |
| A value the builder already holds, such as an outside service's key | The builder's own file or environment | Call `set_app_secret` with the `appId`, the `name` and `value`, read from that file |

A secret's `name` is lower-case letters, digits and hyphens, and it reaches the
app upper-cased with underscores, so `app-key` reaches it as `APP_KEY`.

Take `bytes` and `prefix` from the app's own code, from the line that checks
the key. A check that the key decodes to 32 bytes asks for `bytes` of 32, and
one that the key starts with `base64:` asks for that `prefix`. When the code
checks neither, leave both out, and mitstack draws 32 bytes and stores their
base64.

Never ask the builder to paste a value into this conversation, and never write
one in a message. Ask which file holds a value the builder already has. After
their yes, read that one line, as `sed -n 's/^SMTP_PASSWORD=//p' .env` does
for `SMTP_PASSWORD`, and pass it as `value` without the quotes around it.

Call `list_app_secrets` with the `appId` to confirm what is saved. It lists
each name and its version but never a value. A name the app already holds
keeps its value, and the write says so. Replacing one is a person's act, in
the Secrets section of the app's page in the console.

A value still missing shows in a failed deploy's reason, which `get_app`
answers, and in the log lines `get_app_logs` returns for the failed part. Save
the value as above and follow the app again. Saving it updates each part of
the app's stack that receives the app's secrets, with no new commit. On a
Docker host, the host then runs the release command again.

Nobody logs in to a host mitstack manages, over SSH or any other way, or edits
a file there, because mitstack writes the app's environment there from the
saved secrets and replaces any change made by hand.

## Once the app is active

`get_app` with the `appId` answers with the clone address of the app's code
repository and the address it is live at. The build-your-app skill takes the
builder from there to their own code running live.

## When a step is refused

Every refusal comes back as an error result whose text says what to change.
Read it to the builder in plain words, fix the call when the text says how,
and ask the builder only for what a call cannot supply.
