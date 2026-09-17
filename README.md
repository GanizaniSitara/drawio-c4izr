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
pip install -r requirements.txt
```

`lxml` is required. `anthropic` is only needed for image input; see
[VISION_SETUP.md](VISION_SETUP.md).

## Usage

Convert a single file, or every `.drawio` file in a directory:

```
python main.py diagram.drawio -o converted.drawio
python main.py diagrams/ -o converted/
```

When a diagram contains more than one candidate system, you are asked which is the main
one. `--non-interactive` picks the first instead.

Convert an image:

```
python main.py diagram.png -o converted.drawio --from-image
```

### Options

| Option | Effect |
|---|---|
| `-o`, `--output` | Output file, or output directory for a directory input (default `output.drawio`) |
| `-s`, `--scaling-factor` | Scales element sizes (default 1.4) |
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

`test_unified.py` is a smoke test covering serialisation round-tripping, a basic
conversion and file processing. Run it with `python test_unified.py`.

`runner.py` is an earlier entry point kept for reference. Use `main.py`.

## Licence

BSD 3-Clause. See [LICENSE](LICENSE).
