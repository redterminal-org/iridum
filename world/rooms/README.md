# world/rooms/
All Room typeclasses go into this directory. It's best to group related commands
or objects in one separate file or if it's a bigger creation in a subdirectory.
If you use a subdirectory, you have to put an empty `__init__.py` file in it, so
evennia can find it's contents.

Rooms that can be used as base classes can be placed here too. For example,
the `world.rooms.meadow.Meadow` typeclass can be used as a base typeclass
for other Meadow rooms.

You can also add commands to your rooms, which are available if the player is in
in the room. Look at the `Meadow` Room typeclass as an example. It adds the
command `pick flower` which lets you pick a random flower.

But be careful with commands not to clash with other commands available at a
given moment.

If you want to make an outdoor room add a tag with the category 'climate' to the
room. For now the only available climate is 'temperate', so you have to use the
command `<room>.tags.add("temperate", category="climate")`.
