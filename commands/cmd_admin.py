"""

Admin commands

"""

import re
import time
import subprocess
from os.path import isfile

from django.conf import settings

import evennia
from evennia.server.models import ServerConfig
from evennia.utils import class_from_module, evtable, logger, search
from server.block_wiki_user import block_wiki_user, unblock_wiki_user

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)

PERMISSION_HIERARCHY = [p.lower() for p in settings.PERMISSION_HIERARCHY]

_FILE_PHP_RUN = "/var/www/html/maintenance/run.php"

# regex matching IP addresses with wildcards, eg. 233.122.4.*
IPREGEX = re.compile(r"[0-9*]{1,3}\.[0-9*]{1,3}\.[0-9*]{1,3}\.[0-9*]{1,3}")


def list_bans(cmd, banlist):
    """
    Helper function to display a list of active bans. Input argument
    is the banlist read into the two commands ban and unban below.

    Args:
        cmd (Command): Instance of the Ban command.
        banlist (list): List of bans to list.
    """
    if not banlist:
        return "No active bans were found."

    table = cmd.styled_table("|wid", "|wname/ip", "|wdate", "|wreason")
    for inum, ban in enumerate(banlist):
        table.add_row(str(inum + 1), ban[0] and ban[0] or ban[1], ban[3], ban[4])
    return f"|wActive bans:|n\n{table}"


class CmdBan(COMMAND_DEFAULT_CLASS):
    """
    ban an account from the server

    Usage:
      ban [<name or ip> [: reason]]

    Without any arguments, shows numbered list of active bans.

    This command bans a user from accessing the game. Supply an optional
    reason to be able to later remember why the ban was put in place.

    It is often preferable to ban an account from the server than to
    delete an account with accounts/delete. If banned by name, that account
    account can no longer be logged into.

    IP (Internet Protocol) address banning allows blocking all access
    from a specific address or subnet. Use an asterisk (*) as a
    wildcard.

    Banning an account also blocks write access to the Wiki for the duration of
    the ban.

    Examples:
      ban thomas             - ban account 'thomas'
      ban/ip 134.233.2.111   - ban specific ip address
      ban/ip 134.233.2.*     - ban all in a subnet
      ban/ip 134.233.*.*     - even wider ban

    A single IP filter can be easy to circumvent by changing computers
    or requesting a new IP address. Setting a wide IP block filter with
    wildcards might be tempting, but remember that it may also
    accidentally block innocent users connecting from the same country
    or region.

    """

    key = "ban"
    aliases = ["bans"]
    locks = "cmd:perm(ban) or perm(Developer)"
    help_category = "Admin"

    def func(self):
        """
        Bans are stored in a serverconf db object as a list of
        dictionaries:
          [ (name, ip, ipregex, date, reason),
            (name, ip, ipregex, date, reason),...  ]
        where name and ip are set by the user and are shown in
        lists. ipregex is a converted form of ip where the * is
        replaced by an appropriate regex pattern for fast
        matching. date is the time stamp the ban was instigated and
        'reason' is any optional info given to the command. Unset
        values in each tuple is set to the empty string.
        """
        banlist = ServerConfig.objects.conf("server_bans")
        if not banlist:
            banlist = []

        if not self.args or (
            self.switches and not any(switch in ("ip", "name") for switch in self.switches)
        ):
            self.msg(list_bans(self, banlist))
            return

        now = time.ctime()
        reason = ""
        if ":" in self.args:
            ban, reason = self.args.rsplit(":", 1)
        else:
            ban = self.args
        ban = ban.lower()
        ipban = IPREGEX.findall(ban)
        if not ipban:
            # store as name
            typ = "Name"
            bantup = (ban, "", "", now, reason)
        else:
            # an ip address.
            typ = "IP"
            ban = ipban[0]
            # replace * with regex form and compile it
            ipregex = ban.replace(".", r"\.")
            ipregex = ipregex.replace("*", "[0-9]{1,3}")
            ipregex = re.compile(r"%s" % ipregex)
            bantup = ("", ban, ipregex, now, reason)

        ret = yield (f"Are you sure you want to {typ}-ban '|w{ban}|n' [Y]/N?")
        if str(ret).lower() in ("no", "n"):
            self.msg("Aborted.")
            return

        # save updated banlist
        banlist.append(bantup)
        ServerConfig.objects.conf("server_bans", banlist)
        self.msg(f"{typ}-ban '|w{ban}|n' was added. Use |wunban|n to reinstate.")
        if typ == "Name" and len(evennia.search_account(bantup[0])) > 0:
            if block_wiki_user(bantup[0]):
                self.caller.msg(
                    f"[WIKIBAN] Banning '{bantup[0]}' SUCCESSFUL!"
                )
            else:
                self.caller.msg(
                    f"[WIKIBAN] Banning '{bantup[0]}' FAILED!"
                )
        logger.log_sec(
            f"Banned {typ}: {ban.strip()} (Caller: {self.caller}, IP: {self.session.address})."
        )


