from typing import Dict, Any
from ray import serve
from utils import TelegramChatListener, DataBaseBinding


@serve.deployment
class Scrapper:

    def __init__(self):
        self.listener = TelegramChatListener()

    async def __call__(self) -> Dict[str, Any]:
        async with self.listener.client:
            self.listener.client.loop.run_until_complete(
            self.listener.listen())
