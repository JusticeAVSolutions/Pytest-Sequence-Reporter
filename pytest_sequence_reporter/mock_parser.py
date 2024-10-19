# mock_parser.py
import argparse

class MockGroup:
    def __init__(self, parser, name, description=None):
        self.parser = parser
        self.name = name
        self.description = description

    def addoption(self, *args, **kwargs):
        """Replicates the addoption method expected by pytest plugins."""
        self.parser.add_argument(*args, **kwargs)

    def addini(self, *args, **kwargs):
        """Replicates the addini method for ini file options."""
        self.parser.addini(*args, **kwargs)

class MockParser(argparse.ArgumentParser):
    def __init__(self):
        # Initialize attributes before calling super().__init__()
        self.plugin_options = {}
        self.current_plugin = None
        super().__init__()

    def set_current_plugin(self, plugin_name):
        """Sets the current plugin context."""
        self.current_plugin = plugin_name

    def add_argument(self, *args, **kwargs):
        """Captures command-line options added by plugins."""
        if self.current_plugin:
            if self.current_plugin not in self.plugin_options:
                self.plugin_options[self.current_plugin] = []
            option = {
                'name': list(args),
                'help': kwargs.get('help', ''),
                'default': kwargs.get('default', ''),
                'type': self._get_type(kwargs.get('type', 'str')),
            }
            self.plugin_options[self.current_plugin].append(option)
        # Call the superclass method to ensure no side effects
        super().add_argument(*args, **kwargs)

    def addoption(self, *args, **kwargs):
        """Handles addoption calls from plugins by delegating to add_argument."""
        self.add_argument(*args, **kwargs)

    def getgroup(self, *args, **kwargs):
        """Replicates the getgroup method expected by pytest plugins."""
        # Accept any keyword arguments and ignore unexpected ones
        name = args[0] if len(args) > 0 else 'default'
        description = kwargs.get('description', None)
        return MockGroup(self, name, description)

    def addini(self, *args, **kwargs):
        """Captures ini file options added by plugins."""
        if len(args) < 1:
            # Handle missing name gracefully
            return
        name = args[0]
        if self.current_plugin and name:
            if self.current_plugin not in self.plugin_options:
                self.plugin_options[self.current_plugin] = []
            ini_option = {
                'ini_name': name,
                'help': kwargs.get('help', ''),
                'default': kwargs.get('default', ''),
                'type': kwargs.get('type', 'str'),
            }
            self.plugin_options[self.current_plugin].append({'ini': ini_option})

    def error(self, message):
        """Overrides the default error method to prevent argparse from exiting."""
        pass

    def _get_type(self, type_obj):
        """Utility method to get a string representation of the type."""
        if isinstance(type_obj, type):
            return type_obj.__name__
        elif callable(type_obj):
            return type_obj.__name__
        elif isinstance(type_obj, str):
            return type_obj
        else:
            return str(type_obj)
