"""Vercel entrypoint for the public demo or password-protected test deployment."""

import os

deployment_mode = os.environ.get("SEHAT_ENV", "demo").strip().lower()
if deployment_mode not in {"demo", "test"}:
    raise RuntimeError("Vercel deployments must use SEHAT_ENV=demo or the protected SEHAT_ENV=test mode.")
os.environ["SEHAT_ENV"] = deployment_mode

from webapp.main import app  # noqa: E402
