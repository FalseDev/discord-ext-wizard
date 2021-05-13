import asyncio
import inspect
from typing import Any, Callable, Dict, List, Optional, Union

from discord.abc import Messageable
from discord.ext.commands import AutoShardedBot, Bot, CommandError, UserInputError

from discord import Color, Embed, Emoji, Member, Message, Reaction, User

from .converters import ConverterMapping
from .prompt import Prompt

BotType = Union[Bot, AutoShardedBot]


async def maybe_async(func, *args, **kwargs):
    res = func(*args, **kwargs)
    if inspect.iscoroutine(res):
        return await res
    return res


class WizardFailure(CommandError):
    pass


class EmbedWizard:
    def __init__(
        self,
        *,
        prompts: List[Prompt],
        bot: BotType,
        channel: Messageable,
        user: Union[User, Member],
        converters: Dict[type, Callable] = None,
        default_timeout=60,
        yes_emoji: str = "\u2705",
        no_emoji: str = "\u274c",
    ) -> None:
        self.prompts: List[Prompt] = prompts
        self.channel: Messageable = channel
        self.user: Union[User, Member] = user
        self.bot: BotType = bot
        self._message: Optional[Message] = None
        self.converters: ConverterMapping = ConverterMapping(
            {} if converters is None else converters
        )
        self.default_timeout: int = default_timeout
        self.results: List[Any] = []

        # Emojis
        self.yes_emoji: str = yes_emoji
        self.no_emoji: str = no_emoji

    # Properties

    @property
    def message(self) -> Message:
        if not self._message:
            raise RuntimeError("Wizard hasn't started")
        return self._message

    @property
    def embed(self) -> Embed:
        return self.message.embeds[0]

    # Default checks

    def default_message_check(self, m: Message) -> bool:
        return m.channel == self.channel and self.user == m.author

    def default_reaction_check(self, r: Reaction, u: User) -> bool:
        return u == self.user and self.message == r.message

    # Check combiners

    def combine_message_checks(self, check: Optional[Callable]):
        if not check:
            return self.default_message_check

        def combined_check(m: Message):
            return self.default_message_check(m) and check(m)

        return combined_check

    def combine_reaction_checks(self, check: Optional[Callable]):
        if not check:
            return self.default_reaction_check

        def combined_check(r: Reaction, u: User):
            return self.default_reaction_check(r, u) and check(r, u)

        return combined_check

    # Helpers

    def get_timeout(self, prompt_timeout):
        return prompt_timeout or self.default_timeout

    # Input methods

    async def get_actual_input(self, prompt: Prompt):
        if not prompt.reaction_interface and not issubclass(
            prompt.res_type, (Reaction, Emoji)
        ):
            return await self.get_message_input(prompt)
        return await self.get_reaction_input(prompt)

    async def get_message_input(self, prompt: Prompt):
        converter = self.converters[prompt.res_type]
        check = self.combine_message_checks(prompt.check)
        timeout = self.get_timeout(prompt.timeout)
        msg = await self.bot.wait_for("message", check=check, timeout=timeout)
        ctx = await self.bot.get_context(msg)
        return await maybe_async(converter, ctx, msg.content)

    async def get_reaction_input(self, prompt: Prompt):
        timeout = self.get_timeout(prompt.timeout)
        if prompt.res_type in (Reaction, Emoji):
            check = self.combine_reaction_checks(prompt.check)
            reaction, _ = await self.bot.wait_for(
                "reaction_add", check=check, timeout=timeout
            )
            if prompt.res_type is Reaction:
                return reaction
            return reaction.emoji

        if prompt.res_type is bool:
            await self.message.add_reaction(self.yes_emoji)
            await self.message.add_reaction(self.no_emoji)

            def bool_check(reaction: Reaction, user: User):
                return reaction.emoji in (self.yes_emoji, self.no_emoji)

            check = self.combine_reaction_checks(bool_check)
            reaction, _ = await self.bot.wait_for(
                "reaction_add", check=check, timeout=timeout
            )
            return reaction.emoji == self.yes_emoji

        raise NotImplementedError(
            "Reaction input for given res_type {0.res_type} is unavailable!".format(
                prompt
            )
        )

    # Front Facing methods
    async def get_input(self, prompt: Prompt):
        retries = 0
        while retries < prompt.max_retries:
            try:
                result = await self.get_actual_input(prompt)
                if prompt.post_check:
                    await maybe_async(prompt.post_check, result)
                return result
            except UserInputError as e:
                await self.handle_error(e)
            retries += 1
        raise WizardFailure("Maximum retries reached")

    async def start(self) -> None:
        if self._message:
            raise RuntimeError("Wizard already started")
        embed = Embed(title="Wizard", color=Color.green())
        prompt = self.prompts[0]
        embed.add_field(
            name=prompt.title,
            value=prompt.get_waiting_message(),
            inline=False,
        )
        self._message = await self.channel.send(embed=embed)

    async def update_message(
        self, prompt: Prompt, next_prompt: Optional[Prompt], result
    ) -> None:
        self.update_embed(prompt, next_prompt, result)
        await self.message.edit(embed=self.embed)

    def update_embed(
        self, prompt: Prompt, next_prompt: Optional[Prompt], result
    ) -> None:
        embed = self.embed
        embed.remove_field(-1)
        embed.add_field(name=prompt.title, value=self.to_str(result), inline=False)
        if next_prompt:
            embed.add_field(
                name=next_prompt.title,
                value=next_prompt.get_waiting_message(),
                inline=False,
            )
        else:
            embed.add_field(name="End", value="Wizard has ended", inline=False)

    async def run(self):
        await self.start()
        for index in range(len(self.prompts)):
            prompt = self.prompts[index]
            result = await self.get_input(prompt)
            self.results.append(result)
            next_prompt = (
                self.prompts[index + 1] if len(self.prompts) > (index + 1) else None
            )
            await self.update_message(prompt, next_prompt, result)
        return self.results

    async def handle_error(self, e: Exception):
        await self.channel.send(e)

    def to_str(self, result):
        if hasattr(result, "mention"):
            return result.mention
        if isinstance(result, Message):
            return "Message with ID {0.id} in {0.channel.mention}".format(result)
        return str(result)
