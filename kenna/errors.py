class ReadError(Exception):
    pass


class WriteError(Exception):
    pass


class NotFoundError(Exception):
    pass


class _CredentialError(ValueError):
    pass


class MissingCredentialsError(_CredentialError):
    pass


class InvalidCredentialsError(_CredentialError):
    pass


class InvalidRegionError(Exception):
    pass


class DataExportRequiredError(Exception):
    pass
