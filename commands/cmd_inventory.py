"""
General Commands

General Commands describe the general functionality the account/character can do
in the game.
"""
import re
from collections import defaultdict

from evennia import settings
from evennia.utils.utils import (list_to_string)

from world.utils.utils import wrap
from .command import Command

_WIDTH = settings.DEFAULT_WIDTH


class CmdInventory(Command):
    """
    Views inventory.

    Usage:
      inventory
      inv

    Shows the things you are carrying at the given moment, your inventory.
    """

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """
        Check your inventory. Overwritten to look better and more uniform

        Usage:
            inventory
            inv
            i
        """
        items = self.caller.contents
        string = "|c%s|n: Inventory|/" % (
            self.caller.get_display_name(self.caller))
        string += "|B" + "=" * _WIDTH + "|n"
        # get and identify all objects
        things = defaultdict(list)
        for obj in items:
            key = obj.get_display_name()
            # things can be pluralized
            things[key].append(obj)

        thing_strings = []
        for key, itemlist in sorted(things.items()):
            nitem = len(itemlist)
            if nitem == 1:
                key, _ = itemlist[0].get_numbered_name(
                    nitem, self.caller, key=key)
            else:
                key = [item.get_numbered_name(nitem, self.caller, key=key)[
                    1] for item in itemlist][0]
            thing_strings.append(key)

        if len(self.caller.contents) > 0:
            string += wrap(f"|/|yYou carry:|n " + list_to_string(thing_strings),
                           width=_WIDTH)
            string += f"|/You have |m{len(self.caller.contents)}|n items."
        else:
            string += f"|/|yYou carry:|n |gnothing|n."

        string += "|/|B" + "=" * _WIDTH + "|n"
        self.caller.msg(f"{string}")
