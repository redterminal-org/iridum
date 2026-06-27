#### Imports ####
from evennia import settings

from world.typeclasses.objects import Object
from world.utils.utils import wrap, wrap_para

_WIDTH = settings.DEFAULT_WIDTH


#### README Object ####
class Readme(Object):
    """
    A README document which can't be picked up.
    """

    class_perm = {"create": "Beginner Builder"}

    @classmethod
    def get_default_lockstring(cls, account=None, caller=None, **kwargs):
        new_obj_lockstring = super().get_default_lockstring(account, caller, **kwargs)
        if caller is not None:
            id = caller.id
            pid = caller.account.id

            new_obj_lockstring += "control:perm(Developer);"
            new_obj_lockstring += (
                f"attrcreate:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += (
                f"edit:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += f"get:id({id}) or pid({
                pid}) or perm(Expert Builder);"

        elif account is not None:
            pid = account.id

            new_obj_lockstring += "control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({
                pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"edit:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"get:pid({pid}) or perm(Expert Builder);"

        else:
            new_obj_lockstring += "control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:perm(Expert Builder);"
            new_obj_lockstring += f"edit:perm(Expert Builder);"
            new_obj_lockstring += f"get:perm(Expert Builder);"
        return new_obj_lockstring

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
            attrlocks = f"attrread:all();attredit:perm(Expert Builder);"

        self.attributes.add(
            "get_err_msg",
            wrap(
                f"Please leave this {
                    self.get_display_name()
                } here, so other people|/can read it. Use |c'look {
                    self.get_display_name()
                }'|n to read it.",
                width=_WIDTH,
            ),
            None,
            attrlocks,
        )

    def at_object_creation(self):
        "Called when object is first created"
        super().at_object_creation()
        self.db.desc = ""
        self.db.get_err_msg = ""
        self.db.text = ""

    def return_appearance(self, looker):
        """
        Called by the  look command. We want to return
        a README text when we look at it.
        """
        # first get thee base string from the
        # parent's return_appearance
        return self.set_appearance(looker, desc=self.db.desc,
                                   text=wrap_para(self.db.text))
