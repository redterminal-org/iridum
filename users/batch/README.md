# Batch Code Processor

This directory contains [Batch Code Files](https://www.evennia.com/docs/latest/Components/Batch-Code-Processor.html)
which shoud be placed within a subdirectory with the name of the `account`
making the contibutions and **must** end with `.py` and they are normal Python
files, but have some extra *code marking* features which can be run separately
in `interactive mode. Read the documentation above to write clean and tidy
`Batch Code Files`

These files can only be run by the *superuser* (`@batchcode`) and should be
properly documented for the *superuser* to understand what's happening in these
files.

## Delete old Objects first

They have also to take care about being run multiple times if possible, so they
should delete their changes, before being run a second time!
