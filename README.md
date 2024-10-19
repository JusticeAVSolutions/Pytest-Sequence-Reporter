# Pytest-Sequence-Reporter

`pytest-sequence-reporter` is a Pytest plugin that enables reporting of test execution events to a test sequencer GUI via HTTP requests. This plugin allows you to send notifications when tests start and finish, along with custom details, enhancing your test monitoring and reporting capabilities.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Installing from GitHub](#installing-from-github)
- [Usage](#usage)
  - [Command-Line Options](#command-line-options)
  - [Adding Custom Options](#adding-custom-options)
  - [Logging Test Values](#logging-test-values)

## Features

- **HTTP Notifications**: Send HTTP notifications to a sequencer GUI when tests start and finish.
- **Customizable API URL**: Easily configure the sequencer API URL.
- **Extendable Options**: Add custom command-line options that can be utilized by the test sequencer.

## Installation

You can install `pytest-sequence-reporter` directly from the GitHub repository using `pip`.

### Installing from GitHub

```bash
pip install git+https://github.com/JusticeAVSolutions/pytest-sequence-reporter.git
```

## Usage

After installing the plugin, you can use the provided command-line options to enable and configure sequencer reporting.

### Command-Line Options

- `--enable-sequencer-reporting`: Enable notifications to the test sequencer GUI.
- `--sequencer-api URL`: Specify the API URL for the sequencer (default: http://localhost:8765/).
- `--list-options`: List all custom Pytest options with their default values.

### Adding Custom Options

You can add custom command-line options to Pytest and have them recognized by the test sequencer by declaring `__pytest_sequencer_plugin__ = True` in modules and plugins.

Example:

```python
__pytest_sequencer_plugin__ = True

def pytest_addoption(parser):
    parser.addoption("--custom-option", action="store", default="default_value", help="Description of the custom option.")
```

### Logging Test Values

Values, readings, measurements, etc. can be logged and sent to the GUI using the Pytest builtin fixture `record_property`. These will be contained in the `details` object of the test_finished event message.

Example:
```python
def test_example(record_property):
    value = 1
    expected = 2
    record_property("value", value)
    record_property("expected", expected)
    assert value == expected, f"value {value} does not equal {expected}"
```

Results in message details: `[['value', 1], ['expected', 2]]`
