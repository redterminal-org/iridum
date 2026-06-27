# A meadow where you can pick flowers
from evennia import CmdSet
from evennia.prototypes import prototypes, spawner

from world.typeclasses.rooms import Room
from commands.command import Command


class RestrictedRoom(Room):
    """
    This room is a meadow, where you can pick flowers.
    """
    class_perm = {"create": "Advanced Builder"}

    def at_object_creation(self):
        # call inheritated function
        super().at_object_creation()
