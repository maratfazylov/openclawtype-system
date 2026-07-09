"""Jenkins connector tools.

The connector supports the common Jenkins job API shape:
- read job metadata from ``<job-url>/api/json``;
- trigger a job through ``build`` or ``buildWithParameters``.

Build triggering is real by default because this connector targets a test
Jenkins instance. Pass ``dry_run=True`` to preview a request without starting a
build.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import httpx
from langchain_core.tools import tool


DEFAULT_JENKINS_JOB_URL = "https://devops.brojs.ru/job/marat/"
JENKINS_TIMEOUT = 20.0


def _env(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def _job_url(job_url: str | None = None) -> str:
    return (job_url or _env("JENKINS_JOB_URL") or DEFAULT_JENKINS_JOB_URL).rstrip("/") + "/"


def _job_token() -> str | None:
    return _env("JENKINS_JOB_TOKEN")


def _auth() -> tuple[str, str] | None:
    username = _env("JENKINS_USERNAME")
    api_token = _env("JENKINS_API_TOKEN")
    if username and api_token:
        return username, api_token
    return None


def _json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _mask_secret(secret: str | None) -> str:
    if not secret:
        return "<missing>"
    if len(secret) <= 8:
        return "<set>"
    return f"{secret[:4]}...{secret[-4:]}"


def _with_query(url: str, params: dict[str, str]) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.update(params)
    return urlunparse(parsed._replace(query=urlencode(query)))


def _jenkins_root_url(job_url: str) -> str:
    parsed = urlparse(job_url)
    return urlunparse((parsed.scheme, parsed.netloc, "/", "", "", ""))


def _crumb_headers(client: httpx.Client, base_url: str) -> dict[str, str]:
    crumb_url = urljoin(_jenkins_root_url(base_url), "crumbIssuer/api/json")
    response = client.get(crumb_url)
    if response.status_code == 404:
        return {}
    response.raise_for_status()
    payload = response.json()
    field = payload.get("crumbRequestField")
    crumb = payload.get("crumb")
    if isinstance(field, str) and isinstance(crumb, str):
        return {field: crumb}
    return {}


@tool
def get_jenkins_job_info(job_url: str | None = None) -> str:
    """Read basic metadata for the configured Jenkins job."""
    resolved_job_url = _job_url(job_url)
    api_url = urljoin(resolved_job_url, "api/json")
    params = {
        "tree": "name,url,buildable,color,lastBuild[number,url,result,timestamp],lastSuccessfulBuild[number,url]",
    }

    try:
        response = httpx.get(api_url, params=params, auth=_auth(), timeout=JENKINS_TIMEOUT)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        return _json(
            {
                "ok": False,
                "job_url": resolved_job_url,
                "error": str(exc),
            }
        )

    return _json(
        {
            "ok": True,
            "job_url": resolved_job_url,
            "job": response.json(),
        }
    )


@tool
def trigger_jenkins_job(
    job_url: str | None = None,
    parameters: dict[str, str] | None = None,
    dry_run: bool = False,
) -> str:
    """Trigger the configured Jenkins job, or preview the request when dry_run is true.

    Args:
        job_url: Jenkins job URL. If omitted, JENKINS_JOB_URL is used.
        parameters: Optional build parameters. When present, buildWithParameters is used.
        dry_run: When true, return the prepared request without starting a build.
            Defaults to false for the test Jenkins environment.
    """
    resolved_job_url = _job_url(job_url)
    build_path = "buildWithParameters" if parameters else "build"
    build_url = urljoin(resolved_job_url, build_path)
    token = _job_token()

    query_params = {key: str(value) for key, value in (parameters or {}).items()}
    if token:
        query_params["token"] = token
    request_url = _with_query(build_url, query_params) if query_params else build_url

    preview = {
        "job_url": resolved_job_url,
        "method": "POST",
        "endpoint": build_path,
        "uses_job_token": bool(token),
        "job_token": _mask_secret(token),
        "uses_basic_auth": bool(_auth()),
        "parameters": parameters or {},
    }

    if dry_run:
        return _json({"dry_run": True, **preview})

    if not token and not _auth():
        return (
            "Jenkins credentials are not set. Set JENKINS_JOB_TOKEN or "
            "JENKINS_USERNAME/JENKINS_API_TOKEN, or call with dry_run=True."
        )

    try:
        with httpx.Client(auth=_auth(), timeout=JENKINS_TIMEOUT) as client:
            headers = _crumb_headers(client, resolved_job_url) if _auth() else {}
            response = client.post(request_url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return _json({"ok": False, **preview, "error": str(exc)})

    return _json(
        {
            "ok": True,
            **preview,
            "status_code": response.status_code,
            "queue_url": response.headers.get("Location"),
        }
    )


JENKINS_TOOLS = [get_jenkins_job_info, trigger_jenkins_job]
