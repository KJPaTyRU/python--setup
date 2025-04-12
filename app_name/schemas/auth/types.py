from typing import Annotated

from pydantic import StringConstraints

UserNameStr = Annotated[
    str,
    StringConstraints(
        to_lower=True,
        min_length=3,
        max_length=64,
        pattern=r"^[0-9a-zA-Z_\-\.]+$",
    ),
]

PasswordStr = Annotated[str, StringConstraints(min_length=3)]
