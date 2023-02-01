from __future__ import annotations

from cleo.io.io import IO
from poetry.config.config import Config
from poetry.core.packages.package import Package
from poetry.core.semver.version import Version
from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry
from poetry.repositories.legacy_repository import LegacyRepository
from poetry.repositories.pypi_repository import PyPiRepository
from subprocess import PIPE, Popen
from poetry.repositories.repository_pool import Priority

# Hopefully the default repo name never changes. It'd be nice if this value was
# exposed in poetry as a constant.
DEFAULT_REPO_NAME = "PyPI"


class UsePipGlobalIndexUrlPlugin(Plugin):
    # If pypi.org and common mirroring/pull-through-cache software used the same
    # standard API this plugin could simply modify the URL used by
    # PyPiRepository. Unfortunately, PyPiRepository uses the unstable
    # non-standard warehouse JSON API. To ensure maximum mirror compatibility
    # through standards compliance we replace the pypi.org PyPiRepository with a
    # (modified) LegacyRepository - which uses the PEP 503 API.
    def activate(self, poetry: Poetry, io: IO):
        # Using Popen like this silences any stderr when global.index-url can't be found.
        pip_global_index_url_out = Popen("pip config get global.index-url", shell=True, stdout=PIPE, stderr=PIPE)
        pip_global_index_url, stderr = pip_global_index_url_out.communicate()
        pip_global_index_url = pip_global_index_url.decode().strip()

        if not pip_global_index_url:
            return

        # It would be nice to print something out to say that we're using the index
        # at the url specified in pip config, but printing things here interferes with
        # outputs from other poetry commands.

        # All keys are lowercased in public functions
        repo_key = DEFAULT_REPO_NAME.lower()

        pypi_prioritized_repository = poetry.pool._repositories.get(repo_key)

        if pypi_prioritized_repository is None or not isinstance(
            pypi_prioritized_repository.repository, PyPiRepository
        ):
            return

        replacement_repository = SourceStrippedLegacyRepository(
            DEFAULT_REPO_NAME,
            pip_global_index_url,
            config=poetry.config,
            disable_cache=pypi_prioritized_repository.repository._disable_cache,
        )

        priority = pypi_prioritized_repository.priority

        poetry.pool.remove_repository(DEFAULT_REPO_NAME)
        poetry.pool.add_repository(
            repository=replacement_repository,
            default=priority == Priority.DEFAULT,
            secondary=priority == Priority.SECONDARY,
        )


class SourceStrippedLegacyRepository(LegacyRepository):
    def __init__(
        self,
        name: str,
        url: str,
        config: Config | None = None,
        disable_cache: bool = False,
    ) -> None:
        super().__init__(name, url, config, disable_cache)
    # Packages sourced from PyPiRepository repositories *do not* include their
    # source data in poetry.lock. This is unique to PyPiRepository. Packages
    # sourced from LegacyRepository repositories *do* include their source data
    # (type, url, reference) in poetry.lock. This becomes undesirable when we
    # replace the PyPiRepository with a LegacyRepository PyPI mirror, as the
    # LegacyRepository begins to write source data into the project. We want to
    # support mirror use without referencing the mirror repository within the
    # project, so this behavior is undesired.
    #
    # To work around this, we extend LegacyRepository. The extended version
    # drops source URL information from packages attributed to the repository,
    # preventing that source information from being included in the lockfile.
    def package(
        self, name: str, version: Version, extras: list[str] | None = None
    ) -> Package:
        try:
            index = self._packages.index(Package(name, version))
            package = self._packages[index]
        except ValueError:
            package = super().package(name, version, extras)
        # It is a bit uncomfortable for this plugin to be modifying an internal
        # attribute of the package object. That said, the parent class does the
        # same thing (although it's not released independently like this plugin
        # is). It'd be preferable if there was a way to convey our goal
        # explicitly to poetry so we could avoid unintentional breaking changes.
        #
        # As one example of the potential danger, the existence of a non-None
        # package._source_url value currently determines if source data will be
        # written to poetry.lock. If this conditional changes, users of the
        # plugin may suddenly see unexpected source entries in their lockfiles.
        package._source_url = None
        return package
