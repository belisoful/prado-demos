# Quickstart maintenance references

Working references for maintaining the `quickstart` documentation against PRADO 4.3.3.
`AGENTS.md` and `CLAUDE.md` hold the rules; this file holds the recipes, the tables and
the framework behaviors the pages work around. Verify everything here against the
installed `vendor/pradosoft/prado` before relying on it for a later release.

## Verification recipes

All of these assume the demos are served: `composer webserver` (all demos on
`http://127.0.0.1:8080`), a page renders at `?page=Section.Name` under `/quickstart/`.

**Render every page and catch PHP error markers.** A page that throws still answers 200
in Performance mode, so grep the body (the `[^t]` keeps `<tt>TExitException</tt>` in prose
from matching):

```bash
cd quickstart/protected/pages
for f in $(find . -name '*.page' | sed 's#^\./##'); do
  pg=$(echo "$f" | sed -E 's#\.page$##; s#/#.#g')
  code=$(curl -s -o /tmp/body.html -w '%{http_code}' "http://localhost:8080/quickstart/?page=$pg")
  if [ "$code" != 200 ] || LC_ALL=C grep -qE 'Exception</[^t]|Fatal error|Warning: |Notice: |Deprecated: ' /tmp/body.html; then
    echo "$code $pg"
  fi
done
```

The localized `Advanced/Samples/I18N/Home.<lang>.page` templates are not pages; render
`Advanced.Samples.I18N.Home` with an `Accept-Language` header to see one.

**Mechanical greps** (run over the page set being audited):

| Check | Command |
|---|---|
| pre-namespace paths in prose or config | `grep -n 'System\.[A-Z]'` |
| deprecated properties presented as current | `grep -nE 'ImageAlign\|CellSpacing\|CellPadding\|GridLines=\|CategoryText\|CaptionAlign\|DescriptionUrl\|ImageWidth\|ImageHeight\|Scheme=\|HorizontalAlign=\|VerticalAlign='` then confirm each host's setter carries `@deprecated` |
| plain-http links | `grep -noE 'href="http://[^"]+"'` |
| dead intra-doc links | every `?page=A.B` must exist as `pages/A/B.page` |
| unpaired XML configuration | every `Language="xml"` block that is configuration is followed by `The same configuration in the PHP format:` |
| paragraph balance | count `<p` against `</p>` per file, and flag a `<com:TTextHighlighter>`, `<ul>`, `<ol>`, `<table>`, `<pre>` or heading that opens while a `<p>` is open |
| badges | values are shipped releases, none above 4.3.3, none inside a `<p>` |

**Configuration pairing.** `tools/config-compare.php` loads an XML fragment and its PHP
equivalent through a fresh module or service instance, one process per form, and prints
the registered state side by side:

```bash
php tools/config-compare.php 'Prado\Web\Services\TJsonService' json.xml json.php
```

`json.xml` holds the `<service>` (or `<module>`) element; `json.php` returns the service
(or module) entry. Exit status 0 means the two forms register the same state.

**Search index.** The Lucene index under `quickstart/protected/index/quickstart/` is
gitignored and must be rebuilt after content changes:

```bash
cd quickstart/protected/index/ && php QuickstartIndex.php
```

**Published assets in Performance mode.** The quickstart runs `Mode="Performance"`, where
`TAssetManager` publishes a file only when the destination is absent. After changing an
already-published SVG, refresh the one copy under `quickstart/assets/<hash>/` with a `cp`
overwrite (never remove the assets tree without approval), then confirm the page and the
asset both answer 200.

## Diagrams

Every diagram is an SVG written by a stdlib-only Python generator under `tools/diagrams/`;
edit the generator, never the `.svg`. The generator's docstring cites the framework files
and lines that verify each box and edge.

1. **Reference.** For a legacy Visio GIF (`.vsd` beside it), keep its structure and text
   placement, with text inside every shape border. For a new diagram, draw the verified
   mechanism: a hierarchy, a flow, a lifecycle, a precedence order.
2. **Content.** Correct the diagram to 4.3.3 while drawing it, and update the page prose
   around it. Minimal flair: a subtle drop shadow and clean strokes.
3. **Text metrics.** Size boxes from the generator's embedded Verdana advance-width table
   (`text_px`); monospace text is about `0.6 × font-size` per character, bold about 6%
   wider. The browser renders the page font, so a box sized from other metrics clips.
