---
name: check-app-status
description: Checking whether a mitstack app's stack has finished building and whether its latest change deployed. Use when the builder asks if their app is live, ready, deployed or broken.
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
| `active` | The part is built. Once every part is, the app is live at its address |
| `failed` | Read them the answer's opening sentence in plain words, then the part's log, below |
| `upgrading` | The part is moving to a newer version, so wait as for provisioning |

For a failed part, call `get_app_logs` with the `appId` and `subscriptionId`,
set to the part's `id`, for the newest lines of its log. Once the builder has
fixed the cause and agrees, call `retry_member` with the `appId` and
`stackSubscriptionId`, set to the stack subscription's `id`, which retries
every failed part.

For a part whose health is not `healthy`, call `get_app` with the `appId` and
`healthHistory`, set to the part's `id`, for its health checks, newest first,
each with the resource it checked.

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
