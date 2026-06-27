"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.
"""

from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import pad

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    !!!IMPORTANT CHANGE FOR CHILD CLASSES!!!:
        Sets the class property `class_perm` which acts as typeclass permission
        dict and contains accesstypes as keys and permissions as values. This
        should be set on every child class to restrict access.

        Example:
            class_perm = {"create": "Beginner Builder"}
            - gives "Beginner Builder" "create" permission
            - These should be checked by all functions which let users create
              objects (like the custom 'spawn()' function defined in
              `world.utils.utils`, which therefore should be used to spawn
              objects instead of Evennias default 'spawn()' function.
    """

    class_perm = {"create": "Expert Builder"}

    @classmethod
    def get_default_lockstring(cls, account=None, caller=None, **kwargs):
        if caller is not None:
            id = caller.id
            pid = caller.account.id

            new_obj_lockstring = f"control:id({id}) or pid({
                pid}) or perm(Developer);"
            new_obj_lockstring += f"attrcreate:id({id}) or pid({
                pid}) or perm(Admin);"
            new_obj_lockstring += f"delete:id({id}) or pid({
                pid}) or perm(Admin);"
            new_obj_lockstring += f"edit:id({id}) or pid({
                pid}) or perm(Admin);"
            new_obj_lockstring += f"get:id({id}) or pid({pid}) or perm(Admin);"
            new_obj_lockstring += f"examine:id({id}) or pid({
                pid}) or perm(Admin);"
            new_obj_lockstring += f"call:false();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:id({id}) or pid({
                pid}) or perm(Admin);"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"

        elif account is not None:
            pid = account.id

            new_obj_lockstring = f"control:pid({pid}) or perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({pid}) or perm(Admin);"
            new_obj_lockstring += f"delete:pid({pid}) or perm(Admin);"
            new_obj_lockstring += f"edit:pid({pid}) or perm(Admin);"
            new_obj_lockstring += f"get:pid({pid}) or perm(Admin);"
            new_obj_lockstring += f"examine:pid({pid}) or perm(Admin);"
            new_obj_lockstring += f"call:false();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:pid({pid}) or perm(Admin);"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"

        else:
            new_obj_lockstring = f"control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:perm(Admin);"
            new_obj_lockstring += f"delete:perm(Admin);"
            new_obj_lockstring += f"edit:perm(Admin);"
            new_obj_lockstring += f"get:perm(Admin);"
            new_obj_lockstring += f"examine:perm(Admin);"
            new_obj_lockstring += f"call:false();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:perm(Admin);"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"
        return new_obj_lockstring

    def at_object_creation(self):
        super().at_object_creation()
        # add generic character tag
        self.tags.add("character", category="generic")
        # set paging of look output to True
        self.db.disable_page = False

    def after_spawn(self, account=None, caller=None, **kwargs):
        super().after_spawn(caller=caller)

    def basetype_setup(self):
        """
        This sets up the default properties of an Character, just before
        the more general at_object_creation.

        You normally don't need to change this unless you change some
        fundamental things like names of permission groups.

        """
        # the default security setup fallback for a generic
        # object. Overload in child for a custom setup. Also creation
        # commands may set this (create an item and you should be its
        # controller, for example)

        # run inherited basetype_setup()
        super().basetype_setup()

        id = self.id
        self.locks.add(
            ";".join(
                [
                    # edit properties/attributes
                    f"edit:perm(Admin) or id({id})",
                    f"delete:perm(Expert Builder) or id({
                        id})",  # delete object
                    "call:false()",  # allow to call commands on this object
                    "tell:perm(Admin)",  # allow emits to this object
                    "get:false()",  # can't get a character
                    "teleport:perm(Admin)",
                    "teleport_here:perm(Admin)",
                ]
            )
        )

    def return_appearance(self, looker, **kwargs):
        """returns the appearance and hides carried objects."""

        if not looker:
            return ""

        # Check, if the character is in "away" mode to display this information
        # on a look at it.
        if self.db.away:
            awaystring = "|R(away)|n"
        else:
            awaystring = ""

        # populate the appearance_template string.
        return self.set_appearance(
            looker,
            extra_name_info=self.get_extra_display_name_info(
                looker) + " " + awaystring,
        )
