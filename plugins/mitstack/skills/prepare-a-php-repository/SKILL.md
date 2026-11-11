---
name: prepare-a-php-repository
description: Checking an existing PHP repository on the builder's own machine for what mitstack's build, image and Docker host will refuse or trip over, ending in a report with no code in it. Use when the builder wants to prepare a PHP app for mitstack before connecting anything.
---

# Prepare a PHP repository for mitstack

This procedure is for a builder with an existing PHP app bound for App on a
Hetzner Docker host, the mitstack stack that runs one app in Docker on an
org's own server. A stack is a set of managed services, and an org is your
organisation's account on mitstack. You need no org or server to follow this
file. You walk its checks over your own checkout, fix what you choose, and end
with a report. The report names what mitstack would refuse or trip over, each
with its fix, and holds none of your code.

You can follow this file by hand in a terminal, with no mitstack account. In
Claude Code, start it as `/mitstack:prepare-a-php-repository`. Where this file
says the builder, it means you: by hand, you decide each step and write the
report yourself, and under an AI tool, the tool asks you.

A block is one of those managed services. `managed-ci` builds your image,
`app-scaffold` commits the files that build needs, `docker-app-slice` runs your
container, and `docker-mariadb` runs your database. Every check was read from
these block versions, and the report repeats this line so its reader knows
which versions its verdicts describe:

`Read at managed-ci 2.15.1, docker-app-slice 0.11.0, docker-mariadb 0.5.0, app-scaffold 2.8.0.`

## What leaves your machine

Nothing in this procedure reaches mitstack. It calls no mitstack MCP tool, and
it needs no network. A person following it by hand sends nothing anywhere.
Under an AI tool, that tool's provider sees what the tool reads, under your own
account.

Four rules keep your code and your values out of what is read:

1. Run only the commands in this file. They print a file and a line number, or
   a variable's name, and never a value.
2. Under an AI tool, open no source file whole, since a password you have not
   found yet could sit in it. To see the shape of one line, print it with its
   strings masked by this command, replacing `FILE` and `LINE`:

   ```sh
   sed -n 'LINEp' FILE | sed -E "s/'[^']*'/'***'/g; s/\"[^\"]*\"/\"***\"/g"
   ```

3. Never open `.env` or a file like it. `.env.example` is the one exception,
   and the scan reads only the variable names in it.
4. Change a file only after the builder says yes to that one change. Show a
   change with `git diff --stat`, because `git diff` prints the old line.

## What judges your repository

No dry run reads your code. A dry run is the check mitstack runs before it
creates anything, and you reach it once you have an account. The console's
Create wizard, at <https://api.mitstack.dev>, runs one as you fill in the app's
settings. It reads only the `Dockerfile` and `.env.example` on your
repository's default branch. A dry run for an existing app, through mitstack's
MCP tools for AI assistants, reads the same two files, and so does subscribe,
the step that adds the stack to an app.

The verdict on everything else is the first build, and then the app's health on
the host. That build starts when you create the app from your repository in the
console, whose Guide column walks you through each step. Its result shows as
the `managed-ci` check on your pull request, and the check's log lives in the
app's build repository, `<app>-ci`, beside yours. The first deploy also sets up
a new database.

The build runs a series of gates, each one a check that can fail it, such as
`gitleaks` for secrets, Semgrep for code and Trivy for the image. This file can
miss something. A check it misses still meets its gate, and that gate's last log
line names what steers it.

This file does not check the host's room, which is the CPU, memory and disk left
on the server, or your org's limits. The dry run judges those, so you learn them
in the Create wizard once you have an account and a host.

## Run the scan

Run this whole block from the root of your checkout. It needs only `git`,
`grep`, `sed`, `sort` and `cut`, and it reads the committed files, since the
image holds only those.

