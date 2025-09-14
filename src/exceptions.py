class AuthError(Exception):
    pass


class InvalidTokenError(AuthError):
    pass


class ExpiredTokenError(AuthError):
    pass


class LinkNotFoundException(Exception):
    pass


class LinkDeleteException(Exception):
    pass


class LinkAlreadyExistsException(Exception):
    pass


class UserAlreadyExistsException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class InvalidPasswordException(Exception):
    pass


class ClicksNotFoundException(Exception):
    pass
