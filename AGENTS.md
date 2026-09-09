# PRADO Demos — Agent Guidelines -- CC0

*Borrowed from the PRADO framework `AGENTS.md` and customized for `prado-demos`.
This repository holds PRADO **applications**, not framework source. Framework
coding/build/test machinery (phpstan, php-cs-fixer, phpunit on `framework/`) does
not apply here; the work is authoring and maintaining PRADO apps — above all the
**quickstart**, which is the framework's end-user documentation.*

## What This Is

`pradosoft/prado-demos` is the collection of example PRADO applications. It depends on
`pradosoft/prado` (`^4.3`) via Composer and contains no framework source of its own.
Each demo is a self-contained PRADO app (its own `index.php`, `protected/`, `assets/`,
`themes/`, `runtime/`).

The demo applications:

| App | Purpose |
|---|---|
| `quickstart` | **The end-user documentation** (267 `.page` files). The primary focus of current work. Also the biggest app: component examples + source, with a Lucene search index. |
| `site` | The PRADO website (itself a demo). |
| `helloworld` | Minimal starter app. |
| `blog`, `blog-tutorial` | Blog app + its step-by-step tutorial. |
| `address-book`, `personal`, `time-tracker`, `currency-converter`, `chat` | Feature demos (DB, AJAX, forms, i18n). |
| `northwind-db`, `sqlmap`, `soap`, `composer` | Data-access, SqlMap, SOAP, and composer-install demos. |

- **Target PRADO version: 4.3.3.** (README declares `v4.3.3`.)
- **Installed framework:** `vendor/` currently resolves `pradosoft/prado` at **4.3.2**
  (`composer.lock`). The authoritative **4.3.3** source for verification is the sibling
  checkout at `../prado.master` (symlinked `../prado`). Reconcile this before trusting
  a rendered demo as proof of 4.3.3 behavior (see "Framework source of truth").

## Current Focus — Quickstart → 4.3.3

The quickstart documentation froze editorially at the 3.1/3.2.3 era and was only
mechanically ported to 4.0 namespaces. Bringing it current to 4.3.3 is the active
task. Working documents (gitignored, in `local/`):

- `local/quickstart-doc-history-research.md` — forensic baseline: when the docs froze,
  what the framework added after.
- `local/quickstart-doc-update-plan-4.3.3.md` — the update plan (workstreams, phasing,
  badge policy, per-page recipe, verification gates).
- `local/framework-agents-kb-inaccuracies.md` — running log of framework Working
  Knowledge errors found while sourcing content (for a later batch review on that repo).

## Repository Layout

```
prado-demos/
├── autoload.php            # shared Composer-autoloader shim (3 install layouts); each demo's index.php requires it
├── composer.json           # requires pradosoft/prado ^4; defines webserver scripts + post-install chmod
├── <app>/                  # one directory per demo application
│   ├── index.php           # entry point: requires ../autoload.php; new \Prado\TApplication; ->run()
│   ├── assets/             # published assets (must be web-writable)
│   ├── themes/             # app themes/skins
│   └── protected/
│       ├── application.xml  # app configuration (modules, services, parameters)
│       ├── pages/           # .page templates (+ .php backing) and Samples/
│       ├── controls/        # portlets/master templates (.tpl + .php)
│       └── runtime/         # cache/state (must be web-writable)
└── local/                  # gitignored scratch: plans, research, review logs (never shipped)
```

The `quickstart` app additionally has `protected/controls/TopicList.tpl` (the
hand-maintained table of contents) and `protected/index/` (the search-index builder).

## Running the Demos

```bash
# Serve the whole repo (all demos) on http://127.0.0.1:8080
composer webserver          # == php -S 127.0.0.1:8080 -t ./
composer webserver:stop     # pkill the server

# Serve a single app
php -S localhost:8080 -t quickstart
```

- `assets/` and `protected/runtime/` for each app must be web-writable. `composer
  install`/`update` run `chmod` on them via `post-install-cmd`/`post-update-cmd`.
- Rebuild the quickstart search index (run from inside its `index` dir):

  ```bash
  cd quickstart/protected/index/
  php QuickstartIndex.php
  ```

