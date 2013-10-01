
# Python 3 modules for HexChat

To use these modules you have to add the path to the modules directory
to sys.path of your python addons.
The easiest way is to add them directly inside of the plugins.
If "modules" is inside the HexChat "addons" folder, it could look like this:

```python
import hexchat
import sys
import os
sys.path.append(os.path.join(
    hexchat.get_info('configdir'), 'addons', 'modules')
```

Or by setting the environment variable PYTHONPATH to include the path to the
module.

More information about that in the [Python Docs][RefPythonPath].

A 3rd. option might be to edit python.c of the HexChat plugin to include the
path and build HexChat yourself.

After that you should be able to import the the python modules.

```python
import hexchat
import tools
import hooks
hooks.use_error_context(True)
```

## Examples

A simple `/reverse` command.

```python
@hooks.command('REVERSE')
def reverse(ctx, word, word_eol, userdata):
    if len(word) <= 1:
        ctx.prnt('Usage: /reverse <text>')
        return hexchat.EAT_HEXCHAT
    
    rtext = word_eol[1][::-1]
    ctx.command('SAY {}'.format(rtext))
```

Other hooks work as well.

```python
@hooks.timer(1000, userdata={'value': 0})
def task(ctx, userdata):
    userdata['value'] += 1
    ctx.prnt('Task #{}'.format(userdata['value']))
    return hooks.STOP_TIMER # or simply use 0 (stop) or 1 (continue) like always

@hooks.server('PRIVMSG')
def privmsg(ctx, word, word_eol, userdata):
    ctx.prnt(word_eol[0])
```

You can specify channel commands, e.g. `!slap`.
This is hooked into the text event "Channel Message".

```python
@hooks.chancmd('!', 'slap')
def slap(ctx, nick, text, mod, idf, userdata):
    words = text.split(None, 1)
    if len(words) > 1:
        target = words[1]
    else:
        target = nick
    ctx.command('ME slaps {} around'.format(target))
```

Channel commands using `hooks.prefixer()`

```python
prefixed = hooks.prefixer('!')

@prefixed('slap')
def slap(ctx, nick, text, mod, idf, userdata):
    words = text.split(None, 1)
    if len(words) > 1:
        target = words[1]
    else:
        target = nick
    ctx.command('ME slaps {} around'.format(target))

@prefixed('reverse')
def reverse(ctx, nick, text, mod, idf, userdata):
    words = text.split(None, 1)
    if len(words) > 1:
        target = words[1]
    else:
        target = nick
    ctx.command('SAY {}'.format(target[::-1]))
```

`hooks.provide()` is an experimental feature to add a simple way to provide an
interface to your addon for other addons to use.

In one addon you provide the command `/testdata`, that then can be used by
other addons to request data from this addon.

```python
@hooks.provide('TESTDATA')
def testdata(ctx, remote, word, word_eol, userdata):
    
    ctx.prnt(word_eol[0])
    remote.send('data set 1')
    remote.send('data set 2')
    remote.send('data set 3')
    return hexchat.EAT_HEXCHAT
```

Other addons then can use this provided command using `tools.request_data()`.

```python
def results_received(ctx, result_sets):
    for result in result_sets:
        ctx.prnt(result)

@hooks.command('TESTME')
def testget(ctx, word, word_eol, userdata):
    ctx.prnt('Requesting Data')
    tools.request_data('TESTDATA', results_received, 'additional parameters')
    return hexchat.EAT_HEXCHAT
```

[RefPythonPath]: http://docs.python.org/3.3/using/cmdline.html#envvar-PYTHONPATH
