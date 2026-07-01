"""
Evennia settings file.

The available options are found in the default settings file found
here:

/home/muddev/evennia/evennia/settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from urllib.parse import non_hierarchical

from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Iridum"
GAME_SLOGAN = "Experimental Evennia Virtual Text Environment Developing System"
SERVER_HOSTNAME = "iridum.redterminal.org"
TELNET_INTERFACES = ["::"]
TELNET_ENABLED = False
SSL_INTERFACES = ["::"]
SSL_ENABLED = True
SSL_PORTS = [4444]

SSL_CERTIFICATE_ISSUER = {
    "C": "EV",
    "ST": "Evennia",
    "L": "Evennia",
    "O": "redterminal.org",
    "OU": "Iridum Experimental Evennia MUD",
    "CN": "iridum.redterminal.org",
}

STAFF_CONTACT_EMAIL = '-fab- <fab@redterminal.org>'

# Start the evennia django+twisted webserver so you can
# browse the evennia website and the admin interface
# (Obs - further web configuration can be found below
# in the section  'Config for Django web features')
WEBSERVER_ENABLED = True
# This is a security setting protecting against host poisoning
# attacks.  It defaults to allowing all. In production, make
# sure to change this to your actual host addresses/IPs.
ALLOWED_HOSTS = ["*"]
# The webserver sits behind a Portal proxy. This is a list
# of tuples (proxyport,serverport) used. The proxyports are what
# the Portal proxy presents to the world. The serverports are
# the internal ports the proxy uses to forward data to the Server-side
# webserver (these should not be publicly open)
WEBSERVER_PORTS = [(4001, 4005)]
# Interface addresses to listen to. If 0.0.0.0, listen to all. Use :: for IPv6.
WEBSERVER_INTERFACES = ["127.0.0.1"]
# IP addresses that may talk to the server in a reverse proxy configuration,
# like NginX or Varnish. These can be either specific IPv4 or IPv6 addresses,
# or subnets in CIDR format - like 192.168.0.0/24 or 2001:db8::/32.
UPSTREAM_IPS = ["127.0.0.1"]
# The webserver uses threadpool for handling requests. This will scale
# with server load. Set the minimum and maximum number of threads it
# may use as (min, max) (must be > 0)
WEBSERVER_THREADPOOL_LIMITS = (1, 20)
# Start the evennia webclient. This requires the webserver to be running and
# offers the fallback ajax-based webclient backbone for browsers not supporting
# the websocket one.
WEBCLIENT_ENABLED = True
# Activate Websocket support for modern browsers. If this is on, the
# default webclient will use this and only use the ajax version if the browser
# is too old to support websockets. Requires WEBCLIENT_ENABLED.
WEBSOCKET_CLIENT_ENABLED = True
# Server-side websocket port to open for the webclient. Note that this value will
# be dynamically encoded in the webclient html page to allow the webclient to call
# home. If the external encoded value needs to be different than this, due to
# working through a proxy or docker port-remapping, the environment variable
# WEBCLIENT_CLIENT_PROXY_PORT can be used to override this port only for the
# front-facing client's sake.
WEBSOCKET_CLIENT_PORT = 4002
# Interface addresses to listen to. If 0.0.0.0, listen to all. Use :: for IPv6.
WEBSOCKET_CLIENT_INTERFACE = "::"
# Actual URL for webclient component to reach the websocket. You only need
# to set this if you know you need it, like using some sort of proxy setup.
# If given it must be on the form "ws[s]://hostname[:port]". If left at None,
# the client will itself figure out this url based on the server's hostname.
# e.g. ws://external.example.com or wss://external.example.com:443
WEBSOCKET_CLIENT_URL = "wss://webclient.iridum.redterminal.org/ws"
# This determine's whether Evennia's custom admin page is used, or if the
# standard Django admin is used.
EVENNIA_ADMIN = True
# Needed to avoid CSRF errors
CSRF_TRUSTED_ORIGINS = ["https://webclient.iridum.redterminal.org"]
# Send keep alive "idle" commands
IDLE_TIMEOUT = -1

CMD_IGNORE_PREFIXES = "#&/+@"

### SSH CONFIG ###
SSH_ENABLED = True
SSH_PORTS = [8022]
SSH_INTERFACES = ["::"]

### Game Time Setup ###
# The TIME_UNITS are defined in the
# python script: world.gametime.gametime
TIME_ZONE = "UTC"
TIME_FACTOR = 4
TIME_GAME_EPOCH = 0
TIME_IGNORE_DOWNTIMES = True

### DISABLE RSS ###
RSS_ENABLED = False

IDMAPPER_CACHE_MAXSIZE = 1024

### Chatacter Creation Settings ###
MULTISESSION_MODE = 2
MAX_NR_CHARACTERS = 5
AUTO_CREATE_CHARACTER_WITH_ACCOUNT = False
AUTO_PUPPET_ON_LOGIN = True

### Default width for displaying lines ###
DEFAULT_WIDTH = 80

### Permissions Hierarchy ###
PERMISSION_HIERARCHY = [
    "Guest",  # note-only used if GUEST_ENABLED=True
    "Player",
    "Helper",
    "Beginner Builder",
    "Advanced Builder",
    "Expert Builder",
    "Admin",
    "Developer",
]

### Commands sets and commands ###
CMDSET_UNLOGGEDIN = "commands.default_cmdsets.UnloggedinCmdSet"
CMDSET_SESSION = "commands.default_cmdsets.SessionCmdSet"
CMDSET_CHARACTER = "commands.default_cmdsets.CharacterCmdSet"
CMDSET_PATHS = ["commands", "evennia", "evennia.contrib"]

CMDSET_FALLBACKS = {
    CMDSET_CHARACTER: "evennia.commands.default.cmdset_character.CharacterCmdSet",
    CMDSET_ACCOUNT: "evennia.commands.default.cmdset_account.AccountCmdSet",
    CMDSET_SESSION: "evennia.commands.default.cmdset_session.SessionCmdSet",
    CMDSET_UNLOGGEDIN: "evennia.commands.default.cmdset_unloggedin.UnloggedinCmdSet",
}

COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"

### Typeclasses and other paths ###
TYPECLASS_PATHS = [
    "world.typeclasses",
    "evennia",
#    "evennia.contrib",
#    "evennia.contrib.game_systems",
#    "evennia.contrib.base_systems",
#    "evennia.contrib.full_systems",
#    "evennia.contrib.tutorials",
#    "evennia.contrib.utils",
]
BASE_ACCOUNT_TYPECLASS = "world.typeclasses.accounts.Account"
BASE_OBJECT_TYPECLASS = "world.typeclasses.objects.Object"
BASE_CHARACTER_TYPECLASS = "world.typeclasses.characters.Character"
BASE_ROOM_TYPECLASS = "world.typeclasses.rooms.Room"
BASE_EXIT_TYPECLASS = "world.typeclasses.exits.Exit"
BASE_CHANNEL_TYPECLASS = "world.typeclasses.channels.Channel"
BASE_SCRIPT_TYPECLASS = "world.typeclasses.scripts.Script"

BASE_BATCHPROCESS_PATHS = [
    "world.batch",
    "users.batch",
]

### Prototypes ###
PROTOTYPE_MODULES += ["world.prototypes"]
PROTOTYPE_MODULES += ["users.prototypes"]

### Help entries ###
FILE_HELP_ENTRY_MODULES = ["world.help"]

### Set own command parser ###
COMMAND_PARSER = "server.conf.cmdparser.cmdparser"

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
