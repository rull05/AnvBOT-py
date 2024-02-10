from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GroupDesc:
    """Group description"""
    topic: str
    topic_id: str
    set_at: int
    set_by: str
    topic_deleted: bool

@dataclass
class GroupSubject:
    """Group subject"""
    name: str
    set_by: str
    set_at: int


@dataclass
class GroupParticipant:
    """Group participant"""
    lid: str
    jid: str
    is_admin: Optional[str]
    display_name: str


@dataclass
class GroupMetadata:
    """Group metadata class"""
    owner_jid: str
    jid: str
    desc: GroupDesc
    subject: GroupSubject
    participants: List[GroupParticipant]
    is_locked: bool
    is_announce: bool
    is_ephemeral: bool
    is_incognito: bool
    is_parent: bool
    group_linked_parent_jid: str
    is_default_sub_group: bool
    created_at: float
