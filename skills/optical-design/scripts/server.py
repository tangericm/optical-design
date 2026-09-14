# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp==2.2.0", "numpy>=1.26"]
# ///
"""Owned optical CLI jobs over official MCP stdio; see references/audited/interactive.md."""
from __future__ import annotations

import argparse
import sys
from contextlib import asynccontextmanager
from typing import Any, Literal

# Keep the installed skill tree unchanged during normal CLI use.
sys.dont_write_bytecode = True

from _lib.tool_jobs import JobManager
from mcp.server import MCPServer
from pydantic import BaseModel, ConfigDict


class StartRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    action: Literal['inspect', 'edit', 'audit', 'refocus', 'tolerance', 'optimize', 'sensitivity']
    backend: Literal['optiland', 'zos']
    model: str
    model_sha256: str
    spec: str | None = None
    spec_sha256: str | None = None
    changes: str | None = None
    changes_sha256: str | None = None
    perturbations: str | None = None
    perturbations_sha256: str | None = None
    tolerances: str | None = None
    tolerances_sha256: str | None = None
    variables: str | None = None
    variables_sha256: str | None = None
    validation_spec: str | None = None
    validation_spec_sha256: str | None = None


def create_server(manager):
    @asynccontextmanager
    async def lifespan(server):
        try:
            yield manager
        finally:
            manager.close()

    server = MCPServer('Optical Design', lifespan=lifespan,
                       instructions='Start copied-model CLI jobs; job completion is separate from optical acceptance.')

    @server.tool()
    def capabilities() -> dict[str, Any]:
        """List supported actions, declared roots, and installed optional engine versions."""
        return manager.capabilities()

    @server.tool()
    def start(request: StartRequest) -> dict[str, Any]:
        """Start one allowlisted CLI job using exact SHA256-checked input snapshots."""
        return manager.start(**request.model_dump())

    @server.tool()
    def status(job_id: str) -> dict[str, Any]:
        """Read owned job state and independently checked optical acceptance."""
        return manager.status(job_id)

    @server.tool()
    def cancel(job_id: str) -> dict[str, Any]:
        """Cancel this server's owned process tree; partial artifacts remain diagnostic only."""
        return manager.cancel(job_id)

    @server.tool()
    def results(job_id: str) -> dict[str, Any]:
        """Return only a fully validated receipt; always retain owned diagnostic log paths."""
        return manager.results(job_id)

    @server.tool()
    def review(job_id: str) -> dict[str, Any]:
        """Render a verified owned job receipt as a local HTML and Markdown review package."""
        return manager.review(job_id)

    return server


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, help='host-declared directory for all job artifacts')
    parser.add_argument('--input-root', required=True, action='append', help='host-declared read directory; repeatable')
    args = parser.parse_args(argv)
    manager = JobManager(args.workspace, args.input_root)
    try:
        create_server(manager).run(transport='stdio')
    finally:
        manager.close()


if __name__ == '__main__':
    main()
