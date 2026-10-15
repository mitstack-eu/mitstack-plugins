---
name: build-your-app
description: Building a mitstack app's code in a clone of its repository and deploying it with a push. Use when the builder wants to write, change or ship the code of an app they created on mitstack.
---

# Build your app and deploy it

You write the app's code yourself, in a clone of the repository mitstack made
for the app. mitstack sees only what is pushed, and a push to the default
branch builds and deploys it through the stack's pipeline. This describes the
stacks with the `managed-ci` and `managed-cd` blocks, such as `web-app-aws`.
For any other stack, read its blocks with `plan_stack` and `get_manifest`
first, and tell the builder how it deploys before you change anything.

## Steps

1. Ask the builder for the repository address. It is on the app's page in the
   console, at `https://api.mitstack.dev/apps/<appId>`, under Repository. No
   tool returns it, and it appears once the stack subscription is active.
2. Clone it with `gh repo clone <owner>/<repo>` and work inside the clone. The
   builder's GitHub account needs write access to push.
3. Ask the builder what the app should do, in their own words, and build it in
   small steps they can see. Keep the `Dockerfile`, since the build makes the
   app's image from it.
4. Run the app's tests before each push. The build runs `go test` when the
   repository holds a `go.mod` and `npm test` when it holds a `package.json`,
   and a failing test stops it before anything is deployed.
5. Commit, and push to the default branch. A pull request is built and checked
   but not deployed, and a push to any other branch starts nothing.
6. Follow the build with the check-app-status skill, then open the app's
   address with the builder to see the change live.

## What to leave alone

Leave `.mitstack/` and the `mitstack-*.yml` workflows as they are, since every
subscribe, upgrade and retry of the stack rewrites them. Add no workflow of
your own under `.github/workflows/`, because the same runs remove every other
file there. The build itself lives in the `<app>-ci` repository and the deploy
in `<app>-cd`, which the platform owns.

Put no secret, such as an API key or a password, in the repository. Every
member of the repository can read it, and so can everything that builds it.
