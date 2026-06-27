"""
Object

The Object is the class for general items in the game world.

Use the ObjectParent class to implement common features for *all* entities
with a location in the game world (like Characters, Rooms, Exits).

"""

from collections import defaultdict

from evennia.objects.objects import DefaultObject
from evennia import settings
from evennia.utils.utils import iter_to_str
from evennia.scripts.models import ScriptDB as _ScriptDB

from world.utils.utils import wrap_para, wrap

_WIDTH = settings.DEFAULT_WIDTH


class ObjectParent:
    """
    This is a mixin that can be used to override *all* entities inheriting at
    some distance from DefaultObject (Objects, Exits, Characters and Rooms).

    Just add any method that exists on `DefaultObject` to this class. If one
    of the derived classes has itself defined that same hook already, that will
    take precedence.

    """

    appearance_template = "{header}|c{name}|n{extra_name_info}|n|/"
    appearance_template += "|B" + "=" * _WIDTH + "|n|/"
    appearance_template += "{desc}|/"
    appearance_template += "|B" + "=" * _WIDTH + "|n"
    appearance_template += "{text}{characters}{exits}{things}{footer}"

    def at_object_creation(self):
        pass

    def after_spawn(self, account=None, caller=None, **kwargs):
        """
        called after a spawn was successful. Implemented because it can take
        an account or caller, and is called by the custom 'spawn' function from
        `world.utils.utils`, which should be used instead of Evennias original
        'spawn' function.
        """
        pass

    def received(self, giver, obj, **kwargs):
        giver.location.msg_contents(wrap(
            f"$You() $conj(give) {obj.key}"
            f" to {self.get_display_name()}."), from_obj=giver)
        return

    def basetype_setup(self):
        """
        This sets up the default properties of an Object, just before
        the more general at_object_creation.

        You normally don't need to change this unless you change some
        fundamental things like names of permission groups.
        """
        # the default security setup fallback for a generic
        # object. Overload in child for a custom setup. Also creation
        # commands may set this (create an item and you should be its
        # controller, for example)

        # run inherited basetype_setup()
        super().basetype_setup()

        self.locks.add(
            ";".join(
                [
                    # edit locks/permissions, delete
                    "control:perm(Developer)",
                    "call:true()",  # allow to call commands on this object
                    "examine:perm(Beginner Builder)",  # examine properties
                    "delete:perm(Expert Builder)",  # delete object
                    "edit:perm(Expert Builder)",  # edit properties/attributes
                    "view:all()",  # look at object (visibility)
                    "search:all()",
                    "drop:holds()",  # drop only that which you hold
                    "tell:perm(Admin)",  # allow emits to this object
                    "puppet:perm(Developer)",
                    "teleport:perm(Expert Builder)",
                    "teleport_here:perm(Expert Builder)",
                    "attrcreate:perm(Expert Builder)",
                ]
            )
        )

    def search(
        self,
        searchdata,
        global_search=False,
        use_nicks=True,
        typeclass=None,
        location=None,
        attribute_name=None,
        quiet=False,
        exact=False,
        candidates=None,
        use_locks=True,
        nofound_string=None,
        multimatch_string=None,
        use_dbref=None,
        tags=None,
        stacked=0,
    ):
        """
        Refefined 'search()' function to set 'use_dbref' to True if player has
        'Beginner Builder' permissions, because the PERMISSION_HIERARCHY was
        changed.
        """

        # Change use_dbref to True if has 'Beginner Builder' permissions
        use_dbref = (
            self.locks.check_lockstring(self, "_dummy:perm(Beginner Builder)")
            if use_dbref is None
            else use_dbref
        )
        return super().search(
            searchdata,
            global_search=global_search,
            use_nicks=use_nicks,
            typeclass=typeclass,
            location=location,
            attribute_name=attribute_name,
            quiet=quiet,
            exact=exact,
            candidates=candidates,
            use_locks=use_locks,
            nofound_string=nofound_string,
            multimatch_string=multimatch_string,
            use_dbref=use_dbref,
            tags=tags,
            stacked=stacked,
        )

    def delete(self, **kwargs):
        """
        Deletes this object.  This also deletes all objects which this object
        contains by the recursively called 'at_object_delete()' method. All
        Objects the caller is not allowed to delete will be moved to their
        respective home locations, as well as clean up all exits to/from the
        object.

        Returns:
            bool: Whether or not the delete completed successfully or not.

        """
        try:
            caller = kwargs["caller"]
        except KeyError:
            caller = None

        delete_ok = self.at_object_delete(caller=caller)
        if not self.pk or not delete_ok:
            # This object has already been deleted,
            # or the pre-delete check return False
            return False

        # See if we need to kick the account off.

        for session in self.sessions.all():
            session.msg(
                ("Your character {key} has been destroyed.").format(key=self.key)
            )
            # no need to disconnect, Account just jumps to OOC mode.
        # sever the connection (important!)
        if self.account:
            # Remove the object from playable characters list
            self.account.characters.remove(self)
            for session in self.sessions.all():
                self.account.unpuppet_object(session)

        # unlink account/home to avoid issues with saving
        self.db_account = None
        self.db_home = None

        for script in _ScriptDB.objects.get_all_scripts_on_obj(self):
            script.delete()

        # Destroy any exits to and from this room, if any
        self.clear_exits()
        # Clear out any non-exit objects located within the object
        self.clear_contents()
        self.attributes.clear()
        self.nicks.clear()
        self.aliases.clear()
        self.location = None  # this updates contents_cache for our location

        # Perform the deletion of the object
        super().delete()
        return True

    def at_object_delete(self, **kwargs):
        """
        This method is called when deleting an instance of this object. It also
        calls the 'delete()' method on all objects contained by this obbject.
        The "caller" is passed to the 'delete()' method, which calls itself this
        method with a "caller" key in **kwargs.

        This function checks, if the caller has permissions to delete this
        object.

        This way, all objects contained by this object will recursively deleted
        if the caller has permissions.
        """
        # delete all objects inside the object on deletetion of the
        # object itself
        try:
            caller = kwargs["caller"]
        except KeyError:
            caller = None

        # Check permissions if caller
        if caller:
            if not (self.access(caller, "control") or self.access(caller, "delete")):
                caller.msg(
                    wrap(
                        f"You are |Rnot allowed|n to delete |G{self.name}|n.",
                        width=_WIDTH,
                    )
                )
                return False

            for obj in self.contents:
                obj.delete(caller=caller)
            caller.msg(wrap(f"|G{self.key}|n |Rdeleted|n.", width=_WIDTH))
            return True

        else:
            for obj in self.contents:
                obj.delete()
        return True

    def get_display_exits(self, looker, **kwargs):
        """
        Get the 'exits' component of the object description. Called by
        `set_appearance()` which is called by `return_appearance()`.

        Args:
            looker (DefaultObject): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.

        Keyword Args:
            exit_order (iterable of str): The order in which exits should be listed, with
                unspecified exits appearing at the end, alphabetically.

        Returns:
            str: The exits display data.

        Examples:
        ::

            For a room with exits in the order 'portal', 'south', 'north', and 'out':
                obj.get_display_name(looker, exit_order=('north', 'south'))
                    -> "Exits: north, south, out, and portal."  (markup not shown here)
        """

        def _sort_exit_names(names):
            exit_order = kwargs.get("exit_order")
            if not exit_order:
                return names
            sort_index = {name: key for key, name in enumerate(exit_order)}
            names = sorted(names)
            end_pos = len(sort_index)
            names.sort(key=lambda name: sort_index.get(name, end_pos))
            return names

        exits = self.filter_visible(
            self.contents_get(content_type="exit"), looker, **kwargs
        )
        exit_names = (exi.get_display_name(looker, **kwargs) for exi in exits)
        exit_names = iter_to_str(_sort_exit_names(exit_names), endsep=(", and"))
        e = "|/|mExits:|n"
        return f"{e} {exit_names}" if exit_names else ""

    def get_display_things(self, looker, **kwargs):
        """
        Returns a string of objects contained by this object as a string to use
        in `set_appearance()` which was implemented to be called by
        `return_appearance()`
        """
        # get and identify all objects
        things = defaultdict(list)
        for obj in self.contents_get(content_type="object"):
            key = obj.get_display_name(looker)
            # things can be pluralized
            things[key].append(obj)

        thing_strings = []
        for key, itemlist in sorted(things.items()):
            nitem = len(itemlist)
            if nitem == 1:
                key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
            else:
                key = [
                    item.get_numbered_name(nitem, looker, key=key)[1]
                    for item in itemlist
                ][0]
            thing_strings.append(key)

        things_names = iter_to_str(thing_strings)
        o = "|/|mObjects:|n"
        return f"{o} {things_names}" if things_names else ""

    def get_display_characters(self, looker, **kwargs):
        """
        Get the 'characters' component of the object description. Called by
        `set_appearance()` in `return_appearance()`.

        Args:
            looker (DefaultObject): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.
        Returns:
            str: The character display data.

        """
        characters = self.filter_visible(
            self.contents_get(content_type="character"), looker, **kwargs
        )
        character_names = iter_to_str(
            (
                f"|C{char.get_display_name(looker, **kwargs)}|n{
                    ' |R(away)|n' if char.db.away else ''
                }"
                for char in characters
            ),
            endsep=(", and"),
        )
        c = "|/|mPeople:|n"
        return f"{c} {character_names}" if character_names else ""

    def set_appearance(self, looker, **kwargs):
        """
        Custom method, which is called by `return_appearance()` and takes the
        keys to every variable in the `appearance_template` in **kwargs to
        overwrite the default values returned by the `get_display...` methods,
        which will be used by default.

        Args:
            looker (DefaultObject): Object doing the looking
            **kwargs: The arguments to overwrite in the appearance_template
                      if you want to.
        Returns:
            str: The formatted appearance string
        """

        # set appearance arguments
        try:
            name = kwargs["name"]
        except KeyError:
            name = self.get_display_name(looker)
        try:
            extra_name_info = kwargs["extra_name_info"]
        except KeyError:
            extra_name_info = self.get_extra_display_name_info(looker)
        try:
            desc = kwargs["desc"]
        except KeyError:
            desc = self.get_display_desc(looker)
        try:
            header = kwargs["header"]
        except KeyError:
            header = self.get_display_header(looker)
        try:
            footer = kwargs["footer"]
        except KeyError:
            footer = self.get_display_footer(looker)
        try:
            exits = kwargs["exits"]
        except KeyError:
            exits = self.get_display_exits(looker)
        try:
            characters = kwargs["characters"]
        except KeyError:
            characters = self.get_display_characters(looker)
        try:
            things = kwargs["things"]
        except KeyError:
            things = self.get_display_things(looker)
        try:
            text = kwargs["text"]
            output = "|/"
            output += text
            output += "|/|B" + "=" * _WIDTH + "|n"
            text = output
        except KeyError:
            text = ""

        return self.appearance_template.format(
            name=name,
            extra_name_info=extra_name_info,
            desc=wrap_para(desc),
            text=text,
            header=header,
            footer=footer,
            exits=wrap(exits),
            characters=wrap(characters),
            things=wrap(things),
        )

    def return_appearance(self, looker):
        """
        This returns the standard appearance for an object created from the
        `set_appearance()` method, which formats the 'appearance_template' and
        overwrites default values if needed.
        """
        return self.set_appearance(looker)


