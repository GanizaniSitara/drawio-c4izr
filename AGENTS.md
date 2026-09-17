# Working in this repo

Converts draw.io diagrams into a consistent C4 representation, and can read a diagram out
of an image with a vision model first. Python 3.12+, `lxml` required, `anthropic` optional.

## Layout

| File | Holds |
|---|---|
| `c4izr.py` | The converter. Transition of vertices/edges into C4 objects, styles, geometry |
| `drawio_serialization.py` | The deflate/base64 encoding draw.io uses inside `<diagram>` |
| `drawio_utils.py` | File writing, id generation, layer and label helpers |
| `main.py` | The CLI, and the only entry point |
| `vision_diagram_parser.py` | Image to structured JSON, via the Anthropic API |
| `png2drawio.py` | That JSON to plain draw.io XML, which then goes through `c4izr.py` |
| `test_c4izr.py` | The suite |

## Commands

```bash
python -m pytest -q
python -m ruff check .
python -m mypy .
python main.py TwoBoxes.drawio -o /tmp/out.drawio --non-interactive
```

All three checks must be clean before pushing. On the author's Windows workstation use the
full interpreter path `C:/miniconda3/envs/python312/python.exe` rather than bare `python`.

`ruff format` has been applied to `c4izr.py`, `main.py` and `test_c4izr.py` only. The
remaining modules are intentionally left unformatted so a formatting sweep does not hide a
behavioural change in the diff; format them in a commit of their own if you want to.

## Invariants — do not regress these

1. **The main system is identified by element id, never by label.** Comparing labels meant
   two boxes sharing a name both came out styled as the main system, and the old code
   warned about that rather than fixing it.
   `test_duplicate_labels_yield_exactly_one_main_system` guards it.
2. **The library installs no logging handlers.** `c4izr.__init__` used to attach a
   `StreamHandler` per instance, so log lines multiplied with each one. The module has a
   `NullHandler` and nothing else; `main.py` calls `configure_logging`.
   `test_constructing_the_translator_adds_no_handlers` guards it.
3. **The scaling factor is spacing, not size.** Boxes are always `C4_BOX_WIDTH` x
   `C4_BOX_HEIGHT`; the factor pushes positions out from the diagram centre. Uniform box
   size is the point of the tool. The README said otherwise for a long time — do not
   "restore" that.
4. **Main-system selection is injected, not prompted for in the library.** `translate()`
   must stay callable without a terminal. The console prompt lives in `main.py` as
   `console_selector`; the default is `first_candidate`.
5. **`main.py` is the only entry point.** `runner.py` was a second CLI and was deleted; the
   demo block in `c4izr.py` was a third and went with it. Do not add a `__main__` to the
   library.
6. **A floating edge is kept, not dropped.** An edge with no source or target cannot become
   a C4 relationship, but silently discarding it would change the diagram.

## Testing notes

Tests parse output as XML rather than substring-matching, so a failure names the element at
fault. Anything writing a file uses `tmp_path` — nothing may write into the repo root, which
the old harness did with `test_output.drawio`.

The vision path is covered only by an import test. It needs an API key and a live call, so
exercise it by hand:

```bash
python main.py diagram.png -o out.drawio --from-image --save-intermediate -v
```

Conversion is visual. Tests passing is not sufficient evidence a change is good — open the
output in draw.io and look at it.

## Public repo

No employer, client or colleague names, no internal system or tool names, no internal URLs,
no personal paths. Fixtures are invented data. Commit messages describe the change and carry
no ticket identifiers. An API key belongs in `ANTHROPIC_API_KEY`, never in the source.
