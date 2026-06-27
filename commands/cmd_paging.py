"""
General Commands

General Commands describe the general functionality the account/character can do
in the game.
"""
import re

from .command import Command


class CmdPaging(Command):
    """
    toggle "paging" mode

    Usage:
      paging

    This toggles your paging mode. You can turn paging off if you prefer to
    use the scroll function of your MUD client. If you run the command again,
    paging is turned on again, if you prefer that.
    """

    key = "paging"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement command"""

        caller = self.caller

        if caller.db.disable_page == None or caller.db.disable_page == False:
            caller.db.disable_page = True
            caller.msg("- You turned paging OFF! -")
        else:
            caller.db.disable_page = False
            caller.msg("- You turned paging ON! -")
