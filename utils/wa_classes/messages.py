from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from src.core import Runner
    from .groups import GroupMetadata

@dataclass
class QuotedMessage:
    id: str
    sender: str
    msg_type: str
    text: str
    is_admin_group: bool
    is_owner: bool
    is_bot: bool
    download: callable 
    reply: callable 
    # args: List[str] = field(default_factory=list, init=True)
    # body: Optional[str] = field(default=None, init=True)
    # command: Optional[str] = field(default=None, init=True)
    # used_prefix: Optional[str] = field(default=None, init=True)

    def __repr__(self) -> str:
        string = f'''QuotedMessage (
            id: {self.id},
            sender: {self.sender},
            msg_type: {self.msg_type},
            text: {self.text},
            is_admin_group: {self.is_admin_group},
            is_owner: {self.is_owner},
            is_bot: {self.is_bot},
            reply: reply(text=str),
            download: download()
        )
        '''.strip()
        return string


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
    group_metadata: Optional[GroupMetadata]
    is_admin_group: bool
    is_owner: bool
    is_bot: bool
    reply: callable
    runner: Runner
    # The following are optional and it will be set by the CommandHandler.handle method
    quoted: Optional[QuotedMessage] = field(default=None, init=True)
    args: List[str] = field(default_factory=list, init=True)
    body: Optional[str] = field(default=None, init=True)
    command: Optional[str] = field(default=None, init=True)
    used_prefix: Optional[str] = field(default=None, init=True)

    def __repr__(self) -> str:
        return f'''Message (
            id: {self.id},
            text: {self.text},
            sender: {self.sender},
            chat: {self.chat},
            is_group: {self.is_group},
            is_from_me: {self.is_from_me},
            msg_type: {self.msg_type},
            download: download(),
            quoted: {self.quoted},
            group_metadata: {self.group_metadata},
            is_admin_group: {self.is_admin_group},
            is_owner: {self.is_owner},
            is_bot: {self.is_bot},
            reply: reply(text=str),
            runner: Runner(name={self.runner.bot_name})
        )
        '''.strip()
