# tools/diagrams

Generators for the quickstart documentation diagrams (SVG). Each script is
self-contained (Python 3 standard library only) and writes its SVG in place under
`quickstart/protected/pages/`.

| Script | Output | Diagram |
|---|---|---|
| `gen_applifecycles.py` | `quickstart/protected/pages/Fundamentals/applifecycles.svg` | `TApplication` lifecycle (scoped to 4.3.3) |

## Regenerate

```bash
python3 tools/diagrams/gen_applifecycles.py
```

The script writes the SVG in place. Edit the script (node text, spacing, colors, the
exception decision) rather than the generated `.svg` by hand, then re-run it.

## After regenerating

1. **Validate** by rendering the SVG to pixels and checking that no text breaks through a
   shape border. See `local/quickstart-doc-update-plan-4.3.3.md` (§4a) for the renderer
   notes (Chrome headless gives exact output; launch it backgrounded, poll for the PNG,
   then kill it).
2. **Refresh the published copy.** The quickstart runs `Mode="Performance"`, so
   `TAssetManager` publishes an asset only when the destination is absent and does not
   re-check timestamps. Overwrite the published copy so the change shows:

   ```bash
   cp quickstart/protected/pages/Fundamentals/applifecycles.svg \
      quickstart/assets/<hash>/applifecycles.svg
   ```

   (Never `rm` the `assets/` tree without approval; a fresh deploy publishes from source.)

## Scope

Keep diagrams to features present in the documented version (currently 4.3.3). Do not add
4.4.0-only nodes or labels.
