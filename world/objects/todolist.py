#### Imports ####
from evennia import CmdSet, create_object, search_object, settings

from world.typeclasses.objects import Object
from world.utils.gametime import custom_gametime
from world.utils.utils import wrap

from commands.command import MuxCommand
from world.utils import evmore

_STATES = ["todo", "canceled", "done"]
_WIDTH = settings.DEFAULT_WIDTH


#### A TodoList ####
class TodoList(Object):
    """
    This typeclass describes a TodoList, to which Entries can be added,
    shown and deleted. Also there can be made comments to each entry.
    Use 'help TODO' for help to this command.

    Some examples:

        'TODO': To list all active list entries
        'TODO/add <text>': Add a new TODO list item
        'TODO/addcomment <nr> = <text>': Add a comment with <text> to TODO list
                                         entry number <nr>

    Each 'TODO/add' creates a new entry, which will be sorted
    in reverse order on read.
    """

    class_perm = {"create": "Expert Builder"}

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
            new_obj_lockstring += f"get:id({id}) or pid({pid}) or perm(Expert Builder);"

        elif account is not None:
            pid = account.id

            new_obj_lockstring += "control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"edit:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"get:pid({pid}) or perm(Expert Builder);"

        else:
            new_obj_lockstring += "control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:perm(Expert Builder);"
            new_obj_lockstring += f"edit:perm(Expert Builder);"
            new_obj_lockstring += f"get:perm(Expert Builder);"
        return new_obj_lockstring

    def after_spawn(self, account=None, caller=None, **kwargs):
        super().after_spawn(caller=caller)

    def at_object_creation(self):
        "This is called only when object is first created"
        super().at_object_creation()
        # set some Object attributes
        self.db.desc = ""
        self.db.get_err_msg = ""

        self.db.maxref = 0

        # Add GuesbootCmdSet
        self.cmdset.add(TodoCmdSet, persistent=True)

    def return_appearance(self, looker):
        """
        Disables the output of things inside the Guestbook which
        would be the GuestbookEntries. We don't want to show these.
        """
        return self.set_appearance(looker, things="")


#### TodoEntry ####
class TodoEntry(Object):
    """
    A TodoEntry. It holds the signers name, the ingame date, the entry text
    and all comments.

    DON'T CREATE AN OBJECT FROM THIS TYPECLASS!!! It's only used in
    Guestbooks.
    """

    class_perm = {"create": "Developer"}

    def at_object_creation(self):
        "This is called only when the object is first created"
        super().at_object_creation()

        # set some locks
        self.locks.add("control:perm(Developer);")
        self.locks.add("attrcreate:perm(Developer);")
        self.locks.add("get:false();delete:perm(Expert Builder);edit:perm(Developer);")
        self.locks.add("iscontainer:false();getfrom:false();getcontainer:false();")
        self.locks.add("examine:perm(Expert Builder);")
        self.locks.add("teleport:false();teleport_here:false();view:false();")
        self.locks.add("puppet:false();traverse:false();")

    def return_appearance(self):
        return self.set_appearance(things="")

    def __lt__(self, other):
        return self.db.entry_ref < other.db.entry_ref

    def __gt__(self, other):
        return self.db.entry_ref > other.db.entry_ref


#### TodoCommentEntry ####
class TodoCommentEntry(Object):
    """
    A TodoCommentEntry. It holds the signers name, the ingame date the
    entered text and a reference to the TODO list entry

    DON'T CREATE AN OBJECT FROM THIS TYPECLASS!!! It's only used in
    Guestbooks.
    """

    class_perm = {"create": "Developer"}

    def at_object_creation(self):
        "This is called only when the object is first created"
        super().at_object_creation()

        # set some locks
        self.locks.add("control:perm(Developer);")
        self.locks.add("attrcreate:perm(Developer);")
        self.locks.add("get:false();delete:perm(Expert Builder);edit:perm(Developer);")
        self.locks.add("iscontainer:false();getfrom:false();getcontainer:false();")
        self.locks.add("examine:perm(Expert Builder);")
        self.locks.add("teleport:false();teleport_here:false();view:false();")
        self.locks.add("puppet:false();traverse:false();")

    def return_appearance(self):
        return self.set_appearance(things="")

    def __lt__(self, other):
        return self.db.entry_desc[:17] < other.db.entry_desc[:17]

    def __gt__(self, other):
        return self.db.entry_desc[:17] > other.db.entry_desc[:17]


