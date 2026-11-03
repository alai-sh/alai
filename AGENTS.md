# Agent notes

Rules the code and tooling don't show. Keep this short: link to `design/` for
reasons, and drop anything a tool now enforces.

- Modules in `src/alai/` are private (`_name.py`) until a public Python API is
  designed. Only `__init__.py` and `__main__.py` are public.
- The Rust in `src/rust/` is built into the package as `alai._native` by
  maturin, typed by `src/alai/_native.pyi`; keep the stub in step with it.
  It's required, with no Python fallback, so building alai, the tests and
  the docs needs `cargo`. alai's version is in the root `Cargo.toml`
  (`[workspace.package]`), which `pyproject.toml` takes through maturin.
  `uv sync` builds it into `src/alai/`, named for the Python's ABI, so
  after switching `.venv` to another Python, delete `src/alai/_native*.so`:
  3.15 loads an old `.abi3.so` before a new `.abi3t.so`
  (`tests/test_native.py` fails if more than one is there).
- Every `.py`, `.pyi` and `.rs` file starts with the two-line copyright/MIT
  header; copy it from an existing file.
- What users read is US English: `docs/`, `README.md`, and the CLI's help
  and output. `design/` and code comments can stay as written.
- How what users read is written:
  - Start with the situation the reader is in, then what happens or what to
    do. Describe an option by the problem it solves, such as "When a
    collection is only needed to run the tests, add it to a group", not as
    a bare instruction.
  - Give each sentence one main idea. Join a second point to it with "and",
    "so", "as", "but", "when" or "which" only when it completes or explains
    the first, and start a new sentence for the next idea.
  - Don't join two clauses with `;` or `:`. A `:` that leads into a code
    block, table or list is fine.
  - Keep a sentence to two commas or fewer. One that needs more is carrying
    more than one idea, so split it where the ideas change.
  - Don't write runs of very short sentences that only make sense together.
    Join the halves with one of the words above instead.
  - Don't push a phrase into the middle of a clause, between a subject and
    its verb or between "which" and what it says. A condition goes at the
    start or the end of a sentence.
  - Each sentence should make sense on its own, so name the thing rather
    than opening with "this", "that" or "it" pointing at the sentence before.
  - Don't drop words to shorten a phrase, such as "`sha256`, its artifact's"
    for "the artifact's sha256 checksum".
- `docs/` is the published user documentation and describes current behaviour
  only, except `docs/roadmap.md`, which summarises what's planned: keep it in
  step with the roadmap in `design/README.md`. Keep it to plain Markdown plus
  admonitions.
- Plans, rationale and open questions go in `design/` (see
  `design/README.md`). Update the relevant note in the same change as the
  code; turn resolved questions and finished plans into decisions. A
  decision users may want the other way also goes in
  `design/user-questions.md`, with what to ask them.
- Follow uv: before designing a command or behaviour, try what uv does in
  a scratch project and match its defaults, flags and output; for Ansible's
  side, read ansible-core's source. Record what was tested in the design
  note, and why whenever alai differs (see `design/README.md`).
- Nothing is released, so there are no backwards-compatibility shims or
  aliases: rename and replace outright.
- Checks:
  - `uv run tox run -f sanity` (ruff, basedpyright, `cargo fmt` and clippy)
  - `uv run tox run -f py314` (tests; any of `py310` to `py315`, and the
    free-threaded `py314t` and `py315t`)
  - `uv run tox run -e docs` (the CLI reference against the parser, the
    terminal recordings, the strict docs build, then every link between
    the pages, anchors included, which the build doesn't check)
