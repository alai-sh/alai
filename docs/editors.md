---
description: How to set up an editor to run and debug Ansible with alai.
---

# Editors

This page covers how to set up an editor to run and debug Ansible against a
project's collections.

!!! note "Expect some rough edges"

    Running and debugging Ansible from an editor involves the editor,
    Python's debugger, ansible-core, ansible-test and alai, so it's a
    complex area. What's here should work, but don't be surprised if
    something doesn't. Please report any problems in the
    [issue tracker](https://github.com/alai-sh/alai/issues), so the
    docs can cover them and alai can fix what it can.

When an editor runs or debugs Ansible, it needs to set the same
environment variables as [`alai run`](running-ansible.md), so that Ansible
only loads the project's collections. alai doesn't change editor settings
itself, as editor settings are usually personal and merging into each
editor's configuration would be very difficult. Instead,
`alai env --output-format dotenv` prints the environment variables Ansible
needs in a file format that editors can load.

## Visual Studio Code

When using VS Code, the Python debugger has to run in the same Python
environment that ansible-core is installed in. alai is usually installed as
a uv tool in an environment of its own, so VS Code launches the debug task
with an environment file that `alai env` writes for the project.

### Running a playbook under the debugger

`.vscode/tasks.json` installs the project's collections and writes the
variables into `./.vscode/alai.env` before each launch:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "alai env",
      "type": "shell",
      "command": "alai sync && alai env --output-format dotenv > ${workspaceFolder}/.vscode/alai.env",
      "presentation": { "reveal": "silent" }
    }
  ]
}
```

`.vscode/launch.json` runs `ansible-playbook` with the `alai.env` values,
under the Python debugger:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "ansible-playbook site.yml",
      "type": "debugpy",
      "request": "launch",
      "module": "ansible",
      "args": ["playbook", "site.yml", "-i", "inventory.ini"],
      "cwd": "${workspaceFolder}",
      "envFile": "${workspaceFolder}/.vscode/alai.env",
      "preLaunchTask": "alai env",
      "console": "integratedTerminal"
    }
  ]
}
```

- `"module": "ansible"` runs ansible-core's `python -m ansible`, whose
  first argument names the command: `playbook` for `ansible-playbook`,
  `adhoc` for `ansible`, `doc` for `ansible-doc`, `inventory` for
  `ansible-inventory`, and so on.
