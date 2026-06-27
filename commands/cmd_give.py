"""
General Commands

General Commands describe the general functionality the account/character can do
in the game.
"""

from evennia.commands.default.general import NumberedTargetCommand
from evennia.utils import utils

from world.utils.utils import wrap

class CmdGive(NumberedTargetCommand):
    """
    give away something to someone

    Usage:
      give <inventory obj> <to||=> <target>

    Gives an item from your inventory to another person,
    placing it in their inventory.
    """

    key = "give"
    rhs_split = ("=", " to ")  # Prefer = delimiter, but allow " to " usage.
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement give"""

        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: give <inventory object> = <target>")
            return
        # find the thing(s) to give away
        to_give = caller.search(
            self.lhs,
            location=caller,
            nofound_string=f"You aren't carrying {self.lhs}.",
            multimatch_string=f"You carry more than one {self.lhs}:",
            stacked=self.number,
        )
        if not to_give:
            return
        # find the target to give to
        target = caller.search(self.rhs)
        if not target:
            return

        # the 'stacked' search sometimes returns a list, sometimes not, so we make it always a list
        # NOTE: this behavior may be a bug, see issue #3432
        to_give = utils.make_iter(to_give)

        singular, plural = to_give[0].get_numbered_name(len(to_give), caller)
        if target == caller:
            caller.msg(f"You keep {plural if len(to_give) > 1 else singular} to yourself.")
            return

        # if any of the objects aren't allowed to be given, cancel the give
        for obj in to_give:
            # calling at_pre_give hook method
            if not obj.at_pre_give(caller, target):
                return

        # do the actual moving
        moved = []
        for obj in to_give:
            if obj.move_to(target, quiet=True, move_type="give"):
                moved.append(obj)
                # Call the object's at_give() method.
                obj.at_give(caller, target)

        if not moved:
            caller.msg(f"You could not give that to {target.get_display_name(caller)}.")
        else:
            obj_name = to_give[0].get_numbered_name(len(moved), caller, return_string=True)
            if getattr(target, "received", None):
                target.received(caller, to_give[0], move_type="give")
            else:
                caller.location.msg_contents(wrap(
                    f"Give: $You() $conj(give) {obj_name} to"
                    f" {target.get_display_name(caller)}.")
                )
