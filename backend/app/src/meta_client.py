import json

from config import settings
from src.http_client import post_json

SYSTEM_PROMPT = """
You are Veritas, an engineering evidence
verification assistant for industrial maintenance.

You support human engineers during
troubleshooting investigations.

You do NOT make autonomous engineering
decisions.

Your responsibilities are to:

- analyze supplied engineering evidence
- identify relevant historical incidents
- verify procedure revision context
- identify superseded information
- detect conflicts between sources
- distinguish confirmed evidence from hypotheses
- identify missing information
- recommend investigation steps
- cite the supplied source filenames

Important safety rules:

- Never claim that equipment has been diagnosed
  unless the supplied evidence proves it.
- Never invent measurements.
- Never invent maintenance history.
- Never invent documents.
- Never authorize equipment operation,
  shutdown, repair, or replacement.
- Prefer CURRENT technical procedures over
  SUPERSEDED procedures.
- Clearly state uncertainty.
"""


def get_api_key():
    """
    Support either generic MODEL_API_KEY
    or BASETEN_API_KEY.
    """

    return settings.MODEL_API_KEY


def model_is_configured():
    """
    Return True if an API key is available.
    """

    return bool(
        get_api_key()
    )


def get_model_name():
    """
    Get model name from environment.
    """

    return settings.MODEL_NAME


async def ask_muse(
    prompt,
    temperature=0.2
):
    """
    Send an investigation prompt
    to Muse Spark Open.
    """

    model = get_model_name()

    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "No model API key found. "
            "Configure MODEL_API_KEY or BASETEN_API_KEY "
            "in Worker secrets or local .env."
        )

    try:
        response = await post_json(
            f"{settings.MODEL_BASE_URL.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            payload={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
            },
        )
    except Exception as error:
        raise RuntimeError(
            "Muse API request failed. Check your API key, model name, "
            f"credits, and provider access. Original error: {error}"
        ) from error

    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("Muse API returned an unexpected response.") from error


if __name__ == "__main__":

    if not model_is_configured():

        print(
            "Muse is not configured yet."
        )

        print(
            "Add BASETEN_API_KEY "
            "to your .env file."
        )

    else:

        print(
            "Testing model:",
            get_model_name()
        )

        import asyncio

        answer = asyncio.run(
            ask_muse("Reply with exactly: Veritas online.")
        )

        print(
            "\nResponse:\n"
        )

        print(answer)