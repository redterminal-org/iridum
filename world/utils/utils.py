"""
This file contains some useful utility functions or replacements for functions
from the original Evennia Systems, which should be used instead of the original
functions (like 'spawn' which should be used instead of the Evennia 'spawn'
function.

It contains also some functions for text processing like the 'wrap' or
'wrap_para' functions, which should be used to wrap a single line to a specific
width without breaking words, or 'wrap_para', which will preserve blank lines.

There is also the 'check_typeclass_perm' function, to check if a specific user
or account has access permission to the typeclass of an object. If you ever
want to develop new typeclasses or commands, you should add permission checks
for using typeclasses in your self made commands with this function.

Functions:
    check_typeclass_perm(obj, typeclass, check, default)

    Description: Checks the 'class_perm' dict of a given typeclass for
    specific permissions (you HAVE to add a 'class_perm' dict to your own
    typeclasses at least with the "create" key and the permission string as
    value eg. "Beginner Builder", so "Beginner Builder"s have access to the
    typeclass.

        Args:
        - obj: accessing object
        - typeclass: typeclass or object to access
        - check: the 'key' to check. at least the key "create" should be present
        - default: The default value returned, when no key is found (False)
        Returns:
        bool: Returns "True" if  access is granted otherwise "False"

    wrap(text, width, indent)
        Args:
        - text: Input string to line wrap
        - width: Maximum line width, should be taken from
                 'settings.DEFAULT_WIDTH'
        - indent: Number of spaces the text should be indented at the beginning
                  of each line. Only if needed but should be multiples of 4.
        Returns:
        string: a properly wrapped and indented string with given properties

    wrap_para(text, width)
        Args:
        - text: Input string with multiple blank lines and paragraphs.
        - width: Maximum line width, should be taken from
                 'settings.DEFAULT_WIDTH'
        Returns:
        string: a properly wrapped string with blank lines preserved.

    spawn(*prototypes, caller=None, **kwargs)
        Args:
        - *prototypes: list of prototypes to spawn
        - caller: caller (player or account running the command)
        - **kwargs: Additional parameters
        Returns:
        list of objects: a list of spawned Objects, which has appropriate lock
                         string for 'caller' if given.
"""

#### Imports ####
import textwrap
import re

from evennia.utils.utils import class_from_module
from evennia import settings

_WIDTH = settings.DEFAULT_WIDTH


# Check if an object has permissions to access a typeclass
def check_typeclass_perm(obj, typeclass, check="create", default=False):
    """
    Description: Checks the 'class_perm' dict of a given typeclass for
    specific permissions (you HAVE to add a 'class_perm' dict to your own
    typeclasses at least with the "create" key and the permission string as
    value eg. "Beginner Builder", so "Beginner Builder"s have access to the
    typeclass.

        Args:
        - obj: accessing object
        - typeclass: typeclass or object to access
        - check: the 'key' to check. at least the key "create" should be present
        - default: The default value returned, when no key is found (False)
        Returns:
        bool: Returns "True" if  access is granted otherwise "False"
    """
    try:
        if type(typeclass) is str:
            try:
                typeclass = class_from_module(typeclass)
            except ImportError:
                obj.msg("IMPORT ERROR")
                return False
        typeclass_permission = typeclass.class_perm[check]
        if not obj.is_superuser:
            return obj.permissions.check(typeclass_permission)
        else:
            return True
    except (KeyboardInterrupt, ValueError, AttributeError):
        if obj.is_superuser:
            return True
        return default


# Wraps multiple paragraphs with blank lines
def wrap(text, width=_WIDTH, indent=0):
    """
    wrap(text, width, indent)
        Args:
        - text: Input string to line wrap
        - width: Maximum line width, should be taken from
                 'settings.DEFAULT_WIDTH'
        - indent: Number of spaces the text should be indented at the beginning
                  of each line. Only if needed but should be multiples of 4.
        Returns:
        string: a properly wrapped and indented string with given properties
    """
    text = ' '.join(text.split())
    text = text.strip()
    initial_indent = " " * indent
    return textwrap.fill(
        text,
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=initial_indent,
    )


# For Imports
# alias for 'wrap' function
fill = wrap


