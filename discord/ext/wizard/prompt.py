from dataclasses import dataclass
from typing import Callable, Optional


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
    res_type: type = str
