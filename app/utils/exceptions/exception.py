class Base(Exception):
    ...


class ServiceException(Base):

    def __init__(self, message, status_code=200) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
