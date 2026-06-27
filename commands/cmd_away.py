"""
General Commands

General Commands describe the general functionality the account/character can do
in the game.
"""
import re

from .command import Command


class CmdAway(Command):
    """
    toggle "away" mode

    Usage:
      away

    This toggles your "away" mode. If you're not in away mode, it is turned
    on when using the "away" command.
    If you're "away", it takes you back to normal mode.

    All it does, is showing the text "(away)" after your character name and
    nothing else. You can act normally, but are shown as "(away)".

    If you log out during away mode, you will reconnect in the same mode you
    were in when you left.
    """

    key = "away"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement command"""

        caller = self.caller
        location = caller.location

        if caller.db.away == None or caller.db.away == False:
            caller.db.away = True
            location.msg_contents(
                f"|Y$You() $conj(get) into |R\"away\"|Y mode now.|n", from_obj=caller)
        else:
            caller.db.away = False
            location.msg_contents(
                f"|Y$You() $conj(become) |R\"active\"|Y again and $conj(exit) \"away\" mode.|n", from_obj=caller)