- In a [collection project](projects.md#collection-project), give a
  playbook in the collection by its fully qualified name rather than its
  path, so the playbook's short names for the collection's content resolve.
  For example, use `"args": ["playbook", "my_ns.my_col.site"]`. See
  [In a collection project](running-ansible.md#in-a-collection-project).
- The launch runs with the Python interpreter selected for the workspace,
  which must be the one ansible-core is installed in, such as the project's
  `.venv`. Set `"python"` in the configuration to choose another.
- `alai env` doesn't install anything, so the task runs `alai sync` first.
  The file `.vscode/alai.env` is specific to that machine, so add it to
  `.gitignore`.
- To step into ansible-core's controller code, add `"justMyCode": false`.
  Modules aren't debugged by this launch, as
  [What breakpoints hit](#what-breakpoints-hit) explains.

### Attaching to `alai run`

To start Ansible with `alai run` instead, have it run Python under
debugpy, waiting for the editor:

```console
$ alai run python -m debugpy --listen 5678 --wait-for-client -m ansible playbook site.yml -i inventory.ini
```

Then attach the editor to it with a configuration such as:

```json
{
  "name": "Attach to alai run",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "localhost", "port": 5678 }
}
```

The `python` in that command is whichever is first on `PATH`, so first
activate the environment ansible-core is in and install debugpy into it.

### What breakpoints hit

Breakpoints hit in code that runs in the `ansible-playbook` process, such
as filter, lookup, action, callback and inventory plugins and the
`module_utils` they import. Breakpoints in modules don't, as Ansible runs
each module in a process of its own.

To debug modules, use
[ansible-test](#debugging-with-ansible-test), which has
modules connect back to the debugger.

In a [collection project](projects.md#collection-project), Ansible loads
the collection through a link in its collections directory, as it does a
collection from an
[editable directory](collection-sources.md#an-editable-directory). Although
that path differs from your checkout, breakpoints set in your checkout still
hit, as the debugger matches them on the real path the link leads to.

The call stack shows the file's path in your checkout when you use
`alai run` or `alai env`, but `ansible-test` currently shows the path in the
collections directory that Ansible loaded it from. Module breakpoints
have further limitations described in
[Debugging with ansible-test](#debugging-with-ansible-test).

### Debugging with ansible-test

To debug the Python modules that ansible-test launches, use its
`--dev-debug-on-demand` option. With that option, ansible-test sets up
Ansible and the modules it runs to connect back to the debugger
automatically when they start.

A launch configuration for `--dev-debug-on-demand` is the same as any
other. Set `args` to `test ... --dev-debug-on-demand`, and use the `envFile`
and `preLaunchTask` defined above:

```json
{
  "name": "ansible-test shell",
  "type": "debugpy",
  "request": "launch",
  "module": "ansible",
  "args": ["test", "shell", "--dev-debug-on-demand"],
  "envFile": "${workspaceFolder}/.vscode/alai.env",
  "preLaunchTask": "alai env",
  "console": "integratedTerminal"
}
```

With ansible-core 2.21 and older, `debugpy` must be installed in the same
Python environment as ansible-core. Later versions automatically use the copy
bundled with VS Code.

The following table describes the different modes that ansible-test can use to
debug collection code and what does and does not work:

| `args` | Use it for | Controller code, such as action and filter plugins | Modules |
|---|---|---|---|
| `test shell` | Running Ansible commands by hand on this machine | Set in your checkout | Set in your checkout, when the command is run with `alai run` |
| `test integration` | Debugging an integration target as it runs | Set in your checkout | Doesn't work yet: run the module from `test shell` with `alai run` instead |
| `test shell`, `test integration` with `--docker` or `--remote` | The same, in a container or on another host | Set in the collections directory | Doesn't work yet |
| `test windows-integration`, `test network-integration` | Integration targets on Windows or network hosts | Set in your checkout | ansible-test doesn't connect these hosts to the debugger |

Commands with `--venv` and `test units --local` don't work in a
collection project, as
[Running Ansible](running-ansible.md#in-a-collection-project) explains.

#### `ansible-test shell`

`ansible-test shell` opens a shell that can be used to launch subsequent
Ansible commands with a debugger attached. As `ansible-test` clears environment
variables like the ones `alai.env` sets, run any Ansible
commands in this shell through `alai run ...`.

#### `ansible-test integration`

Unlike `ansible-test shell`, `ansible-test integration` runs the given
integration test target under the debugger rather than opening a shell for
any command. For example,
`"args": ["test", "integration", "--dev-debug-on-demand", "my_target"]`
runs the `tests/integration/targets/my_target` target with the debugger
attached.

alai can't hook into the integration run, so module breakpoints don't hit,
and the call stack for controller-side plugins shows the path in the collections
directory rather than your checkout. To debug a module the
target uses, run it from [`ansible-test shell`](#ansible-test-shell) with
`alai run` instead.

### Troubleshooting ansible-test debugging

If breakpoints don't hit, check the following from inside the shell that
ansible-test set up:

| Check | Expected | If not |
|---|---|---|
| `command -v ansible` | A path in ansible-test's temporary directory, `/tmp/ansible-test-…-injector/ansible` | Something put another `ansible` first, usually the terminal's environment activation. Run `deactivate`, or see below |
| `echo "$ANSIBLE_TEST_DEBUGGER_CONFIG"` | JSON with `-m debugpy --connect localhost:<port>` | ansible-test didn't detect the debugger, so it wasn't started from the launch configuration. Add `"-v"` to the launch's `args`, and ansible-test says `Enabling on-demand debugging.` when it does, and `Debugging disabled because no debugger was detected.` when it doesn't |
| `echo "$ANSIBLE_COLLECTIONS_PATH"` | The collections directory `alai env` prints | Something in the shell's startup files, such as `~/.bashrc`, set its own. Run the command with `alai run` |

To tell a process that isn't connected from a breakpoint that doesn't
match, put `import debugpy; debugpy.breakpoint()` in the code. It stops
only when the process is connected to the debugger.

To stop the terminal activation, turn it off for the workspace in
`.vscode/settings.json`:

```json
{
  "python.terminal.activateEnvironment": false
}
```

The selected environment is still used to run and debug Python, but
terminals VS Code opens no longer activate it. Commands typed into those
terminals, such as `ansible`, `pytest` or `alai run ansible-playbook …`,
then use whatever `PATH` finds. VS Code has no way to turn off the
environment activation for a single launch configuration.

Another option is to set the Python Environments extension's
`python-envs.terminal.autoActivationType` to `shellStartup`. With
`shellStartup`, the environment is activated as a terminal starts rather
than typed into the terminal as a command, so it doesn't override
ansible-test's `ansible`. `python-envs.terminal.autoActivationType` is a
machine-wide setting and can't be set in `.vscode/settings.json` for the
workspace.

For more detail from debugpy, add `"logToFile": true` to the launch
configuration to write its logs to the extension's directory. In the shell,
export `DEBUGPY_LOG_DIR=/tmp/debugpy-logs` before running a command.

### Other tools

The Python extension can load the same `alai.env` file for its terminals
and test runs when `python.envFile` is set to
`${workspaceFolder}/.vscode/alai.env`.
