#### Imports ####
import inflect
import random

from evennia import settings, create_script, search_script, CmdSet
from evennia import signals
from evennia.utils import ansi

from world.typeclasses.objects import Object
from world.objects.testobjects import Flower
from world.utils.utils import wrap

from commands.command import Command

_INFLECT = inflect.engine()
_WIDTH = settings.DEFAULT_WIDTH

_GOBLIN_NAMES = {
        "male": ['Fruic', 'Wrakx', 'Arthur', 'Brolix', 'Grunt', 'Vuld', 'Irt',
                 'Gnarz', 'Krag', 'Larg'],
        "female": ['Griqa', 'Proisa', 'Flaxa', 'Bhyssa', 'Eenxi',
                   'Jeka', 'Sluna', 'Lexia', 'Truxi'],
}

#### Goblin Object ####
class Goblin(Object):
    """
    This typeclass describes a Goblin.
    """

    class_perm = {"create": "Beginner Builder"}

    @classmethod
    def get_default_lockstring(cls, account=None, caller=None, **kwargs):
        if caller is not None:
            id = caller.id
            pid = caller.account.id

            new_obj_lockstring = f"control:id({id}) or pid({pid}) or perm(Developer);"
            new_obj_lockstring += (
                f"attrcreate:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += (
                f"delete:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += (
                f"edit:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += (
                f"examine:id({id}) or pid({pid}) or perm(Beginner Builder);"
            )
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"

        elif account is not None:
            pid = account.id

            new_obj_lockstring = f"control:pid({pid}) or perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"delete:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"edit:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += f"examine:pid({pid}) or perm(Beginner Builder);"
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"

        else:
            new_obj_lockstring = f"control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:perm(Expert Builder);"
            new_obj_lockstring += f"delete:perm(Expert Builder);"
            new_obj_lockstring += f"edit:perm(Expert Builder);"
            new_obj_lockstring += f"get:false();"
            new_obj_lockstring += f"examine:perm(Beginner Builder);"
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"
        return new_obj_lockstring

    @classmethod
    def create(cls, key, account=None, caller=None, method="create", **kwargs):
        obj, errors = super().create(
            key, account=account, caller=caller, method=method, **kwargs
        )
        return obj, errors

    def after_spawn(self, account=None, caller=None, **kwargs):
        super().after_spawn(caller=caller)
        return

    def at_object_creation(self):
        "This is called only when object is first created"
        # add tag
        self.tags.add("creature", category="generic")

        if self.key == "Random Goblin":
            self.db.gender = random.choice(["male", "female"])
            self.key = random.choice(_GOBLIN_NAMES[self.db.gender])
            self.name = self.key
            self.aliases.add([self.db.key, self.get_display_name()])
            if self.db.gender == "female":
                self.attributes.add(
                    "get_err_msg",
                    wrap(
                       f"{self.key} fights with all her strength against your"
                       f" attempts to pick her up. She twists and squirms,"
                       f" squealing loudly until you give up."),
                    )
                self.attributes.add(
                    "desc",
                    wrap(
                         f"You see a goblin girl dressed in a burlap sack with"
                         f" feathers in her hair. She is laden with bags and"
                         f" pouches all around her. When she smiles, you can see"
                         f" some gaps in her teeth. Her name is '{self.key}'.")
                    )
            else:
                self.attributes.add(
                    "get_err_msg",
                    wrap(
                        f"{self.key} screams and struggles while you're trying to"
                        f" get him. It seems, he doesn't want to be taken, so"
                        f" you release the poor goblin.")
                    )
                self.attributes.add(
                    "desc",
                    wrap(
                        f"You see a green, little goblin with bad teeth and"
                        f" dressed with a loincloth and a head covering made of"
                        f" leather. His name is '{self.key}'.")
                    )

        script = create_script(
            "world.scripts.mobilescript.MobileScript",
            key="MobileScript",
            desc="Mobile Objects Script",
            persistent=True,
            interval=10,
            start_delay=True,
            repeats=0,
        )
        self.scripts.add(script, autostart=True)

        # Add Dynamic CmdSet
        self.cmdset.add(GoblinCmdSet, persistent=True)

        return

    def at_pre_object_receive(self, arriving_object,
                              source_location, **kwargs):
        try:
            move_type = kwargs["move_type"]
        except KeyError:
            move_type = "drop"
        if move_type == "give" and arriving_object.is_typeclass(Flower):
            return True
        if move_type == "give" and arriving_object.db.edible:
            return True
        source_location.location.msg_contents(wrap(
            f"{self.get_display_name()} doesn't want the"
            f" {arriving_object.get_display_name()} from $You()."),
            from_obj=source_location)
        return False

    def received(self, giver, obj, **kwargs):
        try:
            move_type = kwargs["move_type"]
        except KeyError:
            move_type = "drop"
        if move_type == "give" and obj.is_typeclass(Flower):
            if self.db.gender == "female":
                self.location.msg_contents(wrap(
                    f"{self.get_display_name()} smiles as $You() $conj(give)"
                    f" her $an({obj.get_display_name()})."
                ), from_obj=giver)
            else:
                self.location.msg_contents(wrap(
                    f"{self.get_display_name()} smiles as $You() $conj(give)"
                    f" him $an({obj.get_display_name()})."
                ), from_obj=giver)
            return True
        if move_type == "give" and obj.db.edible:
            if self.db.gender == "female":
                self.location.msg_contents(wrap(
                    f"{self.get_display_name()} jumps up and down with joy"
                    f" as $You() give her $an({obj.get_display_name()}), and"
                    f" eats it with loud smacking. She smiles at $You()"
                    f" gratefully."
                ), from_obj=giver)
            else:
                self.location.msg_contents(wrap(
                    f"{self.get_display_name()} jumps up and down with joy"
                    f" as $You() give him $an({obj.get_display_name()}), and"
                    f" eats it with loud smacking. She smiles at $You()"
                    f" gratefully."
                ), from_obj=giver)
            obj.delete()
            self.db.follow = giver
            mobilescript = search_script("MobileScript", obj=self, 
                typeclass="world.scripts.mobilescript.MobileScript").first()
            mobilescript.pause()
            return True
        return False

    def at_init(self):
        # Add signal to follow somebody
        signals.SIGNAL_EXIT_TRAVERSED.connect(self.follow_signal_handler)


    def get_display_name(self, looker=None, **kwargs):
        return f"{self.name} the Goblin"

    def get_numbered_name(self, count, looker, **kwargs):
        kwargs["no_article"] = True
        key = kwargs.get("key", self.get_display_name(looker))
        key = ansi.ANSIString(key)  # this is needed to allow inflection of colored names
        try:
            plural = _INFLECT.plural(key, count)
            plural = "{} {}".format(_INFLECT.number_to_words(count, threshold=12), plural)
        except IndexError:
            # this is raised by inflect if the input is not a proper noun
            plural = key
        singular = _INFLECT.an(key)
        if not self.aliases.get(plural, category=self.plural_category):
            # we need to wipe any old plurals/an/a in case key changed in the interrim
            self.aliases.clear(category=self.plural_category)
            self.aliases.add(plural, category=self.plural_category)
            # save the singular form as an alias here too so we can display "an egg" and also
            # look at 'an egg'.
            self.aliases.add(singular, category=self.plural_category)

        if kwargs.get("no_article") and count == 1:
            if kwargs.get("return_string"):
                return key
            return key, key

        if kwargs.get("return_string"):
            return singular if count == 1 else plural

        return singular, plural

    def follow_signal_handler(self, sender, traverser, **kwargs):
        if traverser == self.db.follow:
            if sender not in self.location.exits:
                self.db.follow = None
                script = search_script("MobileScript", obj=self,
                    typeclass="world.scripts.mobilescript.MobileScript").first()
                script.unpause()
            old_location = self.location
            can_leave = False
            if sender.access(self, "traverse") and traverser == self.db.follow:
                self.location.msg_contents(wrap(
                    f"{self.get_display_name()} follows {traverser.get_display_name()}"
                    f" the way to {sender.get_display_name()}"))
                self.move_to(sender, quiet=True)
                signals.SIGNAL_EXIT_TRAVERSED.send(sender=sender,
                                                   traverser=self)
                can_leave = True
            else:
                if sender.db.err_traverse:
                    self.location.msg_contents(sender.db.err_traverse)
                else:
                    sender.at_failed_traverse(self)

            if can_leave is False:
                self.location.msg_contents(wrap(
                    f"{self.get_display_name()} tries to leave"
                    f" the room through '{sender.get_display_name()}',"
                    f" but fails."
                ))
                self.db.follow = None
                mobilescript = search_script("MobileScript", obj=self,
                    typeclass="world.scripts.mobilescript.MobileScript").first()
                mobilescript.unpause()
                return

            self.location.msg_contents(wrap(
                f"{self.get_display_name()} follows {traverser.get_display_name()}"
                f" the way from {old_location.get_display_name()}"))
            return

