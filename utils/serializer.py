from typing import Optional, TYPE_CHECKING, List
from utils.wa_classes import GroupMetadata, Message, GroupParticipant, GroupDesc, GroupSubject
from .jid import str_to_jid, jid_to_str

if TYPE_CHECKING:
    from src.core import Runner
    from neonize.events import MessageEv
    from neonize.proto.Neonize_pb2 import SendResponse, GroupParticipant as GroupParticipantsProto, GroupTopic, GroupName, GroupInfo
    

class GroupSerialize:

    @staticmethod
    def serialize(__group_info: 'GroupInfo') -> GroupMetadata:
        group_jid = str_to_jid(__group_info.JID)
        group_owner_jid = jid_to_str(__group_info.OwnerJID)
        group_participants = GroupSerialize._serialize_participants(__group_info.Participants)
        group_desc = GroupSerialize._serialize_desc(__group_info.GroupTopic)
        group_subject = GroupSerialize._serialize_subject(__group_info.GroupName)

        return GroupMetadata(
            owner_jid=group_owner_jid,
            jid=group_jid,
            desc=group_desc,
            subject=group_subject,
            participants=group_participants,
            is_locked=__group_info.GroupLocked.isLocked,
            is_announce=__group_info.GroupAnnounce.IsAnnounce,
            is_ephemeral=__group_info.GroupEphemeral.IsEphemeral,
            is_incognito=__group_info.GroupIncognito.IsIncognito,
            is_parent=__group_info.GroupParent.IsParent,
            group_linked_parent_jid=jid_to_str(__group_info.GroupLinkedParent.LinkedParentJID),
            is_default_sub_group=__group_info.GroupIsDefaultSub.IsDefaultSubGroup,
            created_at=__group_info.GroupCreated,
        )

    @staticmethod
    def _serialize_participants(participants: List['GroupParticipantsProto']) -> List[GroupParticipant]:
        return [
            GroupParticipant(
                jid=jid_to_str(p.JID),
                is_admin='super_admin' if p.IsSuperAdmin else 'admin' if p.IsAdmin else None,
                display_name=p.DisplayName,
            ) for p in participants
        ]

    @staticmethod
    def _serialize_desc(group_topic: 'GroupTopic') -> GroupDesc:
        return GroupDesc(
            topic=group_topic.Topic,
            topic_id=group_topic.TopicID,
            set_at=group_topic.TopicSetAt,
            set_by=jid_to_str(group_topic.TopicSetBy),
            topic_deleted=group_topic.TopicDeleted,
        )

    @staticmethod
    def _serialize_subject(group_name: 'GroupName') -> GroupSubject:
        return GroupSubject(
            name=group_name.Name,
            set_by=jid_to_str(group_name.NameSetBy),
            set_at=group_name.NameSetAt,
        )


class MessageSerialize:
    def __init__(self, runner: 'Runner', message: 'MessageEv'):
        self._runner = runner
        self._message = message

    def serialize(self) -> Message:
        return Message(
            id=self._id,
            text=self._text,
            sender=self._sender,
            chat=self._chat,
            is_group=self._is_group,
            is_from_me=self._is_from_me,
            msg_type=self._msg_type,
            download=self._download,
            quoted=self._quoted,
            group_metadata=self._group_metadata,
            is_admin_group=self._is_admin_group,
            is_owner=self._is_owner,
            is_bot=self._is_bot,
            reply=self._reply,
            runner=self._runner,
        )

    def _download(self):
        return self._runner.download_any(self._message.Message)

    def _reply(self, text: str) -> 'SendResponse':
        return self._runner.reply_message(text, self._message)

    @property
    def _is_bot(self) -> bool:
        return self._id.startswith('3EB0')

    @property
    def _msg_type(self) -> str:
        return self._message.Info.Type

    @property
    def _quoted(self) -> Optional['MessageSerialize']:
        return MessageSerialize(self._runner, self._message)

    @property
    def _group_metadata(self) -> Optional[GroupMetadata]:
        if self._is_group:
            group_info = self._runner.group_metadata(self._chat)
            return GroupSerialize.serialize(group_info)
        return None

    @property
    def _is_admin_group(self) -> bool:
        if self._is_group:
            for member in self._group_metadata.participants:
                if member.jid == self._sender:
                    return bool(member.is_admin)
        return False

    @property
    def _is_owner(self) -> bool:
        # TODO: Implement this
        return self._is_from_me

    @property
    def _is_from_me(self) -> bool:
        return self._msg_source.IsFromMe

    @property
    def _sender(self) -> str:
        if self._is_group:
            return self._extract_jid(self._msg_source.Sender)
        return self._extract_jid(self._msg_source.Chat)

    @property
    def _chat(self) -> str:
        return self._extract_jid(self._msg_source.Chat)

    @property
    def _is_group(self) -> bool:
        return self._msg_source.IsGroup

    @property
    def _text(self) -> str:
        msg = self._message.Message
        msg_fields = msg.ListFields()
        if msg_fields:
            _, field_value = msg_fields[0]
            if isinstance(field_value, str):
                return field_value
            text_attrs = ['text', 'caption']
            for attr in text_attrs:
                if hasattr(field_value, attr):
                    return getattr(field_value, attr)
        return ''

    @property
    def _id(self) -> str:
        return self._message.Info.ID

    @property
    def _msg_source(self):
        return self._message.Info.MessageSource

    def _extract_jid(self, chat) -> str:
        return f"{chat.User}@{chat.Server}"
