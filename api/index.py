"""Vercel Python entrypoint for the Hypothesis WSGI app."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable

ResponseStart = Callable[[str, list[tuple[str, str]]], None]

REQUIRED_ENV_VARS = ("DATABASE_URL", "ELASTICSEARCH_URL", "SECRET_KEY")


class LazyApp:
    """Create the Pyramid app only when Vercel handles a request."""

    def __init__(self) -> None:
        self._app = None

    def __call__(self, environ: dict, start_response: ResponseStart) -> Iterable[bytes]:
        missing_vars = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
        if missing_vars:
            start_response("503 Service Unavailable", [("Content-Type", "text/plain")])
            return [
                (
                    "Hypothesis is deployed, but the Vercel environment is missing: "
                    f"{', '.join(missing_vars)}"
                ).encode()
            ]

        if self._app is None:
            from h.app import create_app

            self._app = create_app({})

        return self._app(environ, start_response)


# Vercel's Python runtime expects a module-level `app` WSGI callable.
app = LazyApp()
