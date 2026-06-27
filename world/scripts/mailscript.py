"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

import evennia
from evennia import settings, create_object, CmdSet
from evennia import EvEditor
from evennia.accounts.accounts import DefaultAccount
from evennia.utils.utils import interactive, dbref, inherits_from
from evennia.utils.dbserialize import ObjectDoesNotExist

from world.typeclasses.objects import Object
from world.typeclasses.scripts import Script
from world.utils.gametime import custom_gametime
from world.utils import evmore

from commands.command import MuxCommand

from world.utils.utils import wrap, wrap_para

_WIDTH = settings.DEFAULT_WIDTH

### Find Script on Account ###
def find_mailscripts(account):
    """
    This function finds the mailscripts on an Account. Should only be one,
    but it returns a list anyways.
    """
    scripts = []
    for script in evennia.search_script("MailScript",
                                        typeclass=MailScript):
        if script.account == account:
            scripts.append(script)
    return scripts


#### Mail typeclass ####
class Mail(Object):
    """
    A Mail Object. Used to be exchanged between users.

    DON'T CREATE AN OBJECT FROM THIS TYPECLASS BY YOURSELF!!! It's only usd by
    the MailScript.
    """

    class_perm = {"create": "Developer"}

    def at_object_creation(self):
        "This is called only when the object is first created"
        super().at_object_creation()

        # set some locks
        self.locks.add("control:perm(Developer);")
        self.locks.add("attrcreate:perm(Developer);")
        self.locks.add("get:false();delete:perm(Admin);edit:perm(Developer);")
        self.locks.add("iscontainer:false();getfrom:false();getcontainer:false();")
        self.locks.add("examine:perm(Developer);")
        self.locks.add("teleport:false();teleport_here:false();view:false();")
        self.locks.add("puppet:false();traverse:false();")

    def return_appearance(self):
        return self.set_appearance(things="")

    def __lt__(self, other):
        return self.db.date < other.db.date

    def __gt__(self, other):
        return self.db.date > other.db.date


#### Thread typeclass ####
class Thread(Object):
    """
    A Thread Object. Used to be exchanged between users.

    DON'T CREATE AN OBJECT FROM THIS TYPECLASS BY YOURSELF!!! It's only usd by
    the MailScript.
    """

    class_perm = {"create": "Developer"}

    def at_object_creation(self):
        "This is called only when the object is first created"
        super().at_object_creation()

        # set some locks
        self.locks.add("control:perm(Developer);")
        self.locks.add("attrcreate:perm(Developer);")
        self.locks.add("get:false();delete:perm(Admin);edit:perm(Developer);")
        self.locks.add("iscontainer:false();getfrom:false();getcontainer:false();")
        self.locks.add("examine:perm(Developer);")
        self.locks.add("teleport:false();teleport_here:false();view:false();")
        self.locks.add("puppet:false();traverse:false();")

        self.db.mails = []

    def at_object_delete(self, **kwargs):
        if self.db.mails and self.db.mails is not None:
            for mail in self.db.mails:
                try:
                    if mail is not None:
                        mail.delete()
                except ObjectDoesNotExist:
                    pass
        return True

    def return_appearance(self):
        return self.set_appearance(things="")

    def __lt__(self, other):
        return self.db.last_updated < other.db.last_updated

    def __gt__(self, other):
        return self.db.last_updated > other.db.last_updated


class MailScript(Script):
    """
    This Script gives accesss to the mail system and is added to every newly
    created Account. It also gives the Account the 'mail' command that
    provides all the functionality.

    The documentation is available with 'help mail'.

    DON'T CREATE A SCRIPT FROM THIS TYPECLASS BY YOURSELF!!! It's only usd by
    the Mail System and automatically added .
    """

    class_perm = {"create": "Developer", "global_script": "Developer"}

    def at_script_creation(self):
        # run inheritated function:
        super().at_script_creation()
        # check if already a MailScript is present
        if len(find_mailscripts(self.account)) > 1:
            # If an Object already has a Mailscript
            # we delete ourselves
            self.account.msg(wrap("|RError:|n 'MailScript' already present!"))
            self.delete()

        # Add 'unread' (int) and a threads (list) attribute
        self.db.unread = 0
        self.db.threads = []

        # Add MailCmdSet Command Set
        self.account.cmdset.add(MailCmdSet, persistent=True)


    def at_script_delete(self):
        # Delete all mails from Database
        if self.db.threads is not None:
            for thread in self.db.threads:
                if thread is not None:
                    thread.delete()

        # Remove MailCmdSet
        self.account.cmdset.remove(MailCmdSet)
        return True

    ## SEND Mail ##
    def send_mail(self, mail):
        # copy mail
        receiver_account = evennia.search_account(mail.db.receiver).first()
        if not inherits_from(receiver_account, DefaultAccount):
            self.obj.msg(
                wrap(
                    f"|RError:|n Account |Y{mail.db.receiver}|n not found!"
                    f" Mail |Rnot|n sent!"
                )
            )
            mail.db.failed = True
            mail.db.postponed = False
            mail.db.unread = False
            return False
        mail_to_send = create_object(
            typeclass=Mail,
            key="mail",
            location=None,
            attributes=[
                ("receiver", mail.db.receiver),
                ("sender", mail.db.sender),
                ("sender_id", mail.db.sender_id),
                ("subject", mail.db.subject),
                ("message", mail.db.message),
                ("date", mail.db.date),
                ("postponed", False),
                ("archived", False),
                ("unread", True),
                ("failed", False),
            ],
        )
        # Find receiver Script
        try:
            receiver_mailscript = find_mailscripts(receiver_account)[0]
        except IndexError:
            self.obj.msg(
                wrap(f"|RError:|n Account |Y'{mail.db.receiver}'| can't receive Mail.")
            )
            mail.db.failed = True
            mail.db.postponed = False
            mail.db.unread = False
            return False

        # send mail to receiver
        ok = receiver_mailscript.receive_mail(mail_to_send)
        # Check if send was successful
        if not ok:
            mail.db.failed = True
            self.obj.msg(wrap("|RError:|n sending failed! Maybe wrong receiver."))
            mail.db.postponed = False
            mail.db.unread = False
            return False
        mail.db.postponed = False
        mail.db.unread = False
        return True

    ## RECEIVE Mail ##
    def receive_mail(self, mail):
        # Initialization
        if not self.db.threads or self.db.threads is None:
            self.db.threads = []
        self.db.mail = mail
        # check if it's really for us or return False
        if self.db.mail.db.receiver != self.obj.key:
            return False

        # Check threads
        self.db.thread = None
        self.db.mail.db.received = True
        thread_name = f"{mail.db.sender}: '{mail.db.subject.strip()}'"
        for thread in self.db.threads:
            if thread.db.name == thread_name:
                thread.db.unread = True
                thread.db.archived = False
                self.db.thread = thread
        if not self.db.thread or self.db.thread is None:
            # New thread
            self.db.thread = create_object(
                typeclass=Thread,
                key="thread",
                location=None,
                attributes=[
                    ("name", thread_name),
                    ("with_account", mail.db.sender),
                    ("subject", mail.db.subject.strip()),
                    ("last_updated", mail.db.date),
                    ("mails", []),
                    ("unread", True),
                    ("archived", False),
                ],
            )
            # Append thread to script
            self.db.threads.append(self.db.thread)

        # prepare Mail
        self.db.mail.db.thread_name = self.db.thread.db.name
        self.db.mail.db.postponed = False
        self.db.mail.db.archived = False
        self.db.mail.db.unread = True
        self.db.mail.db.failed = False
        self.db.mail.db.received = True
        # Update Thread date and append Mail to thread
        self.db.thread.db.last_updated = mail.db.date
        self.db.thread.db.mails.append(self.db.mail)

        # Inform Script owner of receipt
        self.obj.msg(
            wrap(f"|YNEW MAIL:|n You received a new mail from |G'{mail.db.sender}'|n!")
        )

        # Update 'unread' attribute on script and Character
        self.db.unread += 1
        self.obj.db.unread_mail += 1
        # return True for no errors
        return True