```sh
hits() { git grep -nIE "$@" -- . ':(exclude,glob)**/vendor/**' ':(exclude,glob)**/node_modules/**' ':(exclude,glob)**/.env*' | cut -d: -f1,2; }
src() { git grep -nIE "$@" -- '*.php' '*.inc' '*.phtml' ':(exclude,glob)**/vendor/**' ':(exclude,glob)**/node_modules/**' ':(exclude,glob)**/tests/**' ':(exclude,glob)**/test/**' | cut -d: -f1,2; }
say() { printf '\n== %s\n' "$*"; }
say A1 image-source; git ls-files Dockerfile composer.json index.php public/index.php
say A2 own-dockerfile; [ -f Dockerfile ] && grep -nEi '^(FROM|EXPOSE)[[:space:]]' Dockerfile | cut -c1-80
say A3 php-constraint; [ -f composer.json ] && grep -n '"php"[[:space:]]*:' composer.json | cut -c1-80
say A4 composer-extensions; awk '/"require":[[:space:]]*\{/{b=1;next} b&&/\}/{b=0} b' composer.json composer.lock 2>/dev/null | grep -oE '"ext-[a-z0-9_-]+"' | sort -u
say A5 calls-gd; src '\b(imagecreate[a-z]*|imagepng|imagejpeg|imagegif|imagewebp)[[:space:]]*\('
say A5 calls-intl; src '\b(Collator|NumberFormatter|IntlDateFormatter|Normalizer|grapheme_[a-z]+)\b'
say A5 calls-zip; src '\bZipArchive\b'
say A5 calls-other; src '\b(SoapClient|bcadd|bcsub|bcmul|bcdiv|gmp_[a-z]+|ldap_[a-z]+|exif_[a-z_]+|socket_create|XSLTProcessor|pcntl_[a-z]+)\b'
say A6 removed-functions; src '\b(mysql_[a-z_]+|ereg[i]?|split|mcrypt_[a-z_]+|create_function)[[:space:]]*\('
say B1 first-page-setup; git grep -nIE "(header[[:space:]]*\([[:space:]]*['\"]Location|install\.php|setup\.php)" -- index.php public/index.php | cut -d: -f1,2
say C1 served-root; git ls-files public | head -1
say C2 reachable-files; git ls-files | grep -Ev '\.(php|inc|phtml|css|js|map|png|jpe?g|gif|svg|ico|webp|woff2?|ttf|eot|html?)$' | grep -Ev '(^|/)\.|^vendor/|/vendor/|^node_modules/|composer\.(json|lock)$' | head -40
say C3 short-open-tags; src '<\?([[:space:]]|$)'
say C4 export-ignore-lines; [ -f .gitattributes ] && grep 'export-ignore' .gitattributes | cut -d' ' -f1
say D1 ignored-files; git status --ignored --short | sed -n 's/^!! //p' | grep -Ev '(^|/)(vendor|node_modules)/?$' | head -40
say D2 submodules; git ls-files -s | sed -n 's/^160000 [0-9a-f]* [0-9]*[[:space:]]//p'
say D3 dockerignore; git show HEAD:.dockerignore 2>/dev/null | grep -vE '^[[:space:]]*(#|$)' | head -40
say E1 writes; src '\b(file_put_contents|fopen|mkdir|touch|tempnam|move_uploaded_file|rename|copy|unlink|session_save_path)[[:space:]]*\('
say E2 writes-in-own-folder; src '\b(file_put_contents|fopen|mkdir|touch|move_uploaded_file)[[:space:]]*\(.*(__DIR__|dirname|getcwd|\./)'
say E3 folders-named-for-writing; git ls-files | sed -n -E 's#^((cache|tmp|temp|uploads?|files|logs?|data|sessions|storage|bootstrap/cache)/).*#\1#p' | sort -u
say F1 hard-coded-credentials; hits -i "(\\\$[a-z_]*(pass|pwd|secret)[a-z_]*|db_pass[a-z_]*)['\"]?[[:space:]]*(=>?|,)[[:space:]]*['\"][^'\"]+['\"]"
say F2 connections-with-a-literal; src "(new[[:space:]]+(PDO|mysqli)|mysqli_connect)[[:space:]]*\(.*,[[:space:]]*['\"][^'\"]+['\"][[:space:]]*\)"
say F3 local-database-address; src "['\"=:](localhost|127\.0\.0\.1)(['\";:]|$)"
say F4 variable-names-read; git grep -ohIE "(getenv[[:space:]]*\(|_ENV\[|_SERVER\[)[[:space:]]*['\"][A-Za-z0-9_]+['\"]" -- '*.php' '*.inc' '*.phtml' ':(exclude,glob)**/vendor/**' | sed -E "s/.*['\"]([A-Za-z0-9_]+)['\"]/\1/" | grep -Ev '^(HTTP_|REQUEST_|REMOTE_|SERVER_|SCRIPT_|PHP_|QUERY_|DOCUMENT_|CONTENT_|argv|argc)' | sort -u
say G1 data-files; git ls-files '*.sql' '*.sql.gz' '*.dump' '*.sqlite' '*.sqlite3' '*.db' | head -20
say G2 generated-key-names; hits '_ibfk_[0-9]+'
say H1 env-example-names; [ -f .env.example ] && sed -n -E 's/^[[:space:]]*(export[[:space:]]+)?([A-Za-z_][A-Za-z0-9_]*)=.*/\2/p' .env.example
say H2 committed-env-files; git ls-files | grep -E '(^|/)\.env(\.|$)' | grep -v '\.env\.example$'
say I1 scan-output-from-request; src '\b(echo|print|printf|vprintf)\b.*\$_(GET|POST|REQUEST|COOKIE)'
say I2 scan-sql-from-request; src '(query|real_query|multi_query|exec)[[:space:]]*\(.*\$_(GET|POST|REQUEST|COOKIE)'
say I3 scan-command-from-request; src '\b(exec|system|passthru|shell_exec|popen|proc_open)[[:space:]]*\(.*\$_(GET|POST|REQUEST|COOKIE)'
say I4 scan-code-evaluation; src '\beval[[:space:]]*\('
say I5 scan-include-from-request; src '\b(include|require)(_once)?\b.*\$_(GET|POST|REQUEST|COOKIE)'
say I6 scan-unserialize-from-request; src 'unserialize[[:space:]]*\(.*\$_(GET|POST|REQUEST|COOKIE)'
say I7 scan-weak-password-hash; src -i '\b(md5|sha1)[[:space:]]*\([^)]*(passw|pwd)'
say J1 refused-scan-files; git ls-files .trivyignore trivy.yaml trivy-secret.yaml; git ls-files | grep -E '(^|/)osv-scanner\.toml$'
say J2 lockfiles; git ls-files | grep -E '(^|/)(composer\.lock|package-lock\.json|npm-shrinkwrap\.json)$' | grep -Ev '(^|/)(vendor|node_modules)/'
say K1 php-manifests; git ls-files | grep -E '^([^/]+/){0,2}composer\.json$' | grep -Ev '(^|/)(vendor|node_modules)/'
say K2 node-manifests; git ls-files | grep -E '^([^/]+/){0,2}package\.json$' | grep -v 'node_modules/'
say K3 phpunit-configs; git ls-files | grep -E '^([^/]+/){0,2}(phpunit\.xml|phpunit\.xml\.dist|phpunit\.dist\.xml)$' | grep -Ev '(^|/)(vendor|node_modules)/'
say K4 phpunit-required; git grep -nI '"phpunit/phpunit"' -- '*composer.json' ':(exclude,glob)**/vendor/**' | cut -d: -f1,2
say L1 default-branch; git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null
say M1 scheduled-or-background; git ls-files | grep -Ei '(cron|worker|supervisor|queue)' | grep -Ev '(^|/)(vendor|node_modules)/' | head -20; src '\b(pcntl_fork|set_time_limit[[:space:]]*\([[:space:]]*0)'
say N1 scaffold-paths; git ls-files .github/workflows/mitstack-ci.yml .mitstack/scaffold.lock
```

