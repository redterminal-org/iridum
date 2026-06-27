# world/objects/
All objects go into this directory. It's best to group related objects in one
separate file.

Objects that can be used as base classes can be placed here too. For example,
the `world.objects.objects.Container` typeclass can be used as a base typeclass
for objects that should be able to hold other objects.

You can also add commands to your objects, which are available if the object is
in the location the player is in or in the players inventory.

But be careful with commands not to clash with other commands available at a
given moment.
