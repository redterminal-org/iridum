#### README_OBJECTS Prototypes ####
"""
Prototypes

A prototype is a simple way to create individualized instances of a
given typeclass. It is dictionary with specific key names.

For example, you might have a Sword typeclass that implements everything a
Sword would need to do. The only difference between different individual Swords
would be their key, description and some Attributes. The Prototype system
allows to create a range of such Swords with only minor variations. Prototypes
can also inherit and combine together to form entire hierarchies (such as
giving all Sabres and all Broadswords some common properties). Note that bigger
variations, such as custom commands or functionality belong in a hierarchy of
typeclasses instead.

A prototype can either be a dictionary placed into a global variable in a
python module (a 'module-prototype') or stored in the database as a dict on a
special Script (a db-prototype). The former can be created just by adding dicts
to modules Evennia looks at for prototypes, the latter is easiest created
in-game via the `olc` command/menu.

Prototypes are read and used to create new objects with the `spawn` command
or directly via `world.utils.utils.spawn`.

A prototype dictionary have the following keywords:

Possible keywords are:
- `prototype_key` - the name of the prototype. This is required for db-prototypes,
  for module-prototypes, the global variable name of the dict is used instead
- `prototype_parent` - string pointing to parent prototype if any. Prototype inherits
  in a similar way as classes, with children overriding values in their partents.
- `prototype_tags` - Tags added to the prototype itself. Please look at additional
  information below.
- `key` - string, the main object identifier.
- `typeclass` - string, if not set, will use `settings.BASE_OBJECT_TYPECLASS`.
- `location` - this should be a valid object or #dbref.
- `home` - valid object or #dbref.
- `destination` - only valid for exits (object or #dbref).
- `permissions` - string or list of permission strings.
- `locks` - a lock-string to use for the spawned object.
- `aliases` - string or list of strings.
- `attrs` - Attributes, expressed as a list of tuples on the form `(attrname, value)`,
  `(attrname, value, category)`, or `(attrname, value, category, locks)`. If using one
   of the shorter forms, defaults are used for the rest.
- `tags` - Tags, as a list of tuples `(tag,)`, `(tag, category)` or `(tag, category, data)`.
-  Any other keywords are interpreted as Attributes with no category or lock.
   These will internally be added to `attrs` (eqivalent to `(attrname, value)`.

See the `spawn` command and `world.utils.utils.spawn` for more info.

** Additional Information: **
If you don't want your prototype to be updated on a world update, add "no_update"
to the `prototype_tags`. Also please add a the category to your `prototype_tags`.
This is especially needed for prototypes which are dynamically spawned. If you
don't add this `prototype_tag` to dynamically spawned prototypes, the attributes
are always dynamically recreated on each world update with `@batchcode 02-update`,
for example if you create the key of the spawned object from a random list. Look
at the `TEST_FLOWER` object for an example.
"""

#### Please prefix all readme prototypes with "README_" in this file ####

#### Proto: README_NEWCOMER ####
_README_NEWCOMER_TEXT = """|RWelcome to the |GIridum|n |RNewcomer README!|n

You have just connected to an highly experimental, virtual and interactive
text world. It's not meant to be a roleplaying MUD, but to build and create
an organic virtual environment. At first you should just look around and
explore this world a little. Play with the gadgets and things you find and
try out in which way you can use them.

Exits can be used by simply typing their name like |c'Teleportation Pods'|n,
or one of it's aliases |c'pods'|n or |c'teleportation'|n for example.

There is also extensive documentation accessible with the |c'help
[topic||command]'|n command, but it's a continuous work. For further
documentation about the underlying Evennia Python MUD/MUSH Creation System
look at:

|yhttps://www.evennia.com/|n

If you don't want to use the integrated pager, use |c'set me/disable_page =
True'|n, if you want to use your scrolling in your MUD client. I have not
fully made it switchable, so you might get in contact with the pager again.

If you have gathered enough experience with "playing" in this space, you could
try to build things yourself, if you ask the Administrator of this MUD/MUSH
nicely. All I ask you for, is being nice to each other and don't destroy other
peoples creations. And please keep this place as tidy as you can. Delete old,
unneeded objects and don't let your litter lay around. If you still only have
"player" permissions, you can put trash in one of the waste bins with |c'drop
<object> into <target>'|n. Most objects have shortcuts or aliases like "bin"
for "wastebin" and "Newcomer" for "Newcomer README".

To talk to to all people currently logged in, you can use "channels". just
put "pub " before what you want to say and send it to the "public" channel,
which every user is part of.

So I hope you have fun with the things you or other people have built and
make this a place for creative recreation, learning and communication.

Have fun, fab (administrator)"""

