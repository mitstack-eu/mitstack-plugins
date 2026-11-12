---
name: create-an-app
description: Creating an app on mitstack and subscribing it to a stack, from choosing the stack to the app's first live address, on a new repository or one the builder already has, with each value the app's code reads. Use when the builder asks to start, create or set up an app on mitstack, to put their existing repository on mitstack, or to give an app a key or another value it reads, such as one a failed deploy says is missing. Use it too when the builder asks to run a one-off admin command in a live app, such as adding a user to its table.
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
connections the builder makes in mitstack's console, so no account key passes
through this conversation. The Connections page at
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
three sources. For a PHP app, the report the prepare-a-php-repository skill
writes names each variable and its source. Without that report, ask the
builder which names the code reads. Then give each name its source from this
table. A part is one block of the app's stack, as `get_app` lists it.

| The value | Where it comes from | What you do |
|---|---|---|
| A database value, such as `DB_HOST` | The app's database part, such as `docker-mariadb`, gives it | Nothing, since the stack hands it over |
| A key the app needs made once, such as an encryption or signing key | mitstack makes it and shows it to nobody, this conversation included | Call `generate_app_secret` with the `appId`, the `name`, `bytes` and `prefix` |
| A value the builder already holds, such as an outside service's key | The builder's own file or environment | Call `set_app_secret` with the `appId`, the `name` and `value`, read from that file |

A secret's `name` is lower-case letters, digits and hyphens, and it reaches the
app upper-cased with underscores. So the variable `APP_KEY` takes the name
`app-key`, and `SMTP_PASSWORD` takes `smtp-password`.

Take `bytes` and `prefix` from the line of the app's own code that checks the
key. In a clone, this command lists the file and line number of each line
naming `APP_KEY`, and prints no code:

```sh
git grep -nIw APP_KEY -- . ':(exclude,glob)**/vendor/**' ':(exclude,glob)**/.env*' | cut -d: -f1,2
```

Read a line it names only with its quoted text masked, as the
prepare-a-php-repository skill's rule 2 and its prefix command show. A check
that the key decodes to 32 bytes asks for `bytes` of 32, and one that the key
starts with `base64:` asks for that `prefix`. When the code checks neither,
leave both out, and mitstack draws 32 bytes and stores their base64.

mitstack draws a key only in that form, base64 behind an optional prefix. When
the code wants another, such as hex or a set count of characters, tell the
builder. They make that key themselves and save it as a value they hold.

Never ask the builder to paste a value into this conversation, and never write
one in a message to them. For a value the builder already has, ask to read
that one variable from the file that holds it, and say that the AI tool's
provider sees the value it reads. After their yes, read only that line, as
`sed -n 's/^SMTP_PASSWORD=//p' .env` does for `SMTP_PASSWORD`, and pass it as
`value` without the quotes around it.

Call `list_app_secrets` with the `appId` to confirm what is saved. It lists
each name and its version but never a value. A name the app already holds
keeps its value, and the write says so. Replacing one is a person's act, in
the Secrets section of the app's page in the console.

A value still missing shows in a failed deploy's reason, which the opening
sentence of `get_app` gives. It also shows in the log lines `get_app_logs`
returns with the `appId` and the `subscriptionId` of the part that failed.
Save the value as above and follow the app with the check-app-status skill.
Saving it updates each part of the app's stack that receives the app's
secrets, and the builder needs no new commit.

Nobody logs in to a host mitstack manages, over SSH or any other way, or edits
a file there, because mitstack writes the app's environment there from the
saved secrets and replaces any change made by hand.

## Once the app is active

`get_app` with the `appId` answers with the clone address of the app's code
repository and the address it is live at. The build-your-app skill takes the
builder from there to their own code running live.

## Run a command in the app

Some admin steps run once in a live app, such as adding a user to the app's
own users table. Run such a step through mitstack. It runs the command in a
fresh container made from the image the app serves, with the app's
environment, on the machine that runs the app, which mitstack calls the host.
A step that must run with every deploy, such as a migration, belongs in the
release command instead.

1. Read the app's code for what the command needs, such as the table, its
   columns and the variable names the code reads. Show the builder the command
   and what it changes, and run it only after their yes, since a command can
   change the live app's data.
2. Call `run_app_command` with the `appId` and the `command`. It answers the
   run's id at once. Leave out `subscriptionId` when one part of the app runs
   commands. On the stack App on a Hetzner Docker host that part is
   `docker-app-slice`. When the call is refused and lists several parts, call
   again with `subscriptionId` set to one of them, a part's `id` as `get_app`
   lists it. Leave out `process`, which names one container of the part,
   since `docker-app-slice` runs one, `web`, and refuses a run naming another.
3. The host usually starts the run within about a minute. Call `get_app_run`
   with the `appId` and the `runId` about every 20 seconds until its `status`
   reads `succeeded` or `failed`. Then tell the builder the exit code and the
   output under `result`, which holds at most the output's newest 8 KiB. A run
   that never reached its end, such as one refused or one the host did not
   answer within 30 minutes, holds `error` instead, so read that to them.

A part runs one command at a time, and refuses a second while the first runs.
The command is one line of at most 1,000 printable ASCII characters, and a
shell runs it, so `&&` and quotes work. Each run gets no input, so a command
that waits for an answer, such as the `mysql` client's own prompt, does not
work. When the builder asks for such a prompt, say so, and offer a one-line
command that does their step.

mitstack commits the command's text to the host's repository, the private
GitHub repository the host takes its work from, and Git history keeps it there.
mitstack also keeps each run for 90 days, with the command and who ran it.
So the command reads each secret from the app's environment by its variable's
name, as `getenv("DB_PASSWORD")` does in PHP. Never write a secret value into a
command or offer to, even one the builder typed into this conversation. Never
repeat such a value in a message, and never have a command print a secret.
When a command needs a secret the app does not hold yet, such as a new user's
password, save it first as the part "Give the app its values" shows. The
command then reads it by its name.

This command is a template. It adds a user to a `users` table with `name` and
`email` columns, and reads every database value by the names the app's
database part gives. Put in the app's own table, columns and variable names:

```sh
php -r '$p=new PDO("mysql:host=".getenv("DB_HOST").";port=".getenv("DB_PORT").";dbname=".getenv("DB_NAME"),getenv("DB_USER"),getenv("DB_PASSWORD"));$p->prepare("INSERT INTO users (name,email) VALUES (?,?)")->execute(["Ada","ada@example.com"]);echo "inserted id ",$p->lastInsertId(),PHP_EOL;'
```

Any member of the org may run a command. A builder without an AI tool runs the
same command in the Commands panel on the app's page in the console. Nobody
logs in to the host to run one.

## When a step is refused

Every refusal comes back as an error result whose text says what to change.
Read it to the builder in plain words, fix the call when the text says how,
and ask the builder only for what a call cannot supply.
