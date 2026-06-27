#### Imports ####
import evennia
from evennia import logger

from world.scripts import game_time_script
from world.scripts.day_night import create_day_and_night

# Make sure to import your own weatherscript and also run the 'creaet_weather()'
# function on it below
from world.scripts import weather_temperate
from world.objects.wastebin import _collect_waste
from world.scripts.mailscript import MailScript

#### Helper: creates the needed global scripts ####


def _create_global_scripts():
    """create all global scripts"""
    # create 'destroy_waste' scripts (00:00, 06:00, 12:00, 18:00)
    game_time_script.schedule(
        "destroy_waste", _collect_waste, repeat=True, hour=0, min=0, sec=1)
    game_time_script.schedule(
        "destroy_waste", _collect_waste, repeat=True, hour=6, min=0, sec=1)
    game_time_script.schedule(
        "destroy_waste", _collect_waste, repeat=True, hour=12, min=0, sec=1)
    game_time_script.schedule(
        "destroy_waste", _collect_waste, repeat=True, hour=18, min=0, sec=1)

    # Add your own weather script here
    weather_temperate.create_weather()

    # create day and night scripts
    create_day_and_night()

    logger.log_info("Global scripts CREATED!")

#### Helper: deletes all global scripts, except from prototypes ####


def _delete_global_scripts():
    """delete all global scripts, except from prototypes"""
    for script in evennia.GLOBAL_SCRIPTS.all():
        if (not script.attributes.has("prototype")
                and not isinstance(script, MailScript)):
            script.delete()
    logger.log_info("All global scripts DELETED!")

#### Helper: log all GLOBAL_SCRIPTS ####


def log_global_scripts():
    script_keys = []
    for script in evennia.GLOBAL_SCRIPTS.all():
        script_keys.append(script.key)
    logger.log_info(f"{script_keys}")

#### delete global scripts (except from prototypes) and recreate them ####


def recreate_global_scripts():
    # delete GLOBAL_SCRIPTS except from prototypes
    _delete_global_scripts()
    # create GLOBAL_SCRIPTS
    _create_global_scripts()