## Read the scan

Each row below names a section of the scan's output, what mitstack does, and
how to read it. An empty section reads `ok`, unless its row says otherwise.

| Scan | Check | What mitstack does today | Verdict and fix |
|---|---|---|---|
| A1 | The image's source | A root `composer.json`, `index.php` or `public/index.php` with no `Dockerfile` gets a contributed image, and any other repository with no `Dockerfile` gets none | None of the four files: `fix`, add a `Dockerfile` of your own. Otherwise `ok` |
| A2 | A `Dockerfile` of your own | Only a root `Dockerfile` counts. Its last stage must expose 8080, and the image must hold a shell and `wget` or `curl`, because the host probes with one of them | A last stage exposing only other ports: `fix`, listen on 8080 and change the `EXPOSE` line. A base image's contents read as `not read` |
| A3 | PHP version | The gates and the contributed image run PHP 8.5 | A constraint that excludes 8.5: `fix`, widen it and test on 8.5 |
| A4 | Extensions in Composer | `composer.lock` chooses the extensions, or `composer.json` when no lock is committed. An extension outside PHP's own source, such as `redis`, `imagick` or `apcu`, stops the build naming it | Such an extension: `fix`, install it in a `Dockerfile` of your own |
| A5 | Extensions with no Composer | The contributed image adds only `pdo_mysql` and `mysqli` unless Composer asks, beside what PHP's image holds, such as `curl`, `mbstring`, `openssl`, `sodium` and `sqlite3`. A page calling `gd`, `intl`, `zip`, `soap`, `bcmath`, `gmp`, `ldap`, `exif`, `sockets`, `pcntl` or `xsl` answers 500 with an empty page | Any hit whose extension A4 does not list: `fix`, add `composer.json` requiring it, as the fixes below show |
| A6 | Functions PHP removed | A page calling `mysql_connect` or another removed function answers 500 with an empty page | Any hit: `fix`, move that call to `mysqli` or PDO. `split` may be a method of your own, so read the masked line first |
| B1 | The health answer | `/` on port 8080 must answer below 400 with no setup step done first, or the deploy rolls back | A hit: `note`, `/` may send a new install to a setup page, so check what it answers. The answer itself reads `not read`, because the first deploy judges it |
| C1 | The served folder | `public/` is served when it holds files, and the root otherwise | `note` naming which one |
| C2 | What the web can reach | A root-served app serves every file in the image, except `vendor`, dot paths and `composer.json` and `composer.lock`. A `README.md` or a `Dockerfile` answers 200, and any `.php` file runs when requested | Listed files, of which the scan shows the first 40: `note`, with the fix of a `.dockerignore` entry for any you would not publish and the app does not read. Ask the builder, and a file they name reads `fix` |
| C2 | A missing address | A missing address that is not a `.php` file answers with your `index.php`, so a missing page reads 200 | `note` |
| C3 | Short open tags | The image's production `php.ini` turns them off, so a file opening with `<?` is sent to the browser as text, source and all | Any hit: `fix`, change `<?` to `<?php` |
| C4 | `export-ignore` lines | These lines shape your release archives only, and a marked file reaches the image | No defect. On a root-served app: `note`, each marked file you commit is also reachable, so add a `.dockerignore` entry for any you would not publish and the app does not read |
| D1 | Ignored files | The image holds the committed tree, so an ignored file is absent | Each listed file: `not read`, since only the builder knows whether the app needs it, with the fix of committing it or reading its values from the environment. A file like `.env` reads `note`, the image does not hold it, so its values must reach the app as secrets |
| D2 | Submodules | A submodule's files are absent from the image | Any hit: `fix`, commit those files or install them through Composer |
| D3 | `.dockerignore` | The image leaves out each file the committed `.dockerignore` lists. A listed file the app needs at run time is missing from the image, and the build still succeeds. A listed file that a `Dockerfile` of your own copies by name fails the build, naming that file | Entries listed: `note`, check each against the files the app reads at run time, because the build does not catch a missing one. None: `ok` |
| E1, E2, E3 | Writes in its own folder | The image runs as `USER 33:33` and root owns the app. The `Dockerfile` a new app receives lets that user write only in the folders that `writablePaths` names, a setting in the Create wizard holding a comma-separated list of folders, such as `cache,var/log`. A write anywhere else in the app's folder fails. The build creates a listed folder your repository lacks, and fails if that user cannot write one | An E2 hit: `fix`, write to the system's temporary folder, which that user can write to, or name its folder in the report's line and set `writablePaths` to it when you create the app. With a `Dockerfile` of your own, give that folder to the user your image runs as in that file instead. An E3 folder: `note`, a write there fails unless `writablePaths` names it. E1 hits whose target you cannot tell: one `not read` line per file |
| E1, E3 | Files that outlive a deploy | Each deploy starts a new container, so whatever the app writes is lost on each deploy, in a `writablePaths` folder too | Any file that must last, such as an upload: `fix`, keep it in the database or in outside storage |
| F1, F2 | A hard-coded database password | The host generates the password, so a hard-coded one cannot connect and answers error `1045`. A random-looking one stops the build first, at `gitleaks` | A hit on your app's database login: `fix`, read it from the environment. Any other hit, such as a test's: `note`, since `gitleaks` reads it too |
| F3, F4 | How it reads its database | Five values (`host`, `port`, `dbName`, `username`, `password`) reach the app as `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` and `DB_PASSWORD`. The database is `app`, the user is `app`, and the host is the database container's name, so `localhost` cannot connect | An F3 hit on a database setting: `fix`. An F3 hit you cannot place, even from its masked line: `not read`. A name in F4 for one of those values under another name: `fix`, rename it through `docker-mariadb`'s `env` setting in the Create wizard, one entry per name, as `DB_PASS=password,DB_LOGIN=username` |
| G1 | Schema and existing data | `releaseCommand`, a setting in the Create wizard, is one line of at most 1,000 printable characters, run on each new image before it serves. It can create your schema. No step imports an existing dump or existing files, so an app with data starts empty | Always `note`, in those words. Decide before you go live whether the app can start empty, because mitstack gives you no route for that data yet. A dump of your data that G1 lists: `fix`, naming the one you choose, remove it from the repository with `git rm`, or keep it and add it to `.dockerignore`, since a committed one reaches the image and a root-served app's web. Either way it stays in the git history, which `gitleaks` reads each Monday. A schema file the app reads stays: `note`. Whether your migrations run on the host reads as `not read` |
| G1 | The database engine | The database is MariaDB 12.3.3. A migration written for MySQL may fail there, a failed `releaseCommand` stops the deploy, and on a first deploy the app does not start | Always `not read`, because only the first deploy runs them |
| G2 | A foreign key's generated name | MariaDB 12.3.3 names a foreign key created with no name `1`, `2` and so on, where MariaDB 11.8 and 12.0 named it like `comments_ibfk_2`. A migration that drops `comments_ibfk_2` by that name stops on error `1091`, and the deploy stops with it | Any hit: `fix`, look the name up before each drop. Read `CONSTRAINT_NAME` from `information_schema.KEY_COLUMN_USAGE` for the current database, that table and that column, where `REFERENCED_TABLE_NAME` is set, and drop each name it gives |
| H1, H2, F4 | Secrets | A secret is a value your app reads and nobody should see, which mitstack keeps for the app once it exists. Its name is lower-case letters, digits and hyphens, and it reaches the app upper-cased with underscores, so `app-key` reaches it as `APP_KEY`. A clash with a value the database gives is refused. A variable the app needs at start goes in `.env.example`, which the dry run reads, and its value is saved before the first image lands | An F4 name missing from H1, or any F4 name when `.env.example` is absent, other than a database value the F3 and F4 row covers: `fix`, add it to `.env.example`. A name with lower-case letters: `fix`, since no secret can give it. An H2 file: `fix`, stop committing it. Each F4 and H1 name also takes a line naming where its value comes from, as the part after this table shows |
| I1 to I7 | Code scan | Seven rules: `php-output-from-request`, `php-sql-from-request`, `php-command-from-request`, `php-code-evaluation`, `php-include-from-request`, `php-unserialize-from-request` and `php-weak-password-hash`. A finding fails the build | Any hit: `fix`. I1: pass the value through `htmlspecialchars()`. I2: bind it with `prepare`. I3: pass it through `escapeshellarg()`, or choose from a fixed list. I4: write the logic as code. I5: choose the file from a fixed list. I6: use `json_decode()`, or pass `['allowed_classes' => false]`. I7: use `password_hash()` and `password_verify()`. These searches read one line, and Semgrep follows a value across lines, so an empty section reads as `not read` |
| None | Secrets and dependency scans | `gitleaks` reads the tree on each build and the whole history each Monday. Trivy refuses a fixable vulnerability of any severity, and `osv-scanner` refuses what its ignore lists do not hold | Always `not read`, because these need a network or the built image |
| J1 | Files a scan refuses | `.trivyignore`, `trivy.yaml` and `trivy-secret.yaml` at the root, and an `osv-scanner.toml` ignore of an advisory with a fix | A root Trivy file: `fix`, remove it. An `osv-scanner.toml`: `not read`, since the advisory lookup needs a network |
| J2 | Lockfiles | The dependency scans read each lockfile, and with none they have nothing to scan | No lockfile: `note`, the scans pass having read no dependency |
| K1, K3, K4 | The test gate | A `composer.json` within three levels runs `composer validate` and `composer install`, and any PHPUnit config beside it runs its suite, which needs `phpunit/phpunit` in `require-dev`. mitstack records a coverage floor for the app, which only rises | A config beside a K1 `composer.json` with no K4 hit in that folder: `fix`, add it to `require-dev`. A config with no `composer.json` beside it never runs: `note` |
| K2 | The Node gate | A `package.json` within three levels runs `npm install`, or `npm ci` with a lockfile, and then its build and test scripts | `note` naming each folder |
| K3 | The test database | `testSetupCommand` starts a throwaway MariaDB that hands over `DB_DATABASE` and `DB_USERNAME`, names that differ from the running app's `DB_NAME` and `DB_USER` | A suite that needs a database: `note`, read both pairs of names |
| L1 | How a change lands | The default branch requires the `managed-ci` check on an up-to-date branch, and a direct push is refused, for an admin too. Your pull request merges itself once the check passes and any review your branch requires is given, and the merge deploys | Always `note`: send each change through a pull request |
| M1 | One container | The host runs one `web` service, so a cron job or a worker has no place to run | Any hit: `fix`, run that work inside a request or outside this host |
| N1 | Files the scaffold writes | A first scaffold refuses to replace a file your branch already holds at a path it contributes | Any hit on a repository with no app yet: `fix`, rename or remove it. A contributed `Dockerfile` comes only when you hold none |
| None | GitHub App | Whether the mitstack GitHub App is installed on your repository | Always `not read`, because a checkout cannot answer it |

