import json
from typing import Any


async def post_json(
    url: str,
    *,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    request_headers = {
        **headers,
        "Content-Type": "application/json",
    }
    request_body = json.dumps(payload)

    try:
        from workers import fetch
    except ImportError:
        try:
            import httpx
        except ImportError as error:
            raise RuntimeError(
                "Local HTTP requests require httpx; install the dev dependencies."
            ) from error

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                url,
                headers=request_headers,
                content=request_body,
            )
        if response.is_error:
            raise RuntimeError(
                f"HTTP request failed with status {response.status_code}: "
                f"{response.text}"
            )
        return response.json()

    response = await fetch(
        url,
        method="POST",
        headers=request_headers,
        body=request_body,
    )
    if not 200 <= response.status < 300:
        raise RuntimeError(f"HTTP request failed with status {response.status}")
    return response.json()
