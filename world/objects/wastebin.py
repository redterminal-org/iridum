#### Imports ####
import evennia
from evennia.utils.utils import wrap

from world.objects.objects import Container
from world.utils.gametime import custom_gametime


#### WasteBin Container ####
class WasteBin(Container):
    """
    This typeclass describes a waste bin where you can
    drop litter into or get from. It will be emptied by
    gametime scripts with the '_collect_waste()' callback
    at some given times.

    Look at 'world/scripts/global_scripts.py', which should
    destroy/(re)create all needed global scripts.
    """

    class_perm = {"create": "Expert Builder"}

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
            new_obj_lockstring += (
                f"iscontainer:true();getfrom:true();getcontainer:true();"
            )

        elif account is not None:
            pid = account.id

            new_obj_lockstring += "control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({
                pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"edit:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"get:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += (
                f"iscontainer:true();getfrom:true();getcontainer:true();"
            )

        else:
            new_obj_lockstring += "control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:perm(Expert Builder);"
            new_obj_lockstring += f"edit:perm(Expert Builder);"
            new_obj_lockstring += f"get:perm(Expert Builder);"
            new_obj_lockstring += (
                f"iscontainer:true();getfrom:true();getcontainer:true();"
            )
        return new_obj_lockstring

    def after_spawn(self, account=None, caller=None, **kwargs):
        super().after_spawn(caller=caller)

    def at_object_creation(self):
        "This is called only when object is first created"
        super().at_object_creation()


# Wastebin Container Callback for gametime Script #
def _collect_waste():
    """
    callback function:
    Destroy all objects in all wastebins! This is a
    callback function for a gametime script to destroy
    all objects in a 'wastebin'
    """
    bins = evennia.search_object("wastebin")

    # Get absolute game time
    year, month, week, day, hour, min, sec = custom_gametime(absolute=True)
    # count starts with 0, so 1 must be added
    dayofmonth = (week * 7) + day + 1

    for bin in bins:
        bin.location.msg_contents(
            f"|/It's |Y{hour:02}:{
                min:02}|n o'clock. The |ggarbage truck|n comes around and collects all|/the trash from the {
                bin.get_display_name()
            }s."
        )
        for obj in bin.contents:
            for c in obj.contents:
                c.delete()
            obj.delete()
