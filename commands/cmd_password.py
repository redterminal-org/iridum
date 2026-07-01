"""
Account (OOC) commands. These are stored on the Account object
and self.caller is thus always an Account, not an Object/Character.

These commands go in the AccountCmdset and are accessible also
when puppeting a Character (although with lower priority)

These commands use the account_caller property which tells the command
parent (MuxCommand, usually) to setup caller correctly. They use
self.account to make sure to always use the account object rather than
self.caller (which change depending on the level you are calling from)
The property self.character can be used to access the character when
these commands are triggered with a connected character (such as the
case of the `ooc` command), it is None if we are OOC.

Note that under MULTISESSION_MODE > 2, Account commands should use
self.msg() and similar methods to reroute returns to the correct
method. Otherwise all text will be returned to all connected sessions.

"""
import subprocess
from os.path import isfile
from django.conf import settings

from evennia.utils import logger, utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)
_FILE_PHP_RUN = "/var/www/html/maintenance/run.php"

class CmdPassword(COMMAND_DEFAULT_CLASS):
    """
    change your password

    Usage:
      password <old password> = <new password>

    Changes your password. Make sure to pick a safe one. This also sets the
    password for the Wiki account of the same name.
    """

    key = "password"
    locks = "cmd:pperm(Player)"

    # this is used by the parent
    account_caller = True

    def func(self):
        """hook function."""

        account = self.account
        if not self.rhs:
            self.msg("Usage: password <oldpass> = <newpass>")
            return
        oldpass = self.lhslist[0]  # Both of these are
        newpass = self.rhslist[0]  # already stripped by parse()

        # Validate password
        validated, error = account.validate_password(newpass)

        if not account.check_password(oldpass):
            self.msg("The specified old password isn't correct.")
        elif not validated:
            errors = [e for suberror in error.messages for e in error.messages]
            string = "\n".join(errors)
            self.msg(string)
        else:
            if isfile(_FILE_PHP_RUN):
                wiki_result = subprocess.run(
                ["sudo", "/usr/bin/php", _FILE_PHP_RUN,
                "createAndPromote", self.account.name, newpass, "--force"],
                capture_output=True)
                if wiki_result.returncode != 0:
                    self.msg("MediaWiki: ")
                    self.msg(wiki_result.stderr)
                    self.msg(wiki_result.stdout)
                    return
            account.set_password(newpass)
            account.save()
            self.msg("Account and Wiki Password changed.")
            logger.log_sec(
                f"Password Changed: {account} (Caller: {account}, IP: {self.session.address})."
                )
