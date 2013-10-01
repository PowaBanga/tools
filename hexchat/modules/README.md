
# Python 3 modules for HexChat

To use these modules you have to add the path to the modules directory
to sys.path of your python addons.
The easiest way is to add them directly inside of the plugins.
If "modules" is inside the HexChat "addons" folder, it could look like this:

    import hexchat
    import sys
    import os
    sys.path.append(os.path.join(
        hexchat.get_info('configdir'), 'addons', 'modules')

Or by setting the environment variable PYTHONPATH to include the path to the
module. More information about that in the [Python Docs][RefPythonPath].

A 3rd. option might be to edit python.c of the HexChat plugin to include the
path automatically and build HexChat yourself.

After that you should be able to import the the python files.

    import tools
    import hooks
    hooks.use_error_context(True)

[RefPythonPath]: http://docs.python.org/3.3/using/cmdline.html#envvar-PYTHONPATH
