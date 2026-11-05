---
description: Every alai command and the options it takes.
---

<!-- Written by python -m cli_recorder reference from alai's argument parser. Edit the help there, not here. -->

# CLI reference

Every alai command, with what it does and the options it takes, as
`alai <command> --help` shows them. The recordings were made against a
local index when these docs were built, so their output is alai's own,
though the collections and timings are only examples.

## alai

A fast package manager for Ansible collections.

```console
$ alai [OPTIONS] <COMMAND>
```

| Command | Description |
|---|---|
| [`add`](#alai-add) | Add collections to alai.toml, then lock and sync |
| [`collection`](#alai-collection) | Install, uninstall and list collections outside the project's requirements and alai.lock |
| [`config`](#alai-config) | Inspect alai's settings |
| [`env`](#alai-env) | Print the environment variables alai run sets, for a shell to use |
| [`find`](#alai-find) | Find which collections have a plugin, role or playbook |
| [`lock`](#alai-lock) | Resolve the project's collections into alai.lock |
| [`remove`](#alai-remove) | Remove collections from alai.toml, then lock and sync |
| [`run`](#alai-run) | Run a command, such as ansible-playbook, with the project's collections |
| [`generate-shell-completion`](#alai-generate-shell-completion) | Print the script that enables Tab completion in a shell |
| [`sync`](#alai-sync) | Install the collections alai.lock lists, locking first if needed |

### Options

| Option | Description |
|---|---|
| `-V`, `--version` | Show the alai version and exit |

## Global options

Every command takes these, before or after its name.

| Option | Description |
|---|---|
| `--project DIR` | Find the project from DIR |
| `--config-file PATH` | Read only this config file |
| `--no-config` | Don't read any config files |
| `--cache-dir DIR` | The cache directory |
| `-v`, `--verbose` | Show debug detail, and with `-vv` trace each step too |
| `-q`, `--quiet` | Only show errors |
| `--color {auto,always,never}` | When to color the output, by default only on a terminal (env: `NO_COLOR`, `FORCE_COLOR`) |
| `--no-progress` | Don't draw progress while working (env: `ALAI_NO_PROGRESS`) |

## alai add

Add collections to the project's alai.toml, then lock and install them. A collection given by name alone is written as >= the version locked for it. A directory given with a /, such as ./ns.col, adds the collection it holds, and a [project.sources] entry says where to find it. The collection's name is read from its galaxy.yml, or from MANIFEST.json for a built one. A built collection's tarball, by path or https:// URL, is added the same way, and so is a git repository given as git+URL[@REV][#subdirectory=DIR&version=VERSION]. A directory given with `--editable` is linked to rather than copied, so edits there are seen. Every other line of alai.toml is left as it is.

[Adding collections to a new project](casts/add.cast){ .cli-cast }

[Upgrading a locked collection while adding another](casts/add-upgrade.cast){ .cli-cast }

Here `ansible.posix` is locked at 2.1.0, and 2.2.2 has since been released.
{: .cli-cast-description }

Adding `cisco.ios` leaves `ansible.posix` at 2.1.0. `cisco.ios` needs `ansible.posix>=2.0.0`, which 2.1.0 still satisfies, and alai doesn't change a locked version that still works, even when a newer one is out.
{: .cli-cast-description }

Adding `community.general -P ansible.posix` adds `community.general` and upgrades `ansible.posix`, and only `ansible.posix`, to the newest version that fits, 2.2.2. `-P` takes the name of the collection to upgrade, which needn't be one being added: here it's already in `alai.toml`. Give `-P` again to upgrade more than one, or use `-U` to upgrade every collection.
{: .cli-cast-description }

```console
$ alai add [OPTIONS] [REQUIREMENT ...]
```

### Arguments

| Argument | Description |
|---|---|
| `REQUIREMENT` | A collection such as ansible.posix or 'cisco.ios>=11', a directory holding one such as ../ns.col, a built collection's tarball by path or URL, or a git repository such as git+https://github.com/org/repo@v1.0.0 |

### Options

| Option | Description |
|---|---|
| `--editable DIR` | Add the collection in DIR as editable, so it's linked rather than copied and edits there are seen (can be repeated) |
| `--group NAME` | Add them in group NAME rather than the project. Can't be used with `--dev` |
| `--dev` | The same as `--group dev`. Can't be used with `--group` |
| `--no-sync` | Lock, but don't install. Can't be used with `--frozen` |
| `--frozen` | Only edit alai.toml, without locking or installing. Can't be used with `--no-sync` |
| `--locked` | Resolve, and exit 1 without writing anything if alai.lock is missing or would change |
| `-U`, `--upgrade` | Choose the newest versions that fit, ignoring alai.lock |
| `-P`, `--upgrade-collection NAME` | Choose the newest version of collection NAME that fits (can be repeated) |
| `--upgrade-group NAME` | Choose the newest version of every collection group NAME lists that fits (can be repeated) |
| `--reinstall` | Reinstall every collection, even those already at the right version |
| `--reinstall-collection NAME` | Reinstall collection NAME, even if it's already at the right version (can be repeated) |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |
| `--link-mode {auto,clone,hardlink,copy,symlink}` | How files get from the cache into the collections directory |
| `--offline`, `--no-offline` | Use only what's cached, without connecting to any index |
| `--index NAME=URL` | An index to resolve from, before those in config files (can be repeated) |
| `--default-index [NAME=]URL` | Replace the default index |

Also takes the [global options](#global-options).

## alai collection

Install, uninstall and list collections in the collections directory by hand, as uv pip does for packages. Installing and uninstalling don't use or change the project's requirements or alai.lock, and the next alai sync puts the collections directory back as the lock has it. When the project has an alai.toml, its settings still apply, such as where collections are installed. Listing compares what's installed with alai.lock.

```console
$ alai collection [OPTIONS] <COMMAND>
```

| Command | Description |
|---|---|
| [`install`](#alai-collection-install) | Install collections and what they need |
| [`uninstall`](#alai-collection-uninstall) | Uninstall collections |
| [`list`](#alai-collection-list) | List the installed collections |
| [`path`](#alai-collection-path) | Show where a collection's files are on disk |

Also takes the [global options](#global-options).

## alai collection install

Install collections and what they need into the collections directory, keeping installed versions that fit. Nothing else is removed. Outside a project there's no collections directory to use, so `--collections-dir` or the collections_dir setting has to say where.

[Installing into a project's collections directory](casts/collection-install.cast){ .cli-cast }

An `alai.toml`, even an empty one, marks the project's directory, and collections are installed into `collections/` beside it.
{: .cli-cast-description }

[Installing from a directory inside the project](casts/collection-install-subdirectory.cast){ .cli-cast }

alai looks for the project from the current directory upwards, so run from `playbooks/`, it finds the `alai.toml` above and installs into the project's `collections/`, not one in `playbooks/`.
{: .cli-cast-description }

[Installing where there's only an ansible.cfg](casts/collection-install-ansible-cfg.cast){ .cli-cast }

An `ansible.cfg` doesn't mark a project, only an `alai.toml` does. Without one, alai names the nearest `ansible.cfg` or `galaxy.yml` it passed, as the directory most likely to be the project's root. An empty `alai.toml` there makes it one.
{: .cli-cast-description }

[Installing outside a project](casts/collection-install-outside.cast){ .cli-cast }

With no `alai.toml` in the current directory or above it, there's no project, and alai won't guess where to install. `--collections-dir` says where.
{: .cli-cast-description }

```console
$ alai collection install [OPTIONS] [REQUIREMENT ...]
```

### Arguments

| Argument | Description |
|---|---|
| `REQUIREMENT` | A collection such as ansible.posix or 'cisco.ios>=11', a directory holding one such as ../ns.col, a built collection's tarball by path or https:// URL, or a git repository given as git+URL[@REV][#subdirectory=DIR&version=VERSION]. A directory is copied again every time |

### Options

| Option | Description |
|---|---|
| `-e`, `--editable DIR` | Install the source or built collection in DIR as a link to it, so edits there are seen (can be repeated) |
| `-U`, `--upgrade` | Choose the newest versions that fit, ignoring alai.lock |
| `-P`, `--upgrade-collection NAME` | Choose the newest version of collection NAME that fits (can be repeated) |
| `--reinstall` | Reinstall every collection, even those already at the right version |
| `--reinstall-collection NAME` | Reinstall collection NAME, even if it's already at the right version (can be repeated) |
| `--keep-unversioned` | Treat an installed collection whose version can't be read as the version asked for, rather than replace it, such as a source checkout with no MANIFEST.json |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |
| `--link-mode {auto,clone,hardlink,copy,symlink}` | How files get from the cache into the collections directory |
| `--offline`, `--no-offline` | Use only what's cached, without connecting to any index |
| `--index NAME=URL` | An index to resolve from, before those in config files (can be repeated) |
| `--default-index [NAME=]URL` | Replace the default index |

Also takes the [global options](#global-options).

## alai collection uninstall

Uninstall collections from the collections directory. What they depend on stays. A collection is given by its name, even one installed from a directory, a tarball or a git repository. Outside a project there's no collections directory to use, so `--collections-dir` or the collections_dir setting has to say where.

[Uninstalling from a project's collections directory](casts/collection-uninstall.cast){ .cli-cast }

Only the collections named are uninstalled: the collections `cisco.ios` needed stay installed.
{: .cli-cast-description }

[Uninstalling a collection outside a project](casts/collection-uninstall-outside.cast){ .cli-cast }

```console
$ alai collection uninstall [OPTIONS] NAME [NAME ...]
```

### Arguments

| Argument | Description |
|---|---|
| `NAME` | A collection name, such as ansible.posix, not the directory, tarball or git URL it was installed from |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |
| `--link-mode {auto,clone,hardlink,copy,symlink}` | How files get from the cache into the collections directory |

Also takes the [global options](#global-options).

## alai collection list

List the collections in the collections directory, whatever installed them. When the project has an alai.lock, each is shown as locked, not in it, installed differently, or locked but not installed. Outside a project there's no collections directory to use, so `--collections-dir` or the collections_dir setting has to say where.

[Listing a project's collections against its lock](casts/collection-list.cast){ .cli-cast }

`cisco.ios` and what it needs are locked. `community.docker` was installed by hand, `ansible.posix` was installed by hand at an older version, and `ansible.utils` was uninstalled, so `alai sync` would change all three.
{: .cli-cast-description }

```console
$ alai collection list [OPTIONS]
```

### Options

| Option | Description |
|---|---|
| `--output-format {text,json}` | Text, the default, or json for scripts |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |

Also takes the [global options](#global-options).

## alai collection path

Show where each collection's files are on disk, for tools that read them such as a documentation viewer. alai uses the first copy it finds, checking in order the collection project's own checkout, the collections directory, the version in alai.lock and the newest version in the cache. If none of them has the collection, alai downloads the latest version from the indexes into the cache. The files for ansible.builtin and eda.builtin come from the latest ansible-core or ansible-rulebook release on the Python index. With `--output-format` json, NAME can be left out to show only the project's own collection.

```console
$ alai collection path [OPTIONS] [NAME ...]
```

### Arguments

| Argument | Description |
|---|---|
| `NAME` | A collection, such as community.general |

### Options

| Option | Description |
|---|---|
| `--no-download` | Only use what's already on disk, without downloading anything or checking the indexes for a newer version |
| `--output-format {text,json}` | Text, the default, or json for scripts |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |
| `--offline`, `--no-offline` | Use only what's cached, without connecting to any index |
| `--index NAME=URL` | An index to resolve from, before those in config files (can be repeated) |
| `--default-index [NAME=]URL` | Replace the default index |

Also takes the [global options](#global-options).

## alai config

Inspect alai's settings.

```console
$ alai config [OPTIONS] <COMMAND>
```

| Command | Description |
|---|---|
| [`show`](#alai-config-show) | Show the resolved settings and where they came from |

Also takes the [global options](#global-options).

## alai config show

Show the project, config files and settings alai resolves from the current directory. With KEY, print only that setting's value, for scripts.

[Showing the settings in effect](casts/config-show.cast){ .cli-cast }

```console
$ alai config show [OPTIONS] [key]
```

### Arguments

| Argument | Description |
|---|---|
| `key` | A setting named as in alai.toml, such as link_mode or project.collections_dir |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |
| `--link-mode {auto,clone,hardlink,copy,symlink}` | How files get from the cache into the collections directory |
| `--offline`, `--no-offline` | Use only what's cached, without connecting to any index |
| `--index NAME=URL` | An index to resolve from, before those in config files (can be repeated) |
| `--default-index [NAME=]URL` | Replace the default index |

Also takes the [global options](#global-options).

## alai env

Print the environment variables that make Ansible load collections from the project's collections directory and nowhere else, as alai run sets them, so eval "$(alai env)" sets them in a shell. Nothing is locked or installed, but a warning says when the collections directory doesn't match alai.lock.

```console
$ alai env [OPTIONS]
```

### Options

| Option | Description |
|---|---|
| `--output-format {sh,fish,pwsh,dotenv}` | Sh for POSIX shells, fish or pwsh for fish and PowerShell, or dotenv for KEY=VALUE lines in env files. The default is fish when SHELL is fish, and sh otherwise |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |
| `--index NAME=URL` | An index to resolve from, before those in config files (can be repeated) |
| `--default-index [NAME=]URL` | Replace the default index |

Also takes the [global options](#global-options).

## alai find

Find plugins, roles and playbooks by name in the files of the installed collections and in the indexes' plugin lists. The ones in installed collections, ansible.builtin and eda.builtin are listed first. QUERY is part of a name (user finds win_user too), a glob ('*_info', 'community.general.*') or a FQCN. A FQCN shows that plugin's details, such as where its redirects lead and how to install it.

[Finding plugins](casts/find.cast){ .cli-cast }

`community.general` 11.0.0 is installed. Its `docker_container` moved in 2.0.0: it redirects to `community.docker`'s, so a playbook that uses either name keeps working once `community.docker` is installed. `to_` matches part of each filter's name, underlined on a terminal.
{: .cli-cast-description }

[A plugin's details and where its redirects lead](casts/find-detail.cast){ .cli-cast }

```console
$ alai find [OPTIONS] QUERY
```

### Arguments

| Argument | Description |
|---|---|
| `QUERY` | Part of a name, a glob, or a FQCN |

### Options

| Option | Description |
|---|---|
| `-t`, `--type TYPE` | Only this type, as ansible-doc `-t` names them (module, filter, lookup...) or role or playbook (can be repeated) |
| `-x`, `--exact` | Match whole names only, not names that contain QUERY |
| `--installed` | Only plugins in installed collections, ansible.builtin and eda.builtin |
| `-a`, `--all` | Also list removed plugins and aliases of listed plugins that match part of a name, as ones named exactly always are |
| `--no-index` | Search only installed collections, ansible.builtin and eda.builtin, not the indexes' plugin lists |
| `--refresh` | Read the installed collections' plugins again, rather than from the cache, as after editing one |
| `--limit N` | List at most N matches with installed ones first, or 0 for all. The default is 20 on a terminal, and all when the output is piped or `--output-format` is json |
| `--output-format {text,json}` | Text, the default, or json for scripts |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |
| `--offline`, `--no-offline` | Use only what's cached, without connecting to any index |
| `--index NAME=URL` | An index to resolve from, before those in config files (can be repeated) |
| `--default-index [NAME=]URL` | Replace the default index |

Also takes the [global options](#global-options).

## alai lock

Resolve the collections the project's alai.toml and its groups ask for to one version of each, and write them to alai.lock beside it. Versions already in alai.lock are kept while they still fit.

[Upgrading one collection, then the rest](casts/lock.cast){ .cli-cast }

```console
$ alai lock [OPTIONS]
```

### Options

| Option | Description |
|---|---|
| `--check` | Resolve without writing alai.lock, and exit 1 if it's missing or would change |
| `-U`, `--upgrade` | Choose the newest versions that fit, ignoring alai.lock |
| `-P`, `--upgrade-collection NAME` | Choose the newest version of collection NAME that fits (can be repeated) |
| `--upgrade-group NAME` | Choose the newest version of every collection group NAME lists that fits (can be repeated) |

### Settings

| Option | Description |
|---|---|
| `--offline`, `--no-offline` | Use only what's cached, without connecting to any index |
| `--index NAME=URL` | An index to resolve from, before those in config files (can be repeated) |
| `--default-index [NAME=]URL` | Replace the default index |

Also takes the [global options](#global-options).

## alai remove

Remove collections from the project's alai.toml, then lock and sync, which uninstalls what nothing needs any more. A collection is given by its name, even one added from a directory, a tarball or a git repository. Its [project.sources] entry is removed with it, and every other line of alai.toml is left as it is.

[Removing a collection](casts/remove.cast){ .cli-cast }

```console
$ alai remove [OPTIONS] NAME [NAME ...]
```

### Arguments

| Argument | Description |
|---|---|
| `NAME` | A collection name, such as ansible.posix, not the directory, tarball or git URL it was added from |

### Options

| Option | Description |
|---|---|
| `--group NAME` | Remove them in group NAME rather than the project. Can't be used with `--dev` |
| `--dev` | The same as `--group dev`. Can't be used with `--group` |
| `--no-sync` | Lock, but don't install. Can't be used with `--frozen` |
| `--frozen` | Only edit alai.toml, without locking or installing. Can't be used with `--no-sync` |
| `--locked` | Resolve, and exit 1 without writing anything if alai.lock is missing or would change |
| `-U`, `--upgrade` | Choose the newest versions that fit, ignoring alai.lock |
| `-P`, `--upgrade-collection NAME` | Choose the newest version of collection NAME that fits (can be repeated) |
| `--upgrade-group NAME` | Choose the newest version of every collection group NAME lists that fits (can be repeated) |
| `--reinstall` | Reinstall every collection, even those already at the right version |
| `--reinstall-collection NAME` | Reinstall collection NAME, even if it's already at the right version (can be repeated) |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |
| `--link-mode {auto,clone,hardlink,copy,symlink}` | How files get from the cache into the collections directory |
| `--offline`, `--no-offline` | Use only what's cached, without connecting to any index |
| `--index NAME=URL` | An index to resolve from, before those in config files (can be repeated) |
| `--default-index [NAME=]URL` | Replace the default index |

Also takes the [global options](#global-options).

## alai run

Lock and install what alai.lock lists as alai sync does, then run COMMAND with Ansible loading collections from the project's collections directory and nowhere else. Collections there that alai.lock doesn't list are kept with a warning. `--inexact` keeps them without the warning, and `--exact` removes them. Everything after COMMAND is passed to it.

[Running an Ansible module from a collection just added](casts/run.cast){ .cli-cast }

`alai run` runs Ansible where it can find the collections alai manages.
{: .cli-cast-description }

```console
$ alai run [OPTIONS] COMMAND ...
```

### Arguments

| Argument | Description |
|---|---|
| `COMMAND` | The command to run, found on PATH |
| `ARG` | The command's arguments |

### Options

| Option | Description |
|---|---|
| `--locked` | Resolve, and exit 1 rather than install if alai.lock is missing or would change. Can't be used with `--frozen` or `--no-sync` |
| `--frozen` | Install from alai.lock as it is, without checking it against alai.toml. Can't be used with `--locked` or `--no-sync` |
| `--no-sync` | Run without locking or installing anything first. Can't be used with `--locked` or `--frozen` |
| `--exact` | Remove installed collections alai.lock doesn't list, as alai sync does, rather than warn of them. Can't be used with `--inexact` |
| `--inexact` | Keep installed collections alai.lock doesn't list without warning of them. Can't be used with `--exact` |
| `-U`, `--upgrade` | Choose the newest versions that fit, ignoring alai.lock |
| `-P`, `--upgrade-collection NAME` | Choose the newest version of collection NAME that fits (can be repeated) |
| `--upgrade-group NAME` | Choose the newest version of every collection group NAME lists that fits (can be repeated) |
| `--reinstall` | Reinstall every collection, even those already at the right version |
| `--reinstall-collection NAME` | Reinstall collection NAME, even if it's already at the right version (can be repeated) |

### Groups

| Option | Description |
|---|---|
| `--group NAME` | Also install group NAME (can be repeated) |
| `--no-group NAME` | Don't install group NAME, even if another option asks for it (can be repeated) |
| `--only-group NAME` | Install only group NAME, without the project's own collections (can be repeated) |
| `--all-groups` | Install every group |
| `--no-default-groups` | Don't install the 'dev' group |
| `--no-dev` | The same as `--no-group dev` |
| `--only-dev` | The same as `--only-group dev` |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |
| `--link-mode {auto,clone,hardlink,copy,symlink}` | How files get from the cache into the collections directory |
| `--offline`, `--no-offline` | Use only what's cached, without connecting to any index |
| `--index NAME=URL` | An index to resolve from, before those in config files (can be repeated) |
| `--default-index [NAME=]URL` | Replace the default index |

Also takes the [global options](#global-options).

## alai generate-shell-completion

Print the script that enables Tab completion for alai in SHELL.

```console
$ alai generate-shell-completion [OPTIONS] {bash,zsh,fish,powershell,tcsh}
```

### Arguments

| Argument | Description |
|---|---|
| `{bash,zsh,fish,powershell,tcsh}` | The shell to print the script for |

Also takes the [global options](#global-options).

## alai sync

Install the collections alai.lock lists into the collections directory, and remove those it doesn't, so the directory matches the lock. alai.lock is written first if it's missing or alai.toml has changed since. The project's collections are installed with the 'dev' group, if there is one.

[Installing a project's collections](casts/sync.cast){ .cli-cast }

```console
$ alai sync [OPTIONS]
```

### Options

| Option | Description |
|---|---|
| `--locked` | Resolve, and exit 1 rather than install if alai.lock is missing or would change. Can't be used with `--frozen` |
| `--frozen` | Install from alai.lock as it is, without checking it against alai.toml. Can't be used with `--locked` |
| `--inexact` | Keep installed collections alai.lock doesn't list, rather than removing them |
| `-U`, `--upgrade` | Choose the newest versions that fit, ignoring alai.lock |
| `-P`, `--upgrade-collection NAME` | Choose the newest version of collection NAME that fits (can be repeated) |
| `--upgrade-group NAME` | Choose the newest version of every collection group NAME lists that fits (can be repeated) |
| `--reinstall` | Reinstall every collection, even those already at the right version |
| `--reinstall-collection NAME` | Reinstall collection NAME, even if it's already at the right version (can be repeated) |

### Groups

| Option | Description |
|---|---|
| `--group NAME` | Also install group NAME (can be repeated) |
| `--no-group NAME` | Don't install group NAME, even if another option asks for it (can be repeated) |
| `--only-group NAME` | Install only group NAME, without the project's own collections (can be repeated) |
| `--all-groups` | Install every group |
| `--no-default-groups` | Don't install the 'dev' group |
| `--no-dev` | The same as `--no-group dev` |
| `--only-dev` | The same as `--only-group dev` |

### Settings

| Option | Description |
|---|---|
| `--collections-dir DIR` | Install collections under DIR/ansible_collections |
| `--link-mode {auto,clone,hardlink,copy,symlink}` | How files get from the cache into the collections directory |
| `--offline`, `--no-offline` | Use only what's cached, without connecting to any index |
| `--index NAME=URL` | An index to resolve from, before those in config files (can be repeated) |
| `--default-index [NAME=]URL` | Replace the default index |

Also takes the [global options](#global-options).
