from typing import Optional, Union

from discord.ext.commands import UserInputError

from discord import Emoji, Member, PartialEmoji, Reaction, Role

from .wizard import EmbedWizard

__all__ = (
    "IntRangeCheck",
    "StringLengthCheck",
    "CurrentGuildEmojiCheck",
    "CurrentGuildReactionCheck",
    "RoleBelowMemberCheck",
)


class IntRangeCheck:
    def __init__(
        self,
        min_value: int = None,
        max_value: int = None,
        *,
        too_large_message: str = "Value too small, must be more than {}",
        too_small_message: str = "Value too large, must be less than {}",
    ) -> None:
        if min_value is None and max_value is None:
            raise RuntimeError("Both min and max can't be None")

        self.min_value: Optional[int] = min_value
        self.max_value: Optional[int] = max_value
        self.too_large_message: str = too_large_message
        self.too_small_message: str = too_small_message

    def __call__(self, wizard: EmbedWizard, value: int) -> None:
        if self.min_value is not None and self.min_value > value:
            raise UserInputError(self.too_small_message.format(self.min_value))

        if self.max_value is not None and self.max_value < value:
            raise UserInputError(self.too_large_message.format(self.max_value))


class StringLengthCheck(IntRangeCheck):
    def __init__(
        self,
        min_len: int = None,
        max_len: int = None,
        *,
        too_small_message: str = "Value too short, must be more than {}",
        too_large_message: str = "Value too large, must be less than {}",
    ) -> None:
        super().__init__(
            min_value=min_len,
            max_value=max_len,
            too_large_message=too_large_message,
            too_small_message=too_small_message,
        )

    def __call__(self, wizard: EmbedWizard, value: str) -> None:
        super().__call__(wizard, len(value))


class CurrentGuildEmojiCheck:
    def __init__(self, *, error_message: str = "The emoji is from a different server!"):
        self.error_message: str = error_message

    def __call__(
        self,
        wizard: EmbedWizard,
        emoji: Union[Emoji, PartialEmoji, str],
    ) -> None:
        if isinstance(emoji, str):
            return

        if isinstance(emoji, PartialEmoji):
            if emoji.is_unicode_emoji():
                return
            raise UserInputError(self.error_message)

        if isinstance(wizard.user, Member) and emoji.guild_id == wizard.user.guild.id:
            return
        raise UserInputError(self.error_message)


class CurrentGuildReactionCheck(CurrentGuildEmojiCheck):
    def __init__(
        self,
        *,
        error_message: str = "The emoji used in the reaction is from a different server!",
    ):
        self.error_message: str = error_message

    def __call__(self, wizard: EmbedWizard, reaction: Reaction) -> None:
        super().__call__(wizard, reaction.emoji)


class RoleBelowMemberCheck:
    def __init__(
        self, *, error_message: str = "The role selected is above your highest role!"
    ) -> None:
        self.error_message: str = error_message

    def __call__(self, wizard: EmbedWizard, role: Role) -> None:
        user = wizard.user
        if not isinstance(user, Member):
            raise UserInputError(self.error_message)

        if user.guild.owner==user:
            return

        if (
            role.position >= user.top_role.position
        ):
            raise UserInputError(self.error_message)
