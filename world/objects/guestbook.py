#### Imports ####
from evennia import CmdSet, create_object, search_object, settings
from evennia.utils.utils import wrap

from world.typeclasses.objects import Object
from world.utils.gametime import custom_gametime
from world.utils import evmore

from commands.command import MuxCommand

_WIDTH = settings.DEFAULT_WIDTH


#### A Guestbook ####
class Guestbook(Object):
    """
    This typeclass describes a Guestbook, which can be signed,
    shown and own entries can be deleted. It uses the MuxCommand
    'guestbook' to interact with the Guestbook:

        'guestbook': To look at the guestbook
        'guestbook/sign = <text>': To sign the guestbook
        'guestbook/delete <nr>': To delete an entry (only made by
                                 signer)

    Each 'guestbook/sign' creates a new entry, which will be sorted
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
            new_obj_lockstring += f"get:id({id}) or pid({
                pid}) or perm(Expert Builder);"

        elif account is not None:
            pid = account.id

            new_obj_lockstring += "control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({
                pid}) or perm(Expert Builder);"
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

        # Add GuesbootCmdSet
        self.cmdset.add(GuestbookCmdSet, persistent=True)

    def return_appearance(self, looker):
        """
        Disables the output of things inside the Guestbook which
        would be the GuestbookEntries. We don't want to show these.
        """
        return self.set_appearance(looker, things="")


#### GuestbookEntry ####
class GuestbookEntry(Object):
    """
    A GuestbookEntry. It holds the signers name, the ingame date and
    the entered text.

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
        self.locks.add(
            "get:false();delete:perm(Expert Builder);edit:perm(Developer);")
        self.locks.add(
            "iscontainer:false();getfrom:false();getcontainer:false();")
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
class CmdGuestbook(MuxCommand):
    """
    Interacts with a Guestbook

    Usage:
       guestbook[/switch] [arguments]

    Switches:
       sign - signs the guestbook with the provided text
       delete - deletes an entry of yourself
    Examples:
       guestbook
       guestbook/sign Hello! I like this MUD.
       guestbook/delete 23

    'guestbook' without any switches and arguments shows it's
                entries.
    'guestbook/sign <text>' makes an entry for you with the given
                            text.
    'guestbook/delete <nr>' deletes the entry with the number 'nr'
                            if its by you.

    Guestbook entries are signed with your username and the recent
    ingame time. These will be shown by reading the guestbook.
    """

    key = "guestbook"
    switch_options = ("sign", "delete")
    locks = "cmd:all()"
    aliases = ["book"]
    help_category = "Things and Rooms"

    confirm = True  # set to False to always bypass confirmation
    default_confirm = "yes"  # what to assume if just pressing enter (yes/no)

    def func(self):
        """Implements the command."""

        caller = self.caller
        obj = self.obj
        args = self.args

        if len(self.switches) > 1:
            caller.msg(
                wrap(
                    f"|/Wrong number of switches. Please type |c'help guestbook'|n forhelp.",
                    width=_WIDTH,
                )
            )
            return
        if len(self.switches) == 0:
            unsorted_entries = search_object(
                "guestbookentry", typeclass=GuestbookEntry, candidates=obj.contents
            )
            # sort entries in reverse order
            if unsorted_entries:
                entries = sorted(unsorted_entries, reverse=True)
                # entries = sorted(unsorted_entries, reverse=True)
                entry_num = len(entries)
            else:
                entries = []

            # create output
            output = f"|c{obj.get_display_name(caller)} Entries|n|/"
            output += "|B" + "=" * _WIDTH + "|n|/"
            if not entries:
                output += "No entries yet.|/"
            else:
                for entry in entries:
                    output += f"({entry_num}): {entry.db.entry_desc}|n|/"
                    output += wrap(entry.db.text, width=_WIDTH, indent=4)
                    output += "|/"
                    entry_num -= 1
            output += "|B" + "=" * _WIDTH + "|n"
            if caller.db.disable_page is False:
                evmore.msg(
                    caller,
                    text=output,
                    exit_on_lastpage=True,
                )
            else:
                caller.msg(output)
            return
        if "sign" in self.switches and "delete" not in self.switches:
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

                entry = create_object(
                    typeclass=GuestbookEntry,
                    key="guestbookentry",
                    location=obj,
                    attributes=[
                        ("player", player),
                        ("player_dbref", caller.dbref),
                        ("entry_desc", desc),
                        ("date", date),
                        ("text", args),
                        ("get_err_msg", "You can't get that."),
                    ],
                )

                caller.location.msg_contents(
                    f"$You() signed the {obj.get_display_name(caller)}.",
                    from_obj=caller,
                )
                return
            else:
                caller.msg(
                    wrap(
                        f"Entry text missing. Usage: |c'guestbook/sign <text>'|n. For general help type |c'help guestbook'|n",
                        width=_WIDTH,
                    )
                )
                return
        elif "delete" in self.switches and "sign" not in self.switches:
            try:
                del_entry_num = int(args)
            except ValueError:
                text = """You have to give an entry number as argument. Usage:
|c'guestbook/delete <nr>'|n. Please type |c'help guestbook'|n for
general help."""
                caller.msg(text, width=_WIDTH)
                return
            unsorted_entries = search_object(
                "guestbookentry", typeclass=GuestbookEntry, candidates=obj.contents
            )
            # sort entries in reverse order
            if unsorted_entries:
                entries = sorted(unsorted_entries, reverse=False)
                entry_num = len(entries)
            else:
                entries = []
                caller.msg(
                    wrap(
                        f"No one has signed {
                            obj.get_display_name(caller)
                        } yet.|/So there are no entries to delete.",
                        width=_WIDTH,
                    )
                )
                return
            entry = entries[del_entry_num - 1]
            if (self.obj.access(caller, "edit") 
                    or entry.db.player_dbref == caller.dbref):
                entry.delete()
                caller.location.msg_contents(
                    f"$You() deleted entry '{del_entry_num}' from {
                        obj.get_display_name(caller)
                    }.",
                    from_obj=caller,
                )
                return
            else:
                caller.msg(
                    wrap(
                        f"Entry Number {
                            del_entry_num
                        } is not written by you, so you can't delete it!",
                        width=_WIDTH,
                    )
                )
                return
        else:
            caller.msg(
                wrap(
                    f"|RError:|n Unknown or conflicting switch(es) given."
                    f"Please type |c'help guestbook'|n for general help.",
                    width=_WIDTH,
                )
            )
        return


#### Guestbook Command Set ####
class GuestbookCmdSet(CmdSet):
    """
    This is a CommandSet for a Guestbook
    """

    key = "guestbookcmdset"

    def at_cmdset_creation(self):
        "Called once, when the cmdset is first created"
        self.add(CmdGuestbook())
