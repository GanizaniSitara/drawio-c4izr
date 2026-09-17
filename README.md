# drawio-c4izr

Converts draw.io diagrams into a consistent C4 representation.

Most draw.io diagrams that claim to be C4 are only loosely so: box sizes drift, styling
is inconsistent, and the C4 metadata (`c4Name`, `c4Type`, `c4Description`) is partly
missing. This tool rewrites a diagram into a uniform C4 form — standard box dimensions,
a consistent colour scheme, C4 properties on every element, and a distinction between
the main system and its external dependencies.

It can also take a diagram that is only an image — a Lucidchart export, a screenshot —
and use a vision model to extract the boxes and connections first, then apply the same
conversion.

## Installation

```
pip install -e .
```

`lxml` is the only requirement. Image input additionally needs `anthropic`:

```
pip install -e ".[vision]"
```

See [VISION_SETUP.md](VISION_SETUP.md) for the API key or proxy setup.

## Usage

Convert a single file, or every `.drawio` file in a directory:

```
python main.py diagram.drawio -o converted.drawio
python main.py diagrams/ -o converted/
```

When a diagram contains more than one candidate system, you are asked which is the main
one. `--non-interactive` picks the first instead.

Every C4 box comes out at a uniform 240x120 regardless of its size in the source diagram —
consistent sizing is the point of the conversion. Use the spread factor to change how far
apart the boxes sit, not how big they are.

Convert an image:

```
python main.py diagram.png -o converted.drawio --from-image
```

### Options

| Option | Effect |
|---|---|
| `-o`, `--output` | Output file, or output directory for a directory input (default `output.drawio`) |
| `-s`, `--scaling-factor`, `--spread` | How far apart to push elements, relative to the diagram centre (default 1.4). This scales **spacing**, not element size |
| `--non-interactive` | Do not prompt; use the first system found as the main system |
| `--drawio-path` | Path to the draw.io executable |
| `--open-output` | Open the result in draw.io when done |
| `-v`, `--verbose` | Verbose logging |
| `--from-image` | Treat the input as a PNG/JPG and extract its structure with a vision model |
| `--model` | Vision model to use |
| `--save-intermediate` | With `--from-image`, also write the pre-C4 draw.io file, which is useful when the extraction looks wrong |

## How image conversion works

Three steps. The vision model reads the image and returns the elements, their labels,
their connections and their positions as JSON (`vision_diagram_parser.py`). That JSON
becomes ordinary draw.io XML (`png2drawio.py`). The existing converter then applies the
C4 standardisation to it (`c4izr.py`), so image input and draw.io input end up going
through the same final step.

## Limitations

- Image conversion needs an API key or a proxy, and handles one image per invocation.
- Extraction quality depends on the source image: small text and compressed screenshots
  produce worse results. `--save-intermediate` and `-v` show what was actually detected.
- L0 / multi-level decomposition is not attempted; the output is a single diagram.

## Tests

```
pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m mypy .
```

The suite covers the conversion output element by element, the spread-versus-size
behaviour, the serialisation round trip, and the awkward inputs — a diagram with no
vertices, an edge with no endpoints, non-numeric geometry. Two tests exist specifically to
stop old bugs coming back: duplicate element labels used to produce several main systems,
and constructing the converter used to add another logging handler each time.

Conversion is visual, so a green suite is not proof a change is good. Open the output in
draw.io and look at it.

## Licence

BSD 3-Clause. See [LICENSE](LICENSE).
