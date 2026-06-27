#### Imports ####
from collections import defaultdict

from evennia import settings
from evennia.utils.utils import wrap

from world.typeclasses.objects import Object

_WIDTH = settings.DEFAULT_WIDTH


#### Container Object ####
class Container(Object):
    """
    This typeclass describes a container where you can
    drop things into with the command:
    "drop <obj> into <container>"
    or get objects from with the command:
    "get <obj> from <container>"
    """

    class_perm = {"create": "Beginner Builder"}

    @classmethod
    def get_default_lockstring(cls, account=None, caller=None, **kwargs):
        new_obj_lockstring = super().get_default_lockstring(account, caller, **kwargs)
        if caller is not None:
            new_obj_lockstring += (
                f"iscontainer:true();getfrom:true();getcontainer:false();"
            )

        elif account is not None:
            new_obj_lockstring += (
                f"iscontainer:true();getfrom:true();getcontainer:false();"
            )

        else:
            new_obj_lockstring += (
                f"iscontainer:true();getfrom:true();getcontainer:false();"
            )
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

        return obj, errors

    def after_spawn(self, account=None, caller=None, **kwargs):
        super().after_spawn(caller=caller)

    def at_object_creation(self):
        "This is called only when object is first created"
        super().at_object_creation()
        self.db.desc = "This is a container."
        self.db.maxobjects = 0

    def at_pre_object_receive(self, obj, source_location, **kwargs):
        """
        Overloaded to check if the containers item limit is reached or if it
        can take another object.

        Called before the actual move of obj into self. Checks if
        Container is full or can take another item.
        """
        if int(self.db.maxobjects) == 0:
            return True
        if len(self.contents_get()) >= int(self.db.maxobjects):
            source_location.msg(
                wrap(
                    f"|/The {self.get_display_name()} can't contain more than ({
                        self.db.maxobjects
                    }) objects and it's full",
                    width=_WIDTH,
                )
            )
            return False
        return True

    def return_appearance(self, looker):
        """
        Overloaded to show contents and item count, maximal number of items
        and if it's full or not.
        """
        desc = self.db.desc + "|/"

        if int(self.db.maxobjects) == 0:
            desc += f"|/It contains |y{
                len(self.contents)
            }|n objects. It's size is |Yunlimited|n."
        else:
            desc += f"|/It contains |y{len(self.contents)}|n of up to |Y{
                self.db.maxobjects
            }|n objects."
            if len(self.contents) >= int(self.db.maxobjects):
                desc += "|/It's |Yfull|n and can't take any more items."

        if len(self.contents) <= 0:
            things = "|/|mObjects:|n |GNone|n"
            return self.set_appearance(looker, desc=desc, things=things)

        return self.set_appearance(looker, desc=desc)
