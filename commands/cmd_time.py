"""
General Commands

General Commands describe the general functionality the account/character can do
in the game.
"""

from evennia import settings
from .command import Command

from world.utils import gametime
from world.utils.utils import wrap

_WIDTH = settings.DEFAULT_WIDTH


# Time Command: 'time' returns ingame time #
class CmdTime(Command):
    """
    Display Ingame Time

    Syntax:
        time

    """

    key = "time"
    locks = "cmd:all()"

    def func(self):
        """Execute the time command."""
        # Get absolute game time
        year, month, week, day, hour, min, sec = gametime.custom_gametime(
            absolute=True)
        # count starts with 0, so 1 must be added
        dayofmonth = (week * 7) + day + 1

        string = "We have |g{day} ({dom})|n in the |b{week}|n of |m{month} ({moy})|n, year {year} in {epoch}. It's |y{hour:02}:{min:02}:{sec:02}|n."
        self.msg(
            wrap(
                string.format(
                    epoch=gametime.EPOCH,
                    year=year,
                    month=gametime.MONTH_NAMES[month],
                    moy=month + 1,
                    dom=dayofmonth,
                    week=gametime.WEEK_NAMES[week],
                    day=gametime.DAY_NAMES[day],
                    hour=hour,
                    min=min,
                    sec=sec,
                ),
                width=_WIDTH,
            )
        )
