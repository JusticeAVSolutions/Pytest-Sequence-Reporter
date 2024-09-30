# Pytest-Sequence-Reporter

`pytest-sequence-reporter` is a Pytest plugin that enables reporting of test execution events to a test sequencer GUI via HTTP requests. This plugin allows you to send notifications when tests start and finish, along with custom details, enhancing your test monitoring and reporting capabilities.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Installing from GitHub](#installing-from-github)
- [Usage](#usage)
  - [Command-Line Options](#command-line-options)
  - [Adding Custom Options](#adding-custom-options)

## Features

- **HTTP Notifications**: Send HTTP notifications to a sequencer GUI when tests start and finish.
- **Customizable API URL**: Easily configure the sequencer API URL.
- **Extendable Options**: Add custom command-line options that can be utilized by the test sequencer.

## Installation

You can install `pytest-sequence-reporter` directly from the GitHub repository using `pip`.

### Installing from GitHub

```bash
pip install git+https://github.com/yourusername/pytest-sequence-reporter.git
```

## Usage

After installing the plugin, you can use the provided command-line options to enable and configure sequencer reporting.

### Command-Line Options

- `--enable-sequencer-reporting`: Enable notifications to the test sequencer GUI.
- `--sequencer-api URL`: Specify the API URL for the sequencer (default: http://localhost:8765/).
- `--list-options`: List all custom Pytest options with their default values.

### Adding Custom Options

You can add custom command-line options to Pytest and have them recognized by the test sequencer using the `add_custom_option` function provided by the plugin.

Example:

```python
# conftest.py
from pytest_sequence_reporter.plugin import add_custom_option

def pytest_addoption(parser):
    add_custom_option(
        parser,
        "--my-custom-option",
        action="store",
        default="default_value",
        help="Description of my custom option"
    )
```