4. **Render and iterate.** Headless Chrome renders exactly:
   `chrome --headless --screenshot=out.png --window-size=W,H --force-device-scale-factor=2 --default-background-color=00000000 --user-data-dir=<unique> file://…/name.svg`.
   Launch it in the background, poll for the PNG, then kill it (it may not exit on its
   own). View the PNG and fix until it matches; then take review feedback and re-render
   after every change until it is approved. `qlmanage -t` also renders but pads to a
   square; ImageMagick's built-in SVG renderer fails on fonts.
5. **Wire and publish.** Reference the SVG from its page as
   `<img src="<%~name.svg%>" class="figure" alt="…">` with an `alt` that states what the
   picture shows, load the page once to publish it, and confirm page and asset answer 200.

## Version → feature map (from the installed `HISTORY.md`)

| Subsystem / feature | `SinceVersion` |
|---|---|
| Namespaces, Composer, PSR-4 autoloading | 4.0.0 |
| Config-driven behaviors (`TBehaviorsModule`, `TBehaviorParameterLoader`, `TParameterizeBehavior`) | 4.2.0 |
| RBAC: `TPermissionsManager`, `TAuthorizationRule` priority, per-permission rules | 4.2.0 |
| Cron (`TCronModule`, `TDbCronModule`) | 4.2.0 |
| Composer extensions (`TPluginModule`, `TDbPluginModule`) | 4.2.0 |
| `TDbParameterModule` | 4.2.0 |
| Dynamic-event expansion in configuration, `TMap`/`TPriorityMap` dy-events, `AutoGlobalListen` | 4.2.0 |
| `TGravatar`, `TDataSize`, `TEventContent`, RTL themes, `Prado::createComponent(array)` | 4.2.0 |
| `THtmlArea5`/`TActiveHtmlArea5` (TinyMCE 5) | 4.2.0 |
| `TWeakCallableCollection`, shell refactor (routes and actions), WSAT moved to `pradosoft/prado-wsat` | 4.2.0 |
| General behaviors update (clone/serialize, `IBaseBehavior::init`, Closure `events()`, anonymous behaviors, trait-wide class behaviors) | 4.3.0 |
| Closure event handlers, `TEventHandler`, `TEventSubscription`, reverse `raiseEvent` | 4.3.0 |
| Logging overhaul (profiling, flushing, `TSysLogRoute`, `TDbLogRoute` prefix/RetainPeriod, `TLogger::OnFlushLogs`, colorized `TBrowserLogRoute`) | 4.3.0 |
| `TExitException` and exception chaining | 4.3.0 |
| `THttpRequest::onResolveRequest`, `TRequestConnectionUpgrade` | 4.3.0 |
| `TProcessHelper`, `TSignalsDispatcher`, embedded dev web-server CLI action | 4.3.0 |
| `TRational`/`TURational`, `TBitHelper`, `TArrayHelper`, `TWebColor` | 4.3.0 |
| `TDatePicker::DropDownCssClass`, `THttpSessionHandler` | 4.3.1 |
| Database driver interfaces (`IDataConnection` … `IDataTableInfo`), `TDbPropertiesTrait`, DB2/Firebird metadata, `TDbDriver`, `TDataCharset` | 4.3.3 |
| `TEventParameter`: `IEventCycleParameter`, `ReadOnly`, `ArrayAccess` | 4.3.3 |
| `TApplication`/`TShellApplication` refactor, `onConfiguration`, `TTestApplication`, PradoUnit | 4.3.3 |
| `TModuleView`; render-output filter pipeline (`IFilterRenderable`, `TRenderFilterParameter`) | 4.3.3 |
| HTML5 semantic controls (`TArticle`, `TAside`, `TFooter`, `THeader`, `TMain`, `TMark`, `TNav`, `TSection`) | 4.3.3 |
| `TAssetManager` symlink publishing, timestamp cache busting, `Only`/`Except`; `TUrlMappingPattern` verb filtering | 4.3.3 |
| `TSecurityManager` `UseEncryptionHmac`, `EncryptionKeyAlgorithm` | 4.3.3 |
| `TNull`, `TWeakMap`, `TInitializedTrait`, `TTarFileExtractor`, `CultureInfo` units, `TSimpleDateFormatter` patterns | 4.3.3 |

A badge dates the subject of its section, resolved in this order: the symbol's own
`@since`, then the `HISTORY.md` section that announces it (which wins on conflict), then
the introducing commit. Pre-release tags (`3.1a`, `3.2a`) badge as `3.1` and `3.2`.

## Framework behaviors the quickstart works around

Each of these was observed in 4.3.3 while writing or verifying a page. The page named
states the limitation or uses the working form; none of them is fixed in this repository.

