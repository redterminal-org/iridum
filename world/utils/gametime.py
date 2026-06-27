
#### GameTime Documentation ####
"""
Custom gametime

Contrib - Griatch 2017, vlgeoff 2017

This implements the evennia.utils.gametime module but supporting
a custom calendar for your game world. It allows for scheduling
events to happen at given in-game times, taking this custom
calendar into account.

Usage:

Use as the normal gametime module, that is by importing and using the
helper functions in this module in your own code. The calendar can be
customized by adding the `TIME_UNITS` dictionary to your settings
file. This maps unit names to their length, expressed in the smallest
unit. Here's the default as an example:

    TIME_UNITS = {
        "sec": 1,
        "min": 60,
        "hr": 60 * 60,
        "hour": 60 * 60,
        "day": 60 * 60 * 24,
        "week": 60 * 60 * 24 * 7,
        "month": 60 * 60 * 24 * 7 * 4,
        "yr": 60 * 60 * 24 * 7 * 4 * 12,
        "year": 60 * 60 * 24 * 7 * 4 * 12, }

When using a custom calendar, these time unit names are used as kwargs to
the converter functions in this module.

"""

#### Imports ####
from django.conf import settings
from evennia.utils import gametime

EPOCH = "the era of Creation"

#### Date Units ####
DAY_NAMES = {
    0: "Moonday",
    1: "Windday",
    2: "Waterday",
    3: "Earthday",
    4: "Fireday",
    5: "Starday",
    6: "Sunday",
}

MONTH_NAMES = {
    0: "Japha",
    1: "Fermias",
    2: "Mikha",
    3: "Alphos",
    4: "Mielah",
    5: "Aniyah",
    6: "Paha",
    7: "Raches",
    8: "Sariel",
    9: "Hielaph",
    10: "Kiriel",
    11: "Zaram",
}

WEEK_NAMES = {
    0: "New Moon",
    1: "Second Quarter",
    2: "Full Moon",
    3: "Fourth Quarter",
}

#### TIME FACTOR for slowdown/speedup of realtime ####
TIMEFACTOR = settings.TIME_FACTOR

# These are the unit names understood by the scheduler.
# Each unit must be consistent and expressed in seconds.
UNITS = getattr(
    settings,
    "TIME_UNITS",
    {
        # default custom calendar
        "sec": 1,
        "min": 60,
        "hr": 60 * 60,
        "hour": 60 * 60,
        "day": 60 * 60 * 24,
        "week": 60 * 60 * 24 * 7,
        "month": 60 * 60 * 24 * 7 * 4,
        "yr": 60 * 60 * 24 * 7 * 4 * 12,
        "year": 60 * 60 * 24 * 7 * 4 * 12,
    },
)

# Function that returns the season based on month


def get_season(month):
    """
    Get ingame season from month

    Args:
        month (int): Number of month beginning with 1
    Returns:
        season (string): The season name as a lowercase string
    """
    if month in [12, 1, 2]:
        return "winter"
    if month in [3, 4, 5]:
        return "spring"
    if month in [6, 7, 8]:
        return "summer"
    return "autumn"

#### Helper function that divides seconds to divisors (UNITS) ####