#### Muxcommand: 'guestbook' ####
class CmdTodo(MuxCommand):
    """
    Interacts with a TODO List. The TODO command without any arguments will
    list all active TODO List items with status 'TODO' without its comments.

    Valid statuses: ["TODO", "CANCELED", "DONE"]

    Usage:
       TODO[/switches] [arguments]

    Switches:
       [num] - If you add a number to the 'TODO' command without switches,
               it will only show this entry with comments

       wc - 'With Comments' List entries with comments.
            Makes only sense with TODO alone or /all, /canceled or /done

       add <text> - adds an active TODO list item
       delete <num> - deletes an item of yourself
       change <num> = <status||percent> - change status of an entry
       all - lists ALL TODO list items with all statuses
       canceled - lists 'CANCELED' TODO list items
       done - lists 'DONE' TODO list items
       addcomment <num> = <text> - add comment to entry <num>
       delcomment <num> = <del_num> - delete comment <del_num> from entry <num>

    Examples:
       TODO 5
       TODO/wc
       TODO/add This is a TODO list item
       TODO/delete 23
       TODO/change 23 = DONE
       TODO/change 23 = 50%
       TODO/canceled
       TODO/done
       TODO/addcomment 23 = This is a good idea.
       TODO/delcomment 23 = 3


    All TODO list entries and comments are signed with your username and the
    recent ingame time. They can only be deleted by you.
    """

    key = "TODO"
    switch_options = (
        "add",
        "delete",
        "change",
        "all",
        "canceled",
        "done",
        "addcomment",
        "delcomment",
        "wc",
    )
    locks = "cmd:all()"
    aliases = ["TODO", "todo"]
    help_category = "Things and Rooms"

    confirm = True  # set to False to always bypass confirmation
    default_confirm = "yes"  # what to assume if just pressing enter (yes/no)

    def func(self):
        """Implements the command."""

        caller = self.caller
        obj = self.obj
        args = self.args

        # Check for 'with comments'
        if "wc" in self.switches:
            _WC = True
            self.switches.remove("wc")
        else:
            _WC = False

        if len(self.switches) > 1:
            caller.msg(
                wrap(
                    f"|/Wrong number of switches. Only 'wc' switch can be added"
                    f" to other switches. Please type |c'help TODO'|n"
                    f" for help.",
                    width=_WIDTH,
                )
            )
            return

        # Find exact entry Function

        def _find_entry(entry_num):
            nonlocal caller, obj
            entries = search_object(
                "todoentry", typeclass=TodoEntry, candidates=obj.contents
            )
            found_entry = None
            for entry in entries:
                if entry.db.entry_ref == entry_num:
                    found_entry = entry
                    break
            if found_entry is None:
                caller.msg(
                    wrap(f"No entry with number |w{entry_num}|n found.", width=_WIDTH)
                )
                return None
            return found_entry

        # output list of entries Function

        def _output_entry_list(status="TODO", num=None):
            nonlocal caller, obj, _WC
            # We have an entry number
            if num is not None:
                status = "ALL"
                _WC = True
                entry_string = "enrty"
                found_entry = None
            else:
                entry_string = "entries"
            unsorted_entries = search_object(
                "todoentry", typeclass=TodoEntry, candidates=obj.contents
            )
            filtered_entries = []

            for entry in unsorted_entries:
                if status.lower() != "all":
                    if entry.db.status.lower() != status.lower():
                        continue
                if num is not None:
                    if entry.db.entry_ref == num:
                        found_entry = entry
                        break
                filtered_entries.append(entry)
            # sort entries in reverse order
            if num is not None and found_entry is not None:
                entries = [found_entry]
            elif num is None and filtered_entries:
                entries = sorted(filtered_entries, reverse=True)
            else:
                entries = []

            # create output
            output = f"|c{obj.get_display_name(caller)} {entry_string}|n|/"
            output += "|B" + "=" * _WIDTH + "|n|/"
            if not entries:
                output += f"No {entry_string} found.|/"
            else:
                for entry in entries:
                    output += f"({entry.db.entry_ref}): |M{entry.db.entry_desc}|n"
                    if entry.db.status.upper() == "CANCELED":
                        status = "|RCANCELED|n"
                    elif entry.db.status.upper() == "DONE":
                        status = "|wDONE|n"
                    elif entry.db.status.upper() == "TODO":
                        status = "|GTODO|n"
                    else:
                        status = "|yunknown|n"
                    output += f" ({status} [{entry.db.percent}%])|/"
                    output += wrap(entry.db.text, width=_WIDTH, indent=4)
                    unsorted_comments = search_object(
                        "todocomment",
                        typeclass=TodoCommentEntry,
                        candidates=entry.contents,
                    )
                    if unsorted_comments:
                        comments = sorted(unsorted_comments, reverse=False)
                    else:
                        comments = []
                    if comments and _WC:
                        comment_num = 1
                        for comment in comments:
                            output += "|/"
                            output += (
                                wrap(
                                    f"({comment_num}): |C{comment.db.entry_desc}|n",
                                    width=_WIDTH,
                                    indent=4,
                                )
                                + "|/"
                            )
                            output += wrap(comment.db.text, width=_WIDTH, indent=8)
                            comment_num += 1
                    elif comments:
                        output += "|/" + wrap(
                            "|m- has comments|n", width=_WIDTH, indent=4
                        )
                    output += "|/"
            output += "|B" + "=" * _WIDTH + "|n"
            evmore.msg(
                caller,
                text=output,
                exit_on_lastpage=True,
                page=True
            )
            return

        # List ALL entries with ALL statuses (TODO, CANCELED, DONE)
        if "all" in self.switches:
            _output_entry_list(status="ALL")
            return

        # List all active TODO entries (status: TODO)
        if len(self.switches) == 0 and self.args == "":
            _output_entry_list(status="TODO")
            return

        # List all CANCELED entries (status: CANCELED)
        if "canceled" in self.switches:
            _output_entry_list(status="CANCELED")
            return

        # List all DONE entries (status: DONE)
        if "done" in self.switches:
            _output_entry_list(status="DONE")
            return

        # Show a single TODO list entry ('TODO <num>')
        if len(self.switches) == 0 and self.args:
            try:
                entry_num = int(self.args)
            except ValueError:
                err = (
                    "|RError:|n Argument has to be the entry number if you"
                    " want to show only one entry. Usage: |c'TODO [nr]'|n."
                    " Get help with |c'help TODO'|n."
                )
                caller.msg(wrap(err, width=_WIDTH))
                return
            _output_entry_list(num=entry_num)
            return

        # Add new TODO list item
        if "add" in self.switches:
            if args != "":
                # get ingame time
                date = custom_gametime(absolute=True)
                year, month, week, day, hour, min, sec = date
                month = month + 1
                dayofmonth = (week * 7) + day + 1
                # get character name
                player = caller.get_display_name(caller)
                # create entry_desc
                desc = f"{year:02}-{month:02}-{dayofmonth:02} {hour:02}:{min:02}:{
                    sec:02} - |Y{player}|n:"

                # Generate Entry Object
                entry = create_object(
                    typeclass=TodoEntry,
                    key="todoentry",
                    location=obj,
                    attributes=[
                        ("player", player),
                        ("player_dbref", caller.dbref),
                        ("entry_ref", obj.db.maxref + 1),
                        ("status", "TODO"),
                        ("percent", 0),
                        ("entry_desc", desc),
                        ("date", date),
                        ("text", args),
                        ("get_err_msg", "You can't get that."),
                    ],
                )

                caller.location.msg_contents(
                    wrap(
                        f"$You() added an entry to |G{obj.get_display_name(caller)}|n.",
                        width=_WIDTH,
                    ),
                    from_obj=caller,
                )
                obj.db.maxref += 1
                return
            else:
                caller.msg(
                    wrap(
                        "|RError:|n Entry text missing. Usage: |c'TODO/add"
                        " <text>'|n. For general help type |c'help TODO'|n",
                        width=_WIDTH,
                    )
                )
                return

        # Delete TODO list item ('TODO/delete <num>')
        if "delete" in self.switches:
            try:
                del_entry_num = int(args)
            except ValueError:
                text = """|RError:|n You have to give an entry number as 
                argument. Usage: |c'todo/delete <nr>'|n. Please type
                |c'help TODO'|n for general help."""
                caller.msg(wrap(text, width=_WIDTH))
                return

            found_entry = _find_entry(del_entry_num)
            if found_entry is None:
                return

            # Permision check if we're allowed to delete this Entry
            if (entry.db.player_dbref == caller.dbref) or obj.access(caller, "control"):
                entry.delete()
                caller.location.msg_contents(
                    wrap(
                        f"$You() deleted entry |w'{del_entry_num}'|n from |G{
                            obj.get_display_name(caller)
                        }|n.",
                        width=_WIDTH,
                    ),
                    from_obj=caller,
                )
                return
            else:
                err = (
                    f"|RPermission Error:|n Entry number |w'{del_entry_num}'|n wasn't"
                    f" written by you, so you can't delete it!"
                )
                caller.msg(wrap(err, width=_WIDTH))
                return

        # Change status of entry
        if "change" in self.switches:
            try:
                self.lhs, self.rhs = self.args.split("=", 1)
                entry_num = int(self.lhs)
                status = self.rhs
            except ValueError:
                text = """|RError:|n No valid entry number or status.
                    Usage: |c'todo/change <entry_num> = <STATUS||Percent%>'|n.
                    Please type |c'help TODO'|n for general help."""
                caller.msg(wrap(text, width=_WIDTH))
                return

            found_entry = _find_entry(entry_num)
            if found_entry is None:
                return

            # change percentage
            if "%" in status:
                try:
                    percent, _ = status.split("%", 1)
                    percent = int(percent)
                except ValueError:
                    caller.msg(
                        wrap(
                            "|RError:|n No valid percent integer found!"
                            " Usage: |c'TODO/change <num> = <num>%'|c if"
                            " you want to set the percentage of a TODO entry.",
                            width=_WIDTH,
                        )
                    )
                    return
                percent = percent if percent <= 100 else 100
                percent = percent if percent >= 0 else 0
                found_entry.db.percent = percent

                caller.location.msg_contents(
                    wrap(
                        f"$You() $conj(set) entry |w'{entry_num}'|n to"
                        f" |w'{percent}%'|n.",
                        width=_WIDTH,
                    ),
                    from_obj=caller,
                )
                return

            # change status
            elif status.lower().strip() in _STATES:
                string = status.lower().strip()
                caller.msg(f"'{string}'")
                found_entry.db.status = string
                if string == "canceled":
                    string = "|RCANCELED|n"
                elif string == "done":
                    string = "|wDONE|n"
                elif string == "todo":
                    string = "|GTODO|n"
                else:
                    string = "|yunknown|n"
                caller.location.msg_contents(
                    wrap(
                        f"$You() $conj(set) entry |w'{entry_num}'|n status"
                        f" to {string}.",
                        width=_WIDTH,
                    ),
                    from_obj=caller,
                )
            else:
                # No percent or known status
                caller.msg(
                    wrap(
                        "|RError:|n No valid status found!"
                        " Usage: |c'TODO/change <num> ="
                        " <STATUS||num%>|n if you want to set the status"
                        " of a TODO entry. Use |c'help TODO'|n for general"
                        " help.",
                        width=_WIDTH,
                    )
                )
                return
            return

        # Add comment to TODO list item ('TODO/addcomment <num> = <comment>')
        if "addcomment" in self.switches:
            try:
                self.lhs, self.rhs = self.args.split("=", 1)
                entry_num = int(self.lhs)
            except ValueError:
                err = (
                    "First argument has to be the entry number.|/"
                    "Usage: 'TODO/addcomment <nr> = <text>|/"
                    "Get help with |c'help TODO'|n.",
                )
                caller.msg(wrap(err, width=_WIDTH))
                return

            found_entry = _find_entry(entry_num)
            if found_entry is None:
                return

            # get ingame time
            date = custom_gametime(absolute=True)
            year, month, week, day, hour, min, sec = date
            month = month + 1
            dayofmonth = (week * 7) + day + 1
            # get character name
            player = caller.get_display_name(caller)
            # create entry_desc
            desc = f"{year:02}-{month:02}-{dayofmonth:02} {hour:02}:{min:02}:{
                sec:02} - |Y{player}|n:"

            # Generate Comment Object
            comment = create_object(
                typeclass=TodoCommentEntry,
                key="todocomment",
                location=found_entry,
                attributes=[
                    ("player", player),
                    ("player_dbref", caller.dbref),
                    ("entry_num", entry_num),
                    ("entry_desc", desc),
                    ("date", date),
                    ("text", self.rhs),
                    ("get_err_msg", "You can't get that."),
                ],
            )

            caller.location.msg_contents(
                wrap(
                    f"$You() added a comment to entry |w'{entry_num}'|n in {
                        obj.get_display_name(caller)
                    }.",
                    width=_WIDTH,
                ),
                from_obj=caller,
            )
            return

        # Delete comment from TODO list item ('TODO/delcomment <entry_num> = <comment_num>')
        if "delcomment" in self.switches:
            try:
                self.lhs, self.rhs = self.args.split("=", 1)
                entry_num = int(self.lhs)
                del_comment_num = int(self.rhs)
            except ValueError:
                text = """|RError:|n couldn't parse entry number or comment
                    number.
                    Usage: |c'todo/delcomment <entry_num> = <comment_num>'|n.
                    Please type |c'help TODO'|n for general help."""
                caller.msg(wrap(text, width=_WIDTH))
                return

            found_entry = _find_entry(entry_num)
            if found_entry is None:
                caller.msg(
                    wrap(
                        f"|RError:|n No entry with number |Y'{entry_num}|n found."
                        f" Please type |c'help TODO'|n for general help."
                    )
                )
                return

            unsorted_comments = search_object(
                "todocomment",
                typeclass=TodoCommentEntry,
                candidates=found_entry.contents,
            )
            comments = sorted(unsorted_comments, reverse=False)
            try:
                comment = comments[del_comment_num - 1]
            except IndexError:
                caller.msg(
                    wrap(
                        f"|RError:|n"
                        f" No comment number |w'{del_comment_num}|n found on"
                        f" entry |w'{entry_num}|n. Use |c'help TODO'|n"
                        f" for general help.",
                        width=_WIDTH,
                    )
                )
                return
            if (comment.db.player_dbref == caller.dbref) or obj.access(
                caller, "control"
            ):
                comment.delete()
                caller.location.msg_contents(
                    wrap(
                        f"$You() deleted comment number |w'{del_comment_num}'|n"
                        f" on entry |w'{entry_num}'|n in"
                        f" {obj.get_display_name(caller)}.",
                        width=_WIDTH,
                    ),
                    from_obj=caller,
                )
                return
            else:
                err = (
                    f"|RPermission Error:|n This comment wasn't"
                    f" written by you, so you can't delete it!"
                )
                caller.msg(wrap(err, width=_WIDTH))
                return
        else:
            caller.msg(
                wrap(
                    "|RError:|n Unknown switch(es) given."
                    " Please type |c'help TODO'|n"
                    " for general help.",
                    width=_WIDTH,
                )
            )
        return


#### Guestbook Command Set ####
class TodoCmdSet(CmdSet):
    """
    This is a CommandSet for a TODO List
    """

    key = "todocmdset"

    def at_cmdset_creation(self):
        "Called once, when the cmdset is first created"
        self.add(CmdTodo())