#### Muxcommand: 'mail' ####
class CmdMail(MuxCommand):
    """
    The mail system command. Mails are put together to threads, which are
    named after the subject of the first mail and identified by a unique
    number. So the /send switch with a receiver and a subject is only used for
    the first mail in a thread. All replies to any mail in a thread is added at
    the end of the thread sorted by ingame time.

    The Mails are bound to an Account and not to individual Characters. So if
    you send a mail to a Character name, it is sent to the Account the
    Character belongs to. The <receiver> can be a Character name or Account
    name. The mail will always be delivered to the Account.

    *Note:* "#dbref" means "Database Reference" and identifies a specific item
    in the database. In this case a Mail or a Thread. Its a hash symbol with an
    integer, for example '#573'.

    Usage:
        mail[/switches] [arguments]

    Switches:
        send - sends a mail to another Account
        edit - edits the mail in the editor
        reply - replies to a mail/thread
        threads - shows threads
        unread - lists all threads with unread mails
        archived - lists all threads with archived mails
        postponed - lists all threads with postponed mails
        all - list all threads
        wm - "With Mails" shows threads with Mails
        delete - deletes a mail or a thread
        toggle_archived - toggles the 'archived' bit of a mail or a thread
        toggle_unread - toggles the 'unread' bit of a mail or thread

    Documentation:
        mail
            - will show all unread mails and also toggle their 'Unread' bit to
              false.
        mail <#dbref of mail or thread>
            - will show mail or thread with specified #dbref

        mail/send <receiver> = <subject>[;;<message>]
            - sends a mail to <receiver> with <subject>. When message is
              omitted, the editor will open, even if the /edit switch is not
              present. You will be prompted to '[P]ostpone/Send/Discard' the
              mail.
        mail/send/edit <receiver> = <subject>[;;content in editor]
            - will open editor to send a message even if a message was given as
              initial text. You'll be asked to '[P]ostpone/Send/Discard' the
              mail.
        mail/send[/edit] <#dbref>
            - send postponed message with #dbref number (eg. #752).
              You'll be asked again to '[P]ostpone/Send/Discard' the mail.

        mail/reply <#dbref of (postponed) mail or thread> [= <message>]
            - Replies to thread which #dbref. If you reply to a dbref of a
              mail, it will still appended to the end of the the thread
              this mail belongs to. If you use a dbref to a postponed mail,
              the message on the commandline will be ignored.
              If <message> is omitted, it will open the text editor to edit the
              message. You'll be asked to '[P]ostpone/Send/Discard' the mail.
        mail/reply/edit <#dbref of (postponed) mail or thread> [= <message>]
            - Replies to thread which #dbref. Opens the editor even if you give
              an initial message. If you reply to a dbref of a mail, it will
              still appended to the end of the the thread this mail belongs to.
              If you use a dbref to a postponed mail, the message on the
              commandline will be ignored.
              You'll be asked to '[P]ostpone/Send/Discard' the mail.

        *Note on threads:* If a mail is shown with the /wm switch, its 'Unread'
        Bit is always toggled to false, regardless which switch is used!
        mail/threads[/wm]
            - lists threads (without archived ones)
              when the /wm (With Mails) switch is given, mails are also
              shown.
        mail/all[/wm]
            - lists ALL threads (with archived ones).
              When the /wm (With Mails) switch is given, mails are also shown.
        mail/unread[/wm]
            - lists all threads with unread mails.
              When the /wm (With Mails) switch is given, the unread Mails are
              also shown.
        mail/archived[/wm]
            - lists all threads with archived mails.
              When the /wm (With Mails) switch is given, the archived mails are
              also shown.
        mail/postponed[/wm]
            - lists all threads with postponed mails.
              When the /wm (With Mails) switch is given, the postponed mails
              are also shown.

        mail/delete <#dbref of mail or thread>
            - will delete a single mail or a whole thread. BE CAREFUL! Even
              the Admins are not able to restore deleted mails or threads!

        mail/toggle_archived <#dbref of mail or thread> = <true||false>
            - Toggles the 'Archived' Bit of a whole thread or a single mail to
              "true" or "false".
        mail/toggle_unread <#dbref of message or thread> = <true||false>
            - Toggles the 'Unread' Bit of a whole thread or a single mail to
              "true" or "false"
    """

    key = "mail"
    switch_options = (
        "send",
        "edit",
        "reply",
        "threads",
        "delete",
        "toggle_archived",
        "toggle_unread",
        "postponed",
        "archived",
        "unread",
        "all",
        "wm",
    )
    locks = "cmd:perm(Player)"
    help_category = "Comms"

    confirm = True  # set to False to always bypass confirmation
    default_confirm = "yes"  # what to assume if just pressing enter (yes/no)

    #### toggle unread bit on Thread or Message with dbref ####
    def unread_switch(self):
        caller = self.caller
        no_use = set(
            [
                "send",
                "edit",
                "reply",
                "threads",
                "delete",
                "list",
                "postponed",
                "all",
                "toggle_archived",
                "archive",
                "unread",
                "wm",
            ]
        )
        switches = set(self.switches)
        if switches.intersection(no_use):
            err = (
                "|RConflicting switches:|n You can't use these switches"
                " together."
                "\n\nType |crhelp mail'|n for information to correct usage."
            )
            caller.msg(wrap_para(err))
            return

        # parse args
        try:
            self.lhs, self.rhs = self.args.split("=", 1)
        except ValueError:
            caller.msg(
                wrap_para(
                    f"|RError:|n Couldn't parse Arguments. Use"
                    f" |c'help mail'|n for help.\n\n"
                    f"Usage: |c'mail/toggle_unread <#dbref> = <true||false>|n"
                )
            )
            return
        # Check for dbref and rhs
        if not self.rhs.strip().lower() in ["true", "false"]:
            caller.msg(
                wrap_para(
                    f"|RError:|n Couldn't parse Arguments. Use"
                    f" |c'help mail'|n for help.\n\n"
                    f"Usage: |c'mail/toggle_unread <#dbref> = <true||false>|n"
                )
            )
            return
        ref = dbref(self.lhs.strip())
        if ref is not None:
            # We got a #dbref
            self.mail = evennia.search_object(
                self.lhs.strip(), use_dbref=True, candidates=self.mails, typeclass=Mail
            ).first()
            if self.mail:
                # We got a mail to toggle archive bit
                self.mail.db.unread = (
                    True if self.rhs.strip().lower() == "true" else False
                )
                for thread in self.threads:
                    thread.db.unread = False
                    if thread.db.name == self.mail.db.thread_name:
                        self.thread = thread
                    for mail in thread.db.mails:
                        if mail.db.unread is True:
                            thread.db.unread = True
                            break
                caller.msg(
                    wrap(
                        f"Message unread: |w{self.mail.db.unread}|n."
                        f" Thread unread: |w{self.thread.db.unread}|n."
                    )
                )
                return
            self.thread = evennia.search_object(
                self.lhs.strip(),
                use_dbref=True,
                candidates=self.threads,
                typeclass=Thread,
            ).first()
            if self.thread:
                self.thread.db.unread = (
                    True if self.rhs.strip().lower() == "true" else False
                )
                for mail in self.thread.db.mails:
                    mail.db.unread = (
                        True if self.rhs.strip().lower() == "true" else False
                    )

                caller.msg(wrap(f"Thread unread: |w{self.thread.db.unread}|n."))
                return
            caller.msg(
                wrap(
                    f"Neither Mail nor Thread found with dbref |w{self.lhs.strip()}|n."
                )
            )
            return
        caller.msg(
            wrap_para(
                f"|RError:|n Couldn't parse Arguments. Use"
                f" |c'help mail'|n for help.\n\n"
                f"Usage: |c'mail/toggle_unread <#dbref> = <true||false>|n"
            )
        )
        return

    #### toggle Archive bit on Thread or Message with dbref ####
    def archived_switch(self):
        caller = self.caller
        no_use = set(
            [
                "send",
                "edit",
                "reply",
                "threads",
                "delete",
                "list",
                "postponed",
                "all",
                "toggle_unread",
                "archive",
                "unread",
                "wm",
            ]
        )
        switches = set(self.switches)
        if switches.intersection(no_use):
            err = (
                "|RConflicting switches:|n You can't use these switches"
                " together."
                "\n\nType |c'help mail'|n for information to correct usage."
            )
            caller.msg(wrap_para(err))
            return

        # parse args
        try:
            self.lhs, self.rhs = self.args.split("=", 1)
        except ValueError:
            caller.msg(
                wrap_para(
                    f"|RError:|n Couldn't parse Arguments. Use"
                    f" |c'help mail'|n for help.\n\n"
                    f"Usage: |c'mail/toggle_unread <#dbref> = <true||false>|n"
                )
            )
            return
        # Check for dbref and rhs
        if not self.rhs.strip().lower() in ["true", "false"]:
            caller.msg(
                wrap_para(
                    f"|RError:|n Couldn't parse Arguments. Use"
                    f" |c'help mail'|n for help.\n\n"
                    f"Usage: |c'mail/toggle_unread <#dbref> = <true||false>|n"
                )
            )
            return
        ref = dbref(self.lhs.strip())
        if ref is not None:
            # We got a #dbref
            self.mail = evennia.search_object(
                self.lhs.strip(), use_dbref=True, candidates=self.mails, typeclass=Mail
            ).first()
            if self.mail:
                # We got a mail to toggle archive bit
                self.mail.db.archived = (
                    True if self.rhs.strip().lower() == "true" else False
                )
                for thread in self.threads:
                    if thread.db.name == self.mail.db.thread_name:
                        self.thread = thread
                        break
                for mail in self.thread.db.mails:
                    self.thread.db.archived = True
                    if mail.db.archived is False:
                        self.thread.db.archived = False
                        break
                caller.msg(
                    wrap(
                        f"Message archived: |w{self.mail.db.archived}|n."
                        f" Thread archived: |w{self.thread.db.archived}|n."
                    )
                )
                return
            self.thread = evennia.search_object(
                self.lhs.strip(),
                use_dbref=True,
                candidates=self.threads,
                typeclass=Thread,
            ).first()
            if self.thread:
                self.thread.db.archived = (
                    True if self.rhs.strip().lower() == "true" else False
                )
                for mail in self.thread.db.mails:
                    mail.db.archived = (
                        True if self.rhs.strip().lower() == "true" else False
                    )
                caller.msg(wrap(f"Thread archived: |w{self.thread.db.archived}|n."))
                return
            caller.msg(
                wrap(
                    f"Neither Mail nor Thread found with dbref |w{self.lhs.strip()}|n."
                )
            )
            return
        caller.msg(
            wrap_para(
                f"|RError:|n Couldn't parse Arguments. Use"
                f" |c'help mail'|n for help.\n\n"
                f"Usage: |c'mail/toggle_unread <#dbref> = <true||false>|n"
            )
        )
        return

    ### Create Mail output ###
    def _output_mail(self, mail):
        try:
            output = (
                f"(|w{mail.dbref}|n): |Y{mail.db.sender} ->"
                f" {mail.db.receiver}|n -"
                f" Date: |C{mail.db.date}|n|/"
                f"    Subject: |M'{mail.db.subject}'|n|/"
                f"    Status:"
            )
            if mail.db.receiver == self.account.key:
                if mail.db.unread:
                    output += " (|GUNREAD|n)"
                if mail.db.received:
                    output += " (|Yreceived|n)"
            else:
                if mail.db.postponed:
                    output += " (|Ypostponed|n)"
                elif mail.db.failed:
                    output += "(|RFAILED|n)"
                else:
                    output += " (|Ysent|n)"
            if mail.db.archived:
                output += " (|Marchived|n)"
            if "wm" in self.switches:
                output += "\n"
                output += wrap_para(mail.db.message, indent=4)
            output += "\n"
        except AttributeError:
            output = ""
        return output

    ### Create thread output ###
    def _output_thread(self, threads):
        if not threads:
            if "archived" in self.switches:
                self.caller.msg(wrap("## You don't have any archived Mails!"))
                return
            elif "unread" in self.switches:
                self.caller.msg(wrap("## You don't have any unread Mails!"))
                return
            elif "postponed" in self.switches:
                self.caller.msg(wrap("## You don't have any postponed Mails!"))
                return
            else:
                self.caller.msg(wrap("## No Mails!"))
                return

        output = ""
        # Sort threads in reverse chronological order (newest first)
        sorted_threads = []
        sorted_threads = sorted(threads, reverse=True)
        for thread in sorted_threads:
            output += f"|/## (|w{thread.dbref})|n Thread:"
            output += f" |Y{thread.db.with_account}|n -"
            output += f" |M{thread.db.subject}|n|/"
            output += f"## Last Updated: |C{thread.db.last_updated}|n"
            if thread.db.unread:
                output += " (|GUNREAD|n)"
            if thread.db.archived:
                output += " (|Marchived|n)"

            output += "|/"

            if "wm" in self.switches:
                mails = []
                for mail in thread.db.mails:
                    if "archived" in self.switches:
                        if mail.db.archived is True:
                            mails.append(mail)
                    elif "unread" in self.switches:
                        if mail.db.unread:
                            mails.append(mail)
                    elif "postponed" in self.switches:
                        if mail.db.postponed:
                            mails.append(mail)
                    elif "all" not in self.switches:
                        if not mail.db.archived:
                            mails.append(mail)
                    else:
                        mails.append(mail)

                if not mails:
                    output += "No mails to list.|/"
                else:
                    # sort mails
                    sorted_mails = []
                    sorted_mails = sorted(mails, reverse=False)
                    # create mail output
                    output += "|B" + "=" * _WIDTH + "|n|/"
                    for mail in sorted_mails:
                        output += self._output_mail(mail)
                        mail.db.unread = False
                    output += "|B" + "=" * _WIDTH + "|n"
        if self.caller.db.disable_page == False:
            evmore.msg(
                self.caller,
                text=output,
                always_page=True,
                exit_on_lastpage=True,
                page=True,
            )
        else:
            self.caller.msg(output)
        return

    ### Output Processing message ###
    def _processing_message(self):
        if not self.new:
            adj = "existing"
        else:
            adj = "new"
        text = (
            f"Processing |G{adj}|n message (|w#{self.mail.id}|n) to"
            f" |Y{self.mail.db.receiver}|n -"
            f" |M{self.mail.db.subject}|n -"
        )
        if not self.new:
            text += f" last updated on |C{self.mail.db.date}|n."
        else:
            text += f" |CNew Mail|n."
        self.caller.msg(wrap_para(text))
        return

    ### Process Mail after Editing ###
    @interactive
    def _send_mail(self, caller):
        accs = []
        [accs.append(account.key) for account in evennia.managers.accounts.all()]
        text = ""
        if self.mail.db.receiver not in accs:
            text += (
                f"|G{self.mail.db.receiver}|n Account not found! Message"
                f" can only be postponed or discarded!\n\n"
            )
            text += "|cP|nostpone or |cD|niscard [P]/D?"
        else:
            text += "|cP|nostpone, |cS|nend or |cD|niscard [P]/S/D?"
        text = wrap_para(text)
        answer = yield (text)
        # get ingame time
        date = custom_gametime(absolute=True)
        year, month, week, day, hour, min, sec = date
        month = month + 1
        dayofmonth = (week * 7) + day + 1
        # create entry_desc
        date_str = f"{year:02}-{month:02}-{dayofmonth:02} {hour:02}:{min:02}:{sec:02}"
        if answer.lower() in ["s", "send"]:
            self.mail.db.date = date_str
            self.mail.db.unread = False
            self.thread.db.last_updated = date_str
            if self.mail.db.receiver not in accs:
                self.mail.db.postponed = True
                caller.msg(
                    wrap(
                        f"|YMessage postponed|n because Account "
                        f" |Y{self.mail.db.receiver}|n |Rdoesn't exist|n."
                    )
                )
                return
            else:
                ### Call MailScript on caller to send Mail ###
                ok = self.mailscript.send_mail(self.mail)
                if not ok:
                    self.mail.db.failed = True
                    caller.msg("|RError:|n Send Mail failed!")
                    self.mail.db.postponed = False
                    self.mail.db.unread = False
                    return
                self.mail.db.postponed = False
                self.mail.db.unread = False
                output = f"|GMessage to |Y{self.mail.db.receiver}|G sent!|n"
                caller.msg(wrap(output))
                return
        elif answer.lower() in ["d", "disc", "discard"]:
            self.thread.db.last_updated = date_str
            self.thread.db.mails.remove(self.mail)
            self.mail.delete()
            new_thread = [mail for mail in self.thread.db.mails if mail is not None]
            self.thread.db.mails = new_thread
            if not new_thread:
                self.thread.delete()
                filtered_threads = [thread for thread 
                                    in self.threads
                                    if thread is not None]
                self.threads = sorted(filtered_threads, reverse=False)
            caller.msg(wrap("|RMessage discarded!"))
            return
        elif answer.lower() in ["p", "post", "postpone", ""]:
            self.mail.db.postponed = True
            self.thread.db.last_updated = date_str
            self.mail.db.date = date_str
            self.mail.db.unread = False
            caller.msg(wrap("|YMessage postponed.|n"))
            return
        else:
            self.mail.db.status.lower = "postponed"
            self.thread.db.last_updated = date_str
            self.mail.db.date = date_str
            self.mail.db.unread = False
            caller.msg(wrap("|YMessage postponed as default.|n"))
            return
        return

    ### Run EvEditor ###
    def _edit_handler(self, caller):
        """Activate the line editor"""

        def _load(caller):
            """Called for the editor to load the buffer"""
            nonlocal self
            old_value = self.mail.attributes.get("message")
            if old_value is None or not isinstance(old_value, str):
                old_value = ""
            return str(old_value)  # we already confirmed we are ok with this

        def _save(caller, buf):
            """Called when editor saves its buffer."""
            nonlocal self
            self.mail.db.message = buf
            return True

        def _quit(caller):
            nonlocal self
            self._send_mail(caller)

        # start the editor
        EvEditor(caller, _load, _save, _quit, key="")

    #### Delete Thread or Message with dbref ####
    @interactive
    def delete_switch(self, caller):
        caller = caller
        no_use = set(
            [
                "send",
                "reply",
                "threads",
                "toggle_archived",
                "list",
                "edit",
                "postponed",
                "all",
                "toggle_unread",
                "archive",
                "unread",
                "wm",
            ]
        )
        switches = set(self.switches)
        if switches.intersection(no_use):
            err = (
                "|RConflicting switches:|n You can't use these switches"
                " together."
                "\n\nType |c'help mail'|n for information to correct usage."
            )
            caller.msg(wrap_para(err))
            return

        # Check for dbref
        ref = dbref(self.args.strip())
        if ref is None:
            caller.msg(wrap("|RError:|n Couldn't parse arguments."))
            return False

        # We got a #dbref
        self.mail = evennia.search_object(
            self.args.strip(), use_dbref=True, candidates=self.mails, typeclass=Mail
        ).first()
        if self.mail:
            # We got a mail to delete
            self.thread = None
            if self.caller.db.disable_page == False:
                caller.msg(wrap("|RDeleting Message:|n"))
                evmore.msg(
                    self.caller,
                    text=self._output_mail(self.mail),
                    always_page=True,
                    exit_on_lastpage=True,
                    page=True,
                )
                for thread in self.threads:
                    if thread.db.name == self.mail.db.thread_name:
                        self.thread = thread
                        break
            else:
                caller.msg(wrap("|RDeleting Message:|n"))
                caller.msg(self._output_mail(self.mail))

            if not self.thread:
                caller.msg(
                    wrap(
                        "|RError:|n Thread not found! Please inform Admin."
                        " Message |Rnot|n deleted!"
                    )
                )
                return False
            answer = yield ("Are you sure? Y/[N]")
            if answer.lower() in ["y", "yes"]:
                self.mail.delete()
                caller.msg(wrap("Message |Rdeleted|n!"))
                filtered_mails = [mail for mail in self.thread.db.mails
                                  if mail is not None]
                self.thread.db.mails = sorted(filtered_mails, reverse=False)
                ## Check if last in Thread. If yes, delete Thread
                if not self.thread.db.mails:
                    if self.thread in self.threads:
                        self.thread.delete()
                        output = "Was last message in thread."
                        output += " Thread |Rdeleted|n."
                        filtered_threads = [thread for thread 
                                            in self.threads
                                            if thread is not None]
                        self.threads = sorted(filtered_threads, reverse=False)
                        caller.msg(wrap(output))
                        return
                    else:
                        caller.msg(
                            wrap(
                                "|RError:|n Couldn't delete empty"
                                " thread. Please inform Admin!"
                            )
                        )
                        return
                return
            else:
                caller.msg(wrap("|YDeletion canceled!|n"))
                return
        else:
            # Maybe a thread?
            self.thread = evennia.search_object(
                self.args.strip(),
                use_dbref=True,
                candidates=self.threads,
                typeclass=Thread,
            ).first()
            if self.thread:
                caller.msg(wrap("|RDeleting Thread:|n"))
                self._output_thread([self.thread])
                # We got a thread to delete
                answer = yield ("Are you sure? Y/[N]")
                if answer.lower() in ["y", "yes"]:
                    self.thread.delete()
                    filtered_threads = [thread for thread 
                                        in self.threads
                                        if thread is not None]
                    self.threads = sorted(filtered_threads, reverse=False)
                    caller.msg(wrap("Thread |RDELETED!|n"))
                    return True
                else:
                    caller.msg(wrap("|YDeletion canceled!|n"))
                    return False
            else:
                caller.msg(
                    wrap(
                        f"Neither a Thread nor a Message with"
                        f" dbref |w'{self.args.strip()}'|n found."
                        f" Maybe a typo?"
                    )
                )
                return False

    #### Create new Thread or send postponed Message ####
    def send_switch(self):
        caller = self.caller
        no_use = set(
            [
                "reply",
                "threads",
                "delete",
                "list",
                "archived",
                "postponed",
                "all",
                "unread",
                "toggle_archived",
                "toggle_unread",
                "wm",
            ]
        )
        switches = set(self.switches)
        if switches.intersection(no_use):
            err = (
                "|RConflicting switches:|n You can't use these switches"
                " together."
                "\n\nType |c'help mail'|n for information to correct usage."
            )
            caller.msg(wrap_para(err))
            return
        try:
            receiver, subject = self.args.split("=", 1)
        except ValueError:
            # Maybe we got a single dbref
            ref = dbref(self.args.strip())
            if ref is not None:
                # We got a #dbref
                self.mail = evennia.search_object(
                    self.args.strip(), candidates=self.mails, typeclass=Mail
                ).first()
                if self.mail is not None:
                    if (
                        self.mail.db.receiver != caller.key
                        and self.mail.db.receiver != self.account.key
                    ):
                        thread_name = (
                            f"{self.mail.db.receiver}:"
                            f" '{self.mail.db.subject}'"
                        )
                        thread_name.strip()
                    else:
                        caller.msg(wrap(
                            "|RError:|n You can't send a message to yourself!"
                            " Message discarded."
                        ))
                        return
                    self.mail.db.unread = False
                    for thread in self.threads:
                        if thread.db.name == thread_name:
                            self.thread = thread
                            break
                    if self.thread is None:
                        caller.msg(
                            wrap(
                                f"|RError:|n Thread not found. Please contact an Admin."
                            )
                        )
                        return
                    if not self.mail.db.postponed:
                        caller.msg(
                            wrap(
                                f"|RError:|n"
                                f" Message (|w#{self.mail.id}|n) from"
                                f" |Y{self.mail.sender}|n"
                                f" to |Y{self.mail.db.receiver}|n in"
                                f" thread"
                                f" |M'{self.mail.db.subject}'|n was"
                                f" already sent or received! - Date:"
                                f" |C{self.mail.db.date}|n."
                            )
                        )
                        return

                else:
                    # The dbref is not a vaild
                    err = (
                        "You need at least to supply a receiver and a subject"
                        " or a single |w#dbref|n of a postponed message."
                        "\n\nIf you don't supply a message with a subject"
                        " the editor will"
                        " open even if you don't use the /edit switch."
                        "\n\nUsage: |c'mail/send <receiver> = <subject>"
                        "[;;<message>]'|n to create a new thread or\n\n"
                        "|c'mail/send #dbref'|n to send a postponed message."
                        "\n\nUse |c'help mail|n for help."
                    )
                    caller.msg(wrap_para(err))
                    return

                # We got a valid dbref and process it and end function
                self.new = False
                self._processing_message()
                if "edit" in self.switches and self.mail.db.postponed is True:
                    self._edit_handler(caller)
                else:
                    self._send_mail(caller)
                return

        else:
            # We got a receiver and a subject
            self.new = True
            receiver = receiver.strip()
            accounts = []
            [accounts.append(account.key)
                for account in evennia.managers.accounts.all()]
            chars = []
            [
                chars.append(char.key)
                for account in evennia.managers.accounts.all()
                for char in account.characters
            ]
            if receiver not in accounts and receiver not in chars:
                caller.msg(
                    wrap(
                        f"|RError:|n No Character or Account |Y'"
                        f"{receiver}'|n found. Message discarded."
                    )
                )
                return
            try:
                subject, message = subject.split(";;", 1)
            except ValueError:
                message = ""
            subject = subject.strip()
            message = message.strip()
            if message == "" and "edit" not in self.switches:
                self.switches.append("edit")

            if receiver == caller.key or receiver == self.account.key:
                caller.msg(
                    wrap(
                        "|RError:|n You can't send a message to yourself!"
                        " Message |Rdiscarded|n."
                    )
                )
                return

            # Create self.threads list if nothing present
            if not self.threads or self.threads is None:
                self.threads = []

            # Search Account
            if receiver in accounts:
                receiver_account = evennia.search_account(receiver).first()
                if not receiver_account or receiver_account is None:
                    err = wrap(
                        f"|RError:|n couldn't find Account for"
                        f" |Y'{receiver}|n. Message discarded."
                    )
                    caller.msg(err)
                    return
            elif receiver in chars:
                chars = []
                [chars.append(char)
                    for account in evennia.managers.accounts.all()
                    for char in account.characters]
                receiver_obj = evennia.search_object(receiver,
                                                 candidates=chars).first()
                try:
                    receiver_account = receiver_obj.account
                except AttributeError:
                    receiver_account = None
                if (not receiver_account or receiver_account is None or
                        not inherits_from(receiver_account, DefaultAccount)):
                    err = wrap(
                        f"|RError:|n couldn't find Account for"
                        f" |Y'{receiver}|n. Message discarded."
                    )
                    caller.msg(err)
                    return
                else:
                    caller.msg(wrap(
                        f"Sending message to Account |Y'{receiver_account}'|n"
                        f" of Character |Y{receiver}|n."))
            else:
                caller.msg(wrap(
                    f"|RError:|n No Account or Character |Y{receiver}|n"
                    f" found. Message discarded"))
                return

            thread_name = f"{receiver_account.key}: '{subject}'"
            for thread in self.threads:
                if thread.db.name == thread_name:
                    self.thread = thread
                    break
            if not self.thread or self.thread is None:
                self.thread = create_object(
                    typeclass=Thread,
                    key="thread",
                    location=None,
                    attributes=[
                        ("name", thread_name),
                        ("with_account", receiver_account.key),
                        ("subject", subject),
                        ("last_updated", ""),
                        ("archived", False),
                        ("unread", False),
                        ("mails", []),
                    ],
                )
                self.mailscript.db.threads.append(self.thread)

            self.mail = create_object(
                typeclass=Mail,
                key="mail",
                location=None,
                attributes=[
                    ("receiver", receiver_account.key),
                    ("sender", self.account.key),
                    ("sender_id", self.account.id),
                    ("thread_name", self.thread.db.name),
                    ("subject", subject),
                    ("message", message),
                    ("date", ""),
                    ("postponed", True),
                    ("archived", False),
                    ("unread", False),
                    ("failed", False),
                    ("received", False),
                ],
            )

            # search again for thread
            for thread in self.mailscript.db.threads:
                if thread.db.name == self.mail.db.thread_name:
                    thread.db.mails.append(self.mail)
                    self.thread = thread
                    break

            # We edit and precess the Mail and return
            self._processing_message()
            if "edit" in self.switches:
                self._edit_handler(caller)
            else:
                self._send_mail(caller)
            return

    #### Reply to a Thread or send a postponed message ####
    def reply_switch(self):
        caller = self.caller
        no_use = set(
            [
                "send",
                "threads",
                "delete",
                "list",
                "archived",
                "postponed",
                "all",
                "unread",
                "toggle_archived",
                "toggle_unread",
                "wm",
            ]
        )
        switches = set(self.switches)
        if switches.intersection(no_use):
            err = (
                "|RConflicting switches:|n You can't use these switches"
                " together."
                "\n\nType |c'help mail'|n for information to correct usage."
            )
            caller.msg(wrap_para(err))
            return
        # We need a single dbref of a postponed message
        # or a dbref of a message or thread to reply possibly with a
        # message
        try:
            self.lhs, self.rhs = self.args.split("=", 1)
        except ValueError:
            self.lhs = self.args.strip()
            self.rhs = ""

        self.lhs = self.lhs.strip()
        self.rhs = self.rhs.strip()
        ref = dbref(self.lhs)
        if ref is not None:
            # We got a #dbref
            self.mail = evennia.search_object(
                self.lhs, candidates=self.mails, typeclass=Mail
            ).first()
            if self.mail is not None:
                for thread in self.threads:
                    if thread.db.name == self.mail.db.thread_name:
                        self.thread = thread
                        break
                if self.thread is None:
                    caller.msg(
                        wrap(f"|RError:|n Thread not found. Please contact an Admin.")
                    )
                    return
                if self.mail.db.postponed:
                    # We got a postponed message: process it and end
                    # function
                    self.new = False
                    self._processing_message()
                    if "edit" in self.switches:
                        self._edit_handler(caller)
                    else:
                        self._send_mail(caller)
                    return
            else:
                self.thread = evennia.search_object(
                    self.lhs, candidates=self.threads, typeclass=Thread
                ).first()
            if self.thread is None:
                err = wrap_para(
                    "|RError: The provided dbref is neither a mail nor a"
                    " thread. You have to provide either a dbref to a"
                    " postponed message, a message in a thread or a"
                    " thread."
                    "\n\nUse |c'help mail'|n for information on correct"
                    " usage."
                )
                caller.msg(err)
                return
            # We have a thread
            self.new = True
            self.mail = create_object(
                typeclass=Mail,
                key="mail",
                location=None,
                attributes=[
                    ("receiver", self.thread.db.with_account),
                    ("sender", self.account.key),
                    ("sender_id", self.account.id),
                    ("thread_name", self.thread.db.name),
                    ("subject", self.thread.db.subject),
                    ("message", self.rhs),
                    ("date", ""),
                    ("postponed", False),
                    ("archived", False),
                    ("unread", False),
                    ("failed", False),
                    ("received", False),
                ],
            )
            self.thread.db.mails.append(self.mail)
            self._processing_message()
            self.mail.db.unread = False
            if "edit" in self.switches or self.mail.db.message == "":
                self._edit_handler(caller)
            else:
                self._send_mail(caller)
            return
        else:
            # The dbref is not a vaild
            err = (
                "You need at least to supply a single |w#dbref|n of a"
                " postponed message or of an existing message or thread."
                "\n\nIf you don't supply a message after an equal sign"
                " the editor will open even if you don't use the /edit"
                " switch."
                "\n\nUsage: |c'mail/reply[/edit] <dbref> [= <message>]|n"
                " to create new reply or use the <dbref> of a postponed"
                " message without a <message>."
                "\n\nUse |c'help mail|n for help."
            )
            caller.msg(wrap_para(err))
            return
        return

    ### Output Mail or Thread ###
    def output_switch(self):
        ref = dbref(self.args.strip())
        if ref is not None:
            # We got a #dbref
            # maybe Mail?
            self.mail = evennia.search_object(
                self.args.strip(), use_dbref=True, candidates=self.mails, typeclass=Mail
            ).first()
            if self.mail is not None:
                self.switches.append("wm")
                if self.caller.db.disable_page == False:
                    evmore.msg(
                        self.caller,
                        text=self._output_mail(self.mail),
                        always_page=True,
                        exit_on_lastpage=True,
                        page=True,
                    )
                else:
                    self.caller.msg(self._output_mail(self.mail))
                    # update unread bit on mail and MailScript
                    self.mail.db.unread = False
                return
            else:
                # No mail. Maybe thread?
                self.threads_switch()
                return
        else:
            self.caller.msg(
                wrap("Couldn't parse arguments. Ignoring.Use |c'help mail'|n for help.")
            )
            return

    ### Thread Commands ###
    def threads_switch(self):
        caller = self.caller
        no_use = set(
            ["send", "reply", "edit", "delete",
             "toggle_archived", "toggle_unread"]
        )
        switches = set(self.switches)
        if switches.intersection(no_use):
            err = (
                "|RConflicting switches:|n You can't use these switches"
                " together."
                "\n\nType |c'help mail'|n for information to correct usage."
            )
            caller.msg(wrap_para(err))
            return
        if "all" in self.switches and (
            "archived" in self.switches
            or "unread" in self.switches
            or "postponed" in self.switches
        ):
            caller.msg(
                wrap_para(
                    "|RConflicting switches:|n You can't use [/all] with"
                    " [/unread], [/archived] or [/postponed] switches."
                    "\n\nType |c'help mail'|n for information to correct usage."
                )
            )
            return
        if "archived" in self.switches and "unread" in self.switches:
            caller.msg(
                wrap_para(
                    "|RConflicting switches:|n You can't use [/archived]"
                    "and [/unread] switches together."
                    "\n\nType |c'help mail'|n for information to correct usage."
                )
            )
            return
        if "unread" in self.switches and "postponed" in self.switches:
            caller.msg(
                wrap_para(
                    "|RConflicing switches:|n You can't use [/unread] and"
                    "[/postponed] switches together."
                    "\n\nType |c'help mail'|n for information to correct usage."
                )
            )
            return
        if "archived" in self.switches and "postponed" in self.switches:
            caller.msg(
                wrap_para(
                    "|RConflicting switches:|n You can't use [/archived]"
                    "and [/postponed] switches together."
                    "\n\nType |c'help mail'|n for information to correct usage."
                )
            )
            return
        # sort mails and threads
        pre_sorted_threads = [thread for thread in self.threads
                              if thread is not None]
        threads = sorted(pre_sorted_threads, reverse=True)

        for thread in threads:
            thread.db.unread = False
            mails = [mail for mail in thread.db.mails if mail is not None]

            # sort mails in chronological order (oldest first)
            thread.db.mails = sorted(mails, reverse=False)

            for mail in thread.db.mails:
                if mail.db.unread:
                    thread.db.unread = True
                    break

        sorted_threads = []
        if "archived" in self.switches:
            for thread in threads:
                for mail in thread.db.mails:
                    if mail.db.archived:
                        sorted_threads.append(thread)
                        break
        elif "unread" in self.switches:
            for thread in threads:
                thread.db.unread = False
                for mail in thread.db.mails:
                    if mail.db.unread:
                        thread.db.unread = True
                        sorted_threads.append(thread)
                        break
        elif "postponed" in self.switches:
            for thread in threads:
                for mail in thread.db.mails:
                    if mail.db.postponed:
                        sorted_threads.append(thread)
                        break
        elif "all" in self.switches:
            sorted_threads = threads
        else:
            for thread in threads:
                thread.db.archived = True
                for mail in thread.db.mails:
                    if mail.db.archived is False:
                        thread.db.archived = False
                        sorted_threads.append(thread)
                        break
        for thread in sorted_threads:
            thread.db.archived = True
            thread.db.unread = False
            for mail in thread.db.mails:
                if not mail.db.archived:
                    thread.db.archived = False
                if mail.db.unread:
                    thread.db.unread = True

        # check args for eventual dbref
        ref = dbref(self.args.strip())
        if ref is None:
            pass
        else:
            self.switches = []
            self.switches.append("all")
            self.switches.append("wm")
            sorted_threads = []
            thread = evennia.search_object(
                f"#{ref}", use_dbref=True, candidates=self.threads,
                typeclass=Thread).first()
            if not thread:
                caller.msg(
                    wrap(
                        f"|RError:|n Couldn't find mail or thread with"
                        f" dbref |w{self.args.strip()}|n. Maybe a typo?"
                    )
                )
                return
            sorted_threads = [thread]
            for thread in sorted_threads:
                thread.db.unread = False
                thread.db.archived = True
                for mail in thread.db.mails:
                    if mail.db.unread:
                        thread.db.unread = True
                    if not mail.db.archived:
                        thread.db.archived = False

        if self.args and ref is None:
            caller.msg(wrap("Couldn't parse args. Ignoring."))
        # call output function
        self._output_thread(sorted_threads)

    ### Main Function of the Command ###

    def func(self):
        """Implements the command."""

        ### Initialization ###
        caller = self.caller
        self.account = None
        try:
            self.account = caller.account
        except AttributeError:
            pass
        if inherits_from(caller, DefaultAccount):
            self.account = caller
        if self.account is None:
            caller.msg(wrap(f"|RError:|n No Account for |Y'{caller.key}'|n found!"))
            return
        self.thread = None
        self.mail = None
        try:
            self.mailscript = find_mailscripts(self.account)[0]
        except IndexError:
            caller.msg(wrap(
                "|RError:|n 'MailScript' not found. Please call Admin."))
            return

        if not self.mailscript.db.threads or self.mailscript.db.threads is None:
            self.mailscript.db.threads = []
        # create shortcuts
        self.threads = self.mailscript.db.threads

        # filter None types and sort threads and mails
        filtered_threads = [
            thread for thread in self.mailscript.db.threads if thread is not None
        ]
        self.mailscript.db.threads = sorted(filtered_threads, reverse=False)
        # create shortcuts
        self.threads = self.mailscript.db.threads

        for thread in self.threads:
            mails = [mail for mail in thread.db.mails if mail is not None]
            thread.db.mails = sorted(mails, reverse=False)

        # Add all mails to self.mails and update unread bit of MailScript
        self.mails = []
        [
            self.mails.append(mail)
            for thread in self.threads
            for mail in thread.db.mails
            if mail is not None
        ]

        # No switches or arguments: Return unread mail
        if not self.switches and not self.args.strip():
            self.switches.append("threads")
            self.switches.append("unread")
            self.switches.append("wm")
            self.threads_switch()
            self.switches = []

        # No switches but arguments (dbref of mail)
        if not self.switches and self.args.strip() != "":
            self.output_switch()
            self.switches = []

        # Send Message
        if "send" in self.switches:
            self.send_switch()
            self.switches = []

        # Send Message
        if "reply" in self.switches:
            self.reply_switch()
            self.switches = []

        # show threads
        if "threads" in self.switches:
            ignore = set(["all", "unread", "archived", "postponed"])
            switches = set(self.switches)
            if ignored := switches.intersection(ignore):
                caller.msg(
                    wrap("|RWarning:|n ignoring switches '" +
                         ", ".join(ignored) + "'"))
            if self.args:
                caller.msg(wrap("|RWarning:|n ignoring arguments."))
            self.args = self.lhs = self.rhs = ""
            if "wm" in self.switches:
                self.switches = ["threads", "wm"]
            else:
                self.switches = ["threads"]
            self.threads_switch()
            self.switches = []

        # show all mail
        if "all" in self.switches:
            if self.args:
                caller.msg(wrap("|RWarning:|n Ignoring Arguments."))
            self.args = self.lhs = self.rhs = ""
            self.switches.append("threads")
            self.threads_switch()
            self.switches = []

            # show all unread mails
        if "unread" in self.switches:
            if self.args:
                caller.msg(wrap("|RWarning:|n Ignoring Arguments."))
            self.args = self.lhs = self.rhs = ""
            self.switches.append("threads")
            self.threads_switch()
            self.switches = []

            # show all archived mails
        if "archived" in self.switches:
            if self.args:
                caller.msg(wrap("|RWarning:|n Ignoring Arguments."))
            self.args = self.lhs = self.rhs = ""
            self.switches.append("threads")
            self.threads_switch()
            self.switches = []

            # show all postponed mails
        if "postponed" in self.switches:
            if self.args:
                caller.msg(wrap("|RWarning:|n Ignoring Arguments."))
            self.args = self.lhs = self.rhs = ""
            self.switches.append("threads")
            self.threads_switch()
            self.switches = []

            # delete Messages or threads
        if "delete" in self.switches:
            self.delete_switch(self.caller)
            self.switches = []

        # toggle Archive bit on Messages or Threads
        if "toggle_archived" in self.switches:
            self.archived_switch()
            self.switches = []

        # toggle Unread bit on Messages or Threads
        if "toggle_unread" in self.switches:
            self.unread_switch()
            self.switches = []

        # Update 'unread' number on Threads and on MailScript and Character
        unread_num = 0
        for thread in self.threads:
            thread.db.unread = False
            for mail in thread.db.mails:
                if mail.db.unread is True:
                    thread.db.unread = True
                    unread_num += 1
        self.account.db.unread_mail = unread_num
        self.mailscript.db.unread = unread_num
        return


#### Mail Command Set ####
class MailCmdSet(CmdSet):
    """
    This is a CommandSet for a Guestbook
    """

    key = "mailcmdset"

    def at_cmdset_creation(self):
        "Called once, when the cmdset is first created"
        self.add(CmdMail())