class Object(ObjectParent, DefaultObject):
    """
    This is the root Object typeclass, representing all entities that
    have an actual presence in-game. DefaultObjects generally have a
    location. They can also be manipulated and looked at. Game
    entities you define should inherit from DefaultObject at some distance.

    It is recommended to create children of this class using the
    `evennia.create_object()` function rather than to initialize the class
    directly - this will both set things up and efficiently save the object
    without `obj.save()` having to be called explicitly.

    Note: Check the autodocs for complete class members, this may not always
    be up-to date.

    !!!IMPORTANT CHANGE FOR CHILD CLASSES!!!:
        Sets the class property `class_perm` which acts as typeclass permission
        dict and contains accesstypes as keys and permissions as values. This
        should be set on every child class to restrict access.

        Example:
            class_perm = {"create": "Beginner Builder"}
            - gives "Beginner Builder" "create" permission
            - These should be checked by all functions which let users create
              objects (like the custom 'spawn()' function defined in
              `world.utils.utils`, which therefore should be used to spawn
              objects instead of Evennias default 'spawn()' function.

    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation

     account (Account) - controlling account (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       account above). Use `sessions` handler to get the
                       Sessions directly.
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     has_account (bool, read-only)- will only return *connected* accounts
     contents (list, read only) - returns all objects inside this object
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser
     is_connected (bool, read-only) - True if this object is associated with
                            an Account with any connected sessions.
     has_account (bool, read-only) - True is this object has an associated account.
     is_superuser (bool, read-only): True if this object has an account and that
                        account is a superuser.

    * Handlers available

     aliases - alias-handler: use aliases.add/remove/get() to use.
     permissions - permission-handler: use permissions.add/remove() to
                   add/remove new perms.
     locks - lock-handler: use locks.add() to add new lock strings
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().
     sessions - sessions-handler. Get Sessions connected to this
                object with sessions.get()
     attributes - attribute-handler. Use attributes.add/remove/get.
     db - attribute-handler: Shortcut for attribute-handler. Store/retrieve
            database attributes using self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
            a database entry when storing data

    * Helper methods (see src.objects.objects.py for full headers)

     get_search_query_replacement(searchdata, **kwargs)
     get_search_direct_match(searchdata, **kwargs)
     get_search_candidates(searchdata, **kwargs)
     get_search_result(searchdata, attribute_name=None, typeclass=None,
                       candidates=None, exact=False, use_dbref=None, tags=None, **kwargs)
     get_stacked_result(results, **kwargs)
     handle_search_results(searchdata, results, **kwargs)
     search(searchdata, global_search=False, use_nicks=True, typeclass=None,
            location=None, attribute_name=None, quiet=False, exact=False,
            candidates=None, use_locks=True, nofound_string=None,
            multimatch_string=None, use_dbref=None, tags=None, stacked=0)
     search_account(searchdata, quiet=False)
     execute_cmd(raw_string, session=None, **kwargs))
     msg(text=None, from_obj=None, session=None, options=None, **kwargs)
     for_contents(func, exclude=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, mapping=None,
                  raise_funcparse_errors=False, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     clear_contents()
     create(key, account, caller, method, **kwargs)
     copy(new_key=None)
     at_object_post_copy(new_obj, **kwargs)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False,
            no_superuser_bypass=False, **kwargs)
     filter_visible(obj_list, looker, **kwargs)
     get_default_lockstring()
     get_cmdsets(caller, current, **kwargs)
     check_permstring(permstring)
     get_cmdset_providers()
     get_display_name(looker=None, **kwargs)
     get_extra_display_name_info(looker=None, **kwargs)
     get_numbered_name(count, looker, **kwargs)
     get_display_header(looker, **kwargs)
     get_display_desc(looker, **kwargs)
     get_display_exits(looker, **kwargs)
     get_display_characters(looker, **kwargs)
     get_display_things(looker, **kwargs)
     get_display_footer(looker, **kwargs)
     format_appearance(appearance, looker, **kwargs)
     return_apperance(looker, **kwargs)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_first_save()
     at_cmdset_get(**kwargs) - this is called just before the command handler
                            requests a cmdset from this object. The kwargs are
                            not normally used unless the cmdset is created
                            dynamically (see e.g. Exits).
     at_pre_puppet(account)- (account-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (account-controlled objects only) called just
                            after completing connection account<->object
     at_pre_unpuppet()    - (account-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(account) - (account-controlled objects only) called just
                            after disconnecting account<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_pre_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_post_move(source_location)          - always called after a move has
                        been successfully performed.
     at_pre_object_leave(leaving_object, destination, **kwargs)
     at_object_leave(obj, target_location, move_type="move", **kwargs)
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_pre_object_receive(obj, source_location)
     at_object_receive(obj, source_location, move_type="move", **kwargs) - called when this object receives
                        another object
     at_post_move(source_location, move_type="move", **kwargs)

     at_traverse(traversing_object, target_location, **kwargs) - (exit-objects only)
                              handles all moving across the exit, including
                              calling the other exit hooks. Use super() to retain
                              the default functionality.
     at_post_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_pre_get(getter, **kwargs)
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_pre_give(giver, getter, **kwargs)
     at_give(giver, getter, **kwargs)
     at_pre_drop(dropper, **kwargs)
     at_drop(dropper, **kwargs)          - called when this object has been dropped.
     at_pre_say(speaker, message, **kwargs)
     at_say(message, msg_self=None, msg_location=None, receivers=None, msg_receivers=None, **kwargs)

     at_look(target, **kwargs)
     at_desc(looker=None)

    """

    class_perm = {"create": "Beginner Builder"}

    @classmethod
    def get_default_lockstring(cls, account=None, caller=None, **kwargs):
        if caller is not None:
            id = caller.id
            pid = caller.account.id

            new_obj_lockstring = f"control:id({id}) or pid({pid}) or perm(Developer);"
            new_obj_lockstring += (
                f"attrcreate:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += (
                f"delete:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += (
                f"edit:id({id}) or pid({pid}) or perm(Expert Builder);"
            )
            new_obj_lockstring += f"get:id({id}) or pid({pid}) or all();"
            new_obj_lockstring += (
                f"examine:id({id}) or pid({pid}) or perm(Beginner Builder);"
            )
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"

        elif account is not None:
            pid = account.id

            new_obj_lockstring = f"control:pid({pid}) or perm(Developer);"
            new_obj_lockstring += f"attrcreate:pid({pid}) or perm(Beginner Builder);"
            new_obj_lockstring += f"delete:pid({pid}) or perm(Expert Builder);"
            new_obj_lockstring += f"edit:pid({pid}) or perm(Beginner Builder);"
            new_obj_lockstring += f"get:pid({pid}) or all();"
            new_obj_lockstring += f"examine:pid({pid}) or perm(Beginner Builder);"
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"

        else:
            new_obj_lockstring = f"control:perm(Developer);"
            new_obj_lockstring += f"attrcreate:perm(Beginner Builder);"
            new_obj_lockstring += f"delete:perm(Expert Builder);"
            new_obj_lockstring += f"edit:perm(Beginner Builder);"
            new_obj_lockstring += f"get:all();"
            new_obj_lockstring += f"examine:perm(Beginner Builder);"
            new_obj_lockstring += f"call:all();view:all();"
            new_obj_lockstring += (
                f"iscontainer:false();getfrom:false();getcontainer:false();"
            )
            new_obj_lockstring += f"puppet:false();"
            new_obj_lockstring += f"traverse:false();"
            new_obj_lockstring += f"teleport:false();"
            new_obj_lockstring += f"teleport_here:false();"
        return new_obj_lockstring

    @classmethod
    def create(cls, key, account=None, caller=None, method="create", **kwargs):
        obj, errors = super().create(
            key, account=account, caller=caller, method=method, **kwargs
        )
        return obj, errors

    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add("object", "generic")

    def at_pre_object_receive(self, arriving_object, source_location, **kwargs):
        return False
