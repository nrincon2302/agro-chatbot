user_states = {}


def get_state(user):
    return user_states.get(user)


def set_state(user, category):
    user_states[user] = category


def clear_state(user):
    if user in user_states:
        del user_states[user]
