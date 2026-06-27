#### Imports ####
from commands.command import Command
from evennia import settings, CmdSet
from commands import default_cmdsets

from world.typeclasses.objects import Object
from world.utils.utils import wrap

_WIDTH = settings.DEFAULT_WIDTH


#### Mech Object ####
class Mech(Object):
    """
    This typeclass describes an armed Mech.
    """

    class_perm = {"create": "Developer"}

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
                f"puppet:id({id}) or pid({pid}) or perm(Beginner Builder);"
            )
            new_obj_lockstring += "call:false();"

        elif account is not None:
            pid = account.id

            new_obj_lockstring += "control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({
                pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"edit:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"get:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"puppet:pid({pid}) or perm(Beginner Builder);"
            new_obj_lockstring += "call:false();"

        else:
            new_obj_lockstring += "control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:perm(Expert Builder);"
            new_obj_lockstring += f"edit:perm(Expert Builder);"
            new_obj_lockstring += f"get:perm(Expert Builder);"
            new_obj_lockstring += f"puppet:perm(Beginner Builder);"
            new_obj_lockstring += "call:false();"
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
                f"""You are way to weak and small to lift this collossal {
                    self.key}.""",
                width=_WIDTH,
            ),
            None,
            attrlocks,
        )
        self.attributes.add(
            "desc",
            wrap(f"""This is a very heavy and huge battle robot.""", width=_WIDTH),
            None,
            attrlocks,
        )

    def at_object_creation(self):
        "This is called only when object is first created"
        super().at_object_creation()

        self.attributes.add(
            "get_err_msg",
            wrap(
                f"""You are way to weak and small to lift this collossal {
                    self.key}.""",
                width=_WIDTH,
            ),
            "",
            "attredit:perm(Expert Builder);attrread:all();",
        )
        self.attributes.add(
            "desc",
            wrap(f"""This is a very heavy and huge battle robot.""", width=_WIDTH),
            "",
            "attredit:perm(Expert Builder);attrread:all();",
        )

        self.cmdset.add_default(default_cmdsets.CharacterCmdSet)
        self.cmdset.add(MechCmdSet, persistent=True)


#### Mech Commands ####
class CmdShoot(Command):
    """
    Firing the mech's gun

    Usage:
        shoot [target]

    This will fire your mech's main gun. If no
    target is given, you will shoot in the air.
    """

    key = "shoot"
    aliases = ["fire", "fire!"]

    def func(self):
        "this actually does the shooting"

        caller = self.caller
        location = caller.location

        if not self.args:
            # no arguments given to command - shoot in the air
            message = f"RATATATATATA! {
                caller.get_display_name(caller)
            } fires its gun in the air!"
            location.msg_contents(message)
            return

        # we have an argument, search for target
        target = caller.search(self.args.strip())
        if target:
            message = (
                f"RATATATATATA! {caller.get_display_name(caller)} fires at {
                    target.key}"
            )
            location.msg_contents(message)


class CmdLaunch(Command):
    """
    Launches the mech's missiles

    Usage:
        launch [target]

    This will launch the mech's missiles at a target.
    It won't work without target.
    """

    key = "launch"

    def func(self):
        "This launches the missiles"

        caller = self.caller
        location = caller.location

        if not self.args:
            # no argument (target) given. Don't launch missiles
            message = "You can't launch your missiles without a target."
            caller.msg(message)
            return

        # we have an argument, search target
        target = caller.search(self.args.strip())
        if target:
            message = (
                f"SWOOOSH! {caller.get_display_name(
                    caller)} launches it's missiles."
            )
            message += f"|/BOOM! The missiles hit {
                target.get_display_name(caller)}!"
            location.msg_contents(message)


#### Mech Command Set ####
class MechCmdSet(CmdSet):
    """
    This allows mechs to do mech stuff.
    """

    key = "mechcmdset"

    def at_cmdset_creation(self):
        "Called once, when the cmdset is first created"
        self.add(CmdShoot())
        self.add(CmdLaunch())