| # | Behavior | Where the quickstart handles it |
|---|---|---|
| 1 | `Attributes.aria-label="x"` in a template renders `aria_label`; a bare `aria-label` attribute throws. Hyphenated attributes are set from code with `getAttributes()->add()`. | `Configurations/Templates1.page`; `Controls/Html5Semantic.page` and its sample |
| 2 | `TModuleView` without a `ModuleId` is never active, although its docblock says it then acts like `TConditional`. | `Controls/ModuleView.page` requires a `ModuleId` and points condition-only use to `TConditional` |
| 3 | `TUrlMappingPattern::Verbs` negation (`!DELETE`, `~DELETE`) matches nothing; only positive lists work. | `Configurations/UrlMapping.page` documents positive lists only |
| 4 | A postback that loses `PRADO_PAGESTATE` surfaces as a `base64_decode(): Passing null` deprecation instead of a page-state error (upstream `pradosoft/prado#1006`). The usual trigger is a raw `<form>` nested inside `<com:TForm>`. | Open: no page states it yet. Candidate: a note in `blog-tutorial` `Day1/ShareLayout.page` telling readers not to nest a form. |
| 5 | A `TActiveTableCell` with a handler inside a `TActiveTableRow` with a handler sends two callbacks per click and raises `OnRowSelected` twice. | `ActiveControls/ActiveTableRow.page` sample keeps the two handlers on separate rows |
| 6 | `TRpcService::loadConfig()` type-hints `TXmlElement`, so the service has no PHP configuration form. | `Services/RpcService.page` says XML only |
| 7 | `TMemCache::loadConfig()` reads `<server>` from XML only, so a server pool has no PHP form. | `Advanced/Caching.page` |
| 8 | `TApplicationConfiguration::loadFromPhp()` sends `includes` to the XML loader; an `includes` key in `application.php` is fatal. | `Configurations/AppConfig.page` states the key works in a page configuration |
| 9 | `TUrlMapping`'s docblock PHP example omits the `properties` sub-array its loader requires. | `Configurations/UrlMapping.page` shows the wrapped form |
| 10 | `TPermissionsManager` reads `<permissionrule>` as a direct child only; the PHP key is `permissionrules`, all lowercase; a rule with a `class` still needs an `action`. | `Advanced/Permissions.page` |
| 11 | `TSoapService::createServer()` calls `remove()` on the plain array its PHP loader stores; SOAP has no working PHP form. | `Services/SoapService.page` says XML only |
| 12 | `TCronModule`/`TDbCronManager` docblocks show capitalized job keys; the PHP branch reads lowercase `name`/`schedule`/`task`/`username`. | `Advanced/Cron.page` |
| 13 | `TActiveMultiView` declares `@since 3.1.6` and shipped in 3.1.9. | `ActiveControls/ActiveMultiView.page` badges 3.1.9 |
| 14 | The framework's `phpunit.xml` `functional` suite matches no files after the Playwright migration. | `Advanced/Testing.page` directs readers to `composer functionaltest` |
| 15 | `TJsonService`'s docblock PHP example omits the `json` key its loader reads; the documented shape registers no response. | `Services/JsonService.page` shows the `json`-keyed form |
| 16 | `TFeedService::init()` iterates the whole service entry, so its docblock's `'feed' => […]` nesting registers no usable feed; feeds go beside the `class` key. | `Services/FeedService.page` shows the sibling-key form |

The full entries, with the reproductions and evidence, are kept in the gitignored
`local/framework-code-bugs.md` for the batch review on the framework repository, together
with `local/framework-agents-kb-inaccuracies.md` for the Working Knowledge corrections.

## Open items outside the quickstart

- `sqlmap` manual: its one PRADO configuration example uses the 3.0 `TSQLMap`/`TAdodbProvider`
  API and cannot be paired until that app has a correctness pass; its other XML blocks are
  SqlMap mapping files.
- `blog-tutorial` and `site` carry paragraph-markup defects; the nested-form note for #1006
  belongs in `blog-tutorial` too.
- The demo `application.xml` files, `sqlmap/protected/pages/Manual/config.xml`, five
  `blog-tutorial` pages and the `README.md` example use `class="System.*"` aliases.
- The legacy diagram GIFs replaced by SVGs are still on disk by choice
  (`mastercontent`, `pcrelation`, `logrouter`, `directory` ×2, `applifecycles`,
  `classtree`, `lifecycles`, `objectdiagram`, `wizard`, `sequence`).
