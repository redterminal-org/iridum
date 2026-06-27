# world/prototypes/
Prototypes are predefined objects, with all needed attributes, locks and tags
already set. They can be spawned by builders directly. Look at the `help spawn`
command and the [documentation](https://www.evennia.com/docs/latest/Components/Prototypes.html)
about Spawners and Prototypes on the Evennia site.

## Adding Prototype files
To add a prototype file, you must include it in the `__init__.py` package file.
So to add all prototypes from the file `prototypes.py` in this directory, you
have to put a `from .prototypes import *` line into `__init__.py` file.

