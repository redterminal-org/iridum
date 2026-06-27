"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit
from world.utils.utils import wrap_para

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exits.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects child classes like this.

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
                f"edit:id({id}) or pid({pid}) or perm(Expert Builder);"
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
            new_obj_lockstring += f"traverse:all();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"

        elif account is not None:
            pid = account.id

            new_obj_lockstring = f"control:pid({pid}) or perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({
                pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"delete:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"edit:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += f"examine:pid({
                pid}) or perm(Beginner Builder);"
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:all();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"

        else:
            new_obj_lockstring = f"control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:perm(Expert Builder);"
            new_obj_lockstring += f"delete:perm(Expert Builder);"
            new_obj_lockstring += f"edit:perm(Expert Builder);"
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += f"examine:perm(Beginner Builder);"
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:all();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"
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

        obj.attributes.add("desc", "This is an exit.", lockstring=attrlocks)
        obj.attributes.add("text", "", lockstring=attrlocks)
        obj.attributes.add(
            "get_err_msg", "You can't get an Exit.", lockstring=attrlocks
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
            self.attributes.add("desc", "This is an exit.",
                                lockstring=attrlocks)
        if self.db.text is None:
            self.attributes.add("text", "", lockstring=attrlocks)
        if self.db.get_err_msg is None:
            self.attributes.add(
                "get_err_msg", "You can't take an exit.", lockstring=attrlocks
            )

    def at_object_creation(self):
        super().at_object_creation()
        # add exit tag
        self.tags.add("exit", category="generic")

    def at_pre_object_receive(self, arriving_object, source_location, **kwargs):
        return False

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

        # Extra Infos
        extra_name_info = f"{
            self.get_extra_display_name_info(looker)} |Y(Exit)|n"

        # Set Exit Information
        text = "You can use the following aliases to "
        text += "use it:|/|/"
        text += "|YAliases|n: " + self.key
        if self.aliases.get(return_list=True) != None:
            text += ", " + ", ".join(self.aliases.get(return_list=True))

        # return formatted appearance
        return self.set_appearance(looker, extra_name_info=extra_name_info,
                                   text=wrap_para(text))
