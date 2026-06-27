"""
This creates the GametimeScript scripts for changing night and day by calling
the 'schedule' function with the '_day_change()' callback which is run at 06:00
and the '_night_change()' callback at 20:00. The times are all ingame times.

The scripts are (re)created with the 'create_day_and_night()' function.
"""
#### Imports ####

import random

import evennia
from evennia import search_script
from evennia.utils.search import search_script_tag

from world.utils import gametime
from world.scripts import game_time_script

# Callback that runs, when the sun rises (06:00)


def _day_change():
    """
    Announce the sun rising.
    """
    # get all rooms
    for room in evennia.search_tag("room", category="generic"):
        # Get absolute game time
        year, month, week, day, hour, min, sec = gametime.custom_gametime(
            absolute=True)
        # count starts with 0, so 1 must be added
        dayofmonth = (week * 7) + day + 1

        # announce new day
        room.msg_contents(f"|/It's |g{gametime.DAY_NAMES[day]}|n and |y{
                          hour:02}:{min:02}|n o'clock. The day begins.")
        if room.tags.has(category="climate"):
            room.msg_contents(f"It's getting lighter as the sun rises.")
        else:
            room.msg_contents(
                f"It's getting lighter outside as the sun rises.")

    # Get all scripts with category "weather"
    for script in search_script_tag(category="weatherscript"):
        # call weatherscript's at_repeat() function to update temperature
        script.at_repeat(no_output=True)
        # get daytime/season temperature limits and make a random between these
        try:
            min_max_temperature = script.db.conditions[script.db.daytime][script.db.season]["temperature"]
            temperature = random.randint(
                min_max_temperature[0], min_max_temperature[1])
            script.db.temperature = temperature
        except Exception as e:
            logger.log_warning(
                "Error in function 'world.scripts.day_night._day_change()'")
            logger.log_warning("... Type: {type(e)}")
            logger.log_warning("... Msg: {e}")
        script.at_repeat()

    return

# Callback that runs, when the sun sets (20:00)


def _night_change():
    """
    Announce the sun setting.
    """
    # get all rooms
    for room in evennia.search_tag("room", category="generic"):
        # Get absolute game time
        year, month, week, day, hour, min, sec = gametime.custom_gametime(
            absolute=True)
        # count starts with 0, so 1 must be added
        dayofmonth = (week * 7) + day + 1

        # announce the beginning of the night
        room.msg_contents(f"|/It's |g{gametime.DAY_NAMES[day]}|n and |y{
                          hour:02}:{min:02}|n o'clock. The night begins.")
        if room.tags.has(category="climate"):
            room.msg_contents(f"It's getting darker as the sun sets.")
        else:
            room.msg_contents(f"It's getting darker outside as the sun sets.")

    # Get all scripts with category "weather"
    for script in search_script_tag(category="weatherscript"):
        # call weatherscript's at_repeat() function to update temperature
        script.at_repeat(no_output=True)
        # get daytime/season temperature limits and make a random between these
        try:
            min_max_temperature = script.db.conditions[script.db.daytime][script.db.season]["temperature"]
            temperature = random.randint(
                min_max_temperature[0], min_max_temperature[1])
            script.db.temperature = temperature
        except Exception as e:
            logger.log_warning(
                "Error in function 'world.scripts.day_night._day_change()'")
            logger.log_warning("... Type: {type(e)}")
            logger.log_warning("... Msg: {e}")
        script.at_repeat()

    return

#### Day and Night ###################
# Announces if the sun sets or rises #
######################################


def create_day_and_night():
    # delete Scripts for sunrise (maybe there is more than one)
    for script in search_script("sunrise"):
        script.delete()
    # delete Scripts for sunset (maybe there is more than one)
    for script in search_script("sunset"):
        script.delete()
    # create Script for sun rise
    game_time_script.schedule("sunrise", _day_change,
                              repeat=True, hour=6, min=0, sec=1)
    # create Script for sun setting
    game_time_script.schedule("sunset", _night_change,
                              repeat=True, hour=20, min=0, sec=1)