README_NEWCOMER = {
    "key": "Newcomer README",
    "aliases": ["newcomer", "Newcomer"],
    "typeclass": "world.objects.readme.Readme",
    "attrs": [
        (
            "text",
            _README_NEWCOMER_TEXT,
            None,
            "attredit:perm(Expert Builder);attrread:all();",
        ),
        (
            "desc",
            "You see a paper sheet with some notes on it.",
            None,
            "attredit:perm(Expert Builder);attrread:all();",
        ),
    ],
    "prototype_tags": ["readme"],
    "prototype_desc": "A README document for newcomers",
    "prototype_locks": "spawn:perm(Beginner Builder);edit:perm(Expert Builder);",
}

#### Proto: README_GAMETIME ####
_README_GAMETIME_TEXT = """|RThis is the |GGameTime README|n

The ingame time is not the same as the real time. Ingame time is 4x
times faster than real time. It also has it's own calendar. The days
and month have different names and a month is divided into 4 moon
phases (weeks).

It may be strange at first but ingame time is also used to sign all
editable objects like the Guestbook, the TODO List and all other
things which are marked with a date. A Character-To-Character email
system is planned and the mails will also be marked with ingame
time. This will be strange at first, because you can't easily get
the real time when a TODO or Guestbook entry was made or when a mail
was sent. We could have made the timestamps realtime but we decided
against it, because after all, it's a game with its own mechanics.

Each month has 28 days, divided into 4 moon phases (weeks) and there
are 12 month.

|YDays:|n

1:"Moonday", 2:"Windday", 3:"Waterday", 4:"Earthday", 5:"Fireday",
6:"Starday", 7: "Sunday"

|YMoon phases (weeks):|n

1:"New Moon", 2:"Second Quarter", 3:"Full Moon", 4:"Fourth Quarter",

|YMonths:|n

1:"Japha", 2:"Fermias", 3:"Mikha", 4:"Alphos", 5:"Mielah",
6:"Aniyah", 7:"Paha", 8:"Raches", 9:"Sariel", 10:"Hielaph",
11:"Kiriel", 12:"Zaram"

You can always get the current ingame time with the |c'time'|n
command and we hope, you get used to it.

Have fun, fab (administrator)"""

README_GAMETIME = {
    "key": "Gametime README",
    "aliases": ["gametime", "Gametime"],
    "typeclass": "world.objects.readme.Readme",
    "attrs": [
        (
            "text",
            _README_GAMETIME_TEXT,
            None,
            "attredit:perm(Expert Builder);attrread:all();",
        ),
        (
            "desc",
            "You see a paper sheet with some notes on it.",
            None,
            "attredit:perm(Expert Builder);attrread:all();",
        ),
    ],
    "prototype_tags": ["readme"],
    "prototype_desc": "A README document about ingame time",
    "prototype_locks": "spawn:perm(Beginner Builder);edit:perm(Expert Builder);",
}

#### Proto: README_DEVELOPER ####
_README_DEVELOPER_TEXT = """|GDeveloper README|n

Although 'building' can be a lot of fun in itself, you can just create or
spawn objects, which other people have created. You can change some properties
of the objects, but you can't for example add commands. And especially in
the early stages of development there |wwill|n be bugs. If you can fix them
yourself, I would be pleased to get a a Pull Request from you as well as
PRs for additional Objects, Rooms, Scripts and game mechanics over all.

So it may be better, to work directly on the underlying Python3 code, which
is available at my Codeberg.org git repository:

|yhttps://codeberg.org/fab/Iridum|n

You will find further information in the README.md file in this repository,
especially how to set up a development environment and how to create PRs for
your creations. But the MUSH code is already very complex and I believe it
will take some effort to get into the codebase.

There have also be made some rules how PRs should look like, for example,
try to create your own files in moderation and not mess around with other
peoples code.  This is one of my first public projects where I |wwant|n
people to contibute code in a larger frame.

With Python code you can add commands to your own objects and rooms, which
will inherit the functionality from earlier typeclasses. You can add all
kinds of functionality you can imagine. If you have the knowledge and the
enthusiasm you can even create complete game mechanics.

I'll try to make a backup every night (Central European Time). The only
problem I see is the backup of the SQLiteDB |wduring|n the MUSH being online,
which could possibly corrupt the DB, but I'm sure there are solutions for that.

The complete documentation for the Evennia code base, which you should make
yourself familiar with to make full use of the MUD creation can be found at
these places:

|yhttps://www.evennia.com/docs/latest/index.html|n: Documentation index

|yhttps://www.evennia.com/docs/latest/Components/Components-Overview.html|n:
Core Components

|yhttps://www.evennia.com/docs/latest/Howtos/Howtos-Overview.html#how-tos|n:
Tutorials and HowTo's

You are highly encouraged to contribute Python code to the codebase.
You may send in pull requests on Codeberg.org, if you have an account there,
or you can send in patches via |cgit send-email|n, if you have set up your
git client to send patches/commits with email, if you don't have/want a
Codeberg.org account, which I prefer.

So every contribution to the code is very appreciated and would be of
great help.

Have fun, fab (administrator)"""

