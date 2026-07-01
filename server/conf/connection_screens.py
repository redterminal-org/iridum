# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function `connection_screen()`, taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from django.conf import settings

from evennia import utils

CONNECTION_SCREEN = """
|b==========================================================================|n
Welcome to |g{}|n, running the "Evennia MUD/MU* Creation System"
version {}!

This is an experimental, virtual and interactive text environment. It's
not meant to be a roleplaying MUD, but a virtual text world for the
users to create and build. You should look around at first as a 'player'
and look at all the README documents laying around everywhere and play
with the gadgets and objects other people have created.

If you want to build and create objects yourself, you can get 'builder'
permissions, if you ask nicely. But please don't break this place and 
be nice to each other. Builder permissions are given on trust!

If you have an existing account, connect to it by typing:
     |cconnect <username> <password>|n
If you don't have an account to create an account, you can create one:
     |ccreate <username> <password>|n

The username may only contain the characters '|Y[a-z][A-Z][0-9]-_|n'.
Usernames and passwords may not contain spaces and must not be in quotes.

Enter |chelp|n for more info. |clook|n will re-show this screen.
|bi==========================================================================|n""".format(
    settings.SERVERNAME, utils.get_evennia_version("short")
    )
