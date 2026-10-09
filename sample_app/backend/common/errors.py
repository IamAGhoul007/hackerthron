class NimbusError(Exception):
    pass

class ValidationError(NimbusError):
    pass
    
class AuthenticationError(NimbusError):
    pass
