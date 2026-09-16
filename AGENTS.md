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
- **Installed framework:** `vendor/pradosoft/prado` is the source for verification. A
  sibling checkout of the framework's release branch may be symlinked in its place while
  a release is being documented; whatever `vendor/pradosoft/prado` resolves to is what a
  rendered page proves.

## Repository Layout

```
prado-demos/
├── autoload.php            # shared Composer-autoloader shim (3 install layouts); each demo's index.php requires it
├── composer.json           # requires pradosoft/prado ^4; defines webserver scripts + post-install chmod
├── tools/diagrams/         # Python generators for the quickstart's SVG diagrams
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
- Images: `<img src="<%~file.svg%>" class="figure" alt="…">`, the source quoted and an
  `alt` that states what the picture shows.
- **Configuration pairing:** every XML configuration block is followed by its PHP
  equivalent, joined by this glue text, verbatim and on one line:
  `<p class="block-content">The same configuration in the PHP format:</p>`
  Never leave an XML configuration block unpaired. See
  [Configuration examples show both formats](#configuration-examples-show-both-formats).

### Configuration examples show both formats

**Every configuration example is written twice, XML first and PHP second.** PRADO reads an
application or page configuration as XML or as a PHP array, the choice is made once in the
entry script, and a reader on either format has to find their own form on the page. An XML
block is therefore followed immediately by one standardized line and the PHP block:

```html
<com:TTextHighlighter Language="xml" CssClass="source block-content">
...
</com:TTextHighlighter>
<p class="block-content">The same configuration in the PHP format:</p>
<com:TTextHighlighter Language="php" CssClass="source block-content">
...
</com:TTextHighlighter>
```

**The connector text is fixed.** Write `The same configuration in the PHP format:` verbatim,
in a single-line `<p class="block-content">`, so the pairing can be grepped and audited. Do
not vary the wording, and do not label the XML block.

**Match the scope of the two blocks.** A whole-file example opens with `<?php` and
`return [`. A fragment shows only the keys the XML fragment covers, so a bare `<module>`
element pairs with a keyed module entry and a bare `<route>` element pairs with one entry of
the module's `routes` list. When a fragment's context is not obvious, say in the prose above
it which key the entry belongs to.

**Translating the shape.** A repeating XML element becomes an array keyed by its `id`, and
that element's attributes become its `properties` array. A module that nests further elements
reads them from a key of its own: `routes` for `TLogRouter`, `urls` for `TUrlMapping`, `jobs`
for `TCronModule`, `behaviors` for `TBehaviorsModule`, `users` and `roles` for
`TUserManager`, `permissionrules` for `TPermissionsManager`, `translate` for
`TGlobalization`, `soap` for `TSoapService`, `database` for `TDataSourceConfig`. A page
configuration adds `authorization`, where `<allow>` and `<deny>` become entries carrying an
`action` key, and `pages`, where the `<pages>` element's own attributes go under the reserved
key `properties`. The `lazy` flag goes inside a module's `properties`.

**Key case is the trap to check every time.** Several loaders call `array_change_key_case()`
in the XML branch and nothing in the PHP branch, so a capitalized key that works in XML is
silently ignored in PHP. Cron jobs need `name`, `schedule`, `task` and `username`. Permission
rules need `name`, `action`, `users`, `roles`, `verb`, `ips` and `priority`, under a
`permissionrules` key that is itself all lowercase. Behaviors need `name`, `class`,
`attachto`, `attachtoclass` and `priority`. A value that reaches `setSubProperty` keeps its
own capitalization, so a behavior's or a route's own properties stay in their documented
case. The framework docblocks get cron wrong.

**Four things have no working PHP form in 4.3.3.** The pages state the limitation instead of
showing an example that fails: `TRpcService` rejects the array outright, `TSoapService`
accepts it and fails when it builds the server, the `<server>` pool of `TMemCache` is read
from XML only, and an application-level `includes` key is a fatal error. A SqlMap mapping
file is XML under both formats by design, and the SqlMap page says so.

**Not every XML block is configuration.** Template markup belongs in `Language="prado"`, and
an XLIFF catalogue or a SqlMap mapping file is neither a configuration nor a template.

**Verify a new pair rather than trusting the docblock.** Load both forms through the real
loaders (`TApplicationConfiguration`, `TPageConfiguration`) and compare the resulting
arrays.

### Diagrams (evaluate for every page)

Evaluate whether a diagram would help, as a step in planning and researching each page —
new pages and pages being updated alike:

- **New pages:** add an SVG when the subject is structural (a hierarchy, a graph, a
  state/flow, a lifecycle, a precedence order) and a picture shows the mechanism better
  than prose. Skip it when the content is linear or a table already carries it.
- **Existing pages:** when updating a page, evaluate its diagrams too — a legacy
  Visio-exported GIF may be stale or inaccurate for 4.3.3 and need conversion to SVG
  with corrected content, or the updated content may now warrant a new diagram.
- **GIF → SVG conversion:** the quickstart's legacy diagrams are Visio exports saved as
  GIF (`.vsd` sources beside them). Convert to SVG using the original GIF as the visual
  reference (same structure, text placement, text inside every shape border), correct
  the content to 4.3.3 while converting, and apply minimal flair only.
- **Generators:** every SVG is produced by a committed, stdlib-only Python script under
  `tools/diagrams/` whose docstring cites the framework files and lines that verify each
  box and edge. Size text with the script's embedded Verdana width table; the browser
  renders the page font, so a box sized from the wrong metrics clips.
- **Feedback loop:** render the SVG to pixels (headless Chrome `--screenshot` at 2x is
  enough), view it, and fix until it matches; then incorporate review feedback and
  iterate (re-render, re-check) until it is approved. Publish by loading the page once,
  then confirm the page and the asset both answer HTTP 200.

### Badge policy — true introduction version

Badge content at the version the feature actually shipped, not a blanket 4.3.3 (mirrors
the framework's `@since` convention). Section-level badges where a page spans versions.
Do **not** exceed 4.3.3. Resolve the version as described under
[Dating a `SinceVersion` badge](#dating-a-sinceversion-badge).

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

The framework is not in this repo. Verify every technical claim against the installed
4.3.3 framework at `vendor/pradosoft/prado`, in this order of authority:

1. **Class docblocks** in `framework/**` (canonical signatures, properties, events).
2. **Working Knowledge** — `agents/framework/**`: per-directory `INDEX.md` +
   `SUMMARY.md`, one `<Class>.md` per class (~912 files). Fast path to integrated
   descriptions.
3. **`HISTORY.md`** — the what/why/when with issue numbers.
4. The framework code and its `tests/unit/`.

Config-module pages: every configurable module class carries XML+PHP configuration
examples in its docblock (framework issue #1123). Copy those verbatim (adapting
formatting) so config snippets are correct. `framework/classes.php` is the canonical
class list — use it to confirm a class exists and is not removed/renamed.

[`docs/quickstart-maintenance.md`](docs/quickstart-maintenance.md) holds the verification
recipes (render loop, greps, `tools/config-compare.php`, search-index rebuild, asset refresh),
the diagram procedure, the version → feature map, and the framework behaviors the pages work
around.

### The Working Knowledge base is ~95% accurate — verify

The framework `agents/` knowledge base is approximately 95% accurate. Treat it as a
lead, not proof. Confirm each sourced fact against the class docblock/code before
writing it into a quickstart page.

### Recording framework findings (cross-repo boundary)

Work in this repository never edits the framework repository or its `agents/` files.
When Working Knowledge is found inaccurate, record it in
`local/framework-agents-kb-inaccuracies.md`: the file path under `agents/…`, what it
claims, what the code actually shows (with the framework file/line as evidence), and the
correction. When the framework code itself misbehaves, record it in
`local/framework-code-bugs.md` the same way. A framework-repo agent reviews these later
in a batch.

## Known Issues and Traps

- **Pre-namespace config aliases:** the demo `protected/application.xml` files,
  `sqlmap/protected/pages/Manual/config.xml`, five `blog-tutorial` `.page` files
  (`Day2/ConnectDB`, `Day2/CreateAR`, `Day3/Auth`, `Day5/ErrorLogging`,
  `Day5/Performance`) and the `README.md` config example use `class="System.*"` paths
  (e.g. `System.Util.TParameterModule`), which run via PRADO 4 backward-compat aliasing.
  Quickstart prose and examples use namespaced `Prado\…` paths. Modernize the rest when
  touched.
- **Bare class names are not defects.** `class="TAuthManager"` in a configuration and
  `class Home extends TPage` in page code resolve through 4.x aliasing and are how the
  demo apps are written. `Prado::using('System.…')` imports of framework classes are
  unnecessary, because the framework autoloads; replace them with `use` statements when
  touched. `<using namespace="Application.…">` for an app's own classes is still needed.
- **Version strings:** the mentions in `GettingStarted/Upgrading32.page` and
  `Upgrading33.page` are historical statements and stay as written.
  `GettingStarted/NewFeatures.page` and `Upgrading.page` render `HISTORY.md` and
  `UPGRADE.md` straight from the installed package, and that render never needs editing.
  `NewFeatures.page` also has an authored "The 4.x subsystems" table above the render
  (subsystem, release, page); update it when a page documenting a 4.x subsystem is added
  or renamed. Use `<com:SinceVersion>` for the release a feature shipped in, and
  `<com:CurrentVersion />` when a page must show the running version.
- **Shared material lives behind anchors** rather than being repeated:
  `ActiveControls/Introduction.page` has `#ClientSideUpdates` and `#AutoPostBackDefaults`,
  and `Fundamentals/Modules.page` has `#shipped`. Add to those rather than to each page.
- **Paragraph markup must stay clean.** A browser closes a paragraph at
  `<com:TTextHighlighter>`, `<ul>`, `<ol>`, `<dl>`, `<table>`, `<pre>` or a heading, so
  writing one inside a paragraph leaves a stray `</p>` that renders as an empty paragraph
  and drops the class from any prose after the block. Close the paragraph before the
  block and open a fresh one after it. `<div>` and `<blockquote>` legally hold paragraphs
  and are not affected. When editing, check both: paragraph tags balance, and no
  `<p>...</p>` span contains a block element.
- **A `<com:SinceVersion>` badge renders its own `<p>`.** Writing one inside a paragraph
  nests a paragraph in a paragraph; the browser closes the outer one at the badge, which
  splits the text and drops its class. Place a badge on its own line above the heading or
  paragraph it dates, one per section. Scan with: a badge is misplaced if any `<p>` is
  open at its position, and duplicated if two badges are separated only by whitespace or a
  single `<p>` opener.
- **Hyphenated template attributes are broken in 4.3.3.** `Attributes.aria-label="x"`
  parses and renders `aria_label="x"`; a bare `aria-label="x"` throws
  `template_property_unknown`. Set them from code with
  `getAttributes()->add('aria-label', 'x')`. Stated on `Configurations/Templates1.page`.
- **Deprecated properties are a recurring trap.** HTML5 obsoleted the attributes behind
  `TImage.ImageAlign` and `DescriptionUrl`, `THyperLink.ImageAlign`/`ImageHeight`/
  `ImageWidth`, `TTable.CellSpacing`/`CellPadding`/`GridLines`,
  `TTableHeaderCell.CategoryText`, `TDataList.CaptionAlign`,
  `TTableItemStyle.HorizontalAlign`/`VerticalAlign` (reached through every
  `ItemStyle`/`PagerStyle`/`HeaderStyle` of the data controls; the setters on `TPanel`,
  `TTableRow` and `TTableCell` are not deprecated), six `TInlineFrame` properties, and
  `TMetaTag.Scheme`. Older prose presented several of them as the way to do the job.
  Grep `@deprecated` under `framework/Web/UI/**` before documenting a property as the
  recommended approach, and name the CSS or ARIA replacement. In a sample, show the
  replacement; where a sample keeps a deprecated property on purpose, say so in its note.
- **Localized sample templates** (`Advanced/Samples/I18N/Home.<lang>.page`) are picked by
  culture, not addressed as pages: request `Home` with an `Accept-Language` header to
  render one, and audit their markup, not their translated prose.

### Dating a `SinceVersion` badge

**Badge the subject of the section, not the file it lives in.** The commit that last
touched a class is not its introduction, and the class's own age is not the age of a
property added to it ten releases later. A page-level badge dates the chapter's subject: a
control page badges the control, and `Fundamentals/Components2.page` carries no badge
because component events are original to 3.0. A section badge dates that section's
feature: `Advanced/Assets.page` badges its publishing-options section 4.3.3 because
`LinkAssets` and `AppendTimestamp` are 4.3.3, while `TAssetManager` itself is 3.0.

**Resolve the version in this order.** Stop at the first answer the later steps do not
contradict.

1. **The `@since` line on the exact symbol** — the class, method, property or constant the
   section is about. 778 framework files carry one, and 1002 members carry their own. This
   is the cheapest and usually the right answer.
2. **The `HISTORY.md` release section that announces the symbol by name.** This outranks
   `@since` when they disagree. `TActiveMultiView` declares `@since 3.1.6`, a release that
   predates the control by three months; `HISTORY.md` announces it under 3.1.9, which is
   the correct badge.
3. **The introducing commit**, when neither of the above names the symbol:
   `git log -S'<symbol>' --pickaxe-regex --reverse --all`, with the symbol wrapped in
   `[^A-Za-z0-9_]` so a longer name containing it does not match. Then take the earliest
   release in `HISTORY.md` dated after that commit whose tag, when the repo has one,
   contains the commit. Scope with a path when the symbol is common. Watch for the 2015
   one-class-per-file split, which can mask an older origin; search the pre-split file too.

**Both shortcuts fail in opposite directions.** The framework repository carries full
history back to 2005, but its tags are sparse: there is no tag for 3.1.1, 3.1.3, 3.1.6
through 3.1.10, 3.2.1 and others. Tag-only lookups under-report because of those missing
tags. Date-only lookups over-report, because a trunk commit often ships two or three
releases later than the next dated release, and because maintenance releases are cut from
older branches. A tagged release that does not contain the commit is one of those branches
and must be skipped.

**A badge never names something that is not a shipped release.** Framework `@since` lines
carry `3.1a`, `3.1b`, `3.1rc1` and `3.2a`, which are alpha, beta and release-candidate
builds. A reader on 3.1 has the feature, so those badge as `3.1` and `3.2`. The same holds
for the release name itself: write `4.0.0` as `HISTORY.md` writes it.

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
- **Never** modify the framework repository (any sibling checkout) or its `agents/`
  knowledge files from a session in this repository; record corrections under `local/`
  instead.
}

## `local/`

`local/` is gitignored working space: plans, research, and review logs. It is never
shipped and never committed. Put session scratch and cross-repo review notes here.
