import logging
import inspect
from functools import wraps
from app.core.responses import CustomResponse

logger = logging.getLogger(__name__)


def try_catch_wrapper(default_message="Something went wrong"):
    def decorator(func):

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except ValueError as ve:
                    return CustomResponse.bad_request(str(ve))
                except Exception as e:
                    logger.exception(f"{func.__name__} failed: {str(e)}")
                    return CustomResponse.server_error(default_message)

            return async_wrapper

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except ValueError as ve:
                    return CustomResponse.bad_request(str(ve))
                except Exception as e:
                    logger.exception(f"{func.__name__} failed: {str(e)}")
                    return CustomResponse.server_error(default_message)

            return sync_wrapper

    return decorator