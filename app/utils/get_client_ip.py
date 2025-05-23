import logging

from fastapi import Request

logger = logging.getLogger(__name__)

def get_client_ip(request: Request):
    """
    Extract the client IP address from the request.

    Checks the X-Client-IP header first, then X-Forwarded-For, and finally falls back to client.host.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        str: The client's IP address.
    """
    x_client_ip = request.headers.get("X-Client-IP")
    if x_client_ip:
        logger.info(f"X-Client-IP header found: {x_client_ip}")
        return x_client_ip.strip()
    
    forward_for = request.headers.get("X-Forwarded-For")
    if forward_for:
        logger.info(f"X-Forwarded-For header found: {forward_for}")
        return forward_for.split(',')[0]  # Extract the first IP in the list
    return request.client.host  # Fallback to the client's IP address