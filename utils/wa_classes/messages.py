from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from src.core import Runner
    from .groups import GroupMetadata


@dataclass
class Message:
    id: str
    text: str
    sender: str
    chat: str
    is_group: bool
    is_from_me: bool
    msg_type: str
    download: callable
    quoted: Optional[Message]
    group_metadata: Optional[GroupMetadata]
    is_admin_group: bool
    is_owner: bool
    is_bot: bool
    reply: callable
    runner: Runner
    # The following are optional and it will be set by the CommandHandler.handle method
    args: List[str] = field(default_factory=list, init=True)
    body: Optional[str] = field(default=None, init=True)
    command: Optional[str] = field(default=None, init=True)
    used_prefix: Optional[str] = field(default=None, init=True)
