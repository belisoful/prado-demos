# CLAUDE.md

This file provides guidance to Agents when working with code in this repository. It is
the fast-path memory file; the full guidelines are in [`AGENTS.md`](AGENTS.md).

## What This Is

`pradosoft/prado-demos` — a collection of example **PRADO applications** that depend on
`pradosoft/prado` (`^4`) via Composer. This repo has **no framework source**; do not
apply framework build/lint/test workflows here.

The star app is `quickstart` — the framework's end-user documentation (267 `.page`
files). Bringing it current to **PRADO 4.3.3** is the active task.

- Target PRADO version: **4.3.3**. `vendor/pradosoft/prado` is symlinked to the local
  4.3.3 checkout `../prado.prado-4.3` (branch `prado-4.3`) so 4.3.3-only controls render;
  the original pre-4.3.3 vendor dir is backed up at `vendor/pradosoft/prado.pre433.bak`.
  4.3.3 source-of-truth for verification: `../prado.prado-4.3` (NOT `../prado.master`,
  which is 4.4.0-dev).
- Session scope: **prado-demos only**. Do not modify the framework repo or its `agents/`
  knowledge base.

## Active Work (see `local/`, gitignored)

- `local/quickstart-doc-update-plan-4.3.3.md` — the update plan.
- `local/quickstart-doc-history-research.md` — the forensic baseline.
- `local/framework-agents-kb-inaccuracies.md` — log of framework Working-Knowledge
  errors for later batch review on that repo.
- `local/framework-code-bugs.md` — log of behavioral **code** bugs found in the 4.3.3
  framework while verifying quickstart examples (distinct from KB errors); same reviewer.

## Commands

```bash
composer webserver        # serve all demos at http://127.0.0.1:8080 (php -S ... -t ./)
composer webserver:stop   # stop it
php -S localhost:8080 -t quickstart   # serve one app

# rebuild the quickstart Lucene search index
cd quickstart/protected/index/ && php QuickstartIndex.php
```

- Per-app `assets/` and `protected/runtime/` must be web-writable (`composer
  install`/`update` chmod them).
- No `phpunit`/`phpstan`/`php-cs-fixer` in this repo. Verify by rendering pages and the
  documentation audits below.

## Repo Layout

Each `<app>/` is a self-contained PRADO app: `index.php` (requires `../autoload.php`,
`new \Prado\TApplication`, `->run()`), `assets/`, `themes/`, `protected/` (with
`application.xml`, `pages/`, `controls/`, `runtime/`). `autoload.php` (repo root) is a
shared Composer-autoloader shim covering standalone, copied-vendor, and symlinked-vendor
layouts. The quickstart TOC is `quickstart/protected/controls/TopicList.tpl`.

## Quickstart Documentation Rules

Match the existing page idiom and the enforced writing style (full detail in AGENTS.md):

- Idiom: `<com:TContent ID="body">`, `<h1>/<h2>/<h3>`, `<p class="block-content">`,
  `<com:TTextHighlighter CssClass="source block-content">`, `<tt>`, and
  `<com:SinceVersion Version="X"/>` / `<com:RequiresVersion Version="X"/>` badges. Add
  new pages to `TopicList.tpl` (a page is navigable only if listed there).
- **Badge at the true introduction version**, section-level where a page spans versions.
  Never exceed 4.3.3.
- **Scope ceiling 4.3.3** — exclude 4.4.0 material (PSR-3 logging: `TPsrLogger`,
  `TPsrLogRoute`, `psr/log`).
- **Style (enforced):** American English, present tense, timeless, SVO declaratives,
  `condition → result` tables. Banned: antithesis ("not just X, it Ys"), em-dash
  dramatic asides, editorializing/filler, rule-of-three lists. One fact per sentence.

## Source of Truth & Verification

Verify every technical claim against the 4.3.3 framework at `../prado.master`, in order:
class docblocks in `framework/**` → Working Knowledge `agents/framework/**`
(`INDEX.md`/`SUMMARY.md`/`<Class>.md`) → `HISTORY.md` → code + `tests/unit/`.
`framework/classes.php` is the canonical class list. Configurable module classes carry
XML+PHP config examples in their docblocks (copy verbatim).

**The `agents/` Working Knowledge base is ~95% accurate — verify before use.** When it
is wrong, do not edit the framework repo; record the path, the false claim, the code
evidence, and the correction in `local/framework-agents-kb-inaccuracies.md`.

## Known Legacy Issues (audit targets)

- 19 files still use pre-namespace `class="System.*"` aliases, which run via 4.x
  backward-compat aliasing: 14 XML configs (one `protected/application.xml` per demo,
  quickstart included, plus `sqlmap/protected/pages/Manual/config.xml`) and 5
  `blog-tutorial` `.page` files. The `README.md` config example shows the same.
  Quickstart prose is done and uses `Prado\…` paths.
- Version-string drift is resolved in `Controls/` only. 34 prose mentions in the form
  "since v3.1.1" or "Since version 3.1" remain in 14 other files, mostly
  `Configurations/`, `Advanced/`, `Database/ActiveRecord.page` (10 of them in code
  comments) and `GettingStarted/AboutPrado.page`, plus `Controls/List.page` and
  `ActiveControls/InPlaceTextBox.page`. Convert them to `<com:SinceVersion>` badges as
  each chapter is revised. The `Upgrading*.page` mentions are historical and stay. Use
  `<com:CurrentVersion />` when a page must show the running version.
- Deprecated properties are a recurring trap. HTML5 obsoleted the attributes behind
  `TImage.ImageAlign`/`DescriptionUrl`, `THyperLink.ImageAlign`/`ImageHeight`/`ImageWidth`,
  `TTable.CellSpacing`/`CellPadding`/`GridLines`, `TTableHeaderCell.CategoryText`,
  `TDataList.CaptionAlign`, six `TInlineFrame` properties, and `TMetaTag.Scheme`. Grep
  `@deprecated` in `framework/Web/UI/**` before documenting a property as the way to do
  something.

### Dating a `SinceVersion` badge

`../prado.prado-4.3` has full history to 2005, but its tags are sparse (no 3.1.1, 3.1.3,
3.1.6-3.1.10, 3.2.1 and others). Resolve a version by finding the introducing commit with
`git log -S<symbol> --reverse --all`, then taking the earliest release in `HISTORY.md`
dated after it whose tag, if the repo has one, contains that commit. Tag-only lookups
under-report; date-only lookups over-report on maintenance branches. Cross-check the
class's `@since` docblock.

## PRADO Naming Conventions

Classes `TPascalCase`; methods/variables `camelCase`; class properties `_camelCase`;
class constants `SCREAMING_SNAKE_CASE`; enumerated constants `PascalCase`; namespaces
`Prado\{Module}`; pages `.page`+`.php`; portlets/masters `.tpl`+`.php`; control tags
`<com:`.

## Anti-Patterns (Required Safeguards)

- **Never** run `git clone/mv/restore/rm/branch/commit/merge/rebase/reset/pull/push`
  without developer approval first.
- **Never** run `rm` on any path without developer approval first.
- **Never** remove Composer `--dev` dependencies.
- **Never** erase or overwrite files whose changes are the subject of the current task.
- **Never** modify `../prado.master` or its `agents/` files from this session.

## `local/`

Gitignored working space (plans, research, review logs). Never shipped or committed.
