class BaseAppError(Exception):
    status_code = 500
    message = "Something went wrong"

    def __init__(self, message=None, status_code=None):
        super().__init__(message)
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code

    def to_dict(self):
        return {"error": self.message}


class UnauthorizedError(BaseAppError):
    status_code = 401
    message = "Unauthorized"

class ForbiddenError(BaseAppError):
    status_code = 403
    message = "Forbidden"