from django.conf import settings
from evennia.utils import class_from_module

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)


class CmdUnconnectedHelp(COMMAND_DEFAULT_CLASS):
    """
    get help when in unconnected state

    Usage:
      help

    This is an unconnected version of the help command,
    for simplicity. It shows a pane of info when not logged
    in.
    """

    key = "help"
    aliases = ["h", "?"]
    locks = "cmd:all()"

    def func(self):
        """Shows help"""

        string = """You are not yet logged into the game. Commands available at this point:

  |ccreate|n - create a new account
  |cconnect|n - connect with an existing account
  |clook|n - re-show the connection screen
  |chelp|n - show this help
  |cencoding|n - change the text encoding to match your client
  |cscreenreader|n - make the server more suitable for use with screen readers
  |cquit|n - abort the connection

First create an account e.g. with |ccreate Anna c67jHL8p|n
(If you have spaces in your name, use double quotes: 
|ccreate "Anna the Barbarian" c67jHL8p|n
Next you can connect to the game: |cconnect Anna c67jHL8p|n

You can use the |clook|n command if you want to see the connect screen again.

"""

        if settings.STAFF_CONTACT_EMAIL:
            string += "For support, please contact: |Y'%s'|n" % settings.STAFF_CONTACT_EMAIL
        self.msg(string)
