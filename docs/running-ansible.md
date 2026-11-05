---
description: How to run Ansible with only the project's collections.
---

# Running Ansible

Ansible looks for collections in `~/.ansible/collections` and the paths in
`ansible.cfg`, so it can load collections the project doesn't list. [`alai
run`](cli.md#alai-run) and [`alai env`](cli.md#alai-env) set the environment
so Ansible loads only the project's collections.

```console
$ alai run ansible-playbook site.yml -i inventory.ini
```

In the example below, a project adds the `ansible.utils` collection and then
runs an ad hoc `ansible` command with a module from that collection:

[Running a module from a collection just added](casts/run.cast){ .cli-cast }

`alai run` first syncs the project as [`alai sync`](cli.md#alai-sync) does.
It then runs the command with environment variables that make Ansible find
only the project's collections. The command's output, signals and exit code
are passed through unchanged, so it behaves as if it was run directly.

`alai env` doesn't sync the project, and prints the environment variables
Ansible needs to see the project's collections without running a command.
Use `alai env` to configure a shell or editor:

```console
$ eval "$(alai env)"
$ ansible-doc community.general.ufw
```

## Which collections Ansible sees

alai doesn't install or choose Ansible, so Ansible must already be on the
`PATH`. How Ansible is installed is up to you, whether through the system
packages, `pip` in a virtual environment, `pipx`, `uv` or something else.

Currently `alai run` sets the following two environment variables:

| Variable | Value | Why |
|---|---|---|
| `ANSIBLE_COLLECTIONS_PATH` | The [collections directory](projects.md#where-collections-are-installed) | Collections load from there, instead of `~/.ansible/collections` or the paths in `ansible.cfg` |
| `ANSIBLE_COLLECTIONS_SCAN_SYS_PATH` | `False` | Collections installed in Python's `site-packages`, such as those the `ansible` package bundles, aren't loaded |

The variables alai sets and their values aren't a public interface, and alai
can change them at any time. The table is only here to explain how `alai
run` and `alai env` work.

With the variables alai sets, Ansible only sees the configured
[collections_dir](alai-toml.md#projectcollections_dir). The variables also
override any `collections_path` set in `ansible.cfg`.

`ansible-playbook` always checks the `collections/` directory next to the
playbook, and no setting turns that off. alai's default `collections_dir` is
that same directory, so keeping the default means Ansible sees only one set
of collections.

alai doesn't check the running Ansible version against the project's
`requires_ansible`, and leaves that check to Ansible. Ansible's
[COLLECTIONS_ON_ANSIBLE_VERSION_MISMATCH](https://docs.ansible.com/projects/ansible/latest/reference_appendices/config.html#collections-on-ansible-version-mismatch)
option sets what happens when a collection's `requires_ansible` doesn't
match the running Ansible. The option can be `warning`, which is the
default, `ignore` or `error`, and can be set in `ansible.cfg`:

```ini
[defaults]
collections_on_ansible_version_mismatch = "error"
```

The option can also be set with an environment variable when running
Ansible:

```console
$ ANSIBLE_COLLECTIONS_ON_ANSIBLE_VERSION_MISMATCH=error \
    alai run ansible-playbook ...
