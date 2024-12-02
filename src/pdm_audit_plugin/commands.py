import argparse
import logging
import sys
from typing import NoReturn, cast

from pip_audit._audit import AuditOptions, Auditor
from pip_audit._dependency_source import DependencySource, DependencySourceError
from pip_audit._fix import ResolvedFixVersion
from pip_audit._format import ColumnsFormat, JsonFormat, MarkdownFormat
from pip_audit._service import ConnectionError, OsvService, PyPIService, ResolvedDependency

from pdm.cli.commands.base import BaseCommand
from pdm.project import Project


def _fatal(msg: str) -> NoReturn:  # pragma: no cover
    logging.error(msg)
    sys.exit(1)


class PDMDependencySource(DependencySource):
    def __init__(self, project: Project) -> None:
        self.project = project

    def collect(self):
        return [
            ResolvedDependency(name, version=version)
            for name, version, _, _ in self.project.get_locked_repository().packages.keys()
            if version and version != ""
        ]

    def fix(self, fix_version: ResolvedFixVersion) -> None:
        pass


class AuditCommand(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-s", "--service", help="The audit source. Default is PyPi, can be pypi, osv.", default="pypi"
        )
        parser.add_argument(
            "-f",
            "--format",
            help="""the format to emit audit results in (choices: columns,
                        json, markdown)
                        (default: columns)""",
            default="columns",
        )
        parser.add_argument(
            "--desc",
            help="""
                        include a description for each vulnerability; `auto`
                        defaults to `on` for the `json` format. This flag has
                        no effect on the `cyclonedx-json` or `cyclonedx-xml`
                        formats. (default: auto)""",
            default="auto",
        )
        parser.add_argument(
            "--enable-cache", help="enable the vulnerability query result or not, (default true)", default=True
        )
        parser.add_argument("--cache-ttl", help="the cache time to live in seconds, (default 3600)", default=1800)

    def handle(self, project: Project, options: argparse.Namespace) -> None:
        if not project.root.joinpath(".audit_cache").exists():
            project.root.joinpath(".audit_cache").mkdir()
        cache_ttl = int(options.cache_ttl)
        enable_cache = options.enable_cache
        format = options.format
        service = PyPIService(project.root.joinpath(".audit_cache") if enable_cache else None, cache_ttl)
        if options.service == "osv":
            service = OsvService(project.root.joinpath(".audit_cache") if enable_cache else None, cache_ttl)
        auditor = Auditor(service, AuditOptions(False))
        source = PDMDependencySource(project)
        result = {}
        try:
            for spec, vulns in auditor.audit(source):
                spec = cast(ResolvedDependency, spec)
                result[spec] = vulns
        except DependencySourceError as e:
            _fatal(str(e))
        except ConnectionError as e:
            # The most common source of connection errors is corporate blocking,
            # so we offer a bit of advice.
            _fatal(str(e))
        formatter = ColumnsFormat(True, True)
        fixes = []
        if format == "json":
            formatter = JsonFormat(True, True)
        elif format == "markdown":
            formatter = MarkdownFormat(True, True)
        print(formatter.format(result, fixes), file=sys.stdout)
