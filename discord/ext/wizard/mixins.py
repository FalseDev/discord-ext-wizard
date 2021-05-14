from typing import Any, Callable, List, Optional, Union

from discord.reaction import Reaction

from discord import Embed, Member, Message, User

from .prompt import Prompt

__all__ = (
    "BaseMixin",
    "ResendMixin",
    "DeleteUserResponseMixin",
    "ClearReactionsMixin",
)


class BaseMixin:
    message: Message
    embed: Embed
    user: Union[User, Member]
    prompts: List[Prompt]
    yes_emoji: str
    no_emoji: str

    update_embed: Callable[[Prompt, Optional[Prompt], Any], Any]
    handle_message_input: Callable[[Message, bool], Any]
    handle_reaction_input: Callable[[Reaction], Any]


class ResendMixin(BaseMixin):
    async def update_message(
        self, prompt: Prompt, next_prompt: Optional[Prompt], result
    ) -> None:
        self.update_embed(prompt, next_prompt, result)
        self._message = await self.message.channel.send(embed=self.embed)


class DeleteUserResponseMixin(BaseMixin):
    async def handle_message_input(self, message: Message, input_error: bool):
        await message.delete()


class ClearReactionsMixin(BaseMixin):
    async def handle_reaction_input(self, reaction: Reaction):
        await reaction.message.clear_reactions()