### Where each value comes from

Each variable your app reads has one of three sources, and the report's line
for it names which, with the verdict `note`, or `ok` for a database value.
Nothing is saved during this procedure, since the app does not exist yet, and
rule 3 holds throughout it. Once the app exists, the create-an-app skill saves
each value through mitstack's MCP tools, and nobody pastes a value into the
chat.

| The value | Where it comes from, once the app exists | The report line's fix |
|---|---|---|
| A database value, as the row on F3 and F4 names | The app's database part, the block `docker-mariadb` in its stack, gives it, so nothing is saved | `DB_HOST: the database part gives it` |
| A key the app needs made once, such as an encryption or signing key | mitstack makes it and shows it to nobody. The AI tool calls `generate_app_secret` with the `appId`, the `name`, `bytes` and `prefix`, which are the byte count and the leading text the app's own code checks the key for | `APP_KEY: generate it as app-key, 32 bytes, prefix base64:, as config.php:8 checks` |
| A value the builder already holds, such as an outside service's key | The builder's own file or environment. Under the create-an-app skill, the AI tool reads that one variable after the builder says yes, so its provider sees that value, and calls `set_app_secret` with the `appId`, the `name` and `value`. By hand, the builder saves it in the Secrets section of the app's page in the console | `SMTP_PASSWORD: set it as smtp-password from your own .env` |

