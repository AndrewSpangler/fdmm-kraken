import os
import types
import errno
from typing import List, Generator
from ..modules.parsing import recursive_update

# Based on https://github.com/pallets/flask/blob/main/src/flask/config.py
def _from_pyfile(path: os.PathLike[str]) -> dict:
    """Loads all-caps values from a config.py file as a dict"""
    path = os.path.join(path)
    d = types.ModuleType("config")
    d.__file__ = path
    try:
        with open(path, mode="rb") as config_file:
            exec(compile(config_file.read(), path, "exec"), d.__dict__)
    except OSError as e:
        if e.errno in (errno.ENOENT, errno.EISDIR, errno.ENOTDIR):
            return False
        e.strerror = f"Unable to load configuration file ({e.strerror})"
        raise
    config = {}
    for key in dir(d):
        if key.isupper():
            config[key] = getattr(d, key)
    return config

def _load_config_modules(modules_to_load:List[os.PathLike]) -> dict:
    """Combines config modules into a dictionary"""
    config = {}
    for m in modules_to_load:
        conf = _from_pyfile(m)
        recursive_update(config, conf)
    return config

def _get_modules(path: str, filename="config.py") -> List[os.PathLike]:
    """
    Finds config modules to load at a given path in form MODULENAME/config.py
    """
    modules = []
    print(f"Searching for config modules at - {path}")
    for e in os.scandir(path):
        if os.path.isfile(m := os.path.join(e.path, filename)):
            modules.append(m)
    print(f"Found {len(modules)} config modules")
    return modules

def load_plugin_config() -> dict[str:os.PathLike]:
    """Loads plugin configuration files without loading the blueprints"""
    modules = _get_modules(os.path.dirname(__file__))
    return _load_config_modules(modules)

def get_blueprints() -> Generator:
    """Blueprint generator object for proper loading"""

    # Load all other blueprints, order matters for plugin dependencies
    # from .network_status import blueprint as network_blueprint
    # from .database_viewer import blueprint as database_blueprint
    from .dashboard import blueprint as dashboard_blueprint
    from .admin import blueprint as admin_blueprint

    # Load order configuration
    blueprints = [ 
        [ # Last
            # database_blueprint,
            dashboard_blueprint,
            admin_blueprint
        ]
    ]

    # Return blueprints in proper load order
    for batch in blueprints:
        for bp in batch:
            yield bp 