---
name: build-your-app
description: Building a mitstack app's code in a clone of its repository and deploying it through a pull request. Use when the builder wants to write, change or ship the code of an app they created on mitstack.
---

# Build your app and deploy it

You write the app's code yourself, in a clone of the repository mitstack made
for the app. mitstack sees only what reaches that repository. Each change goes
in through a pull request, and merging it deploys the change through the
stack's pipeline.

This describes the stacks with the `managed-ci` and `managed-cd` blocks, such
as `web-app-aws`. For any other stack, read its blocks with `plan_stack` and
`get_manifest` first, and tell the builder how it deploys before you change
anything.

## Steps

1. Ask the builder for the repository address. The app's page in the console,
   at `https://api.mitstack.dev/apps/<appId>`, shows it after `Repository`. No
   tool returns it. Until mitstack has made it, the page reads "No repository
   yet — it is provisioned automatically on subscribe."
2. Clone it with `git clone` and work inside the clone. The builder's GitHub
   account needs write access to the repository. Opening and merging pull
   requests is easiest with the GitHub CLI, `gh`, signed in with
   `gh auth login`.
3. Ask the builder what the app should do, in their own words, and build it in
   small steps they can see. Keep the `Dockerfile`, since the build makes the
   app's image from it.
4. Run the app's tests before you push. The build runs `go test` when the
   repository holds a `go.mod` and `npm test` when it holds a `package.json`,
   and a failing test fails the build.
5. Commit on a new branch, push the branch, and open a pull request with
   `gh pr create`. The pull request is built and checked as `managed-ci`, and
   nothing is deployed yet.
6. Once `managed-ci` passes, merge the pull request with `gh pr merge`. The
   default branch accepts only a commit whose `managed-ci` check passed, so a
   direct push to it is refused. The merge starts the deploy.
7. Follow the deploy with the check-app-status skill, then open the app's
   address with the builder to see the change live.

## What to leave alone

Leave `.mitstack/` and the `mitstack-*.yml` workflows as they are, since every
subscribe, upgrade and retry of the stack rewrites them. Add no workflow of
your own under `.github/workflows/`, because the same runs remove every other
file there. The build itself lives in the `<app>-ci` repository and the deploy
in `<app>-cd`, which the platform owns.

Put no secret, such as an API key or a password, in the repository. Every
member of the repository can read it, and so can everything that builds it.
