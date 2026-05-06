from typing import Annotated

from fastapi import Path

ShortCodeParam = Annotated[
    str,
    Path(
        min_length=1,
        max_length=5,
        pattern=r"^[0-9A-Za-z]+$",
        description="Base62 short code (1 to 5 chars)",
    ),
]
