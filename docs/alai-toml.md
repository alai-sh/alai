---
description: Describes alai.toml and the settings and configuration it can contain.
---

# alai.toml

`alai.toml` marks a project, declares what it needs, and holds alai's
settings. The file is TOML, and lives at the
[project root](projects.md#finding-the-project-root) or is used as a user or
system config file. [Configuration](configuration.md) covers where each
config file is found and how its settings combine with flags and environment
variables.

What a file can hold depends on whether it's the project's own `alai.toml`
or a config file:

- **Top-level keys and `[[index]]` are settings.** Settings define how alai
  runs, and any `alai.toml` can set them. Each one also has an environment
  variable, and all but `python_index` have a command-line flag.
- **`[project]`, and everything under it, describes the project.** Only the
  project's own `alai.toml` can have `[project]`, never a user or system
  config file.

Every key below is optional, so an empty `alai.toml` still marks the project
root. An unknown key or a value of the wrong type is an error naming the
file, so a typo never silently does nothing. Keys are written in snake_case
to match their kebab-case CLI options, such as `link_mode` and
`--link-mode`.

```toml
# alai.toml

# Settings: Top-level keys come before any [table] in TOML
cache_dir = "~/.cache/alai"
link_mode = "auto"

# Index: Declares custom indexes in priority order
[[index]]
name = "internal"
url = "https://ansible-index.example.com/"

[[index]]
name = "mirror"
url = "https://alai-mirror.example.com/"
default = true

# Project: Only the project's own alai.toml can have these
[project]
collections_dir = "collections"
requires_ansible = ">=2.17"
collections = [
    "community.general>=9,<11",
    "ansible.windows",
    "corp.tools>=1.2",
]

[project.groups.test]
collections = ["ansible.posix", "community.crypto"]

[project.overrides]
"ansible.netcommon" = ">=6"
ignore_requires_ansible = ["some.collection"]

[project.sources]
"corp.tools" = { index = "internal" }
"corp.dev" = { path = "../corp.dev", editable = true }

# Never read by alai: Used to declare custom entries for future
# tools that may read alai.toml
[tool.my-ci]
deploy_target = "prod"
```

## Settings

| Key | Type | |
|---|---|---|
| [`cache_dir`](#cache_dir) | string | Where downloads, extracted collections and index data are kept, as a [path](configuration.md#paths) |
| [`link_mode`](#link_mode) | string | How files get from the cache into the collections directory |
| [`offline`](#offline) | boolean | Use only what's cached, without connecting to any index |
| [`python_index`](#python_index) | string | The Python package index `alai find` reads ansible-core and ansible-rulebook from |
| [`[[index]]`](#index) | array of tables | The indexes collections are resolved from, before the default one |
| [`[tool]`](#tool) | table | Ignored by alai, for other tools to add future configuration values |

### `cache_dir`

- **Type:** string, a [path](configuration.md#paths)
- **Default:** `$XDG_CACHE_HOME/alai`, else `~/.cache/alai`
- **Flag:** `--cache-dir <dir>`
- **Environment variable:** `ALAI_CACHE_DIR`

Where downloaded artifacts, extracted collections, and index metadata are
kept. The data in this cache is shared by every project.

!!! warning "Keep the cache to the users who need it"

    alai trusts what's in its cache. Anyone who can change it can change
    what alai installs. The default, under your home directory, is only
    writable by you. Others may be able to read and write a `cache_dir`
    elsewhere, such as under `/tmp` or in a directory shared between users or
    CI jobs. Restricting that directory to the users who need it is up to
    you.

### `link_mode`

- **Type:** string
- **Choices:** `auto`, `clone`, `hardlink`, `copy` or `symlink`
- **Default:** `auto`
- **Flag:** `--link-mode <mode>`
- **Environment variable:** `ALAI_LINK_MODE`

How files get from the cache into the
[collections directory](#projectcollections_dir):

- `auto`, the default: try `clone`, then `hardlink`, then `copy`, using the
  first that works.
- `clone`: a copy-on-write reflink, where the filesystem supports one.
- `hardlink`: the file shares its data with the cache, so editing an
  installed file in place also edits the cached copy (see below).
- `copy`: an ordinary copy.
- `symlink`: a link to the cached file, so the installed collection depends
  on the cache. Clearing the cache breaks the installed collection, and so
  does using it in an execution environment or container that doesn't have
  the cache. `auto` never picks `symlink`.

!!! warning "Editing installed files with `hardlink` or `symlink`"

    With either mode, an installed file is tied to the data in the cache.
    Editing a file in the project's collections directory will also edit the
    same file in the cache. Every later install of that collection version
    sees the changes, and so does every existing project installed with
    `hardlink` or `symlink`. To get a clean copy, delete
    `<cache_dir>/collections-v1/` and then run
    `alai sync --reinstall-collection NAME`.

    The `clone` and `copy` modes do not share anything with the cache. The
    `auto` mode tries `clone` first, but falls back to `hardlink` on a
    filesystem without copy-on-write such as ext4.

!!! danger "Avoid `symlink`"

    A collection installed with `symlink` is linked to the cache directory and
    only stays valid while the cache contains the collection. Clearing the
    cache breaks every collection installed with `symlink`. Use another mode
    unless you have a reason not to.

### `offline`

- **Type:** boolean (TOML's `true` or `false`, not a string)
- **Default:** `false`
- **Flags:** `--offline`, `--no-offline`
- **Environment variable:** `ALAI_OFFLINE`, a
  [boolean](configuration.md#environment-variables)

Use only index data and collections alai has already cached, without
connecting to any index. A command that needs something that isn't in the
cache fails, saying what it couldn't find. Offline mode only applies to
indexes over `http://` or `https://`, as an index given as a `file://` URL is
read from disk either way.

### `python_index`

- **Type:** string, an `http://` or `https://` URL
- **Default:** `https://pypi.org/simple/`
- **Environment variable:** `ALAI_PYTHON_INDEX`
- **Flag:** none

The Python package index that `alai find` reads ansible-core's and
ansible-rulebook's own plugins from, as `ansible.builtin` and `eda.builtin`.
The URL is the root of a [simple
index](https://packaging.python.org/en/latest/specifications/simple-repository-api/)
that serves its JSON form, as PyPI does and private indexes such as devpi,
Artifactory and Nexus do. alai downloads each project's latest release from
the index and keeps what it reads in the cache. See [Finding
plugins](finding-plugins.md#ansible-cores-own-plugins).

### `[[index]]`

!!! warning "Only index.alai.sh is supported"

    The index format is still being developed and may change without notice.
    alai can be pointed at another index, such as a mirror of
    `index.alai.sh`. A future release may stop reading that index until it's
    updated to match.

- **Type:** array of tables, one per index
- **Default:** none, and the built-in default index `https://index.alai.sh/`
  is always searched last
- **Flags:** `--index NAME=URL`, which can be repeated, and
  `--default-index [NAME=]URL`
- **Environment variables:** `ALAI_INDEX`, holding `NAME=URL` values
  separated by whitespace, and `ALAI_DEFAULT_INDEX`, holding `[NAME=]URL`

An index to resolve collections from. Repeat `[[index]]` for more than one
index, and they're searched in the order they're written, before the default
index.

| Key | Type | |
|---|---|---|
| `name` | string | Required. The name of the index. Use lowercase letters, digits, `-` and `_`, starting with a letter or digit. `alai` is the default index's name, so an index named `alai` must also set `default = true` |
| `url` | string | Required. The `http://`, `https://` or `file://` URL of the index root, which is the directory holding `config.json`. The URL can't have a query or fragment, and a trailing `/` is added if missing |
| `default` | boolean | Optional, default `false`. Makes this index replace the built-in default index |

`--default-index` and `ALAI_DEFAULT_INDEX` replace the default index. Given
a bare URL, the index keeps the name `alai`, so a mirror of `index.alai.sh`
set this way still answers `[project.sources]` entries naming `alai`.

[Configuration](configuration.md#indexes) covers how the indexes from every
level are combined into one list.

### `[tool]`

alai never reads `[tool]` at any level, so other tools and scripts can keep
their own settings under `[tool.<name>]` without alai flagging them as
invalid.

## Project

| Key | Type | |
|---|---|---|
| [`project.collections_dir`](#projectcollections_dir) | string | Where collections are installed, as a [path](configuration.md#paths) |
| [`project.requires_ansible`](#projectrequires_ansible) | string | The ansible-core versions the project targets |
| [`project.collections`](#projectcollections) | array of strings | The collections the project needs, as [requirements](#requirements) |
| [`[project.groups.<name>]`](#projectgroupsname) | table | Collections only some workflows need, one table per group |
| [`[project.overrides]`](#projectoverrides) | table | Fixes for wrong metadata in the collections you depend on |
| [`[project.sources]`](#projectsources) | table | Where particular collections come from |

Only `collections_dir` has a CLI flag and an environment variable. The
remaining options describe only what the project needs, so they can only be
defined in that project's `alai.toml`.
[Managing collections](managing-collections.md) covers how a project declares
the collections it needs.

### `project.collections_dir`

- **Type:** string, a [path](configuration.md#paths)
- **Default:** `collections` in the project root for a playbook project, or
  a directory of its own in the cache for a
  [collection project](projects.md#collection-project)
- **Flag:** `--collections-dir <dir>`
- **Environment variable:** `ALAI_COLLECTIONS_DIR`

The directory the project's collections are installed into. Each collection
is installed at `<collections_dir>/ansible_collections/<namespace>/<name>`. A
value ending in `ansible_collections` is taken as its parent, as Ansible does
with its collection paths.
[Where collections are installed](projects.md#where-collections-are-installed)
shows an example layout.

A relative value in `alai.toml` is relative to the directory holding the
file. A relative value from the flag or environment variable is relative to
the current directory.

### `project.requires_ansible`

- **Type:** string, a PEP 440 version specifier
- **Default:** none, so any ansible-core

The ansible-core versions the project targets, as a
[PEP 440](https://peps.python.org/pep-0440/#version-specifiers) specifier
such as `>=2.17` or `>=2.17,<2.20`. The syntax is the same as
`requires_ansible` in a collection's `meta/runtime.yml`.

A [collection project](projects.md#collection-project) declares its
ansible-core versions in `meta/runtime.yml` instead, and setting
`project.requires_ansible` there is an error.

### `project.collections`

- **Type:** array of strings, each a [requirement](#requirements)
- **Default:** none

The collections the project needs, as an array of
[requirements](#requirements).

A [collection project](projects.md#collection-project) declares its
dependencies in `galaxy.yml` instead, and setting `project.collections` there
is an error.

### `[project.groups.<name>]`

Collections only some workflows need, such as tests, in a table per group:

```toml
[project.groups.test]
collections = ["ansible.posix", "community.crypto>=2"]
```

| Key | Type | |
|---|---|---|
| `collections` | array of strings | The group's collections, as [requirements](#requirements) |

Group names use lowercase letters, digits, `-` and `_`, starting with a
letter or digit. `alai sync` installs the `dev` group with the project's
collections by default and the others when asked for. See
[Groups](managing-collections.md#groups) for more details.

### `[project.overrides]`

When a collection the project depends on has wrong metadata,
`[project.overrides]` replaces it:

```toml
[project.overrides]
"ansible.netcommon" = ">=6"
ignore_requires_ansible = ["some.collection"]
```

| Key | Type | |
|---|---|---|
| `"<namespace.name>"` | string | A [version requirement](#version-requirements) that replaces every requirement on that collection, including those in other collections' dependencies. `"*"` accepts any version |
| `ignore_requires_ansible` | array of strings | The names of collections whose own `requires_ansible` is ignored |

Collection names contain a dot, so they must be quoted, as in
`"ansible.netcommon" = ">=6"`.

### `[project.sources]`

Where particular collections come from, keyed by collection name.
[Collection sources](collection-sources.md) covers each source type and when
to use it.

```toml
[project.sources]
"corp.tools" = { index = "internal" }
# From the default index only, even if an earlier index has it too
"ansible.netcommon" = { index = "alai" }
"corp.dev" = { path = "../corp.dev" }
"corp.lib" = { path = "../corp.lib", editable = true }
"corp.net" = { path = "dist/corp-net-2.1.0.tar.gz" }
"corp.web" = { url = "https://artifacts.example.com/corp-web-1.4.0.tar.gz" }
"corp.win" = { git = "https://git.example.com/corp/windows.git", rev = "v3.0.0" }
```

| Value | |
|---|---|
| `{ index = "<name>" }` | Take the collection from the [`[[index]]`](#index) with that name, and only from there |
| `{ path = "<dir>" }` | Take the collection from a directory. A directory holding a `galaxy.yml` is built and copied into the collections directory, and one holding a built collection's `MANIFEST.json` is copied as it is. A relative path is relative to the project root |
| `{ path = "<dir>", editable = true }` | The same, but linked to the directory rather than copied, so edits there take effect without installing again. `editable = false` is the same as leaving it out |
| `{ path = "<file>" }` | Take the collection from a built collection's tarball on disk, installed as an index's artifact is. A path to a file is taken as a tarball, which can't be editable |
| `{ url = "<url>" }` | Take the collection from a built collection's tarball at an `http` or `https` URL, downloaded when it's locked. For a file, use `path` |
| `{ git = "<url>" }` | Take the collection from a git repository at the commit `rev` points to when it's locked, and install it as a directory is. The URL can be `https://`, `ssh://` or `file://`, such as `ssh://git@github.com/org/repo.git`. See [Git repository source](collection-sources.md#a-git-repository) for more details |

When a collection's `galaxy.yml` has a placeholder version that its release
fills in, set `version = "<version>"` on its source. The semantic version is
used in place of the one in `galaxy.yml`, and works for a `git` source or a
directory `path` source, editable or not. See
[Overriding galaxy.yml versions](collection-sources.md#overriding-galaxyyml-versions).

An entry applies wherever the collection appears, whether the project lists
it in `collections` or another collection depends on it. Without an entry, a
collection comes from the first index that has it (see
[Configuration](configuration.md#indexes)). Naming the index yourself is
also how to be sure a collection can't come from somewhere else that
happens to have one by the same name.

## Requirements

A requirement is a collection name followed by an optional version
requirement, with the same syntax as ansible-galaxy's `requirements.yml` and
`galaxy.yml`.

```text
NAMESPACE.NAME[VERSION REQUIREMENT]
```

| Requirement | Means |
|---|---|
| `ansible.windows` | Any version |
| `community.general>=9,<11` | 9.0.0 or later, but before 11.0.0 |
| `community.general >= 9` | The same as `community.general>=9`, with spaces around each part |

### Version requirements

A version requirement is `*` for any version, or one or more clauses
separated by commas that must all be met. A clause is an operator and a
version:

| Operator | Means |
|---|---|
| `==` | Exactly this version |
| `!=` | Any version but this one |
| `>=`, `>` | This version or later, or only later |
| `<=`, `<` | This version or earlier, or only earlier |

Collection versions are [semantic versions](https://semver.org/). A version
in a clause can leave out its minor and patch parts, which count as `0`, so
`>=9` is `>=9.0.0` and `==9` is exactly `9.0.0`. Pre-releases are supported,
so `>=2.0.0-rc.1` accepts `2.0.0-rc.1`, any later release candidate and the
final release.

The following forms aren't supported, and each has an alternative to write
instead:

| Written | Write instead |
|---|---|
| `1.2.3` or `=1.2.3` | `==1.2.3` |
| `^1.2.0`, `~1.2.0` | `>=1.2.0,<2.0.0`, `>=1.2.0,<1.3.0` |
| `==1.0.0+build1` | `==1.0.0` |
