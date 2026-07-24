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
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote, urlencode, urljoin, urlparse, urlunparse

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool


DEFAULT_JENKINS_JOB_URL = "https://devops.brojs.ru/job/marat/"
JENKINS_TIMEOUT = 20.0
REPO_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(REPO_ROOT / ".env")


def _env(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def _job_url(job_url: str | None = None) -> str:
    return (job_url or DEFAULT_JENKINS_JOB_URL).rstrip("/") + "/"


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


def _jenkins_full_name_from_job_url(job_url: str) -> str:
    parts = [part for part in urlparse(job_url).path.split("/") if part]
    names = [parts[index + 1] for index, part in enumerate(parts[:-1]) if part == "job"]
    return "/".join(names)


def _parent_folder_url(job_url: str) -> str:
    parsed = urlparse(job_url.rstrip("/") + "/")
    parts = [part for part in parsed.path.split("/") if part]
    job_indexes = [index for index, part in enumerate(parts) if part == "job"]
    if not job_indexes:
        return _jenkins_root_url(job_url)
    last_job_index = job_indexes[-1]
    parent_parts = parts[:last_job_index]
    parent_path = "/" + "/".join(parent_parts) + "/" if parent_parts else "/"
    return urlunparse((parsed.scheme, parsed.netloc, parent_path, "", "", ""))


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


def _folder_child_jobs(client: httpx.Client, folder_url: str) -> list[dict[str, Any]]:
    api_url = urljoin(folder_url, "api/json")
    response = client.get(
        api_url,
        params={"tree": "jobs[name,url,buildable,color]"},
    )
    response.raise_for_status()
    jobs = response.json().get("jobs", [])
    return jobs if isinstance(jobs, list) else []


def _resolve_build_job_url(client: httpx.Client, job_url: str) -> tuple[str, dict[str, Any] | None]:
    jobs = _folder_child_jobs(client, job_url)
    buildable_jobs = [
        job for job in jobs if job.get("buildable") is True and isinstance(job.get("url"), str)
    ]
    if len(buildable_jobs) != 1:
        return job_url, None
    selected = buildable_jobs[0]
    return selected["url"].rstrip("/") + "/", selected


def _client() -> httpx.Client:
    return httpx.Client(auth=_auth(), timeout=JENKINS_TIMEOUT)


def _require_auth() -> tuple[bool, str | None]:
    if _auth():
        return True, None
    return False, "JENKINS_USERNAME/JENKINS_API_TOKEN are required for this Jenkins action."


@tool
def get_jenkins_job_info(job_url: str | None = None) -> str:
    """Read metadata for the configured Jenkins job or folder."""
    resolved_job_url = _job_url(job_url)
    api_url = urljoin(resolved_job_url, "api/json")
    params = {
        "tree": (
            "name,url,buildable,color,"
            "lastBuild[number,url,result,timestamp],"
            "lastSuccessfulBuild[number,url],"
            "jobs[name,url,color,buildable,lastBuild[number,url,result,timestamp],"
            "lastSuccessfulBuild[number,url]]"
        ),
    }
    auth = _auth()

    try:
        response = httpx.get(api_url, params=params, auth=auth, timeout=JENKINS_TIMEOUT)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        return _json(
            {
                "ok": False,
                "job_url": resolved_job_url,
                "uses_basic_auth": bool(auth),
                "error": str(exc),
            }
        )

    payload = response.json()
    return _json(
        {
            "ok": True,
            "job_url": resolved_job_url,
            "uses_basic_auth": bool(auth),
            "is_folder": isinstance(payload.get("jobs"), list),
            "job_count": len(payload.get("jobs", [])) if isinstance(payload.get("jobs"), list) else None,
            "job": payload,
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
        job_url: Jenkins job URL. If omitted, the workshop Jenkins job URL is used.
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
            selected_job = None
            if job_url is None:
                resolved_job_url, selected_job = _resolve_build_job_url(client, resolved_job_url)
                build_url = urljoin(resolved_job_url, build_path)
                request_url = _with_query(build_url, query_params) if query_params else build_url
                preview["job_url"] = resolved_job_url
                if selected_job:
                    preview["selected_from_folder"] = {
                        "name": selected_job.get("name"),
                        "url": selected_job.get("url"),
                    }
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


@tool
def get_jenkins_job_config(job_url: str | None = None) -> str:
    """Read config.xml for a Jenkins job.

    Args:
        job_url: Jenkins job URL. If omitted and the workshop Jenkins URL points to a
            folder with exactly one buildable child job, that child is selected.
    """
    resolved_job_url = _job_url(job_url)
    auth_ok, auth_error = _require_auth()
    if not auth_ok:
        return _json({"ok": False, "job_url": resolved_job_url, "error": auth_error})

    try:
        with _client() as client:
            selected_job = None
            if job_url is None:
                resolved_job_url, selected_job = _resolve_build_job_url(client, resolved_job_url)
            response = client.get(urljoin(resolved_job_url, "config.xml"))
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return _json({"ok": False, "job_url": resolved_job_url, "error": str(exc)})

    return _json(
        {
            "ok": True,
            "job_url": resolved_job_url,
            "selected_from_folder": selected_job,
            "config_xml": response.text,
        }
    )


@tool
def copy_jenkins_job(
    new_job_name: str,
    source_job_url: str | None = None,
    folder_url: str | None = None,
    dry_run: bool = True,
) -> str:
    """Copy a Jenkins job inside a folder using Jenkins createItem mode=copy.

    Args:
        new_job_name: Name of the new Jenkins job, for example test02.
        source_job_url: Source Jenkins job URL. If omitted and the workshop Jenkins URL
            points to a folder with exactly one buildable child job, that child is selected.
        folder_url: Destination folder URL. If omitted, the source job parent folder is used.
        dry_run: When true, preview the createItem request without creating the job.
    """
    normalized_name = new_job_name.strip()
    if not normalized_name or "/" in normalized_name:
        return _json({"ok": False, "error": "new_job_name must be a single Jenkins item name."})

    auth_ok, auth_error = _require_auth()
    auth = _auth()
    resolved_source_url = _job_url(source_job_url)
    selected_job = None
    preview: dict[str, Any] = {
        "method": "POST",
        "source_job_url": resolved_source_url,
        "new_job_name": normalized_name,
        "endpoint": "createItem",
        "mode": "copy",
        "uses_basic_auth": bool(auth),
    }

    try:
        with _client() as client:
            if source_job_url is None:
                resolved_source_url, selected_job = _resolve_build_job_url(client, resolved_source_url)
            resolved_folder_url = (folder_url.rstrip("/") + "/") if folder_url else _parent_folder_url(resolved_source_url)
            source_full_name = _jenkins_full_name_from_job_url(resolved_source_url)
            endpoint_url = urljoin(resolved_folder_url, "createItem")
            query_params = {
                "name": normalized_name,
                "mode": "copy",
                "from": source_full_name,
            }
            request_url = _with_query(endpoint_url, query_params)
            preview.update(
                {
                    "folder_url": resolved_folder_url,
                    "source_job_url": resolved_source_url,
                    "source_full_name": source_full_name,
                    "selected_from_folder": selected_job,
                }
            )

            if dry_run:
                return _json({"dry_run": True, **preview})
            if not auth_ok:
                return _json({"ok": False, **preview, "error": auth_error})

            headers = _crumb_headers(client, resolved_folder_url)
            response = client.post(request_url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return _json({"ok": False, **preview, "error": str(exc)})

    return _json(
        {
            "ok": True,
            **preview,
            "status_code": response.status_code,
            "created_job_url": urljoin(resolved_folder_url, f"job/{quote(normalized_name)}/"),
        }
    )


@tool
def create_jenkins_job_from_config(
    new_job_name: str,
    config_xml: str,
    folder_url: str | None = None,
    dry_run: bool = True,
) -> str:
    """Create a Jenkins job from a config.xml payload.

    Args:
        new_job_name: Name of the new Jenkins job.
        config_xml: Jenkins config.xml payload.
        folder_url: Destination folder URL. If omitted, the workshop Jenkins URL is used
            when it is a folder.
        dry_run: When true, preview the createItem request without creating the job.
    """
    normalized_name = new_job_name.strip()
    if not normalized_name or "/" in normalized_name:
        return _json({"ok": False, "error": "new_job_name must be a single Jenkins item name."})
    if not config_xml.strip():
        return _json({"ok": False, "error": "config_xml must not be empty."})

    resolved_folder_url = (folder_url.rstrip("/") + "/") if folder_url else _job_url()
    auth_ok, auth_error = _require_auth()
    preview = {
        "method": "POST",
        "folder_url": resolved_folder_url,
        "new_job_name": normalized_name,
        "endpoint": "createItem",
        "mode": "config_xml",
        "uses_basic_auth": bool(_auth()),
        "config_xml_bytes": len(config_xml.encode("utf-8")),
    }
    if dry_run:
        return _json({"dry_run": True, **preview})
    if not auth_ok:
        return _json({"ok": False, **preview, "error": auth_error})

    try:
        with _client() as client:
            headers = {
                **_crumb_headers(client, resolved_folder_url),
                "Content-Type": "application/xml",
            }
            response = client.post(
                urljoin(resolved_folder_url, "createItem"),
                params={"name": normalized_name},
                content=config_xml.encode("utf-8"),
                headers=headers,
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return _json({"ok": False, **preview, "error": str(exc)})

    return _json(
        {
            "ok": True,
            **preview,
            "status_code": response.status_code,
            "created_job_url": urljoin(resolved_folder_url, f"job/{quote(normalized_name)}/"),
        }
    )


JENKINS_TOOLS = [
    get_jenkins_job_info,
    trigger_jenkins_job,
    get_jenkins_job_config,
    copy_jenkins_job,
    create_jenkins_job_from_config,
]
