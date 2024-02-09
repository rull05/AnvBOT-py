from neonize.proto.Neonize_pb2 import JID


def str_to_jid(jid: str, raw_agent=0, device=0, integrator=0, is_empty=False) -> JID:
    user, server = jid.split('@')
    return JID(User=user.strip(),
        Server=server.strip(),
        RawAgent=raw_agent,
        Device=device,
        Integrator=integrator, 
        IsEmpty=is_empty
    )

def jid_to_str(jid: JID)-> str:
    if jid.IsEmpty:
        return ''
    if hasattr(jid, 'User') and hasattr(jid, 'Server'):
        return f'{JID.User}@{JID.Server}'
    return ''