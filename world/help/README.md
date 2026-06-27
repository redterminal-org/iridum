# world/help/
Here you find additional help files. There's much work to be done here and many
entries have to be added.

## Adding Help Entry Files
To add a help entry file, you must include it in the `__init__.py` package file.
So to add all help entries from the file `help_evennia.py` in this directory,
you have to put a `from .help_evennia import *` line into `__init__.py` file in
this directory.

If you want to add help entries look at `./help_evennia.py` how to do it.
Preferably you copy this file to `./help_<name>.py`, rename the entry and change
the settings to your wishes and edit the entry.

Especially take care of the right locks. To make the entry readable by everyone,
add `"locks": "read:all();"`, which should be the default. If it should only be
readable by 'Beginner Builders', use `"read:perm(Beginner Builder);"` for
example.

Help for commands is provided by the Docstring under the `class
CmdCmdName(Command):` line. You can also set the 
`"read:perm(Beginner Builder);"` lock, for commands that are only available for
'Beginner Builder'.

Read about locks in this [documentation](https://www.evennia.com/docs/latest/Components/Locks.html).
