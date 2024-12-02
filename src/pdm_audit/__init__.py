from pdm.core import Core

from .commands import AuditCommand


def register_commands(core: Core):
    core.register_command(AuditCommand, "audit")
