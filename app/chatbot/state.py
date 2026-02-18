user_states = {}

def get_state(user):
    return user_states.get(user, {"level": "menu"})

def set_state(user, state):
    user_states[user] = state
