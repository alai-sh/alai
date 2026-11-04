---
description: How alai finds collections through an index.
---

# Indexes

alai reads which collections exist, their versions and what they depend on
from an index, rather than from the Galaxy API. The default is
`https://index.alai.sh/`, a static mirror of Galaxy with a few changes to
make that metadata quicker to fetch. Collections are downloaded from the
location the index gives, and checked against the checksum it lists, which
`alai.lock` records.

Nothing needs configuring to use the default index. When you need another
index, such as a mirror of `index.alai.sh`, add it with
[`[[index]]`](alai-toml.md#index) or `--index`. A collection can be tied to
one index with [`[project.sources]`](alai-toml.md#projectsources). See
[Configuration](configuration.md#indexes) for how indexes are defined and
ordered.

## Running your own index

[alai-index](https://alai.sh/alai-index/) builds an index as a tree of static
files, from collection tarballs or by mirroring a Galaxy server, ready to
publish to a web server or bucket. Its docs also hold the specification:

- [Index format](https://alai.sh/alai-index/index-format/): the files an
  index serves and how alai reads them.
- [Plugin index](https://alai.sh/alai-index/plugin-index/): the plugin lists
  `alai find` searches.
