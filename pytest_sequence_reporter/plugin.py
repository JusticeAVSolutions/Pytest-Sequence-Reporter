import pytest
import requests
import json
import traceback
from pytest_sequence_reporter.mock_parser import MockParser

__pytest_sequencer_plugin__ = True

API_ENDPOINT = '/message'

# Global variables to store configuration
custom_options = []
sequencer_reporting_enabled = False
sequencer_api_url = "http://localhost:8765/"  # Default value
test_reports = {}  # Dictionary to store test reports

def pytest_addoption(parser):
    """
    Hook to add custom command-line options to pytest.
    """
    parser.addoption("--enable-sequencer-reporting",
        action="store_true",
        default=False,
        help="Enable notifications to the test sequencer GUI.")
    
    parser.addoption("--list-options",
        action="store_true",
        default=False,
        help="List all pytest addoptions with their default values")

    parser.addoption("--sequencer-api",
        action="store",
        type=str,
        default="http://localhost:8765/",
        help="API URL for sequencer")

def pytest_sessionstart(session):
    """
    Hook called after command-line options have been parsed and before any tests are collected or executed.
    """
    config = session.config
    if config.getoption("list_options", False):
        # # Exclude the --list-options itself from the output
        # filtered_options = [
        #     option for option in custom_options if option["name"] != "--list-options"
        # ]
        # # Serialize the options to JSON and print
        # json_output = json.dumps(filtered_options)
        # print(json_output)
        # Serialize the options using mock_parser and print as JSON
        plugins_info = []
        plugin_manager = config.pluginmanager
        mock_parser = MockParser()

        for plugin in plugin_manager.get_plugins():
            # Retrieve plugin name accurately
            if hasattr(plugin, '__name__') and plugin.__name__ != '__main__':
                plugin_name = plugin.__name__
            elif hasattr(plugin, '__class__'):
                plugin_name = f"{plugin.__class__.__module__}.{plugin.__class__.__name__}"
            else:
                plugin_name = str(plugin)

            # Check for the custom marker
            if not getattr(plugin, '__pytest_sequencer_plugin__', False):
                continue  # Skip plugins that are not marked as custom

            plugin_options = []

            if hasattr(plugin, 'pytest_addoption'):
                mock_parser.set_current_plugin(plugin_name)
                try:
                    plugin.pytest_addoption(mock_parser)
                except TypeError as e:
                    plugin_options.append({
                        "error": f"Failed to retrieve options: {e}"
                    })
                except Exception as e:
                    plugin_options.append({
                        "error": f"Failed to retrieve options: {e}"
                    })

                # Retrieve options for this plugin
                options = mock_parser.plugin_options.get(plugin_name, [])
                plugin_options.extend(options)

            # **Filter out the --list-options from the plugin options**
            filtered_options = [
                option for option in plugin_options if "--list-options" not in option["name"]
            ]

            plugins_info.append({
                "name": plugin_name,
                "options": filtered_options
            })

        # Output the information as JSON
        print(json.dumps(plugins_info))
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
    if not sequencer_reporting_enabled:
        return

    nodeid = report.nodeid

    if nodeid not in test_reports:
        test_reports[nodeid] = {}

    test_reports[nodeid][report.when] = report

    if report.when == 'teardown':
        # This is the last phase, we can process the reports
        # Determine the overall outcome
        reports = test_reports[nodeid]
        setup_report = reports.get('setup')
        call_report = reports.get('call')
        teardown_report = reports.get('teardown')

        outcome = None

        # Check for errors in setup or teardown
        if ((setup_report and setup_report.outcome == 'failed' and not getattr(setup_report, 'wasxfail', False)) or
            (teardown_report and teardown_report.outcome == 'failed' and not getattr(teardown_report, 'wasxfail', False))):
            outcome = 'error'
        elif call_report:
            if getattr(call_report, 'wasxfail', False):
                if call_report.outcome == 'passed':
                    # Expected to fail but passed
                    outcome = 'xpassed'
                else:
                    # Expected to fail and did fail
                    outcome = 'xfailed'
            else:
                if call_report.outcome == 'passed':
                    outcome = 'passed'
                elif call_report.outcome == 'failed':
                    outcome = 'failed'
                elif call_report.outcome == 'skipped':
                    # Test was skipped without xfail
                    outcome = 'skipped'
                else:
                    outcome = call_report.outcome
        else:
            # No call phase
            if setup_report and setup_report.outcome == 'skipped':
                outcome = 'skipped'
            else:
                outcome = 'error'

        total_duration = sum(rep.duration for rep in reports.values() if rep)

        # Collect user_properties from all phases
        user_properties = []
        for phase in ['call', 'setup', 'teardown']:
            phase_report = reports.get(phase)
            if phase_report and phase_report.user_properties:
                user_properties.extend(phase_report.user_properties)

        message = {
            'event': 'test_finished',
            'test_id': nodeid,
            'outcome': outcome,
            'duration': total_duration,
            #'details': user_properties  # report all phases
            'details': getattr(call_report, 'user_properties', [])  # report just call phase (typical usage)
        }

        try:
            response = requests.post(f"{sequencer_api_url}{API_ENDPOINT}", json=message)
            response.raise_for_status()
            print(f"Sent test_finished message for {nodeid} with outcome: {outcome}")
        except requests.RequestException as e:
            print(f"Failed to send test_finished message for {nodeid}")
            print(f"Exception: {e}")
            traceback.print_exc()
        finally:
            # Clean up the stored reports for this test
            del test_reports[nodeid]

def pytest_sessionfinish(session, exitstatus):
    """
    Hook called after the entire test run has completed.
    """
    # No action needed for HTTP connections
    pass
