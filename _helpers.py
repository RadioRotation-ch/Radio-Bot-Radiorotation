from __future__ import annotations

__all__ = ("_MissingRequiredArgument", "_InvalidArgumentError", "validate_url")

from urllib import parse


class _MissingRequiredArgument(BaseException):
    def __init__(self, missing_args: list[str]):
        msg = f"[Fatal] Expected argument(s) '{', '.join(missing_args)}' but could not the argument(s) in the `.env` file."
        super().__init__(msg)


class _InvalidArgumentError(BaseException):
    def __init__(self, invalid_arg: str, expected_value: str, actual_value: str):
        msg = f"[Fatal] Expected argument {invalid_arg} to be '{expected_value}' but got '{actual_value}'!"
        super().__init__(msg)


def validate_url(url: str) -> bool:
    parsed = parse.urlparse(url)
    return all([parsed.scheme, parsed.netloc])
