"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

from evennia import settings

from evennia.accounts.accounts import DefaultAccount, DefaultGuest
from evennia.utils.utils import is_iter

from world.scripts.mailscript import MailScript

class Account(DefaultAccount):
    """
    An Account is the actual OOC player entity. It doesn't exist in the game,
    but puppets characters.

    This is the base Typeclass for all Accounts. Accounts represent
    the person playing the game and tracks account info, password
    etc. They are OOC entities without presence in-game. An Account
    can connect to a Character Object in order to "enter" the
    game.

    Account Typeclass API:

    * Available properties (only available on initiated typeclass objects)

     - key (string) - name of account
     - name (string)- wrapper for user.username
     - aliases (list of strings) - aliases to the object. Will be saved to
            database as AliasDB entries but returned as strings.
     - dbref (int, read-only) - unique #id-number. Also "id" can be used.
     - date_created (string) - time stamp of object creation
     - permissions (list of strings) - list of permission strings
     - user (User, read-only) - django User authorization object
     - obj (Object) - game object controlled by account. 'character' can also
                     be used.
     - is_superuser (bool, read-only) - if the connected user is a superuser

    * Handlers

     - locks - lock-handler: use locks.add() to add new lock strings
     - db - attribute-handler: store/retrieve database attributes on this
                              self.db.myattr=val, val=self.db.myattr
     - ndb - non-persistent attribute handler: same as db but does not
                                  create a database entry when storing data
     - scripts - script-handler. Add new scripts to object with scripts.add()
     - cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     - nicks - nick-handler. New nicks with nicks.add().
     - sessions - session-handler. Use session.get() to see all sessions connected, if any
     - options - option-handler. Defaults are taken from settings.OPTIONS_ACCOUNT_DEFAULT
     - characters - handler for listing the account's playable characters

    * Helper methods (check autodocs for full updated listing)

     - msg(text=None, from_obj=None, session=None, options=None, **kwargs)
     - execute_cmd(raw_string)
     - search(searchdata, return_puppet=False, search_object=False, typeclass=None,
                      nofound_string=None, multimatch_string=None, use_nicks=True,
                      quiet=False, **kwargs)
     - is_typeclass(typeclass, exact=False)
     - swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     - access(accessing_obj, access_type='read', default=False, no_superuser_bypass=False, **kwargs)
     - check_permstring(permstring)
     - get_cmdsets(caller, current, **kwargs)
     - get_cmdset_providers()
     - uses_screenreader(session=None)
     - get_display_name(looker, **kwargs)
     - get_extra_display_name_info(looker, **kwargs)
     - disconnect_session_from_account()
     - puppet_object(session, obj)
     - unpuppet_object(session)
     - unpuppet_all()
     - get_puppet(session)
     - get_all_puppets()
     - is_banned(**kwargs)
     - get_username_validators(validator_config=settings.AUTH_USERNAME_VALIDATORS)
     - authenticate(username, password, ip="", **kwargs)
     - normalize_username(username)
     - validate_username(username)
     - validate_password(password, account=None)
     - set_password(password, **kwargs)
     - get_character_slots()
     - get_available_character_slots()
     - create_character(*args, **kwargs)
     - create(*args, **kwargs)
     - delete(*args, **kwargs)
     - channel_msg(message, channel, senders=None, **kwargs)
     - idle_time()
     - connection_time()

    * Hook methods

     basetype_setup()
     at_account_creation()

     > note that the following hooks are also found on Objects and are
       usually handled on the character level:

     - at_init()
     - at_first_save()
     - at_access()
     - at_cmdset_get(**kwargs)
     - at_password_change(**kwargs)
     - at_first_login()
     - at_pre_login()
     - at_post_login(session=None)
     - at_failed_login(session, **kwargs)
     - at_disconnect(reason=None, **kwargs)
     - at_post_disconnect(**kwargs)
     - at_message_receive()
     - at_message_send()
     - at_server_reload()
     - at_server_shutdown()
     - at_look(target=None, session=None, **kwargs)
     - at_post_create_character(character, **kwargs)
     - at_post_add_character(char)
     - at_post_remove_character(char)
     - at_pre_channel_msg(message, channel, senders=None, **kwargs)
     - at_post_chnnel_msg(message, channel, senders=None, **kwargs)

    """

    ooc_appearance_template = """|B====================================================================|n
{header}

{sessions}

    |clook|n - show this message
    |cpublic <text>|n - talk on public channel
    |ccharcreate <name> [=description]|n - create new character
    |cchardelete <name>|n - delete a character
    |cic <name>|n - enter the game as character (|cooc|n to get back here)
    |cic|n - enter the game as latest character controlled
    |cmail|n - Use |chelp mail|n to get information how to write to
           "fab" (admin) if you have any problems.
    |chelp|n - more commands

{characters}
{footer}
|B====================================================================|n"""

    def at_account_creation(self):
        """
        Run when a new account is created (e.g. from the login screen).
        """
        # run inheritated functions
        super().at_account_creation()

        # Set the noidletimeout to perm(Beginner Builder)
        # which was peviously perm(Builder) ('Builder' doesn't
        # exist anymore)
        self.locks.add(
            "noidletimeout:perm(noidletimeout) or perm(Beginner Builder);")

        # set some attributes
        self.default_character_typeclass = "world.typeclasses.characters.Character"

        # Add MailScript and MailCmdSet and set 'Unread' mail counter to 0
        self.scripts.add(MailScript, key='MailScript')
        self.db.unread_mail = 0

    # Overloaded delete function to delete scripts
    def delete(self, **kwargs):
        for script in self.scripts.all():
            script.delete()
        super().delete()

    def get_display_name(self, looker, **kwargs):
        return f"{self.key}"

    def at_look(self, target=None, session=None, **kwargs):
        """
        Called when this object executes a look. It allows to customize
        just what this means.

        Args:
            target (Object or list, optional): An object or a list
                objects to inspect. This is normally a list of characters.
            session (Session, optional): The session doing this look.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Returns:
            look_string (str): A prepared look string, ready to send
                off to any recipient (usually to ourselves)
        """

        if target and not is_iter(target):
            # single target - just show it
            if hasattr(target, "return_appearance"):
                return target.return_appearance(self)
            else:
                return f"{target} has no in-game appearance."

        # multiple targets - this is a list of characters
        characters = list(tar for tar in target if tar) if target else []
        ncars = len(characters)
        sessions = self.sessions.all()
        nsess = len(sessions)

        if not nsess:
            # no sessions, nothing to report
            return ""

        # header text
        txt_header = f"Account |g{self.name}|n (you are Out-of-Character)"

        # sessions
        sess_strings = []
        for isess, sess in enumerate(sessions):
            ip_addr = (
                sess.address[0] if isinstance(
                    sess.address, tuple) else sess.address
            )
            addr = f"{sess.protocol_key} ({ip_addr})"
            sess_str = (
                f"|w* {isess + 1}|n"
                if session and session.sessid == sess.sessid
                else f"  {isess + 1}"
            )

            sess_strings.append(f"{sess_str} {addr}")

        txt_sessions = "|wConnected session(s):|n\n" + "\n".join(sess_strings)

        if not characters:
            txt_characters = "You don't have a character yet.|/Use |ccharcreate|n to create a character."
        else:
            max_chars = (
                "unlimited"
                if self.is_superuser or settings.MAX_NR_CHARACTERS is None
                else settings.MAX_NR_CHARACTERS
            )

            char_strings = []
            for char in characters:
                csessions = char.sessions.all()
                if csessions:
                    for sess in csessions:
                        # character is already puppeted
                        sid = sess in sessions and sessions.index(sess) + 1
                        if sess and sid:
                            char_strings.append(
                                f" - |B{char.name}|n [{
                                    ', '.join(char.permissions.all())
                                }] "
                                f"(played by you in session {sid})"
                            )
                        else:
                            char_strings.append(
                                f" - |R{char.name}|n [{
                                    ', '.join(char.permissions.all())
                                }] "
                                "(played by someone else)"
                            )
                else:
                    # character is "free to puppet"
                    char_strings.append(
                        f" - |G{char.name}|n [{
                            ', '.join(char.permissions.all())}]"
                    )

            txt_characters = (
                f"Available character(s) ({ncars}/{
                    max_chars
                }, |cic <name>|n to play):|n\n"
                + "\n".join(char_strings)
            )
        return self.ooc_appearance_template.format(
            header=txt_header,
            sessions=txt_sessions,
            characters=txt_characters,
            footer="",
        )

    def at_post_login(self, session=None, **kwargs):
        """
        Called at the end of the login process, just before letting
        the account loose.

        Args:
            session (Session, optional): Session logging in, if any.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:
            This is called *before* an eventual Character's
            `at_post_login` hook. By default it is used to set up
            auto-puppeting based on `MULTISESSION_MODE`

        """
        # if we have saved protocol flags on ourselves, load them here.
        protocol_flags = self.attributes.get("_saved_protocol_flags", {})
        if session and protocol_flags:
            session.update_flags(**protocol_flags)

        # inform the client that we logged in through an OOB message
        if session:
            session.msg(logged_in={})

        self._send_to_connect_channel(
            ("|G{key} connected|n").format(key=self.key))
        if settings.AUTO_PUPPET_ON_LOGIN:
            # in this mode we try to auto-connect to our last connected object, if any
            try:
                self.puppet_object(session, self.db._last_puppet)
            except RuntimeError:
                self.msg(
                    "\nThe Character does not exist. Entering OOC"
                    " (Out-Of-Character) mode."
                )
                self.msg(
                    self.at_look(target=self.characters, session=session),
                    session=session,
                )
                return
        else:
            # In this mode we don't auto-connect but by default end up at a character selection
            # screen. We execute look on the account.
            self.msg(
                self.at_look(target=self.characters, session=session), session=session
            )


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    """

    pass
