import re
import subprocess

from django.conf import settings

import evennia

from evennia.utils import class_from_module, utils

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

CONNECTION_SCREEN_MODULE = settings.CONNECTION_SCREEN_MODULE

class CmdUnconnectedCreate(COMMAND_DEFAULT_CLASS):
    """
    create a new account account

    Usage (at login screen):
      create <accountname> <password>
      create "account name" "pass word"

    This creates a new account <accountname>. It also creates a new user account
    on the Wiki at https://iridum.redterminal.org/ with the same credentials, so
    you can log in to it with your <accountname> and <password>.

    The <password> has to be at least 8 characters long.

    If you have spaces in your name, enclose it in double quotes.
    """

    key = "create"
    aliases = ["cre", "cr"]
    locks = "cmd:all()"
    arg_regex = r"\s.*?|$"

    def at_pre_cmd(self):
        """Verify that account creation is enabled."""
        if not settings.NEW_ACCOUNT_REGISTRATION_ENABLED:
            # truthy return cancels the command
            self.msg("Registration is currently disabled.")
            return True

        return super().at_pre_cmd()

    def func(self):
        """Do checks and create account"""

        session = self.caller
        args = self.args.strip()

        address = session.address

        # Get account class
        Account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)

        # extract double quoted parts
        parts = [part.strip() for part in re.split(r"\"", args) if part.strip()]
        if len(parts) == 1:
            # this was (hopefully) due to no quotes being found
            parts = parts[0].split(None, 1)
        if len(parts) != 2:
            string = (
                "\n Usage (without <>): create <name> <password>"
                "\nIf <name> or <password> contains spaces, enclose it in double quotes."
            )
            session.msg(string)
            return

        username, password = parts

        # pre-normalize username so the user know what they get
        non_normalized_username = username
        username = Account.normalize_username(username)
        if non_normalized_username != username:
            session.msg(
                "Note: your username was normalized to strip spaces and remove characters "
                "that could be visually confusing."
            )

        # have the user verify their new account was what they intended
        answer = yield (
            f"You want to create an account '{username}' with password '{password}'."
            "\nIs this what you intended? [Y]/N?"
        )
        if answer.lower() in ("n", "no"):
            session.msg("Aborted. If your user name contains spaces, surround it by quotes.")
            return

        # everything's ok. Create the new player account. If not already exists.
        a = evennia.search_account(username)
        if len(a) > 0:
            string = "Account already exists! Choose a different <username>"
            session.msg(string)
            return
        wiki_result = subprocess.run(
        ["sudo", "/usr/bin/php", "/var/www/html/maintenance/createAndPromote.php",
            username, password], capture_output=True)
        if wiki_result.returncode != 0:
            session.msg("MediaWiki: ")
            session.msg(wiki_result.stderr)
            session.msg(wiki_result.stdout)
            return
        account, errors = Account.create(
            username=username, password=password, ip=address, session=session
        )
        if account:
            # tell the caller everything went well.
            string = "A new account '%s' was created. Welcome!"
            if " " in username:
                string += (
                    "\n\nYou can now log in with the command 'connect \"%s\" <your password>'."
                )
            else:
                string += "\n\nYou can now log with the command 'connect %s <your password>'."
            if wiki_result.returncode == 0:
                string += "\nYou can now also login with your new credentials to the Wiki at:\n"
                string +="|mhttps://iridum.redterminal.org|n\n"
            else:
                string += "\n\nThere was an error creating your Wiki account. Please call one of the admins."
            session.msg(string % (username, username))
        else:
            session.msg("|R%s|n" % "\n".join(errors))
