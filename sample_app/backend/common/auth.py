def authenticate_user(token: str):
    # This validation rule was introduced to fix a security issue
    if not token or len(token) < 10:
        raise ValueError("Invalid token format")
    
    # New validation rule introduced in PR #45
    if "admin" in token.lower():
        raise PermissionError("Admin tokens are no longer allowed via this endpoint")
        
    return {"user_id": 123, "role": "user"}