To tell a key made once from a value the builder holds, find the lines that
name it with this command, replacing `NAME`. Print each one masked, as rule 2
shows, and the lines after it when the check sits there:

```sh
git grep -nIw NAME -- . ':(exclude,glob)**/vendor/**' ':(exclude,glob)**/.env*' | cut -d: -f1,2
```

A check that the key decodes to 32 bytes asks for `bytes` of 32. The masked
line hides quoted text, so print a leading text the check compares against
with this command, which shows only a short quoted text ending in a colon, such
as `'base64:'`:

```sh
sed -n 'LINEp' FILE | grep -oE "['\"][A-Za-z0-9._-]{1,15}:['\"]"
```

A check that the key starts with that text asks for it as `prefix`. When the
code checks neither, leave both out, and mitstack draws 32 bytes and stores
their base64. mitstack draws only that form. A key the code wants in another
form, such as hex, a set count of characters or a prefix this command does not
show, reads `not read`, and the builder makes it and saves it as a value they
hold. When you cannot tell where a value comes from, ask the builder.

Once the app exists, `list_app_secrets` confirms each saved name without its
value. A value still missing shows in the failed deploy's reason and in
`get_app_logs`, and the create-an-app skill says how to save it then.

Nobody logs in to a host mitstack manages, over SSH or any other way, or edits
a file there, because the host's agent, the program mitstack runs on it, writes
the app's environment from the saved secrets and replaces any change by hand.

