---
name: connect-mollie-and-sendcloud
description: Connecting Mollie payments and Sendcloud shipping to a mitstack app without the key passing through the AI tool. Use when the builder wants their app to take payments or ship parcels.
---

# Connect Mollie and Sendcloud

A Mollie or Sendcloud key is a secret, so it never passes through this
conversation. The builder pastes it into the console, mitstack stores it
sealed, and a block that needs it receives it when the app is subscribed to
that block. Never ask the builder for the key, and never write one into the
app's repository. If the builder pastes a key here, tell them to revoke it
with the provider and create a new one.

## Find the blocks that use them

Call `list_blocks` and keep the blocks whose `connectsThrough` holds `mollie`
or `sendcloud`. Each of those receives that provider's key. Tell the builder
what each one does, from its `description`.

When no block connects through a provider, tell the builder plainly that
mitstack offers their org no block for it yet, so the app cannot receive that
key through mitstack today. Stop there for that provider.

## Connect the provider

The builder makes the connection on the console's Connections page, at
https://api.mitstack.dev/connections, which needs an owner or admin role.
There they choose Connect a service, find the provider's card, and paste the
key into it.

| Provider | Its card on the Connections page | Where the builder gets the key |
|---|---|---|
| Mollie | Always there. mitstack checks the key with Mollie as it is saved and refuses one Mollie rejects | The Mollie Dashboard, under Developers, then API keys |
| Sendcloud | There once a block visible to the org declares Sendcloud, and the card names each field it needs | Sendcloud's own settings |

## Subscribe the app to the block

Call `validate_composition` with the block's `blockId` and the app's `appId`,
which answers whether the connection is in place. Then call `subscribe` with
the `blockId` and the `appId`, and follow it with the check-app-status skill.
