import asyncio
import inspect
from typing import Callable, Dict, List, Optional, Union

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
        converters: Dict[type, Callable],
        default_timeout=60,
    ) -> None:
        self.prompts = prompts
        self.channel = channel
        self.user = user
        self.bot = bot
        self._message: Optional[Message] = None
        self.converters = ConverterMapping(converters)
        self.default_timeout = default_timeout
        self.results = []

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

    def default_reaction_check(self, u: User, r: Reaction) -> bool:
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

        def combined_check(u: User, r: Reaction):
            return self.default_reaction_check(u, r) and check(u, r)

        return combined_check

    # Helpers

    def get_timeout(self, prompt_timeout):
        return self.default_timeout or prompt_timeout

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
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise WizardFailure from exc
        ctx = await self.bot.get_context(msg)
        return await maybe_async(converter, ctx, msg.content)

    async def get_reaction_input(self, prompt: Prompt):
        raise NotImplementedError("Reaction input system is yet to be added!")

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
            print(f"Retries  {retries}")
        raise WizardFailure("Maximum retries reached")

    async def start(self) -> None:
        if self._message:
            raise RuntimeError("Wizard already started")
        embed = Embed(title="Wizard", color=Color.green())
        prompt = self.prompts[0]
        embed.add_field(
            name=prompt.title,
            value=f"{prompt.description}\nWaiting....",
        )
        self._message = await self.channel.send(embed=embed)

    async def update_message(
        self, prompt: Prompt, next_prompt: Optional[Prompt], result
    ) -> None:
        embed = self.embed
        embed.remove_field(-1)
        embed.add_field(name=prompt.title, value=self.to_str(result))
        if next_prompt:
            embed.add_field(
                name=next_prompt.title,
                value=f"{next_prompt.description}\nWaiting....",
            )
        else:
            embed.add_field(name="End", value="Wizard has ended")
        await self.message.edit(embed=self.embed)

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
        return str(result)
