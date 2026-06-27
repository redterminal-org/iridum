"""
A Forum Room where you can discuss and collaborate
"""

from evennia import CmdSet, create_object, search_object
from evennia import settings
from evennia.utils.dbserialize import ObjectDoesNotExist
from evennia.utils.eveditor import EvEditor
from evennia.utils.utils import dbref, interactive

from world.typeclasses.rooms import Room
from world.typeclasses.objects import Object
from world.utils.utils import wrap, wrap_para
from world.utils.gametime import custom_gametime
from world.utils import evmore

from commands.command import MuxCommand

_WIDTH = settings.DEFAULT_WIDTH

#### ForumComment typeclass ####
class ForumComment(Object):
    """
    A ForumComment Object. Used in a Forum Thread.

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
        self.locks.add("iscontainer:false();getfrom:false();")
        self.locks.add("getcontainer:false();")
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
class ForumThread(Object):
    """
    A Thread Object. Used to discuss in a Forum Room.

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
        self.locks.add("iscontainer:false();getfrom:false();")
        self.locks.add("getcontainer:false();")
        self.locks.add("examine:perm(Developer);")
        self.locks.add("teleport:false();teleport_here:false();view:false();")
        self.locks.add("puppet:false();traverse:false();")

        self.db.comments = []

    def at_object_delete(self, **kwargs):
        if self.db.comments and self.db.comments is not None:
            for comment in self.db.comments:
                try:
                    if comment is not None:
                        comment.delete()
                except ObjectDoesNotExist:
                    pass
        return True

    def return_appearance(self):
        return self.set_appearance(things="")

    def __lt__(self, other):
        return self.db.last_updated < other.db.last_updated

    def __gt__(self, other):
        return self.db.last_updated > other.db.last_updated


