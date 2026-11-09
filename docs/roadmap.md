---
description: What's planned for alai but doesn't work yet.
---

# Roadmap

!!! warning "Plans, not features"

    Nothing on this page works yet. The rest of the documentation describes
    what alai does today, and this page lists what's planned, in no
    particular order. Any of it may change, and feedback is welcome in the
    [issue tracker](https://github.com/alai-sh/alai/issues).

I've opened a few issues around some future plans for alai. If you are
interested or have thoughts on some of these features please post a comment
to them. Some issues have some of my thoughts and ideas already posted while
others are just simple placeholders until I get to them.

- **Index authentication** ([#64](https://github.com/alai-sh/alai/issues/64)): Support
  indexes that require authentication.
- **Collection project metadata** ([#65](https://github.com/alai-sh/alai/issues/65)):
  Replace `galaxy.yml` with metadata stored in `alai.toml` for collection based
  projects. Will allow `alai add`/`alai remove` to manage collection dependencies.
  Will require build support, see below.
- **Building collections** ([#66](https://github.com/alai-sh/alai/issues/66)): Adds an
  `alai build` command that can build a collection using rules and logic defined in
  alai. Opens up support for other compression methods like Zstandard, and supporting a
  collection project `alai.toml` over `galaxy.yml`.
- **Publishing collections** ([#67](https://github.com/alai-sh/alai/issues/67)):
  Support publishing collections/ taking over the default sync for a collection to
  Alai. Also includes features like OIDC support and a pre-cursor for supporting
  signatures and attestation of artifacts.
- **Manage Ansible and Python deps** ([#68](https://github.com/alai-sh/alai/issues/68)):
  Provide a mechanism to manage Ansible and other Python dependencies as defined in
  `alai.toml` or some other metadata file. This might end up delegating to `uv` or some
  other tool using the generic
  [pylock.toml](https://packaging.python.org/en/latest/specifications/pylock-toml/) lock
  file or some other mechanism. A lot of moving parts here but would enable alai to
  orchestrate the whole environment and take into account the actual Ansible version
  when downloading dependencies.
- **Include Python/Bin deps in index** ([#69](https://github.com/alai-sh/alai/issues/69)):
  Collections do have a way to specify their Python and system dependencies in the
  collection itself. We could include this data in the index to make it easier to
  manage. The Python deps might be required for alai to manage the Python deps with
  Ansible as set out above.
- **Meta/set collection data** ([#70](https://github.com/alai-sh/alai/issues/70)):
  Support publicly defined meta/set collections that can provide a range or pinned
  set of collections under a common name. This would be independent of indexes so that
  anyone can define a grouping of collections for their use case and share them.
- **`requirements.yml`** ([#71](https://github.com/alai-sh/alai/issues/71)):
  Support importing collections from an existing `requirements.yml` into `alai.toml`
  or just with installing with `alai collection install -r`. Some hairy edge cases
  around `source` and `signatures` and how to handle them.
- **Excluding newer versions** ([#72](https://github.com/alai-sh/alai/issues/72)):
  A way for alai to ignore newly released collections until a set date has
  passed. Excluding newer versions helps to reproduce an old lock or hold back
  releases until they've been out a while and vetted by others first.
- **Signature/attestation** ([#73](https://github.com/alai-sh/alai/issues/73)):
  Support storing signatures and provide a way for callers to attest an
  artifact using alai. Most likely requires publishing to be in place already.