### Command 'kick' to kick a goblin ###
class CmdKick(Command):
    """
    Kicks a goblin

    Usage:
        kick <Goblin Name>

    Give a goblin a fierce kick.
    """

    key = "kick"
    locks = "cmd:all();"
    help_category = "Creatures"

    def func(self):
        "This kicks the goblin"

        caller = self.caller

        caller.location.msg_contents(wrap(
            f"$You() $conj(give) {self.obj.get_display_name()} a fierce kick."
            f" {self.obj.get_display_name()} screams and squirms in pain."
            f" {self.obj.get_display_name()} grunts at $You() one last time"
            f" and then dissapears."
        ), from_obj=caller)
        script = search_script("MobileScript", obj=self.obj).first()
        self.obj.db.follow = None
        script.unpause()
        script.at_repeat()
        return

#### Goblin Command Set ####
class GoblinCmdSet(CmdSet):
    """
    This is a CommandSet for a goblin
    """

    key = "goblincmdset"

    def at_cmdset_creation(self):
        "Called once, when the cmdset is first created"
        obj = self.cmdsetobj
        # 'kick' dynamic command
        cmd = CmdKick(key=f"kick {obj.get_display_name()}",
                      aliases=[f"kick {obj.key}", "kick goblin"])
        self.add(cmd)