```

## Collections the lock doesn't list

Unlike `alai sync`, `alai run` keeps collections in the collections
directory that `alai.lock` doesn't list, so a collection you're working on
before adding it to the lock isn't deleted. `alai run` warns about those
collections and still lets Ansible use them:

```console
$ alai run ansible-playbook site.yml
warning: Ansible can load collections alai.lock doesn't list here, from collections: my.work
warning: alai run --exact or alai sync removes them
```

To remove those collections as `alai sync` would, run with `--exact`. To
keep them without the warning, run with `--inexact`.

## Options

`alai run` takes the options of `alai sync` that choose what's
installed, for example the [groups](managing-collections.md#groups),
`--locked`, `--frozen`, the upgrade and reinstall options, and the index,
cache and collections directory settings.

| Option | |
|---|---|
| `--no-sync` | Run without locking or installing anything. Can't be used with `--locked` or `--frozen` |
| `--exact` | Remove installed collections `alai.lock` doesn't list before running, rather than warn of them |
| `--inexact` | Keep installed collections `alai.lock` doesn't list without warning of them. Can't be used with `--exact` |

`alai run` needs an `alai.toml`, as without a project there's no collections
directory to point Ansible at.

## In a collection project

In a [collection project](projects.md#collection-project),
`alai run` and `alai env` set two more variables:

| Variable | Value | Why |
|---|---|---|
| `ANSIBLE_TEST_CONTENT_ROOT` | `<collections_dir>/ansible_collections/<namespace>/<name>`, the collection's link | ansible-test needs the collection at a path ending in `ansible_collections/<namespace>/<name>`, which the link gives it wherever the checkout is |
| `PYDEVD_RESOLVE_SYMLINKS` | `1` | The collection is loaded through its link, so debuggers built on debugpy, such as VS Code's, show its files in the checkout rather than through the collection cache |

A playbook project with an
[editable directory](collection-sources.md#an-editable-directory) source
loads that collection through a link too, so `PYDEVD_RESOLVE_SYMLINKS` is set
there as well.

Tools like `ansible-test` can then run from a checkout anywhere, rather than
only in the expected `ansible_collections/<namespace>/<name>` directory:

```console
$ alai run ansible-test sanity --docker
$ alai run ansible-test integration --local my_target
$ alai run ansible-doc my_ns.my_col.my_module
```

!!! warning "`ansible-test units --local` and `--venv` don't work"

    `ansible-test units --local` and every command with `--venv` don't work
    in a collection project, as ansible-test resolves the collection's link.
    Use `--docker` instead.

To run a playbook in the collection's `playbooks/` directory, give its fully
qualified name `<namespace>.<name>.<playbook>` rather than its path:

```console
$ alai run ansible-playbook my_ns.my_col.playbook
```

When a playbook is run by its path, plugin short names in it no longer
resolve to the collection that holds the playbook.

[Running a collection's playbook by name](casts/run-collection-playbook.cast){ .cli-cast }

Ansible loads the collection project through its link in the [collections
directory](projects.md#collection-project), so every path Ansible shows for
the collection is under that directory rather than where you checked it out.
Such a path starts with
`~/.cache/alai/envs/<id>/ansible_collections/<namespace>/<name>/`, and shows
up in tracebacks, verbose output, `ansible-doc`'s output, a plugin's
`__file__` and ansible-test's messages. The files at those paths are the
same files as in your checkout, as Ansible only reaches them through the
link.

## In a shell, CI or an editor

To use the project's collections from a shell or editor, `alai env` prints
the environment variables that tell Ansible where to find them. Pass its
output to your shell's `eval` or the equivalent, and see
[Editors](editors.md) for how to configure a particular editor.

`alai env` never locks or installs collections, so it's quick enough to run
whenever a shell enters the project. To make sure the collections are
installed, run `alai sync` before `alai env`:

```console
$ alai sync && eval "$(alai env)"
```

| Use | How |
|---|---|
| A POSIX shell | `eval "$(alai env)"` |
| fish | `alai env | source` |
| PowerShell | `alai env --output-format pwsh | Out-String | Invoke-Expression` |
| direnv | `eval "$(alai env)"` in `.envrc` |
| A CI step | `alai sync --locked`, then `alai env --output-format dotenv >> "$GITHUB_ENV"` on GitHub Actions |
| An editor | `alai env --output-format dotenv > .vscode/alai.env`, for editors that read `KEY=VALUE` lines (see [Editors](editors.md) for running and debugging Ansible in VS Code) |

`--output-format` can be `sh`, `fish`, `pwsh` or `dotenv`.
