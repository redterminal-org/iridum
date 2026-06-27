"""
General Commands

General Commands describe the general functionality the account/character can do
in the game.
"""
import re

from evennia import utils, settings

from evennia.commands.default.muxcommand import MuxCommand


class CmdDestroy(MuxCommand):
    """
    permanently delete objects

    Usage:
       destroy[/switches] [obj, obj2, obj3, [dbref-dbref], ...]

    Switches:
       override - The destroy command will usually avoid accidentally
                  destroying account objects. This switch overrides this safety.
       force - destroy without confirmation.
    Examples:
       destroy house, roof, door, 44-78
       destroy 5-10, flower, 45
       destroy/force north

    Destroys one or many objects. If dbrefs are used, a range to delete can be
    given, e.g. 4-10. Also the end points will be deleted. This command
    displays a confirmation before destroying, to make sure of your choice.
    You can specify the /force switch to bypass this confirmation.

    This Command is overwritten with a new version, which also destroys all 
    objects inside the object recursively, instead of moving them to their home
    location, except you don't have permissions to delete the contained
    objects. Keep that in mind!!!
    """

    key = "@destroy"
    aliases = ["@delete", "@del"]
    switch_options = ("override", "force")
    locks = "cmd:perm(destroy) or perm(Builder)"
    help_category = "Building"

    confirm = True  # set to False to always bypass confirmation
    default_confirm = "yes"  # what to assume if just pressing enter (yes/no)

    def func(self):
        """Implements the command."""

        caller = self.caller
        delete = True

        if not self.args or not self.lhslist:
            caller.msg(
                "Usage: destroy[/switches] [obj, obj2, obj3, [dbref-dbref],...]")
            delete = False

        def delobj(obj):
            # helper function for deleting a single object
            string = ""
            if not obj.pk:
                string = f"\nObject {obj.db_key} was already deleted."
            else:
                objname = obj.name
                if not (obj.access(caller, "control") or obj.access(caller, "delete")):
                    return f"\nYou don't have permission to delete {objname}."
                if obj.account and "override" not in self.switches:
                    return (
                        f"\nObject {
                            objname} is controlled by an active account. Use /override to"
                        " delete anyway."
                    )
                if obj.dbid == int(settings.DEFAULT_HOME.lstrip("#")):
                    return (
                        f"\nYou are trying to delete |c{
                            objname}|n, which is set as DEFAULT_HOME. "
                        "Re-point settings.DEFAULT_HOME to another "
                        "object before continuing."
                    )

                # check if object to delete had exits or objects inside it
                obj_exits = obj.exits if hasattr(obj, "exits") else ()
                obj_contents = obj.contents if hasattr(obj, "contents") else ()
                had_exits = bool(obj_exits)
                had_objs = any(
                    entity for entity in obj_contents if entity not in obj_exits)

                # do the deletion
                okay = obj.delete()
                if not okay:
                    string += (
                        f"\nERROR: {
                            objname} not deleted, probably because delete() returned False."
                    )
                else:
                    string += f"\n{objname} was destroyed."
                    if had_exits:
                        string += f" Exits to and from {
                            objname} were destroyed as well."
                    # This is changed because objects inside obj are deleted aswell.
                    if had_objs:
                        string += f" Objects inside {
                            objname} are also destroyed."
            return string

        objs = []
        for objname in self.lhslist:
            if not delete:
                continue

            if "-" in objname:
                # might be a range of dbrefs
                dmin, dmax = [utils.dbref(part, reqhash=False)
                              for part in objname.split("-", 1)]
                if dmin and dmax:
                    for dbref in range(int(dmin), int(dmax + 1)):
                        obj = caller.search("#" + str(dbref))
                        if obj:
                            objs.append(obj)
                    continue
                else:
                    obj = caller.search(objname)
            else:
                obj = caller.search(objname)

            if obj is None:
                self.msg(
                    " (Objects to destroy must either be local or specified with a unique #dbref.)"
                )
            elif obj not in objs:
                objs.append(obj)

        if objs and ("force" not in self.switches and type(self).confirm):
            confirm = "Are you sure you want to destroy "
            if len(objs) == 1:
                confirm += objs[0].get_display_name(caller)
            elif len(objs) < 5:
                confirm += ", ".join([obj.get_display_name(caller)
                                     for obj in objs])
            else:
                confirm += ", ".join(["#{}".format(obj.id) for obj in objs])
            confirm += " [yes]/no?" if self.default_confirm == "yes" else " yes/[no]"
            answer = ""
            answer = yield (confirm)
            answer = self.default_confirm if answer == "" else answer

            if answer and answer not in ("yes", "y", "no", "n"):
                caller.msg(
                    "Canceled: Either accept the default by pressing return or specify yes/no."
                )
                delete = False
            elif answer.strip().lower() in ("n", "no"):
                caller.msg("Canceled: No object was destroyed.")
                delete = False

        if delete:
            results = []
            for obj in objs:
                results.append(delobj(obj))

            if results:
                caller.msg("".join(results).strip())
