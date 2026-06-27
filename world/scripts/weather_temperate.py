#### Imports ####
import random

import evennia
from evennia import logger
from evennia import DefaultScript, create_script

from world.utils import gametime
from .day_night import _day_change

# WEATHER: day/night, season, temperature and chances and min/max durations
# of weather conditions
WEATHER = {
    "day": {
        "summer": {
            "name": "summer day",
            "temperature": [23, 35],
            "desc": ["It's a warm summer day."],
            "chances": {
                "clear": {
                    "chance": 50,
                    "dur_min": 60 * 10,
                    "dur_max": 60 * 20,
                    "weather": ["The sun is shining."],
                },
                "rain": {
                    "chance": 10,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 7,
                    "weather": ["It's raining."],
                },
                "cloudy": {
                    "chance": 10,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 7,
                    "weather": ["There are some clouds in the sky."],
                },
                "overcast": {
                    "chance": 10,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 7,
                    "weather": ["It's overcast."],
                },
                "stormy": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 7,
                    "weather": ["It's a little stormy."],
                },
                "thunderstorm": {
                    "chance": 5,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 7,
                    "weather": ["There's a heat thunderstorm going on."],
                },
            },
        },
        "autumn": {
            "name": "autumn day",
            "temperature": [10, 20],
            "desc": ["It's a changeable autumn day."],
            "chances": {
                "clear": {
                    "chance": 10,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 10,
                    "weather": ["The sky is clear at the moment."],
                },
                "rain": {
                    "chance": 50,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 20,
                    "weather": ["It's raining."],
                },
                "hail": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["It's hailing."],
                },
                "cloudy": {
                    "chance": 20,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 10,
                    "weather": ["There are big clouds in the sky."],
                },
                "overcast": {
                    "chance": 30,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 10,
                    "weather": ["The sky is overcast."],
                },
                "stormy": {
                    "chance": 20,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["It's stormy and the wind is blowing heavily."],
                },
                "thunderstorm": {
                    "chance": 5,
                    "dur_min": 60 * 2,
                    "dur_max": 60 * 4,
                    "weather": ["A thunderstorm is raging."],
                },
            },
        },
        "winter": {
            "name": "winter day",
            "temperature": [-10, 5],
            "desc": ["It's a cold winters day."],
            "chances": {
                "clear": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["The weather is clear."],
                },
                "rain": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["It's raining."],
                },
                "hail": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 5,
                    "weather": ["It's hailing."],
                },
                "cloudy": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["There are some clouds in the sky."],
                },
                "overcast": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["The sky is overcast."],
                },
                "snowstorm": {
                    "chance": 20,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 7,
                    "weather": ["There's a snowstorm going on."],
                },
                "snow": {
                    "chance": 50,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 20,
                    "weather": ["It's snowing."],
                },
            },
        },
        "spring": {
            "name": "spring day",
            "temperature": [13, 23],
            "desc": ["It's a a cosy spring day."],
            "chances": {
                "clear": {
                    "chance": 50,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["The sun is shining."],
                },
                "rain": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["There's a light rain."],
                },
                "cloudy": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["There are some big clouds in the sky."],
                },
                "overcast": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["The sky is overcast."],
                },
            },
        },
    },
    "night": {
        "summer": {
            "name": "summer night",
            "temperature": [23, 30],
            "desc": ["It's a warm summer night."],
            "chances": {
                "clear": {
                    "chance": 50,
                    "dur_min": 60 * 10,
                    "dur_max": 60 * 20,
                    "weather": ["The sky is clear."],
                },
                "rain": {
                    "chance": 10,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 7,
                    "weather": ["It's raining."],
                },
                "cloudy": {
                    "chance": 10,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 7,
                    "weather": ["There are some clouds in the sky."],
                },
                "overcast": {
                    "chance": 10,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 7,
                    "weather": ["It's overcast."],
                },
                "stormy": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 7,
                    "weather": ["It's a little stormy."],
                },
                "thunderstorm": {
                    "chance": 5,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 7,
                    "weather": ["There's a heat thunderstorm going on."],
                },
            },
        },
        "autumn": {
            "name": "autumn night",
            "temperature": [10, 20],
            "desc": ["It's a changeable autumn night."],
            "chances": {
                "clear": {
                    "chance": 10,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 10,
                    "weather": ["The sky is clear at the moment."],
                },
                "rain": {
                    "chance": 50,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 20,
                    "weather": ["It's raining."],
                },
                "hail": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["It's hailing."],
                },
                "cloudy": {
                    "chance": 20,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 10,
                    "weather": ["There are big clouds in the sky."],
                },
                "overcast": {
                    "chance": 30,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 10,
                    "weather": ["The sky is overcast."],
                },
                "stormy": {
                    "chance": 20,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["It's stormy and the wind is blowing heavily."],
                },
                "thunderstorm": {
                    "chance": 5,
                    "dur_min": 60 * 2,
                    "dur_max": 60 * 4,
                    "weather": ["A thunderstorm is going on."],
                },
            },
        },
        "winter": {
            "name": "winter night",
            "temperature": [-10, 5],
            "desc": ["It's a cold winters night."],
            "chances": {
                "clear": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["The weather is clear."],
                },
                "rain": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["It's raining."],
                },
                "hail": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["It's hailing."],
                },
                "cloudy": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["There are some clouds in the sky."],
                },
                "overcast": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["The sky is overcast."],
                },
                "snowstorm": {
                    "chance": 20,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 7,
                    "weather": ["There's a snowstorm going on."],
                },
                "snow": {
                    "chance": 50,
                    "dur_min": 60 * 5,
                    "dur_max": 60 * 20,
                    "weather": ["It's snowing."],
                },
            },
        },
        "spring": {
            "name": "spring night",
            "temperature": [13, 23],
            "desc": ["It's a a nice spring night."],
            "chances": {
                "clear": {
                    "chance": 50,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["The sky is clear."],
                },
                "rain": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["There's a light rain."],
                },
                "cloudy": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["There are some big clouds in the sky."],
                },
                "overcast": {
                    "chance": 10,
                    "dur_min": 60 * 3,
                    "dur_max": 60 * 10,
                    "weather": ["The sky is overcast."],
                },
            },
        },
    },
}


