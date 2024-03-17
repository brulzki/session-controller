import os
from pluginbase import PluginBase

import sessionlib

class Manager():
    def __init__(self, path, *args, **kwargs):
        namespace = 'sessionlib.plugins'
        subclass = sessionlib.Plugin

        if path.startswith('~'):
            path = os.path.expanduser(path)

        plugin_base = PluginBase(package=namespace)
        self._source = plugin_base.make_plugin_source(searchpath=[path])

        self.plugins = []
        for plugin_name in self._source.list_plugins():
            module = self._source.load_plugin(plugin_name)
            for name in dir(module):
                attr = getattr(module, name)
                if isinstance(attr, type) and \
                   issubclass(attr, subclass) and attr is not subclass:
                        self.plugins.append(attr(*args, **kwargs))
