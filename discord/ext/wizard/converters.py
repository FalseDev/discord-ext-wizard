from typing import Awaitable, Callable, Dict, Mapping

from discord.ext.commands import BadArgument, BadBoolArgument, Context
from discord.ext.commands import converter as discord_converters


async def convert_int(_, content: str) -> int:
    try:
        return int(content)
    except ValueError as exc:
        raise BadArgument(f"Invalid int value: {content}") from exc


async def convert_bool(_, content: str) -> bool:
    s = content.lower()
    if s in ("yes", "y", "1", "true", "t"):
        return True
    if s in ("no", "n", "0", "false", "f"):
        return False
    raise BadBoolArgument(content)


async def convert_str(_, content: str) -> str:
    return content


class ConverterMapping:
    preset_converters: Dict[type, Callable] = {
        bool: convert_bool,
        str: convert_str,
        int: convert_int,
    }

    def __init__(self, converters: Mapping[type, Callable]) -> None:
        self.converters = converters

    def __getitem__(self, key: type) -> Callable[[Context, str], Awaitable]:
        if key in self.converters:
            return self.converters[key]

        if key in self.preset_converters:
            return self.preset_converters[key]

        try:
            return getattr(discord_converters, key.__name__ + "Converter")().convert
        except AttributeError as exc:
            raise RuntimeError("Couldn't find valid converter") from exc
