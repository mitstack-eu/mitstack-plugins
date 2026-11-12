---
name: check-app-status
description: Checking whether a mitstack app's stack has finished building and whether its latest change deployed. Use when the builder asks if their app is live, ready, deployed or broken, or to run a one-off command in a live app, such as adding a user to its database.
---

# Check an app's status

An app on mitstack has two things to check. The stack subscription says
whether the blocks have built the app's hosting and pipeline. The build and
deploy of the latest change say whether the builder's own code reached that
hosting.

## The stack subscription

Call `get_app` with the `appId`. When the id is not in this conversation,
`list_apps` lists the org's apps. The answer opens with a plain sentence on the
app's state, such as "all 6 parts of its stack are ready". It then names the
app's repository, the clone address and the address the app is live at.

Under `stackSubscriptions`, each stack subscription carries a `status` and a
`progress` that counts its parts that are `active`. Its `children` are the
parts, one per block, each with its own `status` and `healthVerdict`. While a
status is `pending`, `validating` or `provisioning`, call again about once a
minute. Tell the builder when a status or the progress moves, rather than on
every call.

| Status | What to tell the builder |
|---|---|
| `pending`, `validating` or `provisioning` | The part is still being built, so check again in a minute |
| `active` | The part is built. Once every part is, the app is live at its address |
| `failed` | Read them the answer's opening sentence in plain words, then the part's log, below |
| `upgrading` | The part is moving to a newer version, so wait as for provisioning |

For a failed part, call `get_app_logs` with the `appId` and `subscriptionId`,
set to the part's `id`, for the newest lines of its log. Once the builder has
fixed the cause and agrees, call `retry_member` with the `appId` and
`stackSubscriptionId`, set to the stack subscription's `id`, which retries
every failed part.

When the sentence or the log names a value the app could not find, such as a
missing key, save that value as the create-an-app skill's part "Give the app
its values" shows, through `generate_app_secret` or `set_app_secret`. The save
needs no new commit and no change on the machine the app runs on. Follow the
app again with `get_app`, and when the part still reads `failed`, call
`retry_member` as above.

For a part whose health is not `healthy`, call `get_app` with the `appId` and
`healthHistory`, set to the part's `id`, for its health checks, newest first,
each with the resource it checked.

## A command in the running app

When the builder needs one admin step in a live app, such as adding a user to
its table, run it as the create-an-app skill's part "Run a command in the app"
shows. Call `run_app_command` with the `appId` and the `command`, then
`get_app_run` with the `appId` and the `runId` it answered, for the exit code
and output. Nobody logs in to the host for such a step.

Each run gets no input, so a command that waits for an answer, such as the
`mysql` client's own prompt, does not work. Offer a one-line command instead.
mitstack keeps each run for 90 days with its command and who ran it, and the
command's text stays in the host's Git history. So the command reads each
secret from the app's environment by its variable's name, such as
`DB_PASSWORD`, and never holds the value. When the builder types a value into
this conversation, never repeat it, and never put it in a command or offer to.

## The latest change

Call `get_app` with the `appId` and `ci: true` for the app's CI records and
its recent CI jobs, each with the runner it ran on.

On a stack with the `managed-ci` block, such as `web-app-aws`, the build
reports on each commit as a check named `managed-ci`. In a clone of the app's
repository, `gh pr checks` shows it for an open pull request. After the merge,
`gh api repos/<owner>/<repo>/commits/<sha>/check-runs` shows it for the merge
commit on the default branch. A failed check stops the deploy, and its log
says which step failed.

When the check passed but the app does not change, the deploy runs in the
`<app>-cd` repository, whose Actions tab holds the run.

For a stack without `managed-ci`, read its blocks' descriptions with
`plan_stack` and `get_manifest` to learn how it builds and deploys. Tell the
builder what you found there, and say so when the blocks do not describe it.