### Forum typeclass ###
class Forum(Room):
    """
    This room is a Forum, where you can discuss and collaborate.
    """

    class_perm = {"create": "Expert Builder"}

    @classmethod
    def get_default_lockstring(cls, account=None, caller=None, **kwargs):
        if caller is not None:
            id = caller.id
            pid = caller.account.id

            new_obj_lockstring = f"control:id({id}) or pid({
                pid}) or perm(Developer);"
            new_obj_lockstring += (
                f"attrcreate:id({id}) or pid({pid}) or perm(Developer Builder);"
            )
            new_obj_lockstring += (
                f"delete:id({id}) or pid({pid}) or perm(Developer);"
            )
            new_obj_lockstring += (
                f"edit:id({id}) or pid({pid}) or perm(Developer);"
            )
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += (
                f"examine:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += (
                f"teleport_here:id({id}) or pid({
                    pid}) or perm(Advanced Builder);"
            )

        elif account is not None:
            pid = account.id

            new_obj_lockstring = f"control:pid({pid}) or perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({
                pid}) or perm(Developer);"
            new_obj_lockstring += f"delete:pid({pid}) or perm(Developer);"
            new_obj_lockstring += f"edit:pid({pid}) or perm(Developer);"
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += f"examine:pid({
                pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:pid({
                pid}) perm(Advanced Builder);"

        else:
            new_obj_lockstring = f"control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:perm(Developer);"
            new_obj_lockstring += f"delete:perm(Developer);"
            new_obj_lockstring += f"edit:perm(Developer);"
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += f"examine:perm(Expert Builder);"
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:all();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:perm(Advanced Builder);"
        return new_obj_lockstring

    def at_object_creation(self):
        # call inheritated function
        super().at_object_creation()

        # create empty Entry List
        self.db.threads = []

        # add CommandSet
        self.cmdset.add(ForumCmdSet, persistent=True)

    def at_object_delete(self, **kwargs):
        if self.db.threads and self.db.threads is not None:
            for thread in self.db.threads:
                if thread is not None:
                    thread.delete()

        super().at_object_delete()
        return True

    def return_appearance(self, looker, **kwargs):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        """
        if not looker:
            return ""
        caller = looker
        if caller.account is None or not caller.account:
            return
        account = caller.account
        if not self.db.visitors or self.db.visitors is None:
            self.db.visitors = []
        if account.key not in self.db.visitors:
            for thread in self.db.threads:
                thread.db.seen.append(account.key)
                thread.db.seen = list(set(thread.db.seen))
            self.db.visitors.append(account.key)
            self.db.visitors = list(set(self.db.visitors))

        desc = self.db.desc

        text = ""

        threads = [thread for thread in self.db.threads
                   if thread is not None]
        self.db.threads = threads

        pinned_threads = [thread for thread in self.db.threads
                          if thread.db.pinned]
        for pinned in pinned_threads:
            pinned.db.seen = []
        sorted_pinned_threads = sorted(pinned_threads, reverse=True)

        self.unread_threads = []
        for thread in self.db.threads:
            if not thread.db.seen or thread.db.seen is None:
                thread.db.seen = []
            if thread.db.follows is None:
                thread.db.follows = []
            if ((caller.account.key not in thread.db.follows
                    or thread.db.archived) and not thread.db.pinned):
                continue
            for comment in thread.db.comments:
                if comment.db.read is None:
                    comment.db.read = []
                comment.db.read = list(set(comment.db.read))
                if caller.account.key not in comment.db.read:
                    self.unread_threads.append(thread)
                    break

        filtered_threads = [thread for thread in self.db.threads
                            if (caller.account.key not in thread.db.seen
                                or account.key in thread.db.follows)
                            and not thread.db.archived
                            and not thread.db.pinned]

        sorted_threads = sorted(filtered_threads, reverse=True)
        thread_list = sorted_pinned_threads + sorted_threads
        if thread_list:
            text = self._return_threads(caller, thread_list)
        else:
            text = "## No Threads."

        return self.set_appearance(looker, desc=desc, text=text)

    def _return_threads(self, caller, threads):
        thread_num = 0
        text = ""
        for thread in threads:
            text += (
                f"## |w({thread.dbref})|n |Y{thread.db.sender}|n -"
                f" |M'{thread.db.subject}'|n"
            )
            if (caller.account.key not in thread.db.seen 
                    and not thread.db.pinned):
                text += " |Y(unseen)|n"
            if thread in self.unread_threads:
                text += " |G(unread)|n"
            if (caller.account.key in thread.db.follows
                    and not thread.db.pinned):
                text += " |b(followed)|n"
            if thread.db.pinned:
                text += " |b(PINNED)|n"
            text += "|/" + wrap(
                f"## Date: |C{thread.db.date}|n - Last updated:"
                f" |C{thread.db.last_updated}|n"
            )
            if thread.db.last_edited is not None:
                text += "|/" + wrap(
                    f"## Last edited: |C{thread.db.last_edited}|n"
                )
            thread_num += 1
            if thread_num < len(threads):
                text += "\n\n"
        #text += "|/" + wrap_para(thread.db.message, indent=4)
        return text


### Run EvEditor for thread ###
def _edit_thread(self, caller):
    """Activate the line edit"""

    def _load(caller):
        """Called for the edit to load the buffer"""
        nonlocal self
        old_value = self.thread.attributes.get("message")
        if old_value is None or not isinstance(old_value, str):
            old_value = ""
        return str(old_value)  # we already confirmed we are ok with this

    def _save(caller, buf):
        """Called when edit saves its buffer."""
        nonlocal self
        self.thread.db.message = buf
        return True

    def _quit(caller):
        nonlocal self
        self._save_thread(caller)
        if self.create:
            caller.msg(wrap(f"Thread |w({self.thread.dbref})|n created!"))
        else:
            caller.msg(wrap(f"Thread |w({self.thread.dbref})|n updated!"))
        return

    # start the edit
    EvEditor(caller, _load, _save, _quit, key="")


### Run EvEditor for comment ###
def _edit_comment(self, caller):
    """Activate the line edit"""

    def _load(caller):
        """Called for the edit to load the buffer"""
        nonlocal self
        old_value = self.comment.attributes.get("message")
        if old_value is None or not isinstance(old_value, str):
            old_value = ""
        return str(old_value)  # we already confirmed we are ok with this

    def _save(caller, buf):
        """Called when edit saves its buffer."""
        nonlocal self
        self.comment.db.message = buf
        return True

    def _quit(caller):
        nonlocal self
        self._save_comment(caller)
        if self.create:
            caller.msg(wrap(f"Comment |w({self.comment.dbref})|n created!"))
        else:
            caller.msg(wrap(f"Comment |w({self.comment.dbref})|n updated!"))
        return

    # start the edit
    EvEditor(caller, _load, _save, _quit, key="")


### "add" Command to add a Forum entry
class CmdAdd(MuxCommand):
    """
    Adds a Forum thread or comment

    Usage:
        add[/edit] <subject> [= <message>]
        add[/edit] <#dbref> [= <subject>][;;<message>]

    This lets you add a Forum thread or comment to the forum. If you add the
    /edit switch, the editor will open to edit the eventual initial message.
    
    If you want to create a new thread, you have to provide a subject at least.
    Then the editor will open and let you edit your thread entry.

    If you place a #dbref of a thread as fist parameter before the equal sign,
    the "add" command will add a comment to this thread with a <subject> and a
    <message>. You can also only use a <#dbref> to a thread without a subject,
    then the subject of the thread will be used.

    The editor will also open, if you omit the <message> in the command, even
    if you don't specify the /edit switch.
    """

    key = "add"
    switch_options = ("edit",)
    locks = "cmd:perm(Player);"
    help_category = "Forum"

    def func(self):
        "Adds an thread to the Forum"

        caller = self.caller

        # set for _edit_thread() output
        self.create = True

        if not self.args:
            # no argument (target) given. Don't launch missiles
            err = (
                    "|RError:|n This command needs at least a subject to"
                    " create a new thread and open the edit."
                    " Use |c'help add'|n for help."
            )
            caller.msg(wrap(err))
            return
        try:
            self.lhs, self.rhs = self.args.split("=", 1)
            self.lhs = self.lhs.strip()
            self.rhs = self.rhs.strip()
        except ValueError:
            # we have one argument
            self.lhs = self.args.strip()
            self.rhs = ""
        if not self.lhs.strip():
            caller.msg(wrap(
                "You need at least provide a <subject> on the command line"
                " to create a new thread. If you want to comment on a thread"
                " you need to provide the <#dbref> of the thread on the left"
                " side of the equal sign and a <subject> on the right side"
                " of the equal sign. Type |c'help add'|n for help."
            ))
            return
        # Create Message
        if dbref(self.lhs) is None:
            self.thread = create_object(
                typeclass=ForumThread,
                key="forumthread",
                location=None,
                attributes=[
                    ("sender", self.caller.key),
                    ("sender_id", self.caller.id),
                    ("subject", self.lhs),
                    ("message", self.rhs),
                    ("date", None),
                    ("last_updated", None),
                    ("last_edited", None),
                    ("seen", []),
                    ("follows", []),
                    ("archived", False),
                    ("comments", [])
                ],
            )
            caller.msg(wrap(
                f"Processing thread |w({self.thread.dbref})|n from |Y"
                f"{self.thread.db.sender}|n - |M{self.thread.db.subject}|n -"
                f" |CNew Thread|n."
            ))
            ## Edit and save
            if "edit" in self.switches or not self.rhs:
                _edit_thread(self, caller)
                return
            caller.msg(wrap(
                f"Thread |w({self.thread.dbref})|n created!"
            ))
            self._save_thread(caller)
            return
        else:
            # search thread
            self.thread = search_object(f"{self.lhs.strip()}",
                                        candidates=self.obj.db.threads,
                                        typeclass=ForumThread).first()
            if not self.thread:
                caller.msg(wrap(
                    f"|RError:|n No thread with #dbref |w({self.lhs.strip()})"
                    f"|n found! Type |c'help add'|n for help."
                ))
                return
            if self.thread.db.archived:
                caller.msg(wrap(
                    f"Thread |w({self.thread.dbref})|n from |Y"
                    f"{self.thread.db.sender}|n - |M{self.thread.db.subject}|n -"
                    f" |C{self.thread.db.date}|n is |RLOCKED|n (archived)."
                    f" You can't add or edit comments."
                ))
                return
            # Split self rhs in subject and message if possible
            try:
                subject, message = self.rhs.split(";;", 1)
                subject = subject.strip()
                message = message.strip()
            except ValueError:
                if self.rhs.strip() and self.rhs is not None:
                    subject = self.rhs.strip()
                else:
                    subject = self.thread.db.subject
                message = ""
            # create comment
            self.comment = create_object(
                typeclass=ForumComment,
                key="forumcomment",
                location=None,
                attributes=[
                    ("sender", self.caller.key),
                    ("sender_id", self.caller.id),
                    ("thread", self.thread),
                    ("subject", subject),
                    ("message", message),
                    ("read", []),
                    ("archived", False),
                    ("date", None),
                    ("last_edited", None)
                ],
            )
            caller.msg(wrap(
                f"Processing comment |w({self.comment.dbref})|n from |Y"
                f"{self.comment.db.sender}|n - |M{self.comment.db.subject}|n -"
                f" |CNew comment|n to thread"
                f" |w({self.thread.dbref})|n from |Y{self.thread.db.sender}"
                f"|n - |M{self.thread.db.subject}|n from date |C"
                f"{self.thread.db.date}|n."
            ))
            ## Edit and save
            if "edit" in self.switches or not self.comment.db.message:
                _edit_comment(self, caller)
                return
            caller.msg(wrap(
                f"Comment |w({self.comment.dbref})|n created!"
            ))
            self._save_comment(caller)
            return
        return

    def _save_thread(self, caller):
        # get ingame time
        date = custom_gametime(absolute=True)
        year, month, week, day, hour, min, sec = date
        month = month + 1
        dayofmonth = (week * 7) + day + 1
        # create thread_desc
        date_str = f"{year:02}-{month:02}-{dayofmonth:02}"
        date_str += f" {hour:02}:{min:02}:{sec:02}"
        self.thread.db.date = date_str
        self.thread.db.last_updated = date_str
        self.thread.db.last_edited = None
        # add to Forum Thread list.
        self.obj.db.threads.append(self.thread)
        return

    def _save_comment(self, caller):
        # get ingame time
        date = custom_gametime(absolute=True)
        year, month, week, day, hour, min, sec = date
        month = month + 1
        dayofmonth = (week * 7) + day + 1
        # create thread_desc
        date_str = f"{year:02}-{month:02}-{dayofmonth:02} {hour:02}:{min:02}:{sec:02}"
        self.comment.db.date = date_str
        self.comment.db.last_edited = date_str
        self.thread.db.last_updated = date_str
        # add to Forum Thread list.
        self.thread.db.comments.append(self.comment)
        return


### "edit" Command to edit a Forum thread
class CmdChange(MuxCommand):
    """
    Edits a forum thread or comment

    Usage:
        change[/edit] <#dbref of thread> [= <subject>][;;<message>]
        change[/edit] <#dbref of comment> [= <subject>][;;<message>]

    This lets you change a Forum thread or comment by yourself with the given
    <#dbref>. If you add the /edit switch the editor will open to edit the
    already written message and the <message> on the commandline will be
    ignored. Otherwise it will completely replace the old text.

    If you only provide a <#dbref> to a thread or comment, the editor will open
    and you can change it's message without changing the subject.
    If you provide a subject it will change the subject on your comment and
    open the editor to edit the message.

    You can also supply only a message when using [= ;;<message>] and leave the
    subject as it is. But if you don't specify a message, even if you provide a
    subject, the editor will open. To change a message completely from command
    line you have to specify the the full command with <#dbref>, <subject> and
    <message> like this:

        change #453 = My New Subject;;And another new message

    So you see the right side of the equal sign is split at the two semicolons
    ";;". But you can also send a message while leaving the <subject> untouched
    like this:

        change #453 = ;;New message without changing the subject.

    If you specify the /edit switch in your command the editor will open in any
    case and ignore the comment message, but the subject is still changed if
    provided.
    """

    key = "change"
    switch_options = ("edit",)
    locks = "cmd:perm(Player);"
    help_category = "Forum"

    def func(self):
        "This edits the forum thread"

        caller = self.caller

        # set for _edit_thread() output
        self.create = False

        if not self.args:
            # no argument (target) given. Don't launch missiles
            err = (
                    "|RError:|n This command needs at least a <#dbref> of a"
                    " thread. Use |c'help edit'|n for help"
            )
            caller.msg(wrap(err))
            return
        try:
            self.lhs, self.rhs = self.args.split("=", 1)
            self.lhs = self.lhs.strip()
            self.rhs = self.rhs.strip()
        except ValueError:
            # we have one argument
            self.lhs = self.args.strip()
            self.rhs = ""

        ref = dbref(self.lhs)
        if ref is None:
            # can't parse arguments
            err = (
                    "|RError:|n Couldn't parse arguments."
                    " This command needs at least a <#dbref> of a"
                    " thread you wrote yourself. Use |c'help edit'|n"
                    " for help."
            )
            caller.msg(wrap(err))
            return
        self.thread = search_object(f"#{ref}",
                                    candidates=self.obj.db.threads,
                                    typeclass="ForumThread").first()
        if self.thread and self.thread is not None:
            if self.thread.db.archived:
                caller.msg(wrap(
                    f"Thread |w({self.thread.dbref})|n from |Y"
                    f"{self.thread.db.sender}|n -"
                    f" |M{self.thread.db.subject}|n -"
                    f" |C{self.thread.db.date}|n is |RLOCKED|n (archived)."
                    f" You can't add or edit comments."
                ))
                return
            if (self.thread.db.sender_id == caller.id
                    or self.obj.access(caller, "control")):
                caller.msg(wrap(
                    f"Processing thread |w({self.thread.dbref})|n from |Y"
                    f"{self.thread.db.sender}|n -"
                    f" |M{self.thread.db.subject}|n -"
                    f" Date: |C{self.thread.db.date}|n."
                ))
                # Split self rhs in subject and message if possible
                try:
                    subject, message = self.rhs.split(";;", 1)
                    subject = subject.strip()
                    message = message.strip()
                except ValueError:
                    if self.rhs.startswith(";;"):
                        message = self.rhs.replace(";;", "")
                        message = message.strip()
                        subject = ""
                    else:
                        subject = self.rhs.strip()
                        message = ""

                ## Edit and save
                if "edit" in self.switches:
                    if subject:
                        self.thread.db.subject = subject
                    if message:
                        self.thread.db.message = message
                    self.thread.db.seen = []
                    _edit_thread(self, caller)
                    return
                elif not message:
                    if subject:
                        self.thread.db.subject = subject
                    self.thread.db.seen = []
                    _edit_thread(self, caller)
                    return
                else:
                    self.thread.db.subject = subject
                    self.thread.db.message = message
                    self.thread.db.seen = []
                self._save_thread(caller)
                caller.msg(wrap(f"Thread |w({self.thread.dbref})|n updated!"))
                return
            else:
                caller.msg(wrap(
                    f"|RError:|n You don't have permission to"
                    f" edit a Thread from |Y{self.thread.db.sender}|n."))
                return
        else:
            self.comment = search_object(f"#{ref}",
                                         typeclass=ForumComment).first()
            if not self.comment:
                caller.msg(wrap(
                    f"|RError:|n Didn't find any thread or comment with"
                    f" #dbref |w({self.args.strip()})|n. Maybe a typo?"))
                return

            self.thread = self.comment.db.thread
            if not self.thread:
                caller.msg(wrap(
                    "|RError: Comment without thread! Please inform Admin."
                ))
                return
            elif self.comment.db.thread not in self.obj.db.threads:
                caller.msg(wrap(
                    "|RError: You are trying to edit a comment from a"
                    " different Forum Room. This is |Rnot permitted|n."
                ))
                return
            if self.thread.db.archived:
                caller.msg(wrap(
                    f"Thread |w({self.thread.dbref})|n from |Y"
                    f"{self.thread.db.sender}|n -"
                    f" |M{self.thread.db.subject}|n -"
                    f" |C{self.thread.db.date}|n is |RLOCKED|n (archived)."
                    f" You can't add or edit comments."
                ))
                return

            if (self.comment.db.sender_id == caller.id
                    or self.obj.access(caller, "control")):
                caller.msg(wrap(
                    f"Processing comment |w({self.comment.dbref})|n from |Y"
                    f"{self.comment.db.sender}|n -"
                    f" |M{self.comment.db.subject}|n -"
                    f" Date: |C{self.comment.db.date}|n to thread"
                    f" |w({self.thread.dbref})|n"
                    f" from |Y{self.comment.db.sender}"
                    f"|n - |M{self.thread.db.subject}|n from date |C"
                    f"{self.thread.db.date}|n."
                ))
                # Split self rhs in subject and message if possible
                try:
                    subject, message = self.rhs.split(";;", 1)
                    subject = subject.strip()
                    message = message.strip()
                except ValueError:
                    if self.rhs.startswith(";;"):
                        message = self.rhs.replace(";;", "")
                        message = message.strip()
                        subject = ""
                    else:
                        subject = self.rhs.strip()
                        message = ""

                ## Edit and save
                if "edit" in self.switches:
                    if subject:
                        self.comment.db.subject = subject
                    if message:
                        self.comment.db.message = message
                    self.comment.db.read = []
                    _edit_comment(self, caller)
                    return
                elif not message:
                    if subject:
                        self.comment.db.subject = subject
                    self.comment.db.read = []
                    _edit_comment(self, caller)
                    return
                else:
                    self.comment.db.subject = subject
                    self.comment.db.message = message
                    self.comment.db.read = []
                self._save_comment(caller)
                caller.msg(wrap(f"Comment |w({self.comment.dbref})|n updated!"))
                return
            else:
                caller.msg(wrap(
                    f"|RError:|n You don't have permission to"
                    f" edit a comment from |Y{self.comment.db.sender}|n."))
                return

    def _save_thread(self, caller):
        # get ingame time
        date = custom_gametime(absolute=True)
        year, month, week, day, hour, min, sec = date
        month = month + 1
        dayofmonth = (week * 7) + day + 1
        # create thread_desc
        date_str = f"{year:02}-{month:02}-{dayofmonth:02}"
        date_str += f" {hour:02}:{min:02}:{sec:02}"
        self.thread.db.last_edited = date_str
        return

    def _save_comment(self, caller):
        # get ingame time
        date = custom_gametime(absolute=True)
        year, month, week, day, hour, min, sec = date
        month = month + 1
        dayofmonth = (week * 7) + day + 1
        # create thread_desc
        date_str = f"{year:02}-{month:02}-{dayofmonth:02}"
        date_str += f" {hour:02}:{min:02}:{sec:02}"
        self.comment.db.last_edited = date_str
        self.thread.db.last_updated = date_str
        return


### "delete" Command to delete a Forum thread
class CmdDelete(MuxCommand):
    """
    Deletes a forum thread

    Usage:
        delete <#dbref of thread or comment>

    This lets you delete a Forum thread or comment by yourself with the given
    <#dbref>. Note that this will also delete all the comments by other users
    when deleting a thread. Consider archiving the thread with "archive
    <#dbref> = true". This will lock the thread without deleting it.
    """

    key = "delete"
    locks = "cmd:perm(Player);"
    help_category = "Forum"

    @interactive
    def _delete_thread(self, caller):
        text = wrap_para(
            f"|RDeleting:|n Thread |w({self.thread.dbref}|n -"
            f" |M'{self.thread.db.subject}'|n - Date:"
            f" |C{self.thread.db.date}|n. |RDANGER!|n Remember that"
            f" you'll also delete all containing comments. Think about"
            f" archiving this thread. This will also lock it without"
            f" deleting its comments.\n\n"
            f"Are you REALLY sure? [No]/Yes"
        )
        answer = yield (text)
        if answer.lower() in ["y", "yes"]:
            caller.msg(wrap("Thread |Rdeleted|n!"))
            self.thread.delete()
            threads = [thread for thread in self.obj.db.threads
                       if thread is not None]
            self.obj.db.threads = threads
            return
        else:
            caller.msg(wrap("|YDeletion canceled.|n"))
            return

    @interactive
    def _delete_comment(self, caller):
        self.thread = self.comment.db.thread
        if not self.thread:
            caller.msg(wrap(
                "|RError: Comment without thread! Please inform Admin."
            ))
            return
        if self.thread not in self.obj.db.threads:
            caller.msg(wrap(
                "|RError: You are trying to delete a comment from a different"
                " Forum Room. This is |Rnot permitted|n."
            ))
            return
        text = wrap_para(
            f"|RDeleting:|n Comment |w({self.comment.dbref}|n -"
            f" |M'{self.comment.db.subject}'|n - Date:"
            f" |C{self.comment.db.date}|n.\n\n"
            f"Are you REALLY sure? [No]/Yes"
        )
        answer = yield (text)
        if answer.lower() in ["y", "yes"]:
            caller.msg(wrap("Comment |Rdeleted|n!"))
            self.comment.delete()
            comments = [comment for comment in
                        self.thread.db.comments if comment is not None]
            self.thread.db.comments = comments
            return
        else:
            caller.msg(wrap("|YDeletion canceled.|n"))
            return

    def func(self):
        "This deletes a forum thread"

        caller = self.caller

        if not self.args:
            # no argument (target) given. Don't launch missiles
            err = (
                    "|RError:|n This command <#dbref> of a comment or a"
                    " thread. Use |c'help delete'|n for help"
            )
            caller.msg(wrap(err))
            return

        # we have an argument, search target
        if dbref(self.args.strip()) is None:
            caller.msg(wrap(
                "Couldn't parse arguments. You need to provide a <#dbref> of a"
                " thread or comment by yourself."
                " Type |c'help delete thread'|n for help."
            ))
            return
        else:
            self.thread = search_object(f"{self.args.strip()}",
                                        candidates=self.obj.db.threads,
                                        typeclass=ForumThread).first()
            if self.thread and self.thread is not None:
                if (self.obj.access(caller, "control")
                        or (self.thread.db.sender_id == caller.id)):
                    # Delete Thread
                    self._delete_thread(caller)
                    return
                else:
                    caller.msg(wrap(
                        f"|RError:|n You don't have permission to"
                        f" delete a Thread from |Y{self.thread.db.sender}|n."))
                    return
            else:
                self.comment = search_object(f"{self.args.strip()}",
                                             typeclass=ForumComment).first()
                if self.comment and self.comment is not None:
                    if (self.obj.access(caller, "control")
                            or (self.comment.db.sender_id == caller.id)):
                        # Delete ForumComment
                        self._delete_comment(caller)
                        return
                    else:
                        caller.msg(wrap(
                            f"|RError:|n You don't have permission to"
                            f" delete a comment from"
                            f" |Y{self.comment.db.sender}|n."))
                        return
                else:
                    caller.msg(wrap(
                        f"|RError:|n Didn't find any thread or comment with"
                        f" #dbref |w({self.args.strip()})|n. Maybe a typo?"))
                    return
        return


### "archive" Command to archive a Forum thread
class CmdArchive(MuxCommand):
    """
    (Un)Archives a forum thread

    Usage:
        archive <#dbref of thread> = <true||false>

    This lets you (un)archive a Forum thread by yourself with the given
    <#dbref>. This will lock the Forum thread without deleting its comments.
    It's not possible to add further comments to the thread if it's archived.
    You can also un-archive an thread by specifying "false" after the equal
    sign instead of "true" to archive it.
    """

    key = "archive"
    locks = "cmd:perm(Player);"
    help_category = "Forum"

    def func(self):
        "This (un)archives a forum thread"

        caller = self.caller

        if not self.args:
            # no argument (target) given. Don't launch missiles
            err = (
                    "|RError:|n This command needs at least a <#dbref> of a"
                    " thread by yourself and 'true' or 'false' after an equal"
                    "sign. Use |c'help archive'|n for help."
            )
            caller.msg(wrap(err))
            return
        try:
            self.lhs, self.rhs = self.args.split("=", 1)
            self.lhs = self.lhs.strip()
            self.rhs = self.rhs.strip()
        except ValueError:
            # no argument (target) given. Don't launch missiles
            err = (
                    "|RError:|n This command needs at least a <#dbref> of a"
                    " thread by yourself and 'true' or 'false' after an equal"
                    "sign. Use |c'help archive'|n for help."
            )
            caller.msg(wrap(err))
            return

        ref = dbref(self.lhs.strip())
        if ref is None:
            # can't parse arguments
            err = (
                    "|RError:|n This command needs at least a <#dbref> of a"
                    " thread by yourself and 'true' or 'false' after an equal"
                    "sign. Use |c'help archive'|n for help."
            )
            caller.msg(wrap(err))
            return
        if self.rhs.strip().lower() not in ["true", "false"]:
            # can't parse arguments
            err = (
                    "|RError:|n This command needs at least a <#dbref> of a"
                    " thread by yourself and 'true' or 'false' after an equal"
                    "sign. Use |c'help archive'|n for help."
            )
            caller.msg(wrap(err))
            return
        self.thread = search_object(f"#{ref}",
                                    candidates=self.obj.db.threads,
                                    typeclass="ForumThread").first()
        if not self.thread:
            err = (
                    f"|RError:|n Couldn't find thread with dbref"
                    f" |w'{self.lhs.strip()}'|n."
                    f" This command needs at least a <#dbref> of a"
                    f" thread you wrote yourself. Use |c'help archive'|n"
                    f" for help"
            )
            caller.msg(wrap(err))
            return
        if (self.thread.db.sender_id == caller.id
                or self.obj.access(caller, "control")):
            caller.msg(wrap(
                f"Processing thread |w({self.thread.dbref})|n from |Y"
                f"{self.thread.db.sender}|n - |M{self.thread.db.subject}|n -"
                f" Date: |C{self.thread.db.date}|n."
            ))
            if self.rhs.strip().lower() in ["true"]:
                self.thread.db.archived = True
            else:
                self.thread.db.archived = False

            if self.thread.db.archived:
                caller.msg(wrap(
                    f"Thread |w({self.thread.dbref}|n |RLOCKED|n"
                    f" |Y(archived)|n."
                ))
                return
            else:
                caller.msg(wrap(
                    f"Thread |w({self.thread.dbref}|n |GUNLOCKED|n"
                    f" |Y(unarchived)|n."
                ))
                return
        else:
            caller.msg(wrap(
                f"|RError:|n You don't have permission to toggle the Archive"
                f" bit on a Forum Thread of |Y{self.thread.db.sender}|n."
            ))


### "show" Command to show single Forum thread with comments
class CmdShow(MuxCommand):
    """
    Shows a complete thread with all comments or a single message from a thread
    with the given <#dbref>.

    Usage:
        show <#dbref of thread or message>

    Will show you a whole thread with comments or a single message. You can
    also show archived threads.

    *NOTE:* Despite having seen a thread with this command, the '(unseen)' tag
    won't be removed. You have to explicitly 'unfollow <#dbref>' to get rid
    of it or use 'follow <#dbref>' to explicitly follow it. You have to use one
    of these two commands to get rid of the '(unseen)' tag.
    """

    key = "show"
    locks = "cmd:perm(Player);"
    help_category = "Forum"

    def func(self):
        "This shows a forum thread"

        caller = self.caller
        if not caller.account or caller.account is None:
            caller.msg(wrap(
                f"|RError: No account for caller |Y{caller.key}|n found!"
                f" Please contact Admin."
            ))
            return
        else:
            account = caller.account

        ref = dbref(self.args.strip())
        if ref is None:
            caller.msg(wrap(
                "|RError:|n Couldn't parse arguments. The |c'show <#dbref>'"
                "|n is used with a <#dbref> of a thread and nothing else."
                " Type |c'help show'|n for help."
            ))
            return
        self.thread = search_object(f"#{ref}",
                                    candidates=self.obj.db.threads,
                                    typeclass=ForumThread).first()

        if self.thread and self.thread is not None:
            line1 = f"## |YThread|n |w({self.thread.dbref})|n from"
            line1 += f" |Y{self.thread.db.sender}|n"
            line1 += f" |M'{self.thread.db.subject}'|n"
            if self.thread.db.archived:
                line1 += " |R(LOCKED)|n"
            for comment in self.thread.db.comments:
                if ((account.key in self.thread.db.follows
                        or self.thread.db.pinned)
                        and account.key not in comment.db.read):
                    line1 += " |G(unread)|n"
                    break
            if (account.key in self.thread.db.follows
                    and not self.thread.db.pinned):
                line1 += " |b(followed)|n"
            if self.thread.db.pinned:
                line1 += " |b(PINNED)|n"
            line1 = wrap(line1)
            line2 = f"## Date: |C{self.thread.db.date}|n"
            line2 += f" Last updated: |C{self.thread.db.last_updated}|n|/"
            line2 = wrap(line2)
            message = wrap_para(self.thread.db.message, indent=4)
            output = f"{line1}|/{line2}{message}"

            filtered_comments = [comment for comment in self.thread.db.comments
                                 if comment is not None]
            comments = sorted(filtered_comments, reverse=False)
            self.thread.db.comments = comments
            text = ""
            if not comments:
                text += "|/|B" + "=" * _WIDTH + "|n|/"
                text += "## No comments.|/"
                text += "|B" + "=" * _WIDTH + "|n"
            else:
                text += "|/|B" + "=" * _WIDTH + "|n|/"
                comment_num = 0
                for comment in comments:
                    line1 = f"|w({comment.dbref})|n - |Y{comment.db.sender}|n"
                    line1 += f" |M'{comment.db.subject}'|n"
                    if comment.db.read is not None:
                        if (account.key not in comment.db.read
                                and (account.key in self.thread.db.follows
                                     or self.thread.db.pinned)):
                            line1 += " |G(unread)|n"
                            comment.db.read.append(account.key)
                            comment.db.read = list(set(comment.db.read))
                    line1 = wrap(line1)
                    line2 = f"Date: |C{comment.db.date}|n -"
                    line2 += f" Last edited: |C{comment.db.last_edited}|n|/"
                    line2 = wrap(line2)
                    message = wrap_para(comment.db.message, indent=4)
                    text += f"{line1}|/{line2}{message}"
                    comment_num += 1
                    if comment_num < len(comments):
                        text += "\n\n"
                text += "|/|B" + "=" * _WIDTH + "|n"
            text = output + text
            text = text.replace("|/", "\n")
            if caller.db.disable_page is False:
                evmore.msg(caller, text=text)
            else:
                caller.msg(text)
            return
        else:
            self.comment = search_object(f"#{ref}",
                                        typeclass=ForumComment).first()
            if not self.comment or self.comment is None:
                caller.msg(wrap(
                    f"|RError:|n Couldn't find thread or comment with #dbref"
                    f" |w({self.args.strip()})|n. Maybe a typo? Type |c'help"
                    f" show'|n for help."
                ))
                return
            if self.comment.db.thread not in self.obj.db.threads:
                caller.msg(wrap(
                    f"|RError: You are trying to show comment"
                    f" |w({self.comment.dbref})|n which is part of a different"
                    f" Forum. This is |Rnot allowed!|n"
                ))
                return

            self.thread = self.comment.db.thread

            text = (
                f"|B" + "=" * _WIDTH + "|n|/"
                f"## |w({self.thread.dbref})|n |Y{self.thread.db.sender}|n -"
                f" |M'{self.thread.db.subject}'|n"
            )
            if account.key not in self.thread.db.seen:
                text += " |Y(unseen)|n"
            if account.key not in self.comment.db.read:
                text += " |G(unread)|n"
            if (account.key in self.thread.db.follows
                    and not self.thread.db.pinned):
                text += " |b(followed)|n"
            if self.thread.db.pinned:
                text += " |b(PINNED)|n"
            text += "|/" + wrap(
                f"## Date: |C{self.thread.db.date}|n - Last updated:"
                f" |C{self.thread.db.last_updated}|n"
            )
            if self.thread.db.last_edited is not None:
                text += "|/" + wrap(
                    f"## Last edited: |C{self.thread.db.last_edited}|n"
                )
            text += f"|/|B" + "=" * _WIDTH + "|n|/"
            text += wrap(f"Comment: |w({self.comment.dbref})|n"
                         f" |Y{self.comment.db.sender}|n -"
                         f" |M'{self.comment.db.subject}'|n"
                         )
            text += f"|/{wrap_para(self.comment.db.message, indent=4)}"
            text += f"|/|B" + "=" * _WIDTH + "|n|/"
            caller.msg(text)
            return


### "archived" Command to show archived Forum thread
class CmdArchived(MuxCommand):
    """
    Shows archived threads

    Usage:
        archived

    Will show you all archived threads. These are locked and you can't add
    comments to them anymore.
    """

    key = "archived"
    locks = "cmd:perm(Player);"
    help_category = "Forum"

    def func(self):
        "This (un)archives a forum thread"

        caller = self.caller

        text = "|cArchived threads:|n|/"
        text += "|B" + "=" * _WIDTH + "|n|/"
        filtered_threads = [thread for thread in self.obj.db.threads
                            if thread is not None
                            and thread.db.archived]
        if filtered_threads:
            sorted_threads = sorted(filtered_threads, reverse=True)
            thread_num = 0
            for thread in sorted_threads:
                text += self._return_thread(thread)
                thread_num += 1
                if thread_num < len(sorted_threads):
                    text += "\n\n"
        else:
            text += "## No archived Threads."
        text += "|/|B" + "=" * _WIDTH + "|n"
        # Output
        text = text.replace("|/", "\n")
        if caller.db.disable_page is False:
            evmore.msg(caller, text=text)
        else:
            caller.msg(text)

    def _return_thread(self, thread):
        text = wrap(
            f"## |w({thread.dbref})|n |Y{thread.db.sender}|n -"
            f" |M'{thread.db.subject}'|n - |R(LOCKED)|n"
        )
        text += "|/" + wrap(
            f"## Date: |C{thread.db.date}|n - Last updated:"
            f" |C{thread.db.last_updated}|n"
        )
        #if thread.db.last_edited is not None:
        #    text += "|/" + wrap(
        #        f"## Last edited: |C{thread.db.last_edited}|n"
        #    )
        #text += "|/" + wrap_para(thread.db.message, indent=4)
        return text


### "seen" Command to mark new threads as seen
class CmdSeen(MuxCommand):
    """
    Marks all new threads as "seen"

    Usage:
        seen

    Will mark all new threads which you could possibly follow as seen, so they
    are no longer shown in the thread list when you execute the "look" command
    unless you either follow them or they are pinned.
    """

    key = "seen"
    locks = "cmd:perm(Player);"
    help_category = "Forum"

    def func(self):
        "This marks all threads as seen"
        caller = self.caller

        if self.args:
            caller.msg(wrap(
                "|RError:|n This command doesn't take any arguments. Aborted."
            ))
            return

        caller = self.caller
        if not caller.account or caller.account is None:
            caller.msg(wrap(
                f"|RError: No account for caller |Y{caller.key}|n found!"
                f" Please contact Admin."
            ))
            return
        else:
            account = caller.account

        for thread in self.obj.db.threads:
            if thread.db.seen is None:
                thread.db.seen = []
            thread.db.seen = list(set(thread.db.seen))
            if account.key not in thread.db.seen:
                thread.db.seen.append(caller.account.key)
            pass
        caller.msg(wrap(
            "|YAll threads marked as seen.|n They won't show up in the thread"
            " list unless they are pinned or are followed by you manually."
        ))
        return


### "flollow" Command to follow a thread for new messages
class CmdFollow(MuxCommand):
    """
    Explicitly follows a given thread for updates. The '(unseen)' tag will be
    removed.

    Usage:
        follow <#dbref>

    Will show this thread in thread list when executing the "look" command and
    shows if updates are available. The '(unseen)' tag will be removed.
    """

    key = "follow"
    locks = "cmd:perm(Player);"
    help_category = "Forum"

    def func(self):
        "This follows a forum thread"

        caller = self.caller
        if not caller.account or caller.account is None:
            caller.msg(wrap(
                f"|RError: No account for caller |Y{caller.key}|n found!"
                f" Please contact Admin."
            ))
            return
        else:
            account = caller.account

        ref = dbref(self.args.strip())
        if ref is None:
            caller.msg(wrap(
                "|RError:|n Couldn't parse arguments. The |c'follow <#dbref>'"
                "|n command is used with a <#dbref> of a thread and nothing"
                " else. Type |c'help follow'|n for help."
            ))
            return
        self.thread = search_object(f"#{ref}",
                                    candidates=self.obj.db.threads,
                                    typeclass=ForumThread).first()
        if not self.thread:
            caller.msg(wrap(
                f"|RError:|n Couldn't find thread with #dbref |w("
                f"{self.args.strip()})|n. Maybe a typo? Type |c'help show'|n"
                f" for help."
            ))
            return

        if self.thread.db.archived:
            caller.msg(wrap(
                f"Thread |w({self.thread.dbref})|n from |Y"
                f"{self.thread.db.sender}|n -"
                f" |M{self.thread.db.subject}|n -"
                f" |C{self.thread.db.date}|n is |RLOCKED|n (archived)."
                f" You can't follow it anymore."
            ))
            return

        self.thread.db.follows = list(set(self.thread.db.follows))
        if account.key not in self.thread.db.follows:
            self.thread.db.follows.append(account.key)
        caller.msg(wrap(
            f"You now explicitly |Gfollow|n"
            f" Thread |w({self.thread.dbref})|n from |Y"
            f"{self.thread.db.sender}|n -"
            f" |M{self.thread.db.subject}|n -"
            f" |C{self.thread.db.date}|n. It will stay in the list of threads"
            f" when using the |c'look'|n command and updates will be shown."
        ))
        self.thread.db.seen.append(account.key)
        self.thread.db.seen = list(set(self.thread.db.seen))
        return


### "unfolllow" Command to unfollow thread
class CmdUnFollow(MuxCommand):
    """
    Explicitly unfollows a given thread with <#dbref>. The '(unseen)' tag will
    be removed.

    Usage:
        unfollow <#dbref>

    Will hide this thread from the list of threads when executing the "look"
    command in the Forum Room even if there are updates. This also removes the
    '(unseen)' tag. BE CAREFUL: It might be difficult to refind the thread once
    it's removed from the list.
    """

    key = "unfollow"
    locks = "cmd:perm(Player);"
    help_category = "Forum"

    def func(self):
        "This unfollows a forum thread"

        caller = self.caller
        if not caller.account or caller.account is None:
            caller.msg(wrap(
                f"|RError: No account for caller |Y{caller.key}|n found!"
                f" Please contact Admin."
            ))
            return
        else:
            account = caller.account

        ref = dbref(self.args.strip())
        if ref is None:
            caller.msg(wrap(
                "|RError:|n Couldn't parse arguments. The |c'unfollow"
                " <#dbref>'|n command is used with a <#dbref> of a thread and"
                " nothing else. Type |c'help unfollow'|n for help."
            ))
            return
        self.thread = search_object(f"#{ref}",
                                    candidates=self.obj.db.threads,
                                    typeclass=ForumThread).first()
        if not self.thread:
            caller.msg(wrap(
                f"|RError:|n Couldn't find thread with #dbref |w("
                f"{self.args.strip()})|n. Maybe a typo? Type |c'help unfollow'"
                f"|n for help."
            ))
            return

        if self.thread.db.archived:
            caller.msg(wrap(
                f"Thread |w({self.thread.dbref})|n from |Y"
                f"{self.thread.db.sender}|n -"
                f" |M{self.thread.db.subject}|n -"
                f" |C{self.thread.db.date}|n is |RLOCKED|n (archived)."
                f" You can't unfollow it anymore."
            ))
            return

        self.thread.db.follows = list(set(self.thread.db.follows))
        if account.key in self.thread.db.follows:
            self.thread.db.follows.remove(account.key)
        caller.msg(wrap(
            f"You explicitly |Cdon't follow|n "
            f" Thread |w({self.thread.dbref})|n from |Y"
            f"{self.thread.db.sender}|n -"
            f" |M{self.thread.db.subject}|n -"
            f" |C{self.thread.db.date}|n. No updates will"
            f" be shown. The thread will be removed from the threads list when"
            f" using the |c'look'|n command. No updates will be shown."
        ))
        self.thread.db.seen.append(account.key)
        self.thread.db.seen = list(set(self.thread.db.seen))
        return


### "list" Command to list threads
class CmdList(MuxCommand):
    """
    Shows a complete thread list without archived (locked) ones and without
    comments.

    Usage:
        list

    Will show you a list of all threads that are not archived without
    comments.
    """

    key = "list"
    locks = "cmd:perm(Player);"
    help_category = "Forum"

    def func(self):
        "This shows all active forum threads"

        caller = self.caller

        threads = [thread for thread in self.obj.db.threads
                   if thread is not None and not thread.db.archived]
        sorted_threads = sorted(threads, reverse=True)

        if sorted_threads:
            text = wrap("|cSorted thread list|n")
            text += "|/|B" + "=" * _WIDTH + "|n|/"
            text += self._return_threads(caller, sorted_threads)
            text += "|/|B" + "=" * _WIDTH + "|n"
        else:
            text = wrap("|cSorted thread list|n")
            text =+ "|/|B" + "=" * _WIDTH + "|n|/"
            text += "## No threads yet."
            text += "|/|B" + "=" * _WIDTH + "|n"
        text = text.replace("|/", "\n")
        if caller.db.disable_page is False:
            evmore.msg(caller, text=text)
        else:
            caller.msg(text)
        return

    def _return_threads(self, caller, threads):
        thread_num = 0
        text = ""
        for thread in threads:
            text += (
                f"## |w({thread.dbref})|n |Y{thread.db.sender}|n -"
                f" |M'{thread.db.subject}'|n"
            )
            if (caller.account.key not in thread.db.seen
                    and not thread.db.pinned):
                text += " |Y(unseen)|n"
            for comment in thread.db.comments:
                if not comment.db.read or comment.db.read is None:
                    comment.db.read = []
                if (caller.account.key not in comment.db.read
                        and (caller.account.key in thread.db.follows
                             or thread.db.pinned)):
                    text += " |G(unread)|n"
                    break
            if (caller.account.key in thread.db.follows
                    and not thread.db.pinned):
                text += " |b(followed)|n"
            if thread.db.pinned:
                text += " |b(PINNED)|n"
            text += "|/" + wrap(
                f"## Date: |C{thread.db.date}|n - Last updated:"
                f" |C{thread.db.last_updated}|n"
            )
            if thread.db.last_edited is not None:
                text += "|/" + wrap(
                    f"## Last edited: |C{thread.db.last_edited}|n"
                )
            thread_num += 1
            if thread_num < len(threads):
                text += "\n\n"
        #text += "|/" + wrap_para(thread.db.message, indent=4)
        return text


### "pin" Command to pin a thread to the top of the list
class CmdPin(MuxCommand):
    """
    Pins a given thread to the top of the list after a "look"

    Usage:
        pin <#dbref>

    Will pin this thread at the beginning of the thread list.
    """

    key = "pin"
    locks = "cmd:perm(Expert Builder);"
    help_category = "Forum"

    def func(self):
        "This pins a forum thread"

        caller = self.caller
        if not caller.account or caller.account is None:
            caller.msg(wrap(
                f"|RError: No account for caller |Y{caller.key}|n found!"
                f" Please contact Admin."
            ))
            return
        else:
            pass

        ref = dbref(self.args.strip())
        if ref is None:
            caller.msg(wrap(
                "|RError:|n Couldn't parse arguments. The |c'pin <#dbref>'"
                "|n command is used with a <#dbref> of a thread and nothing"
                " else. Type |c'help pin'|n for help."
            ))
            return
        self.thread = search_object(f"#{ref}",
                                    candidates=self.obj.db.threads,
                                    typeclass=ForumThread).first()
        if not self.thread:
            caller.msg(wrap(
                f"|RError:|n Couldn't find thread with #dbref |w("
                f"{self.args.strip()})|n. Maybe a typo? Type |c'help pin'|n"
                f" for help."
            ))
            return

        if self.thread.db.archived:
            caller.msg(wrap(
                f"Thread |w({self.thread.dbref})|n from |Y"
                f"{self.thread.db.sender}|n -"
                f" |M{self.thread.db.subject}|n -"
                f" |C{self.thread.db.date}|n is |RLOCKED|n (archived)."
                f" You can't pin it anymore."
            ))
            return

        caller.msg(wrap(
            f"You pinned Thread |w({self.thread.dbref})|n from |Y"
            f"{self.thread.db.sender}|n -"
            f" |M{self.thread.db.subject}|n -"
            f" |C{self.thread.db.date}|n to the top of the list."
        ))
        self.thread.db.pinned = True
        return


### "unpin" Command to unpin a thread so it's no longer shown at the top
class CmdUnPin(MuxCommand):
    """
    Unpins a given thread from the top of the list after a "look" command.

    Usage:
        unpin <#dbref>

    Will unpin this thread, so it won't be shown at the top of the list any
    longer.
    """

    key = "unpin"
    locks = "cmd:perm(Expert Builder);"
    help_category = "Forum"

    def func(self):
        "This unpins a forum thread"

        caller = self.caller
        if not caller.account or caller.account is None:
            caller.msg(wrap(
                f"|RError: No account for caller |Y{caller.key}|n found!"
                f" Please contact Admin."
            ))
            return
        else:
            pass

        ref = dbref(self.args.strip())
        if ref is None:
            caller.msg(wrap(
                "|RError:|n Couldn't parse arguments. The |c'unpin <#dbref>'"
                "|n command is used with a <#dbref> of a thread and nothing"
                " else. Type |c'help unpin'|n for help."
            ))
            return
        self.thread = search_object(f"#{ref}",
                                    candidates=self.obj.db.threads,
                                    typeclass=ForumThread).first()
        if not self.thread:
            caller.msg(wrap(
                f"|RError:|n Couldn't find thread with #dbref |w("
                f"{self.args.strip()})|n. Maybe a typo? Type |c'help unpin'|n"
                f" for help."
            ))
            return

        if self.thread.db.archived:
            caller.msg(wrap(
                f"Thread |w({self.thread.dbref})|n from |Y"
                f"{self.thread.db.sender}|n -"
                f" |M{self.thread.db.subject}|n -"
                f" |C{self.thread.db.date}|n is |RLOCKED|n (archived)."
                f" You can't unpin it anymore."
            ))
            return

        caller.msg(wrap(
            f"You unpinned Thread |w({self.thread.dbref})|n from |Y"
            f"{self.thread.db.sender}|n -"
            f" |M{self.thread.db.subject}|n -"
            f" |C{self.thread.db.date}|n. It won't be shown on the top of the"
            f" list any longer."
        ))
        self.thread.db.pinned = False
        return


#### Forum Command Set ####
class ForumCmdSet(CmdSet):
    """
    This is a CommandSet for a Forum Room
    """

    key = "forumcmdset"

    def at_cmdset_creation(self):
        "Called once, when the cmdset is first created"
        self.add(CmdAdd())
        self.add(CmdChange())
        self.add(CmdDelete())
        self.add(CmdArchive())
        self.add(CmdShow())
        self.add(CmdArchived())
        # self.add(CmdSeen())
        self.add(CmdFollow())
        self.add(CmdUnFollow())
        self.add(CmdList())
        self.add(CmdPin())
        self.add(CmdUnPin())
        return
