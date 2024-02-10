from neonize.proto.Neonize_pb2 import JID
from neonize.utils.jid import JIDToNonAD, Jid2String


def str_to_jid(jid: str, raw_agent=0, device=0, integrator=0, is_empty=False) -> JID:
    user, server = jid.split('@')
    return JID(User=user,
        Server=server,
        RawAgent=raw_agent,
        Device=device,
        Integrator=integrator, 
        IsEmpty=is_empty
    )

def jid_to_str(jid: JID)-> str:
    return Jid2String(JIDToNonAD(jid))