## Write the report

The report gives one line per finding, and also one for each check that passes
or reads as `not read`. Each line gives the check, its verdict, a file and line
number or a variable name, and the fix. It holds no code and no value.

A verdict is one of four words:

| Verdict | Meaning |
|---|---|
| `ok` | The checkout shows no problem |
| `fix` | mitstack will refuse this or the app will fail, and the line names the fix |
| `note` | This works, and you should know about it |
| `not read` | A checkout cannot answer this, and the line names what judges it |

Open the report with the versions line above, then list the lines:

```text
Read at managed-ci 2.15.1, docker-app-slice 0.11.0, docker-mariadb 0.5.0, app-scaffold 2.8.0.
A hard-coded database password | fix | settings.php:12 | read it from the environment as DB_PASSWORD
Writes in its own folder | fix | export.php:30 | write to the system's temporary folder
Writes in its own folder | fix | upload.php:14 | set writablePaths to uploads when you create the app (your own edit)
What the web can reach | fix | backup/notes.txt | add backup/ to .dockerignore
Secrets and dependency scans | not read | none | the first build's managed-ci check judges these
```

An `ok` line says in a few words what was looked at. A check with two answers
takes two lines. Give a section with many hits one line per file, with its
first line number and the count. Past ten files, give one line with the first
three files and the total. Put a section of names, such as variables, on one
line, and past twenty names give the first ten and the total.

