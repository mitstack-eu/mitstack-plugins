---
name: build-a-block
description: Building a mitstack block from the builder's description of what it creates, from creating it to a passing blockverify run, with each failure explained in plain words. Use when the builder wants to build, write, test or fix a block, or asks why blockverify fails.
---

# Build a block

A block is a small web service, its operator, plus a manifest that declares
what it creates for each app that subscribes. `create_block` writes both into a
new GitHub repository, the scaffold, which leaves the builder one file to
write: `resources.go`. `blockverify`, the conformance suite the catalog runs
before it trusts a block, proves that file.

This skill covers blocks that create GitHub resources, the `github` core. For
a block whose resources are in AWS, Azure or anywhere else, tell the builder
plainly that this skill does not support that core yet, and stop.

## Before you start

The builder needs an owner or admin role in their mitstack org. They also need
the mitstack GitHub App connected in the console, mitstack's web app, at
https://api.mitstack.dev/connections. When a tool answers that it needs
sign-in, ask the builder to run `/mcp`, choose `plugin:mitstack:mitstack` and
approve in the browser.

Check the local tools, and fix what is missing before step 1:

```sh
go version
gh auth status
go env -w GOPRIVATE=github.com/mitstack-eu
gh auth setup-git
```

`go version` must name Go 1.22 or later, and must not contain `gccgo`, which
cannot build the kit. The kit, the library every block builds on, is a private
Go module. `GOPRIVATE` tells Go to fetch it straight from GitHub, and
`go env -w` keeps that setting for every later shell. `gh auth setup-git` lets
the fetch use the builder's GitHub login.

## Steps

1. Ask the builder what the block creates for each app, in their own words.
   Turn that into a name of 2 to 40 characters, a description of 10 to 240
   characters, and a list of resource types. Every type must start with
   `github.`, and the guided type is `github.repository`. For anything else,
   stop as described above.
2. Call `create_block` with `name`, `description` and `resources`, such as
   `{"name": "Docs Repository", "description": "Creates a private GitHub
   repository for the documentation of each app that subscribes.",
   "resources": ["github.repository"]}`. Keep the `blockId` and `repo` it
   returns.
3. Clone the repository with `gh repo clone <repo>` and work inside the clone.
   Run step 5 once on the untouched clone. Every suite but `resources` passes,
   and `resources` fails with `observed absent after subscribe, want present`,
   which step 4 fixes.
4. Write `resources.go` as the next section describes. Edit no other file,
   since the scaffold owns the rest and the suites check it.
5. Run the suite from the clone's root, at the kit version the block's
   `go.mod` requires:

   ```sh
   kit=$(go list -m -f '{{.Version}}' github.com/mitstack-eu/operator-kit/v2)
   go run "github.com/mitstack-eu/operator-kit/v2/blockverify@$kit" --standalone .
   ```

   The first run downloads the kit and the Go toolchain it asks for. The block
   passes when the last line starts with `VERDICT: PASS`.
6. For each line marked `✗`, tell the builder in two sentences what is wrong
   and what to change, from the table under "Reading a failure". Make the
   change, then run step 5 again.
7. Once it passes, commit `resources.go` on a branch and push it. Publishing
   the block, which runs the operator behind HTTPS, comes next. The console's
   guide at
   https://api.mitstack.dev/docs/how-to/author-and-publish-a-block#publish-a-block
   walks the builder through it.

## How to write resources.go

Copy `example-resources.go`, beside this file, as the starting point. It is
the finished file for one `github.repository`, and it passes every suite.
`manifest.yaml` lists the block's resources under `spec.resources`, each with
a `name` and a `type`. For each one, `resources.go` holds a Go type with these
three methods, and the `resources` table maps the resource's `name` to a value
of that type:

```go
func (r repository) Ensure(ctx context.Context, gh *ghapi.Client, d contract.Desired) (map[string]string, error)
func (repository) Observe(ctx context.Context, gh *ghapi.Client, ref contract.ResourceRef) (contract.Observation, error)
func (repository) Delete(ctx context.Context, gh *ghapi.Client, ref contract.ResourceRef) error
```

`d` is the subscribe or upgrade request: `d.SubscriptionID` names the
subscription, and `d.Secrets["github"]["owner"]` is the connected GitHub
organisation. `ref.Identity` is the map `Ensure` returned, which the scaffold
hands back to `Observe` and `Delete`.

