import pytest
import requests
import json
import traceback

API_ENDPOINT = '/message'

# Global variables to store configuration
custom_options = []
sequencer_reporting_enabled = False
sequencer_api_url = "http://localhost:8765/"  # Default value

def add_custom_option(parser, *args, **kwargs):
    """
    Adds a custom option to the pytest parser and stores its details.
    """
    option = parser.addoption(*args, **kwargs)
    custom_options.append({
        "name": args[0],
        "default": kwargs.get("default"),
        "help": kwargs.get("help")
    })
    return option

def pytest_addoption(parser):
    """
    Hook to add custom command-line options to pytest.
    """
    add_custom_option(
        parser,
        "--enable-sequencer-reporting",
        action="store_true",
        default=False,
        help="Enable notifications to the test sequencer GUI."
    )
    add_custom_option(
        parser,
        "--list-options",
        action="store_true",
        default=False,
        help="List all pytest addoptions with their default values"
    )
    add_custom_option(
        parser,
        "--sequencer-api",
        action="store",
        type=str,
        default="http://localhost:8765/",
        help="API URL for sequencer"
    )
    # Add more options using add_custom_option as needed

def pytest_sessionstart(session):
    """
    Hook called after command-line options have been parsed and before any tests are collected or executed.
    """
    config = session.config
    if config.getoption("list_options", False):
        # Exclude the --list-options itself from the output
        filtered_options = [
            option for option in custom_options if option["name"] != "--list-options"
        ]
        # Serialize the options to JSON and print
        json_output = json.dumps(filtered_options)
        print(json_output)
        # Gracefully terminate the pytest session
        pytest.exit("Listed all custom options in JSON format.", returncode=0)

def pytest_configure(config):
    """
    Hook to configure pytest based on the provided command-line options.
    """
    global sequencer_reporting_enabled
    global sequencer_api_url

    sequencer_reporting_enabled = config.getoption("enable_sequencer_reporting", False)
    sequencer_api_url = config.getoption("sequencer_api")

    if sequencer_reporting_enabled:
        print(f"Sequencer reporting is enabled. Messages will be sent to {sequencer_api_url}")
    else:
        print("Sequencer reporting is disabled.")

def pytest_runtest_logstart(nodeid, location):
    """
    Hook called when a test is about to start.
    """
    if not nodeid or not sequencer_reporting_enabled:
        return

    message = {
        'event': 'test_started',
        'test_id': nodeid
    }

    try:
        response = requests.post(f"{sequencer_api_url}{API_ENDPOINT}", json=message)
        response.raise_for_status()
        print(f"Sent test_started message for {nodeid}")
    except requests.RequestException as e:
        print(f"Failed to send test_started message for {nodeid}")
        print(f"Exception: {e}")
        traceback.print_exc()

def pytest_runtest_logreport(report):
    """
    Hook called after each test phase (setup, call, teardown).
    """
    if report.when != 'call' or not sequencer_reporting_enabled:
        return

    message = {
        'event': 'test_finished',
        'test_id': report.nodeid,
        'outcome': report.outcome,
        'duration': report.duration,
        'details': report.user_properties
    }

    try:
        response = requests.post(f"{sequencer_api_url}{API_ENDPOINT}", json=message)
        response.raise_for_status()
        print(f"Sent test_finished message for {report.nodeid}")
    except requests.RequestException as e:
        print(f"Failed to send test_finished message for {report.nodeid}")
        print(f"Exception: {e}")
        traceback.print_exc()

def pytest_sessionfinish(session, exitstatus):
    """
    Hook called after the entire test run has completed.
    """
    # No action needed for HTTP connections
    pass
