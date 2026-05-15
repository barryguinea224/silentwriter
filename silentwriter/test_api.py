def get_user(user_id):
    return {"id": user_id}

def create_order(user_id, items):
    return {"user": user_id, "items": items}
