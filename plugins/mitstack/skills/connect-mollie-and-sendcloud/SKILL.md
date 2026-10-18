---
name: connect-mollie-and-sendcloud
description: Connecting Mollie payments and Sendcloud shipping to a mitstack app through mitstack's own connect page, so no key passes through the AI tool. Use when the builder wants their app to take payments or ship parcels.
---

# Connect Mollie and Sendcloud

This skill connects Mollie, for payments, and Sendcloud, for shipping, to the
builder's org on mitstack. A key for either service is a secret, so it never
passes through this conversation. mitstack's connect page is the one place
the builder enters a Sendcloud key or approves Mollie's sign-in. A block that
needs the service reaches it once the app is subscribed to that block.

Never ask the builder for a key, and never write one into the app's
repository. If the builder pastes a key here, tell them to revoke it with the
provider and create a new one.

## Find the blocks that use them

Call `list_blocks` and keep the blocks whose `connectsThrough` holds `mollie`
or `sendcloud`. Each of those reaches that service once the org connects it.
Tell the builder what each one does, from its `description`.

When no block connects through a service, tell the builder plainly that
mitstack offers their org no block for it yet, so the app cannot reach that
service through mitstack today. Stop there for that service.

## See what the org holds

Call `list_capabilities` and read the entries whose `slug` is `mollie` or
`sendcloud`. An entry whose `holding` reads `not-held` still needs
connecting. Any other holding means the org holds that service already, so go
straight to subscribing for it.

## Open the connect page

Call `connect_capability` with `capability` set to `mollie` or `sendcloud`.
It answers with the connect page for that service:

```json
{ "capability": "sendcloud", "url": "https://api.mitstack.dev/capabilities?capability=sendcloud" }
```

Open the `url` in the builder's browser, or give it to them to open when you
cannot. Signed in to mitstack, they finish the connection on that page.

| Service | What the builder does on the page |
|---|---|
| Mollie | Starts Mollie's sign-in and approves mitstack's access in Mollie, which returns them to the page with Mollie connected |
| Sendcloud | Enters the public and private key of their Sendcloud account. mitstack checks the pair with Sendcloud as it is saved, and refuses a pair Sendcloud rejects |

When the builder says they are done, call `list_capabilities` again. The
entry's `holding` reads something other than `not-held` once the connection
is in place. If it still reads `not-held`, ask what the page showed them.

## Subscribe the app to the block

Call `validate_composition` with the block's `blockId` and the app's `appId`,
which answers whether the connection is in place. Then call `subscribe` with
the `blockId` and the `appId`, and follow it with the check-app-status skill.
