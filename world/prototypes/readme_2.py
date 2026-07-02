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

#### Proto: README_FREEBSD ####
_README_FORUM_TEXT = """|RThis is the |RForum|g README|n

The most difficult thing will be the operation of the integrated editor,
which needs a little practice. Read the "Editor README" with |cl editor|n,
for a short introduction.

The help for the Forum commands can be listed with |chelp forum|n. This
will list all Forum commands provided to you. These are:

1. "add"

- Usage "add[/edit] <subject> [= <message>]". This will add a new Forum
thread with the subject <subject> and the optional message <message>. If the
message is omitted, the editor will open, no matter if you use the "/edit"
switch or not.  If you use the "/edit" swtitch together with a message,
the editor will be initialized with the <message> to begin with.

- Usage "add[/edit] <#dbref> [= <subject>][;;<message>]". Using a <#dbref>
of a thread, will add a comment to the thread, with the subject <subject> and
message <message>. You can only use the <#dbref>, which then uses the subject
of the thread and open the editor, like always if you omit the <message>.

2. "archive"

- Usage "archive <#dbref of thread> = <true||false>". This lets you
(un)archive a thread of yourself. This will (un)lock the thread without
deleting its comments.  If locked, no more comments can be added to the
thread.

3. "archived"

- Usage "archived". This will show you a list of all archived threads. These
are locked and you can't add new comments to it.

4. "change"

- Usage "change[/edit] <#dbref of thread||comment> [=
<subject>][;;<message>]".  This lets you change a Forum thread or comment
by yourself. If <subject> is omitted it won't be changed. If <message> is
omitted the editor will open, even if you didn't specify the "/edit" switch.

- Example "change/edit #453 = My new subject;;A short interesting note". This
will open the thread or comment with <#dbref>, change the subject to
"My new subject" and open the editor with the initial message "A short
interesting note".

5. "delete"

- Usage "delete <#dbref of thread||comment>". This will delete a thread
or comment of yourself with the given <#dbref>. Note that all comments,
even from other users will be deleted, when deleting a thread. Consider
archiving it instead.

6. "follow"

- Usage "follow <#dbref of thread>". This lets you explicitly follow a
specific thread. The '(unseen)' tag will be removed. This will make the
thread appear in the list of threads when emitting the "look" command.

7. "list"

- Usage "list". Shows the complete list of threads without archived
(locked) ones.

8. "pin"

- Usage "pin <#dbref of thread>". This will pin a thread at the beginning
of the list of threads when using the "look" command. This is an "Expert
Builder" command, so it isn't available with lower privileges.

9. "show" - Usage "show <#dbref of thread||comment>". This will show the whole
thread with comments or a single comment. You can also show archived threads.

|yNote|n: Despite having seen the thread, the "(unseen)" tag won't be removed.
You have to explicitly "unfollow <#dbref>" to get rid of seeing it or
"follow <#dbref>" to show it with the "look" command.

10. "unfollow"

- Usage "unfollow <#dbref of thread>". This will hide the thread from the
list when using the "look" command.

11. "unpin"

- Usage "unpin <#dbref of pinned thread>". This will remove the pinned
thread from the top of the list when using the "look" command. This is an
"Expert Builder" command, so it isn't available with lower privileges.

---

I know this is a lot of stuff to learn, like the "mail" command, but the
most complicated thing will be operating the editor, which can be very
complicated at first and needs some practice. Read the "Editor README"
(|cl editor|n) for a short introduction.

Have fun, fab (administrator)"""

README_FORUM = {
    "key": "Forum README",
    "aliases": ["forum"],
    "typeclass": "world.objects.readme.Readme",
    "attrs": [
        (
            "text",
            _README_FORUM_TEXT,
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
    "prototype_desc": "A README document about the Forum",
    "prototype_locks": "spawn:perm(Beginner Builder);edit:perm(Expert Builder);",
}
