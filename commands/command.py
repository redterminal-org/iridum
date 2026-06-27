"""
General Commands

General Commands describe the general functionality the account/character can do
in the game.
"""

from evennia.accounts.accounts import DefaultAccount
from evennia.commands.command import Command as BaseCommand
from evennia.commands.default import muxcommand
from evennia.utils.utils import inherits_from
from evennia import search_script

class MuxCommand(muxcommand.MuxCommand):
    """
    Overloaded 'MuxCommand.at_post_command()' to send prompt after execution.
    Used by the evennia default commands.

    Note that the class's `__doc__` string (this text) is used by Evennia to
    create the automatic help entry for the command, so make sure to document
    consistently here.

    Each Command implements the following methods, called
    in this order (only func() is actually required):
        - at_pre_cmd(): If this returns anything truthy, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_cmd(): Extra actions, often things done after
            every command, like prompts.

    """

    def at_pre_cmd(self):
        """
        Called before any command is run. Used to output the entered string.
        """
        caller = self.caller
        caller.msg(f"\n|C==>|n {self.raw_string.rstrip()}")

    def at_post_cmd(self):
        "called after self.func()"
        caller = self.caller
        session = self.session
        try:
            if session.puppet is not None:
                caller = session.puppet
        except AttributeError:
            pass
        if hasattr(caller, "account"):
            account = caller.account
        else:
            account = caller
        if hasattr(caller, 'location'):
            loc = f" |C[{caller.location.key}]|n"
        else:
            loc = ""
        try:
            if account.db.unread_mail is not None:
                if account.db.unread_mail > 0:
                    mail = f" |G'Unread Mail ({account.db.unread_mail})'|n"
                else:
                    mail = ""
            else:
                mail = ""
        except AttributeError:
            mail = ""
        if caller != account and caller.db.away:
            prompt = f"|y|| |Y[{caller.get_display_name(caller)}]|n |R(away)|n{loc}{mail} |y|||n"
        elif caller == account:
            prompt = f"|y|| |Y[{caller.get_display_name(caller)}]|n{mail} |y|||n"
        else:
            prompt = f"|y|| |Y[{caller.get_display_name(caller)}]|n{loc}{mail} |y|||n"
        try:
            caller.msg(prompt=prompt)
        except TypeError:
            pass

class Command(BaseCommand):
    """
    Inherit from this if you want to create your own command styles from
    scratch. Note that Evennia's default commands inherits from MuxCommand
    instead.

    Overloaded 'at_post_command()' to send a prompt after each command.

    Note that the class's `__doc__` string (this text) is used by Evennia to
    create the automatic help entry for the command, so make sure to document
    consistently here.

    Each Command implements the following methods, called
    in this order (only func() is actually required):
        - at_pre_cmd(): If this returns anything truthy, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_cmd(): Extra actions, often things done after
            every command, like prompts.

    """

    def at_pre_cmd(self):
        """
        Called before any command is run. Used to output the entered string.
        """
        caller = self.caller
        caller.msg(f"|C==>|n {self.raw_string.rstrip()}")

    def at_post_cmd(self):
        "called after self.func()"
        caller = self.caller
        session = self.session
        try:
            if session.puppet is not None:
                caller = session.puppet
        except AttributeError:
            pass
        if hasattr(caller, "account"):
            account = caller.account
        else:
            account = caller
        if hasattr(caller, 'location'):
            loc = f" |C[{caller.location.key}]|n"
        else:
            loc = ""
        try:
            if account.db.unread_mail is not None:
                if account.db.unread_mail > 0:
                    mail = f" |G'Unread Mail ({account.db.unread_mail})'|n"
                else:
                    mail = ""
            else:
                mail = ""
        except AttributeError:
            mail = ""
        if caller != account and caller.db.away:
            prompt = f"|y|| |Y[{caller.get_display_name(caller)}]|n |R(away)|n{loc}{mail} |y|||n"
        elif caller == account:
            prompt = f"|y|| |Y[{caller.get_display_name(caller)}]|n{mail} |y|||n"
        else:
            prompt = f"|y|| |Y[{caller.get_display_name(caller)}]|n{loc}{mail} |y|||n"
        try:
            self.msg(prompt=prompt)
        except TypeError:
            pass
