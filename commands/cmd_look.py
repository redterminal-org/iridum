"""
General Commands

General Commands describe the general functionality the account/character can do
in the game.
"""

from commands.command import MuxCommand
from world.utils import evmore


class CmdLook(MuxCommand):
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<account>

    Observes your location or objects in your vicinity.
    """

    key = "look"
    aliases = ["l", "ls"]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("You have no location to look at!")
                return
        else:
            target = caller.search(self.args)
            if not target:
                return
        desc = caller.at_look(target)
        # add the type=look to the outputfunc to make it
        # easy to separate this output in client.
        desc = desc.replace("|/", "\n")
        evmore.msg(
            caller, desc, exit_on_lastpage=True)
