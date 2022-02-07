# The goal of this module is to serve as the API to the plugins functionalities.
# Other modules must not have to bother about v0 or v1.
import typing as t
from copy import deepcopy

from tutor import exceptions
from tutor.types import Config, get_typed

from . import actions, contexts, filters
from . import v0 as plugins_v0
from . import v1 as plugins_v1

# Key name under which plugins are listed
CONFIG_KEY = "PLUGINS"


def is_installed(name: str) -> bool:
    for plugin in iter_installed():
        if name == plugin.name:
            return True
    return False


def iter_installed() -> t.Iterator[plugins_v0.BasePlugin]:
    """
    Iterate on all installed plugins, sorted by name.

    This will yield all plugins, including those that have the same name.
    """
    plugins: t.List[plugins_v0.BasePlugin] = filters.apply("plugins:installed", [])
    plugins.sort(key=lambda p: p.name)
    yield from plugins


def is_enabled(name: str) -> bool:
    for plugin in iter_enabled():
        if plugin.name == name:
            return True
    return False


# TODO all the logic that is related to configuration should be moved to
# config.py. This module should only take care of managing plugin
# actions/filters, and not the entries in "PLUGINS"
def enable(config: Config, name: str) -> None:
    """
    TODO this does not actually enable the plugin, which is misleading.
    """
    if not is_installed(name):
        raise exceptions.TutorError(f"plugin '{name}' is not installed.")
    if config.get(CONFIG_KEY) is None:
        config[CONFIG_KEY] = []
    enabled = get_typed(config, CONFIG_KEY, list, [])
    if name in enabled:
        return
    enabled.append(name)
    enabled.sort()


def disable(config: Config, plugin: plugins_v0.BasePlugin) -> None:
    # Find the configuration entries that were overridden by the plugin and
    # remove them from the current config
    plugin_context = f"plugins:{plugin.name}"
    overriden_config: Config = filters.apply(
        "config:overrides", {}, context=plugin_context
    )
    for key in overriden_config.keys():
        config.pop(key, None)

    # Remove plugin from list of enabled plugins
    enabled = get_typed(config, CONFIG_KEY, list, [])
    while plugin.name in enabled:
        enabled.remove(plugin.name)

    # Remove actions and filters from that plugin
    filters.clear_all(context=f"plugins:{plugin.name}")
    actions.clear_all(context=f"plugins:{plugin.name}")


def get_enabled(name: str) -> plugins_v0.BasePlugin:
    for plugin in iter_enabled():
        if plugin.name == name:
            return plugin
    raise ValueError(f"Enabled plugin {name} could not be found.")


def iter_enabled() -> t.Iterator[plugins_v0.BasePlugin]:
    """
    Iterate on the list of enabled plugins, sorted by name.

    Note that enabled plugins are not deduplicated. Thus, if two plugins have
    the same name, both will be enabled.
    """
    plugins: t.List[plugins_v0.BasePlugin] = filters.apply("plugins:enabled", [])
    plugins.sort(key=lambda p: p.name)
    yield from plugins


def iter_patches(name: str) -> t.Iterator[t.Tuple[str, str]]:
    """
    Yields: plugin_name (str), patch (str)
    """
    yield from plugins_v1.iter_patches(name)


def iter_hooks(
    hook_name: str,
) -> t.Iterator[t.Tuple[str, t.Union[t.Dict[str, str], t.List[str]]]]:
    """
    Yields: (plugin name, hook)
    """
    yield from filters.apply("apps:tasks", [], hook_name)


def enable_all(config: Config) -> None:
    actions.do("plugins:install")
    plugin_names: t.List[str] = get_typed(config, CONFIG_KEY, list, [])
    for plugin_name in plugin_names:
        actions.do(f"plugins:{plugin_name}:enable")