| Method | It must |
|---|---|
| `Ensure` | Derive the name from `d.SubscriptionID`, create the resource only when GitHub answers 404, tag it with `tagRepository(ctx, gh, repo, d.SubscriptionID)`, and return its identity, such as `{"repo": "acme/sub-123-docs"}` |
| `Observe` | Ask GitHub at `ref.Identity` every time, and answer `contract.Present` with its outputs, or `contract.Absent` on a 404 |
| `Delete` | Delete the resource at `ref.Identity`, and count a 404 as success |

Send every GitHub call through the scaffold's
`callGitHub(ctx, gh, method, path, body, out)`, which returns the HTTP status.
The example's `suffix` field ends each repository's name, so give two
repositories in one block different suffixes.

Check by reading the code that `Ensure` tags, because blockverify at `v2.3.1`
passes a block that never does. The tag carries the subscription's id, and it
is how anything listing one subscription's resources finds this one.

The builder writes no credential and no generated value. The GitHub token
arrives with each call, and the resource's name comes from the subscription.

The scaffold's fake GitHub, in `fakegithub_test.go`, holds only repositories.
Another `github.` type also needs that fake taught to hold it, which this
skill does not guide yet. Tell the builder so before writing code for it.

## Reading a failure

`blockverify` prints one line per suite: `✓` for a pass, `✗` for a failure
and `○` for a skip, which still counts toward a pass. Match each `✗` line's
text against this table.

| Suite | The line contains | What is wrong | What to change |
|---|---|---|---|
| `resources` | `after subscribe, want present` | `Ensure` created nothing, or `Observe` could not find what `Ensure` made | Make `Ensure` create the resource and return its identity, and make `Observe` read GitHub at that identity |
| `resources` | `still observed present after the provider lost it` | `Observe` reports what `Ensure` did instead of asking GitHub | Make `Observe` call GitHub each time and answer absent on a 404 |
| `resources` | `after unsubscribe, want absent` | `Delete` returned success but removed nothing | Make `Delete` send GitHub's delete call for the identity, and accept 204 or 404 |
| `resources` | `has no entry for it` | The `resources` table lacks a resource the manifest declares | Add the resource's name and its type to the `resources` table |
| `resources` | `with no identity` | `Ensure` returned an empty identity | Return the identity, such as `{"repo": "owner/name"}`, from `Ensure` |
| `resources` | `did not name it in replaces` | An upgrade made a new resource instead of finding the existing one | Make `Ensure` derive the same name on every call and reuse what it finds |
| `resources` | `failed:` | One of the three methods returned an error, quoted after the colon | Fix the call that error names |
| `resources` | `has no TestDeclaredResources test` | `declared_resources_test.go`, the scaffold's test that drives each resource against the fake GitHub, is missing | Add it back as the scaffold wrote it: `git checkout $(git rev-list --max-parents=0 HEAD) -- declared_resources_test.go` |
| Several at once | `[build failed]` | The block does not compile | Run `go vet ./...`, fix the first error it names, and run the suite again |
| Several at once | `[setup failed]` | Go cannot resolve a module | Check that `go env GOPRIVATE` prints `github.com/mitstack-eu`, then run `go mod tidy` |
| `trust-plumbing` | `has no go.mod` or `is missing manifest.yaml` | The suite ran outside the block's root | Run it from the clone's root |
| `trust-plumbing` | `redeclares kit-owned symbol` | A function the kit owns is defined again in the block | Delete that function and use the kit's |
| `trust-plumbing` | `ghapi.Base` or `raw apiBase` | Code builds its own GitHub address | Send every GitHub call through `callGitHub` |
| `secret-safety` | `TestNoSecretLeak` | A secret, such as the GitHub token, reached a response or a log | Keep every value from `d.Secrets` out of errors, outputs and log lines |
| `teardown`, `contract`, `deliverable`, `manifest` or `naming` | Anything | A file the scaffold owns was changed or deleted | Restore it from the first commit with `git checkout $(git rev-list --max-parents=0 HEAD) -- <file>` |

When a line matches no row, read the whole line to the builder, say that this
skill does not cover it, and give the suite's name.
