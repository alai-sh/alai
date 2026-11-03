---
description: The projects alai takes ideas from and is built on.
---

# Acknowledgements

alai borrows ideas from a number of projects, and is built on others. If
alai is useful to you, these may be too.

## Inspiration

- **[uv](https://docs.astral.sh/uv/)**, Astral's package and project
  manager for Python. alai's commands, flags, defaults and output are
  heavily modeled on uv's. Commands like `alai add`, `alai lock` and
  `alai sync` are meant to feel and act like their uv counterparts, with
  only a few minor differences.
- **[ModuleFast](https://github.com/JustinGrote/ModuleFast)**, by Justin
  Grote. ModuleFast does for PowerShell modules and the
  [PowerShell Gallery](https://www.powershellgallery.com/) what alai does
  for Ansible collections and Galaxy. Its artifact and index mirroring is
  what inspired me to do the same for Galaxy and collection content.
- **[Cargo](https://doc.rust-lang.org/cargo/)**, Rust's package manager.
  Its
  [registry index](https://doc.rust-lang.org/cargo/reference/registry-index.html)
  shaped alai's index format. Like Cargo's sparse index, alai's is a set of
  static files that any web server or CDN can serve, with one file per
  collection and a line per version.
- **[PwshSpectreConsole](https://pwshspectreconsole.com/)**, by Shaun
  Lawrie, inspired these docs. Its examples are run and recorded, so the
  documentation shows what the commands really print. The recordings in
  these docs do the same for alai.

## Built with

These are some of the key components alai is built with, though the list
isn't exhaustive:

- **[Ansible Galaxy](https://galaxy.ansible.com/)**, the source of alai's
  default index. The content from Ansible Galaxy is mirrored to the alai
  index as part of a regular sync job.

### Python

- **[argcomplete](https://kislyuk.github.io/argcomplete/)** provides
  [shell completion](shell-completion.md).

### Rust

Part of alai is a native extension written in Rust, for the work that's slow
in Python.

- **[PyO3](https://pyo3.rs/)** and **[maturin](https://www.maturin.rs/)**
  build the extension into the Python package.
- **[PubGrub](https://github.com/pubgrub-rs/pubgrub)** chooses the versions,
  as the version solving algorithm uv and Cargo use.
- **[tar](https://crates.io/crates/tar)** and
  **[flate2](https://crates.io/crates/flate2)** extract collection tarballs,
  and **[sha2](https://crates.io/crates/sha2)** checks each file against the
  collection's `FILES.json` as it goes.
- **[reqwest](https://crates.io/crates/reqwest)** downloads from the index
  on **[Tokio](https://tokio.rs/)**, over HTTP/2 where the host supports it.
- **[rustls](https://github.com/rustls/rustls)** makes the TLS connections
  with **[AWS-LC](https://github.com/aws/aws-lc-rs)** for its cryptography,
  and
  **[rustls-platform-verifier](https://github.com/rustls/rustls-platform-verifier)**
  has the operating system verify their certificates.
- **[serde_json](https://crates.io/crates/serde_json)** reads index files
  and each collection's `MANIFEST.json` and `FILES.json`.
- **[libyaml-safer](https://crates.io/crates/libyaml-safer)** reads a
  collection's `galaxy.yml` and `meta/runtime.yml`. libyaml-safer is a Rust
  port of the libyaml parser that ansible-core reads YAML with.
- **[toml_edit](https://crates.io/crates/toml_edit)** reads `alai.toml`,
  `alai.lock` and the config files, and edits `alai.toml` while keeping the
  rest of its text, as Cargo and uv do.

### Docs

- **[Zensical](https://zensical.org/)** builds these docs.
- **[asciinema-player](https://docs.asciinema.org/manual/player/)** plays
  their recordings.
- **[asg](https://github.com/kingsword09/asg)** draws the README's recording
  as an animated SVG.
