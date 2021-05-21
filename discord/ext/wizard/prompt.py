from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

from discord.ext.commands import Context

__all__ = ("Prompt",)


@dataclass
class Prompt:
    title: str
    max_retries: int = 5
    key: Optional[str] = None
    description: Optional[str] = None
    check: Optional[Callable] = None
    post_check: Optional[Callable] = None
    timeout: Optional[int] = None
    reaction_interface: Optional[bool] = None
    res_type: Union[Callable[[Context, str], Any], type] = str
    to_str: Optional[Callable[[Any], str]] = None

    def get_waiting_message(self):
        return f"{self.description}\nWaiting...." if self.description else "Waiting..."
