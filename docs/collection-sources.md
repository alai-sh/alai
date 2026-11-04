---
description: The sources alai can install collections from.
---

# Collection sources

A collection's source is where alai gets the collection from. Most
collections come from an [index](indexes.md) by name and need nothing extra
set. A collection can instead come from a specific index, a directory, a
tarball or a git repository when
[`[project.sources]`](alai-toml.md#projectsources) names it:

```toml
[project]
collections = [
    "cisco.ios",
    "corp.dev",
    "corp.lib",
    "corp.net",
    "corp.web",
    "corp.win",
]

[project.sources]
"ansible.netcommon" = { index = "internal" }
"corp.dev" = { path = "../corp.dev" }
"corp.lib" = { path = "../corp.lib", editable = true }
"corp.net" = { path = "dist/corp-net-2.1.0.tar.gz" }
"corp.web" = { url = "https://artifacts.example.com/corp-web-1.4.0.tar.gz" }
"corp.win" = { git = "https://git.example.com/corp/windows.git", rev = "v3.0.0" }
```

| Source | Written as | Installed by | Use it for |
|---|---|---|---|
| [An index](#an-index) | Nothing, or `{ index = "<name>" }` | Downloading and installing | Published collections |
| [A directory](#a-directory) | `{ path = "<dir>" }` | Copying it, as if built and installed | A collection that isn't published, or a change to one you want to try |
| [An editable directory](#an-editable-directory) | `{ path = "<dir>", editable = true }` | Linking to it | A collection you're working on alongside the project |
| [A tarball](#a-tarball) | `{ path = "<file>" }` or `{ url = "<url>" }` | Extracting it | A built collection that isn't on an index, such as a CI build or a release download |
| [A git repository](#a-git-repository) | `{ git = "<url>", rev = "<rev>" }` | Fetching the commit and installing like a directory | A collection that's only in a repository, or a fix that isn't released yet |

The source is recorded in `alai.toml` and `alai.lock`, so everyone
installing the project gets the same thing.

## An index

An index is the default source, used when a collection has no
`[project.sources]` entry. The collection comes from the first configured
index that has it (see [Configuration](configuration.md#indexes)).
`alai.lock` records the index's URL, the version chosen and its checksum.
`alai sync` downloads exactly that version and checks it against the
checksum:

[Installing a collection, and what it needs, from the index](casts/source-index.cast){ .cli-cast }

When a collection must come from one index, `{ index = "<name>" }` takes it
only from the [`[[index]]`](alai-toml.md#index) with that name. A dependency
can have a source too, so in the example below `ansible.netcommon` comes from
the `internal` index wherever `cisco.ios` came from.

```toml
[[index]]
name = "internal"
url = "https://ansible-index.example.com/"

[project]
collections = ["cisco.ios"]

[project.sources]
# Dependency of cisco.ios, will pull it from the internal index
"ansible.netcommon" = { index = "internal" }
```

Leaving out `index` searches the indexes in order. To use only the default
index and none of the custom ones, set `{ index = "alai" }`.

Name the index only when:

- **A collection is on more than one index**, and it must come from one,
  such as an internal mirror.
- **Its name could be taken elsewhere.** A private collection pinned to the
  private index can't be swapped for a public one of the same name that
  happens to appear on an index searched first.

## A directory

A directory source is the path to a directory holding the collection. alai
copies the directory into the collections directory, so changes to the source
or the copy don't affect each other.

To add a directory as a source, run:

```console
$ alai add <dir>
```

`alai add` writes the following to `alai.toml`:

```toml
[project]
collections = [
    "namespace.name",
]

[project.sources]
"namespace.name" = { path = "<dir>" }
```

[Adding a collection from a directory](casts/source-directory.cast){ .cli-cast }

How the directory is installed depends on what it holds:

- **A collection's source**, with a `galaxy.yml`, is built and the result
  copied into the collections directory, so what `galaxy.yml` leaves out of
  a build isn't copied. The build respects `build_ignore` in `galaxy.yml`,
  but it doesn't support the `manifest` option and leaves out hidden
  directories at the root of the collection.
- **A built collection**, with a `MANIFEST.json`, is copied as it is.

A directory with both a `galaxy.yml` and a `MANIFEST.json` is an error.

alai reads the collection's version and dependencies from `galaxy.yml` or
`MANIFEST.json`, and its `requires_ansible` from `meta/runtime.yml`. The
dependencies are resolved like any other collection, from an index unless
they have a `[project.sources]` entry of their own.

Use one for:

- **A collection that isn't published**, such as one kept in the same
  repository as the playbooks that use it (see
  [Collections in your own repository](#collections-in-your-own-repository)).
- **Trying a change** to a collection, including one the project only gets
  as a dependency.
- **A built collection** you have unpacked, or one installed elsewhere.

Where it falls short:

- **Edits aren't picked up straight away.** The collection is copied again
  when its version or the contents of `galaxy.yml`, `MANIFEST.json` or
  `meta/runtime.yml` change, but not when another file does.
  `alai sync --reinstall-collection NAME` copies it again too, and making
  the directory editable shows every edit.
- **The directory must be there for everyone.** `alai.lock` records its
  path, so a teammate or CI job needs the same directory at the same place
  relative to the project. A git submodule or a sibling checkout that CI
  clones first both work.
- **`galaxy.yml` must be valid.** Installing a directory builds the
  collection, so its `galaxy.yml` must be valid. The check includes fields
  Ansible doesn't use at runtime, such as `readme` and `authors`.

!!! warning "How a directory is built may change"

    The alai build process is still a work in progress (see the [roadmap](roadmap.md)).
    If you depend on a collection directory having a specific file structure that the
    build process might skip, use an editable directory instead.

## An editable directory

An editable directory is like a directory source, but it isn't built or
copied. alai symlinks the directory into the collections directory instead,
so Ansible sees every change made to it.

To add a directory as an editable source, run:

```console
$ alai add --editable <dir>
```

`alai add` writes the following to `alai.toml`:

```toml
[project]
collections = [
    "namespace.name",
]

[project.sources]
"namespace.name" = { path = "<dir>", editable = true }
```

[Adding a collection from a directory, editable](casts/source-editable.cast){ .cli-cast }

Use one for:

- **A collection you're developing** alongside a project that uses it, or
  alongside another collection that depends on it.
- **Debugging.** `alai run` tells a debugger to resolve the link, so
  breakpoints set in the directory hit (see
  [What breakpoints hit](editors.md#what-breakpoints-hit)).

Where it falls short:

- **Nothing is built.** Ansible sees the directory as it is. Anything a build
  would leave out is still there, even though a real release won't have it.
- **The directory must be there for everyone**, as for a copied one.
- **It's a link.** Copying the collections directory somewhere else, such
  as into a container image, copies the link rather than the collection. Use
  a copied directory for that.

To switch between the two, run `alai add` on the same directory with or
without `--editable`.

## Collections in your own repository

A playbook project can keep collections it doesn't publish in its own git
repository. Commit each collection's source, with its `galaxy.yml`, in a
directory of the project, and point a source at it:

```toml
[project]
collections = ["corp.tools", "community.general>=10"]

[project.sources]
"corp.tools" = { path = "collections_src/corp/tools", editable = true }
```

`alai add --editable collections_src/corp/tools` writes both for you. The
path is relative to the project root and is recorded in `alai.lock`, so
anyone who clones the repository gets the same collection with `alai sync`.

An [editable directory](#an-editable-directory) is usually the best fit, as
edits take effect straight away and nothing is built. If the collections
directory is copied somewhere else, such as into a container image, leave
out `editable` to use a [copied directory](#a-directory) instead.

!!! warning "Keep them out of the collections directory"

    Don't commit a collection inside the
    [collections directory](projects.md#where-collections-are-installed),
    such as `collections/ansible_collections/corp/tools`. `alai sync` makes
    that directory hold only what `alai.lock` lists, so it removes a
    collection that has no source. A source pointing inside the collections
    directory is an error.
    Keep your collections in another directory and let alai link or copy them
    in as a project source.

## A tarball

A tarball source is a file path or HTTP URL to a built collection's
`.tar.gz`. alai extracts the tarball into the collections directory as it
does a collection from an index.

To add a tarball as a source, run:

```console
$ alai add dist/corp-local-2.1.0.tar.gz
$ alai add "https://artifacts.example.com/corp-web-1.4.0.tar.gz"
```

`alai add` writes the following to `alai.toml`:

```toml
[project]
collections = [
    "corp.local",
    "corp.web",
]

[project.sources]
"corp.local" = { path = "dist/corp-local-2.1.0.tar.gz" }
"corp.web" = { url = "https://artifacts.example.com/corp-web-1.4.0.tar.gz" }
```

The tarball must be gzipped, as `ansible-galaxy collection build` writes it.
Anything else is refused before it's read or downloaded whole.

[Adding a collection from a tarball](casts/source-tarball.cast){ .cli-cast }

The tarball is installed exactly as one from an index is. Only the files
listed in its `FILES.json` are created, and each one is checked against its
checksum. The collection's version and dependencies come from its
`MANIFEST.json`, and its `requires_ansible` from `meta/runtime.yml`. The
dependencies come from indexes unless they have a source of their own.

`alai.lock` records the tarball's checksum and size, as it does an index's
artifact.

Use one for:

- **A collection published somewhere other than an index**, such as a
  release on a git host, or an internal artifact store.
- **Testing a build** before publishing it, as users of the published
  collection will get it.

Where it falls short:

- **A file must be there for everyone**, as a directory must.
- **Credentials aren't sent**, so a URL has to be readable without them.
- **It can't be editable**, as a tarball is a release. Use a directory to
  work on the collection.

## A git repository

A git source is a collection in a local or remote git repository. The source
can name the branch, tag or commit to use, and options such as `subdirectory`
and `version`.

To add a git collection as a source, run:

```console
$ alai add 'git+https://github.com/corp/monorepo@main#subdirectory=collections/corp.net'
$ alai add 'git+ssh://git@github.com/ansible-collections/community.general@13.5.0'
```

`alai add` writes the following to `alai.toml`:

```toml
[project]
collections = [
    "community.general",
    "corp.net",
]

[project.sources]
"corp.net" = { git = "https://github.com/corp/monorepo", subdirectory = "collections/corp.net", rev = "main" }
"community.general" = { git = "ssh://git@github.com/ansible-collections/community.general", rev = "13.5.0" }
```

[Adding a collection from a git repository](casts/source-git.cast){ .cli-cast }

The following values can also be set with the git source type:

|Key|Purpose|
|---|---|
|rev|The branch, tag or full commit hash to check out, or the default branch when unset|
|subdirectory|The directory in the repository holding the collection's `galaxy.yml`, when it isn't the root|
|version|The version to use in place of the one in `galaxy.yml`, when that isn't valid semver. See [Overriding galaxy.yml versions](#overriding-galaxyyml-versions)|

The repository is given as a URL:

| Over | In `alai.toml` | On the command line |
|---|---|---|
| HTTPS | `https://github.com/corp/windows.git` | `git+https://github.com/corp/windows.git@v3.0.0` |
| SSH | `ssh://git@github.com/corp/windows.git` | `git+ssh://git@github.com/corp/windows.git@v3.0.0` |
| SSH, another port | `ssh://git@git.example.com:2222/corp/windows.git` | `git+ssh://git@git.example.com:2222/corp/windows.git@v3.0.0` |
| A repository on disk | `file:///srv/git/windows.git` | `git+file:///srv/git/windows.git@v3.0.0` |

GitHub gives SSH clone URLs in git's shorter form, such as
`git@github.com:corp/windows.git`, which alai doesn't support. Use the
`ssh://` URL format instead.

alai fetches `rev` into its cache with the `git` you have installed. From
the cache, the collection is installed like [a directory source](#a-directory)
is. Submodules are fetched, but Git LFS artifacts are not.

`alai.lock` records the commit `rev` was at when it was locked, and keeps
it. A branch that has moved on or a tag that was moved doesn't change what
`alai sync` installs. To look `rev` up again, run `alai lock -P corp.net`
(`--upgrade-collection`), or `-U` for everything. A new commit is installed
in place of the old one even when the version in `galaxy.yml` is the same.
Changing the entry in `alai.toml` locks the collection again.

Use one for:

- **A collection that's only published as a repository**, such as many on
  GitHub.
- **A fix that isn't released yet.** Point the collection at the branch or
  commit with the fix, then back at an index once the fix is released.
- **A repository holding several collections**, each taken from its
  directory with `subdirectory`.

Where it falls short:

- **It needs `git`**, and access to the repository for everyone who locks
  the project or installs it with nothing cached.
- **Edits aren't seen**, as a commit is fixed. To work on the collection,
  use an editable directory with a checkout of your own.
- **A commit's abbreviated hash can't be used**, as finding it needs the
  whole history. Give the full hash instead.

!!! warning "ssh may ask questions"

    As with `git clone`, ssh may ask for a key's passphrase or whether to
    trust a host it hasn't seen before. When several repositories are fetched
    at once, their questions can arrive together. Without a terminal, as in
    CI, ssh can't ask and the fetch fails. In those environments, turn the
    prompts off with one of git's settings, such as
    `GIT_SSH_COMMAND="ssh -o BatchMode=yes"`.

## Overriding galaxy.yml versions

Some collections' `galaxy.yml` have a `version` that isn't valid semver, such
as a placeholder for a release process to fill in. alai refuses to build such
a collection, as it can't know what version it is. When a source builds the
collection, as a directory or git source does, its `version` key sets the
version to use instead.

For example, the following clones and builds the repository at the tag
`1.5.0`. The `galaxy.yml` at that tag has `version: '{{ REPLACE_VERSION }}'`,
so the `version` key overrides it.

```console
$ alai add 'git+https://github.com/chocolatey-community/chocolatey-ansible@1.5.0#subdirectory=chocolatey&version=1.5.0'
```

```toml
[project.sources]
"chocolatey.chocolatey" = { git = "https://github.com/chocolatey-community/chocolatey-ansible", subdirectory = "chocolatey", rev = "1.5.0", version = "1.5.0" }
```

The `version` key is used in place of the version in `galaxy.yml`, both in
`alai.lock` and in the installed collection's `MANIFEST.json`. Requirements
other collections have on the collection then mean what they say.
