# poetry-plugin-use-pip-global-index-url

## Description

*poetry-plugin-use-pip-global-index-url* is a
[plugin](https://python-poetry.org/docs/master/plugins/) for
[poetry](https://python-poetry.org/), the Python packaging and dependency
manager. It has poetry substitute the default connection to pypi.org with
a connection to a pypi.org mirror or pull-through cache defined in the global pip config (i.e. the result of ``pip config get global.index-url``) **without requiring
project configuration changes**. This is ideal for situations where an
access-restricted or otherwise unsuitable-for-general-use pypi.org mirror must
be used by a subset of project contributors, and is managed in the pip config.
For example:

* A private PyPI mirror internal to a business, required by company policy
* A limited-access PyPI mirror in a region where pypi.org is restricted
* A regional mirror that is more performant for a few users, and less performant
  for everyone else

These mirrors can be used without this plugin by [adding them as project
repositories](https://python-poetry.org/docs/repositories/). However, this
requires the mirror to be included in the project's configuration, and this also
results in source entries for the mirror appearing in `poetry.lock`. Since only
a subset of project contributors can use these mirrors, that subset of users
would need to replace and remove references to the mirror repository each time
they want to contribute their changes back to the project. This is suboptimal.

## Usage

### Installation

Follow poetry's [plugin installation instructions](https://python-poetry.org/docs/master/plugins/#using-plugins), replacing `poetry-plugin` with `poetry-plugin-use-pip-global-index-url`.

## Compatibility

_poetry-plugin-pypi-mirror_ depends on poetry internals which can change between
poetry releases. It's important to ensure compatibility between the poetry
version in use and the plugin version in use.

| Poetry version(s) | Compatible plugin version(s) |
| ----------------- | ---------------------------- |
| ~1.3.0            | ^0.2.0                       |
| ~1.2.1            | < 0.2.0                      |

## See also

* [poetry-plugin-pypi-mirror](https://github.com/arcesium/poetry-plugin-pypi-mirror) - original plugin which this plugin is forked from

* [python-poetry/poetry#1632](https://github.com/python-poetry/poetry/issues/1632) - poetry feature request to add support for global repository URL replacement
