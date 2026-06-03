import re

def validate_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(pattern, email) is not None



def validate_password(password: str):
    valid, message = __validate_password_policy(password)
    if not valid:
        raise ValueError(message)
    return password



def __validate_password_policy(password: str) -> tuple[bool, str]:
    """
    Enterprise password policy:
    - Min 8 chars
    - At least 1 uppercase
    - At least 1 lowercase
    - At least 1 digit
    - At least 1 special character
    """

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must include at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must include at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must include at least one number"

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must include at least one special character"

    return True, ""