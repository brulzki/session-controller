try:
    from straight.plugin import load
except ModuleNotFoundError:
    import sys
    sys.path.append('straight.plugin')
    from straight.plugin import load

from . import Plugin

class Manager():
    def __init__(self, path, controller):
       plugin_classes = load('plugins', subclasses=Plugin)
       self.plugins = plugin_classes.produce(controller)
