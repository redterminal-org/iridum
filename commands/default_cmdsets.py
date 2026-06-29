""" to look more consistent in the environment
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`,
if you want to add Commands to Objects or Rooms.
"""


from evennia import default_cmds
from evennia.commands.default import general, building, unloggedin, help

from evennia.contrib.rpg import dice
from commands import cmd_give, cmd_look, cmd_get_drop, cmd_away, cmd_inventory
from commands import cmd_time, cmd_unconnected_help, cmd_paging, cmd_help
from commands import builder_cmds, cmd_help_paging, cmd_unconnected_create


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        
        # change help command to recognize "disable_help_pageing"
        self.remove(help.CmdHelp())
        self.add(cmd_help.CmdHelp())
        self.add(cmd_help_paging.CmdHelpPaging())

        # New look command to use evmore.msg
        self.remove(general.CmdLook())
        self.add(cmd_look.CmdLook())

        # New give command to use received()
        self.remove(general.CmdGive())
        self.add(cmd_give.CmdGive())
        #
        # New get and drop commands for getting from and dropping into
        # containers
        self.remove(general.CmdGet())
        self.remove(general.CmdDrop())
        self.add(cmd_get_drop.CmdGet())
        self.add(cmd_get_drop.CmdDrop())

        # New inventory command to look more consistent in the environment
        self.remove(general.CmdInventory())
        self.add(cmd_inventory.CmdInventory())

        # add custom time command
        self.add(cmd_time.CmdTime())
        # add dice command
        self.add(dice.CmdDice())
        # add "away" command
        self.add(cmd_away.CmdAway())
        # add "paging" command
        self.add(cmd_paging.CmdPaging())

        # add new builder_cmds
        builder_cmds.add_builder_cmds(self)


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()

        # New help command
        self.remove(unloggedin.CmdUnconnectedHelp())
        self.add(cmd_unconnected_help.CmdUnconnectedHelp())
        # New create command
        self.remove(unloggedin.CmdUnconnectedCreate())
        self.add(cmd_unconnected_create.CmdUnconnectedCreate())


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #

