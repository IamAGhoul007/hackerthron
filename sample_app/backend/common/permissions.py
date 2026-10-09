class Permissions:
    def has_role(self, user_role: str, required_role: str):
        return user_role == required_role
