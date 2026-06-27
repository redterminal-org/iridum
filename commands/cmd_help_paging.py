"""
General Commands

General Commands describe the general functionality the account/character can do
in the game.
"""
import re

from .command import Command


class CmdHelpPaging(Command):
    """
    toggle paging mode for help pages

    Usage:
      helppaging

    This toggles your HELP paging mode. You can turn HELP paging off if you
    prefer to use the scroll function of your MUD client. If you run the
    "helppaging" command again, HELP paging is turned on again, if you prefer
    that.

    We kept this different from the "paging" command (which toggles paging for
    everything not a HELP page), so you can keep paging HELP pages while not
    paging everything else (typeclasses, scripts or prototypes for example).
    """

    key = "helppaging"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement command"""

        caller = self.caller

        if (caller.db.disable_help_paging == None or
            caller.db.disable_help_paging == False):
            caller.db.disable_help_paging = True
            caller.msg("- You turned OFF help paging! -")
        else:
            caller.db.disable_help_paging = False
            caller.msg("- You turned ON help paging! -")