There is **no** unit/lint/static-analysis suite in this repo. "Verification" here means
rendering the affected pages/apps and clicking through them (plus the documentation
audits below), not running `phpunit`/`phpstan`/`php-cs-fixer`.

## Documentation Authoring Standards (quickstart)

Quickstart pages are PRADO templates. New and rewritten content must be
indistinguishable from the existing body.

### Page idioms

- Page wrapper: `<com:TContent ID="body"> … </com:TContent>` with a matching `.php`
  backing class of the same base name.
- Headings `<h1>`/`<h2>`/`<h3>`; body copy `<p class="block-content"> … </p>`.
- Code: `<com:TTextHighlighter CssClass="source block-content"> … </com:TTextHighlighter>`.
- Inline identifiers: `<tt> … </tt>`.
- Version badges: `<com:SinceVersion Version="X"/>` (available from X onward) and
  `<com:RequiresVersion Version="X"/>` (sample needs minimum X).
- Intra-doc links: `?page=Section.PageName` (same scheme as `TopicList.tpl`); a page
  enters navigation only by being listed in `TopicList.tpl`.

### Diagrams (evaluate for every page)

Evaluate whether a diagram would help, as a step in planning and researching each page —
new pages and pages being updated alike:

- **New pages:** add an SVG when the subject is structural (a hierarchy, a graph, a
  state/flow, a lifecycle) and a picture shows the mechanism better than prose. Skip it
  when the content is linear or a table already carries it. Record the decision (add /
  skip, and why) in the plan while researching the page.
- **Existing pages:** when updating a page, evaluate its diagrams too — a legacy
  Visio-exported GIF may be stale or inaccurate for 4.3.3 and need conversion to SVG
  with corrected content, or the updated content may now warrant a new diagram.
- **GIF → SVG conversion:** the quickstart's diagrams are Visio exports saved as GIF
  (`.vsd` sources beside them). Convert to SVG using the original GIF as the visual
  reference (same structure, text placement, text inside every shape border), correct
  the content to 4.3.3 while converting, and apply minimal flair only.
- **Feedback loop:** render the SVG to pixels, view it, and fix until it matches; then
  incorporate review feedback and iterate (re-render, re-check) until it is approved.
  Generate large/repetitive diagrams with a committed script under `tools/diagrams/`.
- Full procedure and renderer notes: `local/quickstart-doc-update-plan-4.3.3.md` §4a.

### Badge policy — true introduction version

