"""
This file provides the GamtimeScript. This script runs a callback function at a
given ingame time. But you shouldn't create a GametimeScript with the
'create_script()' function. Instead you should use the provided 'schedule()'
function, which is described below.
"""
#### Imports ####
from evennia import DefaultScript
from evennia.utils.create import create_script

from world.utils import gametime

#### Schedule: creates a gametime script to repeat at ingame time ####
# Args: Scriptname, callback func, repeat (true/false),              #
#       optional time units (sec, min, hour, ...)                    #
######################################################################


def schedule(name, callback, repeat=False, **kwargs):
    """
    Call the callback when the game time is up. Use this function instead of
    creating a GametimeScript directly.

    Args:
        - name (str): The name of the script to be created.
        - callback (function): The callback function that will be called. This
            must be a top-level function since the script will be persistent.
        - repeat (bool, optional): Should the callback be called regularly?
        - day, month, etc (str: int, ...): The time units to call the callback; should
            match the keys of 'world.utils.gametime.TIME_UNITS'.

    Returns:
        script (Script): The created script.

    Examples:
        - schedule("name_of_script", func, repeat=True, min=5, sec=0)
          Will call the 'func()' callback ever hour + 5 minutes
        - schedule("name_of_script", func, repeat=True, hour=2, min=30, sec=0)
          Will call the 'func()' callback next time it's at 02:30 o'clock
    Notes:
        This function will setup a script that will be called when the
        time corresponds to the game time.  If the game is stopped for
        more than a few seconds, the callback may be called with a
        slight delay. If `repeat` is set to True, the callback will be
        called again next time the game time matches the given time.
        The time is given in units as keyword arguments.

    """
    seconds = gametime.real_seconds_until(**kwargs)
    script = create_script(
        "world.scripts.game_time_script.GametimeScript",
        key=name,
        desc="A gametime script",
        interval=seconds,
        start_delay=True,
        persistent=True,
        repeats=-1 if repeat else 1,
    )
    script.db.callback = callback
    script.db.gametime = kwargs
    return script

#### Ingame Time Script (use `schedule` to create it ) ####


class GametimeScript(DefaultScript):
    """
    A GametimeScript script. If 'repeats=True it will repeat everytime
    the ingame time matches 'GametimeScript.db.gametime' and calls
    the callback function stored in 'GametimeScript.db.callback' when
    'GametimeScript.at_repeat()' is called.

    !!! DON'T CREATE A GAMETIMESCRIPT WITH THE 'create_script()' FUNCTION!! Use
    the provided 'schedule()' function instead, which is described blow!
    """
    class_perm = {"create": "Expert Builder",
                  "global_script": "Expert Builder"}

    def at_script_creation(self):
        """The script is created."""
        # run inherited at_script_creation()
        super().at_script_creation()

    def at_repeat(self):
        """Call the callback and reset interval."""

        callback = self.db.callback
        if callback:
            callback()

        seconds = gametime.real_seconds_until(**self.db.gametime)
        self.update(interval=seconds)

    def at_server_reload(self):
        """Update interval on a server reload"""
        seconds = gametime.real_seconds_until(**self.db.gametime)
        self.update(interval=seconds)
