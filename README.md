# c4izr

## Project Description

c4izr converts draw.io diagrams to common C4 representation and standardizes existing C4 diagrams into a unified C4 format. This tool has been enhanced with multiple new features including interactive diagram element selection, improved logging, custom mapping configurations, and auto-backup of outputs.

## Current Features

- Converts draw.io diagrams into standardized C4 representations.
- Interactive selection of the main system when multiple diagram elements are present.
- Processes both individual files and directories.
- Modularized conversion logic with enhanced logging and error reporting.
- Supports custom mapping configurations for C4 properties.
- Auto-backup and versioning of output files.
- Comprehensive test suites to validate conversion functionality.

## Upcoming Features

- Web-based preview mode for interactive conversion.
- Uses LLMs to convert bitmap images to draw in C4 format.
- Additional enhancements based on user feedback.

## How to Use

Use c4izr by providing a single .drawio file or a directory containing multiple diagrams, for example:

```cmd
python main.py path\to\diagram.drawio
python main.py path\to\directory\
```

If you prefer non-interactive mode, specify the flag:

```cmd
python main.py path\to\diagram.drawio --non-interactive
```

You can also adjust scaling, logging, and output settings. For example:

```cmd
python main.py path\to\diagram.drawio --scaling-factor=1.6 --verbose
```
