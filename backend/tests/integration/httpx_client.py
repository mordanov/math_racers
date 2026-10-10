from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

import httpx as _httpx

Response = _httpx.Response


def _csrf_details(url: str) -> tuple[str, str]:
    parsed = urlsplit(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    response = _httpx.get(f"{origin}/api/v1/auth/csrf", timeout=10.0)
    response.raise_for_status()
    token = response.cookies.get("csrf_token")
    if not token:
        raise RuntimeError("The API did not issue a CSRF token.")
    return origin, token


def _mutation_args(url: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    origin, token = _csrf_details(url)
    headers = dict(kwargs.pop("headers", {}) or {})
    headers["Origin"] = origin
    headers["X-CSRF-Token"] = token
    headers.pop("Cookie", None)
    cookies = dict(kwargs.pop("cookies", {}) or {})
    cookies["csrf_token"] = token
    kwargs["headers"] = headers
    kwargs["cookies"] = cookies
    return kwargs


def get(url: str, **kwargs: Any) -> Response:
    return _httpx.get(url, **kwargs)


def post(url: str, **kwargs: Any) -> Response:
    return _httpx.post(url, **_mutation_args(url, kwargs))


def put(url: str, **kwargs: Any) -> Response:
    return _httpx.put(url, **_mutation_args(url, kwargs))


def patch(url: str, **kwargs: Any) -> Response:
    return _httpx.patch(url, **_mutation_args(url, kwargs))


def delete(url: str, **kwargs: Any) -> Response:
    return _httpx.delete(url, **_mutation_args(url, kwargs))


class Client(_httpx.Client):
    def request(self, method: str, url: _httpx.URL | str, **kwargs: Any) -> Response:
        if method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            kwargs = _mutation_args(str(self.base_url.join(url)), kwargs)
            cookies = kwargs.pop("cookies", {})
            if cookies:
                headers = dict(kwargs.get("headers", {}))
                headers["Cookie"] = "; ".join(f"{name}={value}" for name, value in cookies.items())
                kwargs["headers"] = headers
        return super().request(method, url, **kwargs)


def __getattr__(name: str) -> Any:
    return getattr(_httpx, name)
