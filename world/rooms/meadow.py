# A meadow where you can pick flowers
from evennia import CmdSet
from world.utils.utils import spawn

from world.typeclasses.rooms import Room
from commands.command import Command


class Meadow(Room):
    """
    This room is a meadow, where you can pick flowers.
    """

    class_perm = {"create": "Beginner Builder"}

    def at_object_creation(self):
        # call inheritated function
        super().at_object_creation()

        # add CommandSet
        self.cmdset.add(MeadowCmdSet, persistent=True)


class CmdPickFlower(Command):
    """
    Picks up a flower

    Usage:
        pick flower

    This lets you pick a flower.
    """

    key = "pick flower"
    aliases = ["pick", "flower"]
    locks = "cmd:all();"
    arg_regex = r"\s|$"
    help_category = "Things and Rooms"

    def func(self):
        "This picks the flower"

        caller = self.caller
        location = caller.location

        if self.args:
            # no argument (target) given. Don't launch missiles
            message = "This command doesn't take any arguments."
            caller.msg(message)
            return

        # we have an argument, search target
        flower = spawn("test_flower")[0]
        flower.move_to(caller, quiet=True, emit_to_obj=caller, move_type="get")
        location.msg_contents(f"$You() $conj(pick) up a {
                              flower.key}.", from_obj=caller)


#### Meadow Command Set ####
class MeadowCmdSet(CmdSet):
    """
    This is a CommandSet for a meadow
    """

    key = "meadowcmdset"

    def at_cmdset_creation(self):
        "Called once, when the cmdset is first created"
        self.add(CmdPickFlower())
