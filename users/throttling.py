from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class LoginRateThrottle(AnonRateThrottle):
    """
    Throttle for login attempts.
    """
    rate = '5/minute'  # 5 login attempts per minute

class RegisterRateThrottle(AnonRateThrottle):
    """
    Throttle for registration attempts.
    """
    rate = '3/hour'  # 3 registration attempts per hour

class PasswordResetRateThrottle(AnonRateThrottle):
    """
    Throttle for password reset requests.
    """
    rate = '3/hour'  # 3 password reset requests per hour 