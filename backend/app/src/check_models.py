import asyncio

from src.meta_client import ask_muse, model_is_configured


async def main():
    if not model_is_configured():
        raise RuntimeError("Configure a model API key before testing Muse.")

    answer = await ask_muse("Reply with exactly: Muse online.")
    print(answer)


asyncio.run(main())