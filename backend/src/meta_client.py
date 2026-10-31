import os

from dotenv import load_dotenv
from openai import OpenAI


# Load values from .env
load_dotenv()


DEFAULT_BASE_URL = (
    "https://inference.baseten.co/v1"
)

DEFAULT_MODEL = (
    "meta-models/"
    "muse-spark-open-1026"
)


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

    return (
        os.getenv(
            "MODEL_API_KEY"
        )
        or os.getenv(
            "BASETEN_API_KEY"
        )
    )


def model_is_configured():
    """
    Return True if an API key is available.
    """

    return bool(
        get_api_key()
    )


def get_client():
    """
    Create an OpenAI-compatible client.
    """

    api_key = get_api_key()

    if not api_key:

        raise RuntimeError(
            "No model API key found. "
            "Add BASETEN_API_KEY to .env."
        )

    base_url = os.getenv(
        "MODEL_BASE_URL",
        DEFAULT_BASE_URL
    )

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=90.0,
    )


def get_model_name():
    """
    Get model name from environment.
    """

    return os.getenv(
        "MODEL_NAME",
        DEFAULT_MODEL
    )


def ask_muse(
    prompt,
    temperature=0.2
):
    """
    Send an investigation prompt
    to Muse Spark Open.
    """

    client = get_client()

    model = get_model_name()

    try:

        response = (
            client
            .chat
            .completions
            .create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content":
                            SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content":
                            prompt,
                    },
                ],
                temperature=
                    temperature,
            )
        )

    except Exception as error:

        raise RuntimeError(
            "Muse API request failed. "
            "Check your API key, model name, "
            "credits, and provider access.\n\n"
            f"Original error: {error}"
        ) from error

    message = (
        response
        .choices[0]
        .message
        .content
    )

    return message


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

        answer = ask_muse(
            "Reply with exactly: "
            "Veritas online."
        )

        print(
            "\nResponse:\n"
        )

        print(answer)