README_DEVELOPER = {
    "key": "Developer README",
    "aliases": ["Developer", "developer"],
    "typeclass": "world.objects.readme.Readme",
    "attrs": [
        (
            "text",
            _README_DEVELOPER_TEXT,
            None,
            "attredit:perm(Expert Builder);attrread:all();",
        ),
        (
            "desc",
            "You see a paper sheet with some notes on it.",
            None,
            "attredit:perm(Expert Builder);attrread:all();",
        ),
    ],
    "prototype_tags": ["readme"],
    "prototype_desc": "A README document about 'development'",
    "prototype_locks": "spawn:perm(Beginner Builder);edit:perm(Expert Builder);",
}

#### Proto: README_BUILDER ####
_README_BUILDER_TEXT = """|GBuilder README|n

If you have made yourself familiar with the Iridum world and know
how to find your way around the help system and had a look at all
the READMEs, you can get 'Builder' permissions, if you ask one of
the admins (which is me for the forseeable future at least).

The permissions hierarchy is ["Player", "Beginner Builder",
"Advanced Builder", "Expert Builder"]. These permissions are given
on trust into the player and with "Expert Builder" permissions you
can almost create and alter everything.

With "Beginner Builder" permissions you can dig rooms with their
correspondig exits, edit (some) descriptions and attributes (eg.
Rooms), add tags and create object from a set of typeclasses and
prototypes. With higher permissions you can create and alter more
things.

Make sure you read the |c'help [command]'|n pages available to
builders. You can list all objects and classes available to you with
the command |c'typeclass/list'|n (typeclasses) or |c'spawn/list'|n
(prototypes) for example. And to get the documentation for a
typeclass, write |c'typeclass/show <typeclass>'|n.

The big problem with 'building' is, that these changes are only made
to the database. And expecially at the beginning of the development,
the world may be reset if the database gets corrupted due to bugs in
code, although I'm relatively sure that that won't happen.

So if you want your creations to be recreated on a rebuild of the
world, you should learn how to use |c'@batchcode'|n scripts, and
send in code patches containing commits to the |c`world/batch/`|n
directory in the Iridum code repository. Documentation about
|c'@batchcode'|n scripts can be found here:

|yhttps://www.evennia.com/docs/latest/Components/Batch-Code-Processor.html|n

And the Iridum repository is accessible with this link:

|yhttps://codeberg.org/fab/Iridum|n

There you'll also find documentation on how to set up a development
environment for Iridum.

Then you've also made your first steps as a 'Developer', which opens
up another whole new world of possibilities.

Have fun, fab (administrator)"""

README_BUILDER = {
    "key": "Builder README",
    "aliases": ["Builder", "builder"],
    "typeclass": "world.objects.readme.Readme",
    "attrs": [
        (
            "text",
            _README_BUILDER_TEXT,
            None,
            "attredit:perm(Expert Builder);attrread:all();",
        ),
        (
            "desc",
            "You see a paper sheet with some notes on it.",
            None,
            "attredit:perm(Expert Builder);attrread:all();",
        ),
    ],
    "prototype_tags": ["readme"],
    "prototype_desc": "A README document about 'building'",
    "prototype_locks": "spawn:perm(Beginner Builder);edit:perm(Expert Builder);",
}
