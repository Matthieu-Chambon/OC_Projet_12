def save_token_locally(token):
    file_path = ".session_token"
    with open(file_path, "w") as f:
        f.write(token)


def load_token():
    file_path = ".session_token"
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None
