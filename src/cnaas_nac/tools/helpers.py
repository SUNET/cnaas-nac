def get_user_replies(username, replies):
    result = []

    for user_reply in replies:
        if 'username' not in user_reply:
            continue
        if user_reply['username'] != username:
            continue
        del user_reply['id']
        del user_reply['username']
        result.append(user_reply)
    return result


def get_user_port(username, nas_ports):
    nas_port = None
    for port in nas_ports:
        if port['username'] == username:
            nas_port = port
    return nas_port


def get_is_active(username, users):
    for user in users:
        if 'username' not in user:
            continue
        if user['username'] != username:
            continue
        if user['op'] == ':=':
            return True
    return False


def get_last_seen(username, last_seen):
    for user in last_seen:
        if 'username' not in user:
            continue
        if user['username'] != username:
            continue
        return str(user['authdate'])
    return None