Mark a fix the builder declines with `(declined)` at the end of its line. A fix
with no command below is reported and not applied, and its line ends
`(your own edit)`.
End the report with a line naming the fixes made, or `Fixes made: none`. When
you stop part way, also list the checks that did not run, each as `did not run`.

## Offer the fixes

Offer each `fix` line that has a command below to the builder, one at a time. Apply a fix only after a
yes to that line. A declined fix changes nothing, and it stays in the report.

These commands make each change without printing a value. Replace `FILE`,
`LINE` and `PATH`.

| Fix | Command |
|---|---|
| Read a password assigned to a variable from the environment | `perl -pi -e 's/=\s*(["\x27]).*?\1\s*;/= getenv(\x27DB_PASSWORD\x27);/ if $. == LINE' FILE` |
| Write to the system's temporary folder | `perl -pi -e 's/__DIR__\s*\.\s*\x27\/[^\x27]*?([^\x27\/]+)\x27/sys_get_temp_dir() . \x27\/$1\x27/ if $. == LINE' FILE` |
| Change short open tags | `perl -pi -e 's/<\?(?=\s|$)/<?php/g' FILE` |
| Keep a file or folder from the image and the web, through the `.dockerignore` at the root, which counts once committed | `{ [ -s .dockerignore ] && [ -n "$(tail -c1 .dockerignore)" ] && echo; printf '%s\n' 'PATH'; } >> .dockerignore` |
| Ask for an extension with no `composer.json` yet, such as `gd` | `printf '{\n    "require": {\n        "ext-gd": "*"\n    }\n}\n' > composer.json` |

A `.dockerignore` entry is a path from the root of the checkout, such as
`backup/` for a folder, and the scan's D3 section shows it only once you commit
it. When a line does not fit its command, `git diff --stat` shows no change to that
file. Say so, and leave that fix to the builder in their own editor. Any other
fix is theirs as well, such as a password passed inside a connection call.

Run `git status --short` after the last answer, and report which fixes were
made. This procedure commits nothing and pushes nothing. Those steps are the
builder's: commit on a branch and open a pull request, since a default branch
under `managed-ci` refuses a direct push.