# Wrap multiple paragraphs with blank lines preserved
def wrap_para(text, width=_WIDTH, indent=0):
    """
    wrap_para(text, width)
        Args:
        - text: Input string with multiple blank lines and paragraphs.
        - width: Maximum line width, should be taken from
                 'settings.DEFAULT_WIDTH'
        Returns:
        string: a properly wrapped string with blank lines preserved.
    """
    if text is None:
        return ""
    text = text.replace("|/", "\n")
    text = re.sub(r"\n\s*?\n", "\n\n", text)
    split = text.split("\n\n")
    paragraphs = []
    for para in split:
        paragraphs.append(wrap(para, width=width, indent=indent))
    return "\n\n".join(paragraphs)


# Spawn with appropriate lock string
def spawn(*prototypes, caller=None, **kwargs):
    """
    Spawn a number of prototyped objects.

    Args:
        prototypes (str or dict): Each argument should either be a
            prototype_key (will be used to find the prototype) or a full
            prototype dictionary. These will be batched-spawned as one object
            each.
    Keyword Args:
        caller (Object or Account, optional): This may be used by protfuncs to
                                              do access checks.
        prototype_modules (str or list): A python-path to a prototype
                                         module, or a list of such paths. These
                                         will be used to build the global
                                         protparents dictionary accessible by
                                         the input prototypes. If not given, it
                                         will instead look for modules defined
                                         by settings.PROTOTYPE_MODULES.
        prototype_parents (dict): A dictionary holding a custom prototype-parent
                                  dictionary. Will overload same-named prototypes
                                  from prototype_modules.
        only_validate (bool): Only run validation of prototype/parents (no
                              object creation) and return the create-kwargs.
        protfunc_raise_errors (bool): Raise explicit exceptions on a
                                      malformed/not-found protfunc. Defaults to
                                      True.

    Returns:
        object (Object, dict or list): Spawned object(s). If `only_validate` is
                                       given, return a list of the creation
                                       kwargs to build the object(s) without
                                       actually creating it.

    """
    import hashlib
    import time

    from django.conf import settings

    import evennia
    from evennia.objects.models import ObjectDB
    from evennia.prototypes import prototypes as protlib
    from evennia.prototypes.spawner import batch_create_object
    from evennia.prototypes.prototypes import (
        PROTOTYPE_TAG_CATEGORY,
        init_spawn_value,
        value_to_obj,
        value_to_obj_or_any,
    )
    from evennia.utils import logger
    from evennia.utils.utils import class_from_module, make_iter

    _CREATE_OBJECT_KWARGS = ("key", "location", "home", "destination")
    _PROTOTYPE_META_NAMES = (
        "prototype_key",
        "prototype_desc",
        "prototype_tags",
        "prototype_locks",
        "prototype_parent",
    )
    _NON_CREATE_KWARGS = _CREATE_OBJECT_KWARGS + _PROTOTYPE_META_NAMES

    #### Begin of spawn function ####
    # search string (=prototype_key) from input
    prototypes = [
        protlib.search_prototype(prot, require_single=True)[0]
        if isinstance(prot, str)
        else prot
        for prot in prototypes
    ]

    if not kwargs.get("only_validate"):
        # homogenization to be more lenient about prototype format when entering the prototype
        # manually
        prototypes = [protlib.homogenize_prototype(prot) for prot in prototypes]

    # overload module's protparents with specifically given protparents
    # we allow prototype_key to be the key of the protparent dict, to allow for module-level
    # prototype imports. We need to insert prototype_key in this case
    custom_protparents = {}
    for key, protparent in kwargs.get("prototype_parents", {}).items():
        key = str(key).lower()
        protparent["prototype_key"] = str(protparent.get("prototype_key", key)).lower()
        custom_protparents[key] = protlib.homogenize_prototype(protparent)

    objs = []
    objsparams = []
    for prototype in prototypes:
        # run validation and homogenization of provided prototypes
        protlib.validate_prototype(
            prototype, None, protparents=custom_protparents, is_prototype_base=True
        )
        prot = evennia.prototypes.spawner._get_prototype(
            prototype,
            protparents=custom_protparents,
            uninherited={"prototype_key": prototype.get("prototype_key")},
        )
        if not prot:
            continue

        # extract the keyword args we need to create the object itself. If we get a callable,
        # call that to get the value (don't catch errors)
        create_kwargs = {}
        init_spawn_kwargs = dict(
            caller=caller,
            prototype=prototype,
            protfunc_raise_errors=kwargs.get("protfunc_raise_errors", True),
        )

        # we must always add a key, so if not given we use a shortened md5 hash. There is a (small)
        # chance this is not unique but it should usually not be a problem.
        val = prot.pop(
            "key",
            "Spawned-{}".format(
                hashlib.md5(bytes(str(time.time()), "utf-8")).hexdigest()[:6]
            ),
        )
        create_kwargs["db_key"] = init_spawn_value(val, str, **init_spawn_kwargs)

        val = prot.pop("location", None)
        create_kwargs["db_location"] = init_spawn_value(
            val, value_to_obj, **init_spawn_kwargs
        )

        val = prot.pop("home", None)
        if val:
            create_kwargs["db_home"] = init_spawn_value(
                val, value_to_obj, **init_spawn_kwargs
            )
        else:
            try:
                create_kwargs["db_home"] = init_spawn_value(
                    settings.DEFAULT_HOME, value_to_obj, **init_spawn_kwargs
                )
            except ObjectDB.DoesNotExist:
                # settings.DEFAULT_HOME not existing is common for unittests
                pass

        val = prot.pop("destination", None)
        create_kwargs["db_destination"] = init_spawn_value(
            val, value_to_obj, **init_spawn_kwargs
        )

        # we need the 'true' path to the typeclass (not its alias), so we make sure to load the typeclass
        # and use its path directly
        val = prot.pop("typeclass", settings.BASE_OBJECT_TYPECLASS)
        typeclass = class_from_module(
            init_spawn_value(val, str, **init_spawn_kwargs), settings.TYPECLASS_PATHS
        )
        create_kwargs["db_typeclass_path"] = (
            f"{typeclass.__module__}.{typeclass.__name__}"
        )

        # extract calls to handlers
        val = prot.pop("permissions", [])
        permission_string = init_spawn_value(val, make_iter, **init_spawn_kwargs)
        lock_string = typeclass.get_default_lockstring(caller=caller)
        val = prot.pop("locks", "")
        lock_string = lock_string + init_spawn_value(val, str, **init_spawn_kwargs)
        val = prot.pop("aliases", [])
        alias_string = init_spawn_value(val, make_iter, **init_spawn_kwargs)

        val = prot.pop("tags", [])
        tags = []
        for tag, category, *data in val:
            tags.append(
                (
                    init_spawn_value(tag, str, **init_spawn_kwargs),
                    category,
                    data[0] if data else None,
                )
            )

        prototype_key = prototype.get("prototype_key", None)
        if prototype_key:
            # we make sure to add a tag identifying which prototype created this object
            tags.append((prototype_key, PROTOTYPE_TAG_CATEGORY))

        val = prot.pop("exec", "")
        execs = init_spawn_value(val, make_iter, **init_spawn_kwargs)

        # extract ndb assignments
        nattributes = dict(
            (
                key.split("_", 1)[1],
                init_spawn_value(val, value_to_obj, **init_spawn_kwargs),
            )
            for key, val in prot.items()
            if key.startswith("ndb_")
        )

        # the rest are attribute tuples (attrname, value, category, locks)
        val = make_iter(prot.pop("attrs", []))
        attributes = []
        for attrname, value, *rest in val:
            attributes.append(
                (
                    attrname,
                    init_spawn_value(value, **init_spawn_kwargs),
                    rest[0] if rest else None,
                    rest[1] if len(rest) > 1 else None,
                )
            )

        simple_attributes = []
        for key, value in (
            (key, value) for key, value in prot.items() if not (key.startswith("ndb_"))
        ):
            # we don't support categories, nor locks for simple attributes
            if key in _PROTOTYPE_META_NAMES:
                continue
            else:
                simple_attributes.append(
                    (
                        key,
                        init_spawn_value(
                            value, value_to_obj_or_any, **init_spawn_kwargs
                        ),
                        None,
                        None,
                    )
                )

        attributes = attributes + simple_attributes
        attributes = [tup for tup in attributes if tup[0] not in _NON_CREATE_KWARGS]
        # pack for call into _batch_create_object
        objsparams.append(
            (
                create_kwargs,
                permission_string,
                lock_string,
                alias_string,
                nattributes,
                attributes,
                tags,
                execs,
            )
        )

    if kwargs.get("only_validate"):
        return objsparams
    objs = batch_create_object(*objsparams)
    for obj in objs:
        if not obj:
            continue

        if getattr(obj, "after_spawn", None):
            obj.after_spawn(caller=caller)
        if spawn_hook := getattr(obj, "at_object_post_spawn", None):
            spawn_hook()
        obj.save()

    if kwargs.get("only_validate"):
        return objsparams

    # return evennia.prototypes.spawner.batch_create_object(*objsparams)
    return objs
