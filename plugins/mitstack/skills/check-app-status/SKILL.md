---
name: check-app-status
description: Checking whether a mitstack app's stack has finished building and whether its latest push deployed. Use when the builder asks if their app is live, ready, deployed or broken.
---

# Check an app's status

An app on mitstack has two things to check. The stack subscription says
whether the blocks have built the app's hosting and pipeline. The build of the
latest push says whether the builder's own code reached that hosting.

## The stack subscription

Call `subscription_status` with the `subscriptionId` that `subscribe`
returned, and `stack: true` for a stack. When the id is not in this
conversation, ask the builder to open the app's page in the console at
`https://api.mitstack.dev/apps/<appId>`, since no tool lists an app's
subscriptions.

The answer carries a `status` and a `percent`. While the status is `pending`,
`validating` or `provisioning`, call again about once a minute. Tell the
builder when the percent moves, rather than on every call.

| Status | What to tell the builder |
|---|---|
| `active` | The stack is built, and the app's page shows its repository and address |
| `failed` | Read them the `failure` text in plain words. On the app's page, the failed block's card has a Troubleshoot button that shows the block's own error, and a Retry button |
| `upgrading` | The stack is moving to a newer version, so wait as for provisioning |

## The latest push

On a stack with the `managed-ci` block, such as `web-app-aws`, the build
reports on each commit as a check named `managed-ci`. In a clone of the app's
repository, `gh pr checks` shows it for a pull request, and
`gh api repos/<owner>/<repo>/commits/<sha>/check-runs` for a commit on the
default branch. A failed check stops the deploy, and its log says which step
failed.

When the check passed but the app does not change, the deploy runs in the
`<app>-cd` repository, whose Actions tab holds the run.

For a stack without `managed-ci`, read its blocks' descriptions with
`plan_stack` and `get_manifest` to learn how it builds and deploys. Tell the
builder what you found there, and say so when the blocks do not describe it.