Badge content at the version the feature actually shipped, not a blanket 4.3.3 (mirrors
the framework's `@since` convention). Section-level badges where a page spans versions.
Do **not** exceed 4.3.3. The version→feature map is in the update plan (§1c).

### Scope ceiling — 4.3.3 only

Document through 4.3.3. Exclude 4.4.0 material (e.g. PSR-3 logging: `TPsrLogger`,
`TPsrLogRoute`, `psr/log`). Note: `GettingStarted/NewFeatures.page` renders the
installed framework's live `HISTORY.md`, which may contain a `4.4.0 - TBA` section;
do not author 4.4.0 content around it.

### Writing style (enforced — from the framework standard)

Direct technical statements. Language: English (American). Present tense. Clear,
thorough, brief (not verbose), integrated, wholistic, timeless ("always was").

_Banned constructions:_
- **Antithesis / "not merely X — it Ys"**: no "does not just X, it Ys", "is not a Y,
  it's a Z", "rather than X, it Ys". State what it does, once.
- **Em-dash dramatic asides** for emphasis or reveal. Use a period or plain clause.
- **Editorializing / filler.**
- **Rule-of-three rhetorical lists** and build-up sentences. One fact per sentence.

Prefer subject–verb–object declaratives and `condition → result` tables/lists.
Documentation informs and describes; it is not persuasive writing. Integrate
additions into the whole at every level of detail; do not bolt on isolated appendices.

## PRADO Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Classes | `TPascalCase` | `TComponent`, `TApplication` |
| Methods | `camelCase` | `getComponent` |
| Variables | `camelCase` | `$componentName` |
| Class Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Enumerated Constants | `PascalCase` | `DeepSkyBlue` |
| Class properties | `_camelCase` | `_propertyOfClass` |
| Namespaces | `Prado\{Module}` | `Prado\Web\UI\TControl` |
| Web Page templates | `.page` with `.php` backing | `Home.page` / `Home.php` |
| Master/portlet templates | `.tpl` with `.php` backing | `TopicList.tpl` |
| TControl tag prefix | `<com:` | `<com:TMain />` |

PRADO framework concepts referenced by the docs (verify against source before writing):
`TComponent` property/event/behavior system; `on`/`dy`/`fx` event prefixes;
Application and Page lifecycles; XML **and** PHP application configuration.

## Framework Source of Truth

The framework is not in this repo. Verify every technical claim against the 4.3.3
source at `../prado.master` (symlink `../prado`), in this order of authority:

1. **Class docblocks** in `../prado.master/framework/**` (canonical signatures,
   properties, events).
2. **Working Knowledge** — `../prado.master/agents/framework/**`: per-directory
   `INDEX.md` + `SUMMARY.md`, one `<Class>.md` per class (~912 files). Fast path to
   integrated descriptions.
3. **`../prado.master/HISTORY.md`** — the what/why/when with issue numbers.
4. The framework code and its `tests/unit/`.

Config-module pages: every configurable module class carries XML+PHP configuration
examples in its docblock (framework issue #1123). Copy those verbatim (adapting
formatting) so config snippets are correct. `../prado.master/framework/classes.php` is
the canonical class list — use it to confirm a class exists and is not removed/renamed.

### The Working Knowledge base is ~95% accurate — verify

The framework `agents/` knowledge base is approximately 95% accurate. Treat it as a
lead, not proof. Confirm each sourced fact against the class docblock/code before
writing it into a quickstart page.

### Recording framework KB inaccuracies (cross-repo boundary)

When Working Knowledge is found inaccurate:

- **Do not** modify the framework repo or its `agents/` files in this session. This
  session's work is scoped to `prado-demos`.
- **Record** the inaccuracy in `local/framework-agents-kb-inaccuracies.md`: the file
  path in `../prado.master/agents/…`, what it claims, what the code actually shows
  (with the framework file/line as evidence), and the correction. A framework-repo
  agent reviews these later in a batch.

## Legacy State / Known Issues (audit targets)

- **Pre-namespace config aliases:** ~26 demo/config files use `class="System.*"`
  paths (e.g. `System.Util.TParameterModule`); zero use namespaced `Prado\…` paths.
  They run via PRADO 4 backward-compat aliasing. The README config example shows the
  same. Modernize as part of the quickstart/demos audit.
- **Stale TOC link:** `TopicList.tpl` links `GettingStarted.Upgrading40`; the on-disk
  file is `Upgrading.page`.
- **Version-string drift:** hardcoded prose versions (`Prado 4.2.0`, `3.2.1`, `3.1`)
  scattered in pages; single-source them.
- **3.1/3.2-era body:** most pages predate 4.x and need a correctness pass, not just
  additive new pages (see the update plan, Workstream C).

## Development Environment

- PHP 8.1 or higher (`composer.json` platform pin: 8.1.0).
- The quickstart search demo uses `zf1/zend-search-lucene`; it degrades gracefully when
  Zend-Search is unavailable.
- `vendor/bin/` provides `prado-cli` (the framework CLI), plus `psysh`,
  `var-dump-server`, `php-parse`.
- Presume Composer dependencies are installed.

## Anti-Patterns (Required Safeguards)

Between these brackets, required without exception:
{
- **Never** run `git clone/mv/restore/rm/branch/commit/merge/rebase/reset/pull/push`
  without developer approval first.
- **Never** run `rm` on any path without developer approval first.
- **Never** remove Composer `--dev` dependencies.
- **Never** erase or overwrite files whose changes are the subject of the current task.
- **Never** modify the framework repo (`../prado.master`) or its `agents/` knowledge
  files from this session; record KB corrections to `local/` instead.
}

## `local/`

`local/` is gitignored working space: plans, research, and review logs. It is never
shipped and never committed. Put session scratch and cross-repo review notes here.
