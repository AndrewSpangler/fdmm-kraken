import os
import sys
import json
import logging
import logging.config
import asyncio
from functools import wraps
from flask import (
    Flask,
    redirect,
    url_for,
    abort,
    flash,
    request
)
from flaskext.markdown import Markdown
from flask_login import LoginManager, login_required, current_user
from pytz import timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import ImmutableDict

from .modules.parsing import (
    pretty_date,
    get_tz_from_localization,
    add_html_breaks,
    format_bytes,
    stringify_float,
    recursive_update
)
from .modules.task_manager import BackgroundTaskManager
from .blueprints import load_plugin_config, get_blueprints

print(disclaimer := """
Disclaimer: This software is provided "as is" and without warranties of 
any kind, whether express or implied, including, but not limited to, the 
implied warranties of merchantability, fitness for a particular purpose, 
and non-infringement. The use of this software is entirely at your own 
risk, and the owner, developer, or provider of this software shall not be
liable for any direct, indirect, incidental, special, or consequential 
damages arising from the use or inability to use this software or any of 
its functionalities. This software is not intended to be used in any 
life-saving, mission-critical, or other applications where failure of the
software could lead to death, personal injury, or severe physical or 
environmental damage. By using this software, you acknowledge that you 
have read this disclaimer and agree to its terms and conditions.
""".strip())


"""
BACKSTORY ABOUT THIS NEXT BIT OF CODE AND HOW IT AFFECTS THE CONSOLE
For months I was randomly running into an issue where the program would 
hang indefinitely. It would stop responding to any requests but didn't 
otherwise seem to have hung. Turns out the Windows console was getting 
clicked at some point which halted execution. It runs correctly until the 
Windows screen lock activates at which point the webserver would stop 
responding to requests until I logged back in and hit the return key.

I hate NT/Windows sometimes.

Anyways the console will no longer be interactable and using the scroll 
wheel doesn't work but it won't freeze the server if somebody happens to 
accidentally highlight something on the command prompt and then go 
inactive until the screen locks.
"""
import os
if os.name == 'nt':
    import ctypes
    if ctypes.windll.kernel32.GetConsoleMode(
        std_in := ctypes.windll.kernel32.GetStdHandle(-10),
        ctypes.byref(mode := ctypes.c_uint())
    ):
        if mode.value & 0x40:
            ctypes.windll.kernel32.SetConsoleMode(std_in, mode.value ^ 0x40)

if sys.platform == 'win32' and sys.version_info[:3] >= (3, 8, 0):
    if type(asyncio.get_event_loop_policy()) is asyncio.WindowsProactorEventLoopPolicy:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

### Instantiate main app object and load config
app = Flask(__name__)
app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
print(f"Welcome to {app.config['APPLICATION_NAME']}")
print(f"{app.config['LOADING_SPLASH']}")
### Add markdown rendering in templates
Markdown(app)

### Load plugin configuration
plugin_config = load_plugin_config()
for k in (
    "NAV_LINKS",
    "ADMIN_NAV_LINKS",
    "DASHBOARD_TABS"
):
    if not k in app.config:
        app.config[k]={}
recursive_update(app.config, plugin_config) # Combines all config files

### Set up logging
logging.basicConfig(level=logging.DEBUG)
logging.config.dictConfig(app.config["LOG_CONFIG"])

### Set up background task scheduler
BackgroundTaskManager(app)

app.models = ImmutableDict() 

### Used to set UI-displayed timezones
app.local_tz = timezone(app.config["TIMEZONE"])

### Make databases dir 
os.makedirs("databases", exist_ok=True)

### Make downloads directory
os.makedirs(app.config["DOWNLOADS_DIR"], exist_ok=True)

def permission_required(_any=["admins"], _all=[]) -> callable:
    """Decorator to limit access to users in certain groups, defaults to admins group"""
    # Args are obscured by wrapping
    # (required_permission, func, *args, **kwargs for direct call)
    def decorator(func) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> callable:

            def check_access(func):
                # return abort(403)
                return func

            return check_access(func)(*args, **kwargs)
        return wrapper
    return decorator

### Make user filters accessible
app.permission_required = permission_required
# Clean way to break long chunks of text for tables
app.add_html_breaks = add_html_breaks

def register_blueprint(bp) -> None:
    """
    Custom blueprint registration for clean app architecture
    Inits a blueprint's db if needed then starts blueprint
    """
    if hasattr(bp, "init_db"):
        bp.init_db(app)
    app.register_blueprint(bp)
    # if hasattr(bp, "settings_link"):
    #     app.settings_links[bp.name] = bp.settings_link

for bp in get_blueprints(): # Load all blueprints from folder
    register_blueprint(bp)

# @login_manager.user_loader
# def load_user(user_id):
#     """Function for the login manager to grab user object from db"""
#     return app.user_loader(user_id)

BOOTSWATCH_THEMES = [ # For theme-selector in context provider
    "default", "cerulean", "cosmo", "darkly", "flatly",
    "journal", "litera", "lumen",
    "minty", "pulse", "sandstone", "simplex",
    "slate", "spacelab", "superhero", "united", "yeti",
    "zephyr"
]

@app.context_processor
def provide_selection() -> dict:
    """
    Context processor which runs before any template is rendered
    Provides access to these objects in all flask templates
    """
    return {
        "show_tz": True, 
        "nav_enabled": True,
        "light_background": False,
        "local_tz": get_tz_from_localization(app.local_tz),
        "add_html_breaks":add_html_breaks,
        "format_bytes":format_bytes,
        "stringify_float":stringify_float,
        "pretty_date": pretty_date,
        "enumerate": enumerate,
        "isinstance": isinstance,
        "len": len,
        "min": min,
        "max": max,
        "sum": sum,
        "int": int,
        "app": app,
        "str": str,
        "json": json,
        "list": list,
        "selected_theme": "simplex",
    }

### Start background tasks
app.scheduler.start()