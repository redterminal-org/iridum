"""
Mobile Script

This lets an object move between rooms in a random time period.
"""
import random

from evennia.server.signals import SIGNAL_EXIT_TRAVERSED

from world.typeclasses.scripts import Script
from world.utils.utils import wrap


class MobileScript(Script):
    """
    A MobileScript which makes creatures move randomly between rooms.
    """

    class_perm = {"create": "Beginner Builder",
                  "global_script": "False"}

    def at_script_creation(self):
        # run inheritated function:
        super().at_script_creation()

        # Set min_repeat and max_repeat interval
        if not self.db.min_repeat or self.db.min_repeat is None:
            self.db.min_repeat = 60 * 5
        if not self.db.max_repeat or self.db.max_repeat is None:
            self.db.max_repeat = 60 * 10

        # restart script with new duration
        duration = random.randint(self.db.min_repeat, self.db.max_repeat)
        self.start(interval=duration, start_delay=True)

        try:
            scripts = self.obj.scripts.all()
            mobilescript_count = 0
            for script in scripts:
                if script.is_typeclass("world.scripts.mobilescript.MobileScript"):
                    mobilescript_count += 1
            if mobilescript_count > 1:
                self.delete()
        except AttributeError:
            pass
        return

    def at_repeat(self):
        exits = self.obj.location.exits
        use_exit = random.choice(exits)
        can_leave = False
        exits.remove(use_exit)
        if use_exit.access(self.obj, "traverse"):
            use_exit.at_traverse(self.obj, use_exit.destination)
            SIGNAL_EXIT_TRAVERSED.send(sender=use_exit, traverser=self.obj)
            can_leave = True
        else:
            if use_exit.db.err_traverse:
                self.obj.msg(use_exit.db.err_traverse)
            else:
                use_exit.at_failed_traverse(self.obj)

        if can_leave is False:
            self.obj.location.msg_contents(wrap(
                f"{self.obj.key} tries to leave"
                f" the room through {use_exit.key},"
                f" but fails to escape."
            ))

        # restart script with new duration
        duration = random.randint(self.db.min_repeat, self.db.max_repeat)
        self.start(interval=duration)
        return

    def at_server_start(self):
        if self.obj.db.follow is not None:
            self.pause()
        else:
            self.start(interval=self.db.time_remaining)
