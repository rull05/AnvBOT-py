from neonize.events import MessageEv
from neonize.client import NewClient
from neonize.proto import Neonize_pb2 as WaProto
from typing import List

class MessageSerialize:
    command: str | None
    body: str | None
    args: List[str] | None

    def __init__(self, runner: NewClient, message: MessageEv):
        self.runner = runner
        self._message = message
        self._msg_source = self._message.Info.MessageSource
    
    @property
    def quoted(self):
        raise NotImplementedError()

    def reply(self, text: str):
        return self.runner.reply_message(text, self._message)

    @property
    def is_from_me(self):
        return self._message.Info.MessageSource.IsFromMe


    @property
    def media_data(self):
        return self.runner.download_any(self._message)
    

    @property
    def sender(self):
        return self._get_sender_jid(msg_source, is_group)


    @property
    def chat(self):
        return self._get_jid(self._msg_source.Chat)
    

    @property
    def is_group(self):
        return self._msg_source.IsGroup


    @property
    def text(self):
        return self._get_message_text()
    

    def _get_jid(self, chat) -> str:
        return chat.User + '@' + chat.Server


    def _get_sender_jid(self, msg_source, is_group) -> str:
        if is_group:
            return self.get_jid(msg_source.Chat)
        return self.get_jid(msg_source.Sender)

    def _get_message_type(self):
        return dir(self._message)[0]


    def _get_message_text(self) -> str:
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


    def set_attr(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
            return True
        return False

