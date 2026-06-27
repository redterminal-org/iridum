# commands/

This folder holds modules for implementing the games own commands and command
sets.

This directory also holds the base Commands and CommandSets. However, you can
add Commands and CommandSets to your Objects and Rooms if you like. You just
have to choose the `commands.command.Command` base class for your Commands and
the `evennia.CmdSet` base class for your CommandSets.

But you _SHOULD_ add your commands and commandsets to the same objects (in
`users/<accountname>/objects/`) or rooms (in `users/<accountname>/rooms/`) for
example in their own files or
subdirectories with the objects themself. They'll be automatically available to
the Character if they're attached to an object, room, exit or whatever.

Also remember that if you create new sub directories you must put (optionally
empty) `__init__.py` files in there so that Python can find your modules.

But be careful to change the base `Command` or `CmdSets` in `commands/`! You
have to know what you're doing! But you may add some general commands in their
own files in the `commands/` directory or any subdirectory thereof if you have a
good idea of a generic command, **but not without discussion**! Open an issue
before creating a PR to change/add files to `commands/`.

Look at the
[documentation](https://www.evennia.com/docs/latest/Components/Components-Overview.html#commands)
for 'Commands' and 'CommandSets' at the Evennia site.

And of course: _DOCUMENT_ your commands and all the things you're creating
with `<docstrings>`. Look for examples in the `cmd_*` files in this directory.
