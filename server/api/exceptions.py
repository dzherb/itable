class APIError(Exception):
    pass


class UnauthorizedError(APIError):
    pass


class NotFoundError(APIError):
    pass
