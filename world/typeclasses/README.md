# world/typeclasses/

This directory holds the game's default typeclasses. Modules for overloading all
the typeclasses representing the game entities and many systems of the game.
Other server functionality not covered here is usually modified by the modules
in `server/conf/`.

Each module holds classes that just import Evennia's defaults. Modifications
done to these classes will overload the defaults. Please use these to create
your own typeclasses.

If you want to create your own typeclasses, please use the subdirectories under
`world/` directly like `world/objects/`, `world/rooms/`, `world/scripts/` etc.
You can use the typeclasses from `world/typeclasses/` to inherit them to your
own typeclasses for example in `world/rooms/` for your own Room typeclasses.

Look at the [README.md](../README.md) file in the `world/` directory for further
information.