class CmdUnban(COMMAND_DEFAULT_CLASS):
    """
    remove a ban from an account

    Usage:
      unban <banid>

    This will clear an account name/ip ban previously set with the ban
    command.  Use this command without an argument to view a numbered
    list of bans. Use the numbers in this list to select which one to
    unban.

    If an account is ubanned, it also regains write access to the Wiki.

    """

    key = "unban"
    locks = "cmd:perm(unban) or perm(Developer)"
    help_category = "Admin"

    def func(self):
        """Implement unbanning"""

        banlist = ServerConfig.objects.conf("server_bans")

        if not self.args:
            self.msg(list_bans(self, banlist))
            return

        try:
            num = int(self.args)
        except Exception:
            self.msg("You must supply a valid ban id to clear.")
            return

        if not banlist:
            self.msg("There are no bans to clear.")
        elif not (0 < num < len(banlist) + 1):
            self.msg(f"Ban id |w{self.args}|n was not found.")
        else:
            # all is ok, ask, then clear ban
            ban = banlist[num - 1]
            value = (" ".join([s for s in ban[:2]])).strip()

            ret = yield (f"Are you sure you want to unban {num}: '|w{value}|n' [Y]/N?")
            if str(ret).lower() in ("n", "no"):
                self.msg("Aborted.")
                return

            del banlist[num - 1]
            ServerConfig.objects.conf("server_bans", banlist)
            if len(evennia.search_account(ban[0])) > 0:
                if unblock_wiki_user(ban[0]):
                    self.caller.msg(
                        f"[WIKIUNBAN] Unbanning '{ban[0]}' SUCCESSFUL!"
                    )
                else:
                    self.caller.msg(
                        f"[WIKIUNBAN] Unbanning '{ban[0]}' FAILED!"
                    )
            self.msg(f"Cleared ban {num}: '{value}'")
            logger.log_sec(
                f"Unbanned: {value.strip()} (Caller: {self.caller}, IP: {self.session.address})."
            )


class CmdNewPassword(COMMAND_DEFAULT_CLASS):
    """
    change the password of an account

    Usage:
      userpassword <user obj> = <new password>

    Set an account's password ingame and for the Wiki.
    """

    key = "userpassword"
    locks = "cmd:perm(newpassword) or perm(Admin)"
    help_category = "Admin"

    def func(self):
        """Implement the function."""

        caller = self.caller

        if not self.rhs:
            self.msg("Usage: userpassword <user obj> = <new password>")
            return

        # the account search also matches 'me' etc.
        account = caller.search_account(self.lhs)
        if not account:
            return

        newpass = self.rhs

        # Validate password
        validated, error = account.validate_password(newpass)
        if not validated:
            errors = [e for suberror in error.messages for e in error.messages]
            string = "\n".join(errors)
            caller.msg(string)
            return

        account.set_password(newpass)
        account.save()
        if isfile(_FILE_PHP_RUN):
            wiki_result = subprocess.run(
            ["sudo", "/usr/bin/php", _FILE_PHP_RUN,
            "createAndPromote", account.name, newpass, "--force"],
            capture_output=True)
            if wiki_result.returncode != 0:
                self.msg("MediaWiki: ")
                self.msg(wiki_result.stderr)
                self.msg(wiki_result.stdout)
                return
        self.msg(f"{account.name} - new password set to '{newpass}'.")
        if account.character != caller:
            account.msg(f"{caller.name} has changed your password to '{newpass}'.")
        logger.log_sec(
            f"Password Changed: {account} (Caller: {caller}, IP: {self.session.address})."
        )
