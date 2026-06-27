#### Prototype Documentation ####
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

#### Please prefix all prototypes with "EDIBLE_" in this file ####

#### Imports ####

#### Proto: EDIBLE_APPLE ####
EDIBLE_APPLE = {
    "key": "fresh red apple",
    "aliases": ["red apple", "apple"],
    "typeclass": "world.typeclasses.objects.Object",
    "attrs": [("desc", "A sweet red $protkey(key).", None, ""),
              ("edible", True, None, "")],
    "prototype_tags": ["edible"],
    "prototype_locks": "spawn:all();edit:all();",
    "prototype_desc": "An Apple",
}

#### Proto: EDIBLE_BERRIES ####
EDIBLE_BERRIES = {
    "key": "handful of berries",
    "aliases": ["berries"],
    "typeclass": "world.typeclasses.objects.Object",
    "attrs": [("desc", "A handful of sweet different berries.", None, ""),
              ("edible", True, None, "")],
    "prototype_tags": ["edible"],
    "prototype_locks": "spawn:all();edit:all();",
    "prototype_desc": "An handful of sweet different berries.",
}

#### Proto: EDIBLE_PEAR ####
EDIBLE_PEAR = {
    "key": "fresh juicy pear",
    "aliases": ["juicy pear", "pear"],
    "typeclass": "world.typeclasses.objects.Object",
    "attrs": [("desc", "A sweet and juicy pear.", None, ""),
              ("edible", True, None, "")],
    "prototype_tags": ["edible"],
    "prototype_locks": "spawn:all();edit:all();",
    "prototype_desc": "A sweet and juicy pear.",
}

#### Proto: EDIBLE_PEACH ####
EDIBLE_PEACH = {
    "key": "ripe yellow peach",
    "aliases": ["yello peach", "ripe peach", "peach"],
    "typeclass": "world.typeclasses.objects.Object",
    "attrs": [("desc", "A sweet and ripe yellow peach.", None, ""),
              ("edible", True, None, "")],
    "prototype_tags": ["edible"],
    "prototype_locks": "spawn:all();edit:all();",
    "prototype_desc": "A sweet and ripe yellow peach.",
}
