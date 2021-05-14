from typing import Any, Callable, List, Optional

from discord import Embed, Message

from .prompt import Prompt

__all__ = (
    "BaseMixin",
    "ResendMixin",
)


class BaseMixin:
    message: Message
    embed: Embed
    prompts: List[Prompt]

    update_embed: Callable[[Prompt, Optional[Prompt], Any], None]


class ResendMixin(BaseMixin):
    async def update_message(
        self, prompt: Prompt, next_prompt: Optional[Prompt], result
    ) -> None:
        self.update_embed(prompt, next_prompt, result)
        self._message = await self.message.channel.send(embed=self.embed)