#### WEATHER: script for 'temperate' climate ####
class Weather(DefaultScript):
    """
    This contains the global 'Weather" script, which sets all weather conditions for
    rooms with the '"temperate, category="climate"' tag.

    DON'T CREATE THIS SCRIPT BY YOURSELF, AS IT INTERFERES WITH THE REAL 'Weather'
    SCRIPT!

    This script is (re)created by the '@batchcode 02-update' and '@batchcode
    01-initialize' scripts and shouldn't be used elsewhere.

    But you can read the actual weather attributes from this scipt as readonly, but
    don't write to them!

    If you want to create another climate zone (eg. '"tropic", category="climate"')
    you can copy this script and change the WEATHER dictionary, and the
    'create_weather()' function accordingly.
    """

    class_perm = {"create": "Expert Builder",
                  "global_script": "Expert Builder"}

    def at_script_creation(self):
        # run inherited at_script_creation()
        super().at_script_creation()

        # Set WEATHER as script attribute
        self.db.conditions = WEATHER
        # get recent ingame time
        year, month, week, day, hour, min, sec = gametime.custom_gametime(
            absolute=True)
        self.db.season = gametime.get_season(month + 1)
        self.db.daytime = f"{'day' if (hour >= 6 and hour < 20) else 'night'}"

    def at_repeat(self, **kwargs):
        """
        repeated everytime the weather changes. The duration of the weather is
        dynamically set from the weather conditions.

        It sets the season, daytime ("night" or "day") and the current weather
        condition (self.db.current_weather) on itself.

        On the rooms with the tag 'self.db.climate, category="climate"' it sets
        temperature, weather_desc, moon_desc and daytime ("night"/"day").

        It also displays the new weather if the weather changes to the rooms
        with that tag.
        """
        # get recent ingame time again
        year, month, week, day, hour, min, sec = gametime.custom_gametime(
            absolute=True)
        self.db.season = gametime.get_season(month + 1)
        self.db.daytime = f"{'day' if (hour >= 6 and hour < 20) else 'night'}"

        moon = {
            0: "It's hard to see in the darkness of the new moon.",
            1: "The waxing moon is spending some light.",
            2: "The night is bright in the full moon.",
            3: "You can still see in the waning moon light.",
        }
        # get a weighted weather condition and duration
        condition, duration = self._get_weighted_weather_condition()
        self.db.current_weather = random.choice(condition["weather"])

        # get all rooms with a 'temperate:climate' tag condition
        weather_rooms = evennia.search_tag(self.db.climate, category="climate")
        # inform rooms of changing weather condition
        for room in weather_rooms:
            season = random.choice(
                self.db.conditions[self.db.daytime][self.db.season]["desc"]
            )
            weather = self.db.current_weather
            # The Temperature is created by the day_night scriot
            room.db.temperature = self.db.temperature
            room.db.weather_desc = (
                f"{season} {weather}|/Temperature: |Y{self.db.temperature}°C|n."
            )
            room.db.moon_desc = f"{moon.get(week)}"
            room.db.daytime = self.db.daytime

            # Check if I should output
            try:
                if kwargs["no_output"] == True:
                    pass
                else:
                    if room.db.current_weather != weather:
                        room.db.current_weather = weather
                        room.msg_contents(weather)
            except KeyError:
                if room.db.current_weather != weather:
                    room.db.current_weather = weather
                    room.msg_contents(weather)

        # restart script with new duration
        self.start(interval=duration)

    def _get_weighted_weather_condition(self):
        """
        Gets a random (weighted) weather condition and duration
        based on 'weather_condition_act'

        Returns
        -------
        str, int
            table: weather condition
            int: duration
        """
        weights = []
        # get conditions and weights for actual weather category
        conditions = {
            k: v
            for k, v in self.db.conditions[self.db.daytime][self.db.season][
                "chances"
            ].items()
        }

        for k, v in conditions.items():
            weights.append(v["chance"])

        # randomize condition based on weight and randomize duration
        condition = random.choices(list(conditions.keys()), weights, k=1)[0]
        condition = {k: v for k, v in conditions[condition].items()}
        duration = random.randint(condition["dur_min"], condition["dur_max"])

        return condition, duration


