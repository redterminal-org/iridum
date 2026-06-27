"""
Room

Rooms are simple containers that has no location of their own.
"""

from collections import defaultdict

from evennia.objects.objects import DefaultRoom
from evennia.utils.utils import list_to_string

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.

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

    class_perm = {"create": "Beginner Builder"}

    @classmethod
    def get_default_lockstring(cls, account=None, caller=None, **kwargs):
        if caller is not None:
            id = caller.id
            pid = caller.account.id

            new_obj_lockstring = f"control:id({id}) or pid({
                pid}) or perm(Developer);"
            new_obj_lockstring += (
                f"attrcreate:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += (
                f"delete:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += (
                f"edit:id({id}) or pid({pid}) or perm(Beginner Builder);"
            )
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += (
                f"examine:id({id}) or pid({pid}) or perm(Beginner Builder);"
            )
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += (
                f"teleport_here:id({id}) or pid({
                    pid}) or perm(Advanced Builder);"
            )

        elif account is not None:
            pid = account.id

            new_obj_lockstring = f"control:pid({pid}) or perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({
                pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"delete:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"edit:pid({pid}) or perm(Beginner Builder);"
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += f"examine:pid({
                pid}) or perm(Beginner Builder);"
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:pid({
                pid}) perm(Advanced Builder);"

        else:
            new_obj_lockstring = f"control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:perm(Expert Builder);"
            new_obj_lockstring += f"delete:perm(Expert Builder);"
            new_obj_lockstring += f"edit:perm(Beginner Builder);"
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += f"examine:perm(Beginner Builder);"
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:all();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:perm(Advanced Builder);"
        return new_obj_lockstring

    @classmethod
    def create(cls, key, account=None, caller=None, method="create", **kwargs):
        obj, errors = super().create(
            key, account=account, caller=caller, method=method, **kwargs
        )

        if caller is not None:
            id = caller.id
            pid = caller.account.id
            attrlocks = f"attrread:all();attredit:id({id}) or pid({
                pid
            }) or perm(Expert Builder);"
        elif account is not None:
            pid = account.id
            attrlocks = f"attrread:all();attredit:pid({
                pid}) or perm(Expert Builder);"
        else:
            attrlocks = f"attrread:all();attredit:perm(Expert Builder)"

        obj.attributes.add("desc", "This is a Room.", lockstring=attrlocks)
        obj.attributes.add("text", "", lockstring=attrlocks)
        obj.attributes.add(
            "get_err_msg", "You can't take a room.", lockstring=attrlocks
        )

        return obj, errors

    def after_spawn(self, account=None, caller=None, **kwargs):
        super().after_spawn(caller=caller)

        if caller is not None:
            id = caller.id
            pid = caller.account.id
            attrlocks = f"attrread:all();attredit:id({id}) or pid({
                pid
            }) or perm(Expert Builder);"
        elif account is not None:
            pid = account.id
            attrlocks = f"attrread:all();attredit:pid({
                pid}) or perm(Expert Builder);"
        else:
            attrlocks = f"attrread:all();attredit:perm(Expert Builder)"

        if self.db.desc is None:
            self.attributes.add("desc", "This is a Room.",
                                lockstring=attrlocks)
        if self.db.text is None:
            self.attributes.add("text", "", lockstring=attrlocks)
        if self.db.get_err_msg is None:
            self.attributes.add(
                "get_err_msg", "You can't take a room.", lockstring=attrlocks
            )

    def at_object_creation(self):
        # call inheritated function
        super().at_object_creation()
        # add generic room tag
        self.tags.add("room", category="generic")

    def return_appearance(self, looker, **kwargs):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        """
        if not looker:
            return ""

        desc = self.db.desc
        try:
            if self.tags.has(category="climate"):
                desc += f"|/|/{self.db.weather_desc}"
                if self.db.daytime == "night":
                    desc += f"|/{self.db.moon_desc}"
        except AttributeError as e:
            pass

        return self.set_appearance(looker, desc=desc)
