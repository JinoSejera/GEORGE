from slowapi import Limiter
from ..utils.get_client_ip import get_client_ip

# Initialize the rate limiter using the client IP extraction function.
limiter = Limiter(key_func=get_client_ip)