#### WEATHER: creates a Weather script for temperate climate #####
# Changes the weather over the day: rain, blue sky, whatever.... #
##################################################################
def create_weather():
    """
    Creates the 'Weather' script. Called by
    'world.utils.set_global_scripts.recreate_global_scripts()' on a '@batchcode
    02-update' to update the world or '@batchcode 01-initialize' to completely
    recreate the world to its initial state (which shouldn't be used).

    If you add another climate zone (eg. "tropic") remember to add this
    function to the 'world/utils/set_global_scripts.py' file from your own
    'Weather' script file.
    """

    script = create_script(
        # change to your scripts typeclass which is in a different file
        # for example "world.scripts.weather_tropical.Weather"
        "world.scripts.weather_temperate.Weather",
        # Change for example to "weather_tropical"
        key="weather_temperate",
        desc="Temperate Weather Script",  # Change eg. "Tropical Weather Script"
        persistent=True,
        interval=10,
        start_delay=True,
        repeats=-1,
    )

    # !!! Important: change "temperate" to "tropical" for example on both
    # !!! lines below. BUT DON'T CHANGE THE TAG CATEGORY, otherwise your script
    # !!! can't be found!
    script.db.climate = "temperate"
    script.tags.add("temperate", category="weatherscript")

    # calls weatherscript's at_repeat() function to update script
    # (without output)
    script.at_repeat(no_output=True)
    # get daytime/season temperature limits and make a random between these
    try:
        min_max_temperature = script.db.conditions[script.db.daytime][script.db.season][
            "temperature"
        ]
        temperature = random.randint(
            min_max_temperature[0], min_max_temperature[1])
        script.db.temperature = temperature
    except Exception as e:
        # Rename function name to your create_weather() function:
        # eg: 'world.scripts.weather_tropical.create_weather()'
        logger.log_warning(
            "Error in function 'world.scripts.weather_temperate.create_weather()'"
        )
        logger.log_warning("... Type: {type(e)}")
        logger.log_warning("... Msg: {e}")
    # run script.at_repeat() once again this time with output
    script.at_repeat()
