"""
General Commands

General Commands describe the general functionality the account/character can do
in the game.
"""
import re

from evennia import utils
from evennia.utils import logger

from evennia.commands.default.general import NumberedTargetCommand


class CmdGet(NumberedTargetCommand):
    """
    Take something from the location or from a container.

    Usage:
      get <obj>
      get <obj> from <container_obj>

    Picks up an item from your location or from a container object and puts it
    in your inventory.
    """

    key = "get"
    aliases = "grab"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """implements the command."""

        caller = self.caller

        # Take an object out of another object
        pattern = r"^\s*.*\s+from\s+.*$"
        if re.match(pattern, self.args) != None:
            lhs, rhs = self.args.split(" from ", maxsplit=2)
            lhs.strip()
            rhs.strip()

            target = caller.search(rhs)

            if not target:
                return

            if not self.args or not rhs:
                caller.msg("Usage: get <object> from <target>")
                return
            # find the thing(s) to take from object
            to_take = caller.search(
                lhs,
                location=target,
                nofound_string=f"There is no {lhs} in {
                    target.get_display_name(caller)}.",
                multimatch_string=f"There is more than one {
                    lhs} in {target.get_display_name(caller)}.",
            )

            if not to_take:
                return

            # the 'stacked' search sometimes returns a list, sometimes not, so we make it always a list
            # NOTE: this behavior may be a bug, see issue #3432
            to_take = utils.make_iter(to_take)

            # if any of the objects aren't allowed to be given, cancel the give
            for obj in to_take:
                if not obj.access(caller, access_type='get', default=False):
                    caller.msg(obj.db.get_err_msg)
                    return
                if not target.access(caller, access_type="getfrom", default=False):
                    caller.msg(f"You can't get {lhs} from {
                               target.get_display_name(caller)}.")
                    return

                # calling at_pre_give hook method
                if not obj.at_pre_give(target, caller):
                    return

            # do the actual moving
            moved = []
            for obj in to_take:
                if obj.move_to(caller, quiet=False, move_type="get"):
                    moved.append(obj)
                    # Call the object's at_give() method.
                    obj.at_give(caller, target)

            if not moved:
                caller.msg(f"You could not get {obj.get_display_name(
                    caller)} from {target.get_display_name(caller)}.")
            else:
                obj_name = to_take[0].get_numbered_name(
                    len(moved), target, return_string=True)
                # caller.msg(f"You get {obj_name} from {target.get_display_name(caller)}.")
                caller.location.msg_contents(f"$You() $conj(pick) up {obj_name} from {
                                             target.get_display_name(caller)}.", from_obj=caller)
                # target.msg(f"{caller.get_display_name(target)} gives you {obj_name}.")

            return

        # Get from location
        if not self.args:
            self.msg("Get what?")
            return
        objs = caller.search(
            self.args, location=caller.location, stacked=self.number)
        if not objs:
            return
        # the 'stacked' search sometimes returns a list, sometimes not, so we make it always a list
        # NOTE: this behavior may be a bug, see issue #3432
        objs = utils.make_iter(objs)

        if len(objs) == 1 and caller == objs[0]:
            self.msg("You can't get yourself.")
            return

        # if we aren't allowed to get any of the objects, cancel the get
        for obj in objs:
            # check the locks
            if not obj.access(caller, "get"):
                if obj.db.get_err_msg:
                    self.msg(obj.db.get_err_msg)
                else:
                    self.msg("You can't get that.")
                return
            # calling at_pre_get hook method
            if not obj.at_pre_get(caller):
                return

        moved = []
        # attempt to move all of the objects
        for obj in objs:
            if obj.move_to(caller, quiet=True, move_type="get"):
                moved.append(obj)
                # calling at_get hook method
                obj.at_get(caller)

        if not moved:
            # none of the objects were successfully moved
            self.msg("That can't be picked up.")
        else:
            obj_name = moved[0].get_numbered_name(
                len(moved), caller, return_string=True)
            caller.location.msg_contents(f"$You() $conj(pick) up {
                                         obj_name}.", from_obj=caller)


