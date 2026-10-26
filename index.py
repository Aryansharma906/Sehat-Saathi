"""Vercel entrypoint for the isolated public demonstration."""

import os

os.environ["SEHAT_ENV"] = "demo"

from webapp.main import app  # noqa: E402
