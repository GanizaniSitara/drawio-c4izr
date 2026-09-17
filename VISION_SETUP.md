# Vision-based conversion setup

`--from-image` sends the input image to a Claude vision model, which returns the
diagram's elements and connections as structured data. That needs either an Anthropic
API key or a local proxy that serves the same API.

## Option 1: Anthropic API

```
export ANTHROPIC_API_KEY=sk-ant-...
pip install -r requirements.txt
```

Leave `ANTHROPIC_BASE_URL` unset.

## Option 2: copilot-api proxy

[copilot-api](https://github.com/ericc-ch/copilot-api) is a third-party proxy that
exposes a GitHub Copilot subscription through an Anthropic-compatible endpoint. It is
not endorsed by GitHub and may be against the Copilot terms of service — your call.

```
npx copilot-api@latest auth      # browser OAuth, once
npx copilot-api@latest start     # leave running on port 4141
```

Then point the client at it:

```
export ANTHROPIC_BASE_URL=http://localhost:4141
export ANTHROPIC_API_KEY=dummy
```

On Windows, `set ANTHROPIC_BASE_URL=http://localhost:4141` in cmd, or
`$env:ANTHROPIC_BASE_URL="http://localhost:4141"` in PowerShell.

## Running it

```
python main.py diagram.png -o converted.drawio --from-image
python main.py diagram.png -o converted.drawio --from-image -v --save-intermediate
```

Accepts PNG, JPEG, GIF and WebP.

## When it goes wrong

**"Anthropic API key required"** — the environment variables above are not set in the
shell you are actually running from.

**Connection refused** — the copilot-api proxy is not running, or is on another port.

**Rate limited** — start the proxy with `--rate-limit 2`, or wait, depending on which
option you are using.

**Elements missing from the output** — run again with `-v` to see how many elements were
detected, and `--save-intermediate` to inspect the extracted diagram before C4
conversion. Low-resolution images and unreadable labels are the usual cause.