def time_to_tuple(seconds, *divisors):
    """
    Helper function. Creates a tuple of even dividends given a range
    of divisors.

    Args:
        seconds (int): Number of seconds to format
        *divisors (int): a sequence of numbers of integer dividends. The
            number of seconds will be integer-divided by the first number in
            this sequence, the remainder will be divided with the second and
            so on.
    Returns:
        time (tuple): This tuple has length len(*args)+1, with the
            last element being the last remaining seconds not evenly
            divided by the supplied dividends.

    """
    results = []
    seconds = int(seconds)
    for divisor in divisors:
        results.append(seconds // divisor)
        seconds %= divisor
    results.append(seconds)
    return tuple(results)

#### Converts gametime to realtime seconds ####
# Args: sec, min, hour, day, week, year       #
# returns: realtime seconds                   #
###############################################


def gametime_to_realtime(format=False, **kwargs):
    """
    This method helps to figure out the real-world time it will take until an
    in-game time has passed. E.g. if an event should take place a month later
    in-game, you will be able to find the number of real-world seconds this
    corresponds to (hint: Interval events deal with real life seconds).

    Keyword Args:
        format (bool): Formatting the output.
        days, month etc (int): These are the names of time units that must
            match the `settings.TIME_UNITS` dict keys.

    Returns:
        time (float or tuple): The realtime difference or the same
            time split up into time units.

    Example:
         gametime_to_realtime(days=2) -> number of seconds in real life from
                        now after which 2 in-game days will have passed.

    """
    # Dynamically creates the list of units based on kwarg names and UNITs list
    rtime = 0
    for name, value in kwargs.items():
        # Allow plural names (like mins instead of min)
        if name not in UNITS and name.endswith("s"):
            name = name[:-1]

        if name not in UNITS:
            raise ValueError(
                "the unit {} isn't defined as a valid " "game time unit".format(name))
        rtime += value * UNITS[name]
    rtime /= TIMEFACTOR
    if format:
        return time_to_tuple(rtime, 31536000, 2628000, 604800, 86400, 3600, 60)
    return rtime

#### Returns game time from realtime ############
# Args: sec, mins, hrs, days, weeks, month, yrs #
# Returns realtime seconds                      #
#################################################


def realtime_to_gametime(secs=0, mins=0, hrs=0, days=0, weeks=0, months=0, yrs=0, format=False):
    """
    This method calculates how much in-game time a real-world time
    interval would correspond to. This is usually a lot less
    interesting than the other way around.

    Keyword Args:
        times (int): The various components of the time.
        format (bool): Formatting the output.

    Returns:
        time (float or tuple): The gametime difference or the same
            time split up into time units.

     Example:
      realtime_to_gametime(days=2) -> number of game-world seconds

    """
    gtime = TIMEFACTOR * (
        secs
        + mins * 60
        + hrs * 3600
        + days * 86400
        + weeks * 604800
        + months * 2628000
        + yrs * 31536000
    )
    if format:
        units = sorted(set(UNITS.values()), reverse=True)
        # Remove seconds from the tuple
        del units[-1]

        return time_to_tuple(gtime, *units)
    return gtime

#### Ingame Time: Returns the ingame time ####
# Args: absolute=False                       #
# Returns a tuple of the ingame time:        #
#     year, month, week, day, hour, minute,  #
#     second                                 #
##############################################


def custom_gametime(absolute=False):
    """
    Return the custom game time as a tuple of units, as defined in settings.

    Args:
        absolute (bool, optional): return the relative or absolute time.

    Returns:
        The tuple describing the game time.  The length of the tuple
        is related to the number of unique units defined in the
        settings.  By default, the tuple would be (year, month,
        week, day, hour, minute, second).

    """
    current = gametime.gametime(absolute=absolute)
    units = sorted(set(UNITS.values()), reverse=True)
    del units[-1]
    return time_to_tuple(current, *units)

#### Real Time seconds until ingame time ######
# Args: sec, min, hour, day, week, month year #
# Returns: real time seconds                  #
###############################################


def real_seconds_until(**kwargs):
    """
    Return the real seconds until game time.

    If the game time is 5:00, TIME_FACTOR is set to 2 and you ask
    the number of seconds until it's 5:10, then this function should
    return 300 (5 minutes).

    Args:
        times (str: int): the time units.

    Example:
        real_seconds_until(hour=5, min=10, sec=0)

    Returns:
        The number of real seconds before the given game time is up.

    """
    current = gametime.gametime(absolute=True)
    units = sorted(set(UNITS.values()), reverse=True)
    # Remove seconds from the tuple
    del units[-1]
    divisors = list(time_to_tuple(current, *units))

    # For each keyword, add in the unit's
    units.append(1)
    higher_unit = None
    for unit, value in kwargs.items():
        # Get the unit's index
        if unit not in UNITS:
            raise ValueError("unknown unit".format(unit))

        seconds = UNITS[unit]
        index = units.index(seconds)
        divisors[index] = value
        if higher_unit is None or higher_unit > index:
            higher_unit = index

    # Check the projected time
    # Note that it can be already passed (the given time may be in the past)
    projected = 0
    for i, value in enumerate(divisors):
        seconds = units[i]
        projected += value * seconds

    if projected <= current:
        # The time is in the past, increase the higher unit
        if higher_unit:
            divisors[higher_unit - 1] += 1
        else:
            divisors[0] += 1

    # Get the projected time again
    projected = 0
    for i, value in enumerate(divisors):
        seconds = units[i]
        projected += value * seconds

    return (projected - current) / TIMEFACTOR