class CmdDrop(NumberedTargetCommand):
    """
    Drop something into the players location or any container object which is
    either in the caller's inventory or in the location.

    Usage:
      drop <obj>
      drop <obj> into <container_obj>

    Lets you drop an object from your inventory in the location you are
    currently in or into any container in the location or the callers
    inventory.
    """

    key = "drop"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement command"""

        caller = self.caller
        location = caller.location

        # Put an object into another object
        pattern = r"^\s*.*\s+into\s+.*$"
        if re.match(pattern, self.args) != None:
            lhs, rhs = self.args.split(" into ", maxsplit=2)
            lhs.strip()
            rhs.strip()

            target = caller.search(rhs)
            if not target:
                return

            if not self.args or not rhs:
                caller.msg("Usage: drop <object> into <target>")
                return
            # find the thing(s) to take from object
            to_drop = caller.search(
                lhs,
                location=caller,
                nofound_string=f"You don't have a {lhs}.",
                multimatch_string=f"You have more than one {
                    lhs} to drop into {target.get_display_name(caller)}.",
            )
            if not to_drop:
                return

            # the 'stacked' search sometimes returns a list, sometimes not, so we make it always a list
            # NOTE: this behavior may be a bug, see issue #3432
            to_drop = utils.make_iter(to_drop)

            # if any of the objects aren't allowed to be given, cancel the give
            for obj in to_drop:
                if not target.access(obj, access_type='iscontainer', default=False):
                    caller.msg(f"You can't put anything into {
                               target.get_display_name(caller)}")
                    return
                if not target.access(obj, access_type="getcontainer", default=False) and obj.access(target, access_type="iscontainer", default=False):
                    errstr = f"You can't put {obj.get_display_name(caller)} into {
                        target.get_display_name(caller)}"
                    errstr += " because it doesn't take containers.|/"
                    caller.msg(errstr)
                    return
                # calling at_pre_give hook method
                if not obj.at_pre_give(caller, target):
                    return

            # do the actual moving
            moved = []
            for obj in to_drop:
                if obj.move_to(target, quiet=False, emit_to_obj=caller,
                               move_type="drop"):
                    moved.append(obj)
                    # Call the object's at_give() method.
                    obj.at_give(caller, target)

            if not moved:
                caller.msg(f"You could not drop {obj.get_display_name(
                    caller)} into {target.get_display_name(caller)}.")
            else:
                obj_name = to_drop[0].get_numbered_name(
                    len(moved), target, return_string=True)
                # caller.msg(f"You drop {obj_name} into {target.get_display_name(caller)}.")
                caller.location.msg_contents(f"$You() $conj(drop) {obj_name} into {
                                             target.get_display_name(caller)}.", from_obj=caller)
                # target.msg(f"{caller.get_display_name(target)} gives you {obj_name}.")

            return

        # Drop into location
        if not self.args:
            caller.msg("Drop what?")
            return

        # Because the DROP command by definition looks for items
        # in inventory, call the search function using location = caller
        objs = caller.search(
            self.args,
            location=caller,
            nofound_string=f"You aren't carrying {self.args}.",
            multimatch_string=f"You carry more than one {self.args}:",
            stacked=self.number,
        )
        if not objs:
            return
        # the 'stacked' search sometimes returns a list, sometimes not, so we make it always a list
        # NOTE: this behavior may be a bug, see issue #3432
        objs = utils.make_iter(objs)

        # if any objects fail the drop permission check, cancel the drop
        for obj in objs:
            # Call the object's at_pre_drop() method.
            if not obj.at_pre_drop(caller):
                return

        # do the actual dropping
        moved = []
        for obj in objs:
            if obj.move_to(caller.location, quiet=True, move_type="drop"):
                moved.append(obj)
                # Call the object's at_drop() method.
                obj.at_drop(caller)

        if not moved:
            # none of the objects were successfully moved
            self.msg("That can't be dropped.")
        else:
            obj_name = moved[0].get_numbered_name(
                len(moved), caller, return_string=True)
            caller.location.msg_contents(
                f"$You() $conj(drop) {obj_name}.", from_obj=caller)
