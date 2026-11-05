# alai

A fast package and environment manager for Ansible collections, heavily
inspired by [uv](https://docs.astral.sh/uv/).

> **Preview:** alai is released in preview, as a 0.x version under
> [semantic versioning](https://semver.org/). Its interface can still change
> as workflows are worked out, so a release that breaks something bumps the
> minor version, from 0.1 to 0.2, and lists the change in the
> [changelog](https://github.com/alai-sh/alai/blob/main/CHANGELOG.md). A
> patch release, such as 0.1.1, only fixes bugs.

> **A word on how alai is made:** alai is written with the help of AI coding
> tools. That doesn't mean a model was handed a prompt and left to get on with
> it: a human argues over every design decision, the reasoning behind them is
> written down in the repository, and features are tried by hand against real
> projects before they land, then tried again when they don't behave. Think of
> it as pair programming where one of the pair never needs a coffee break.
>
> I respect your decision if you'd rather not use software built this way, and
> it seemed better to say so outright rather than after you've read the docs
> or started using the software.

alai installs the collections an Ansible project needs into the project
itself, in `collections/ansible_collections/` next to your playbooks, where
`ansible-playbook` finds them with no extra configuration. It records the
exact versions it chose in a lock file, so every machine and CI run gets the
same collections. Installing them takes a fraction of the time
`ansible-galaxy` takes.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/alai-sh/alai/main/docs/assets/casts/galaxy-comparison-dark.svg">
  <img alt="ansible-galaxy and alai each installing community.general with nothing cached, played side by side from the same start: alai finishes and installs it again into another project while ansible-galaxy is still running" src="https://raw.githubusercontent.com/alai-sh/alai/main/docs/assets/casts/galaxy-comparison-light.svg">
</picture>

**Documentation: <https://docs.alai.sh/>**

## Why alai

- **Lock files.** `alai.lock` records the exact version of every
  collection, dependencies included, and only changes when you change what
  the project needs or ask to upgrade. `alai sync --locked` checks in CI that
  `alai.toml` and `alai.lock` agree.
- **Faster installs.** A first install of `community.general` takes about
  1.2 s where `ansible-galaxy` takes 14.6 s. Each collection is downloaded
  once and linked from a cache, so installing it again into another project
  takes 0.26 s.
- **Reliability.** Every download is checked against its SHA-256 in the lock,
  and every file against the collection's own `FILES.json`. Installs don't
  depend on the Galaxy API being available, and an interrupted install never
  leaves half a collection. When there's no network, `--offline` installs
  from the cache.
- **Collections per project.** Each project has its own collections,
  rather than one shared `~/.ansible/collections` where one project's
  upgrade changes another's. `alai run` makes sure Ansible loads only the
  project's collections.
- **Collection development.** A collection project no longer needs to be in
  the `ansible_collections/<namespace>/<name>` directory layout, and its
  dependencies never end up in the collection you build or the files
  `ansible-test sanity` checks.
- **No Ansible needed.** alai doesn't need Ansible installed, so CI can
  fetch collections before, or without, installing ansible-core.
- **Familiar commands.** `alai add`, `alai remove`, `alai lock` and
  `alai sync` work as uv's do for Python packages.

alai runs on Linux and macOS. Other *nix-like platforms should work but
aren't officially tested. There's no Windows support, as Ansible itself
can't run on Windows.

## Installing

alai is published on PyPI as `alai-sh`. Install it as a tool with
[uv](https://docs.astral.sh/uv/getting-started/installation/), which puts
the `alai` command on your `PATH`:

```console
$ uv tool install alai-sh
```

To update, run `uv tool upgrade alai-sh`. To try alai without installing it,
`uvx --from alai-sh alai` runs it in a temporary environment, such as
`uvx --from alai-sh alai --version`.

The wheels on PyPI cover Linux on x86_64 and aarch64, with glibc or musl,
and macOS on Apple silicon. On any other platform, such as an Intel Mac, uv
builds alai from the source distribution, which needs Rust 1.92 or later
with `cargo` on your `PATH` ([rustup](https://rustup.rs/) installs it).

## Getting started

An `alai.toml` marks the project, so create one beside your playbooks, then
add the collections they use:

```console
$ touch alai.toml
$ alai add ansible.posix 'community.general>=10,<12'
Resolved 2 collections in 522ms
Prepared 2 collections in 1.21s
Installed 2 collections in 41ms
 + ansible.posix==2.2.2
 + community.general==11.4.9
```

`alai.toml` now lists what the project needs, `alai.lock` has the exact
versions chosen, and `collections/` holds them:

```toml
[project]
collections = [
    "ansible.posix>=2.2.2",
    "community.general>=10,<12",
]
```

Commit `alai.toml` and `alai.lock`, and ignore `collections/`. Anyone who
clones the project gets the same collections with `alai sync`:

```console
$ alai sync
Resolved 2 collections in 1ms
Installed 2 collections in 35ms
 + ansible.posix==2.2.2
 + community.general==11.4.9
```

## Common tasks

| Task | Command |
|---|---|
| Add a collection, or change its requirement | `alai add cisco.ios` |
| Add one only some workflows need | `alai add --group test ansible.utils` |
| Remove a collection | `alai remove cisco.ios` |
| Install what `alai.lock` lists, after a pull | `alai sync` |
| Fail CI if `alai.lock` is out of date | `alai sync --locked` |
| Upgrade one collection, a group, or everything | `alai lock -P cisco.ios`, `alai lock --upgrade-group test`, `alai lock -U` |
| Put back a collection edited in place (if its files were hardlinked or symlinked, see [`link_mode`](https://docs.alai.sh/alai-toml/#link_mode) first) | `alai sync --reinstall-collection cisco.ios` |
| Install a collection by hand, outside the lock | `alai collection install ansible.posix` |
| See where each setting comes from | `alai config show` |

Coming from `ansible-galaxy` and a `requirements.yml`? The
[migration guide](https://docs.alai.sh/ansible-galaxy/) covers moving a
project over and the differences you may run into.

## Learn more

- [Projects](https://docs.alai.sh/projects/): how alai finds your project,
  playbook and collection projects, and where collections are installed.
- [Managing collections](https://docs.alai.sh/managing-collections/):
  adding, locking and installing, and workflows for teams and CI.
- [Running Ansible](https://docs.alai.sh/running-ansible/): running
  `ansible-playbook` and the other Ansible commands with `alai run`.
- [Configuration](https://docs.alai.sh/configuration/) and
  [`alai.toml`](https://docs.alai.sh/alai-toml/): every setting and key.
- [CLI reference](https://docs.alai.sh/cli/): every command and option,
  with recordings of them running.
- [Roadmap](https://docs.alai.sh/roadmap/): what's planned next.
- [Acknowledgements](https://docs.alai.sh/acknowledgements/): the projects
  alai is inspired by and built on.

Bugs and ideas are welcome in the
[issue tracker](https://github.com/alai-sh/alai/issues).

## License

MIT, see [LICENSE](https://github.com/alai-sh/alai/blob/main/LICENSE).
