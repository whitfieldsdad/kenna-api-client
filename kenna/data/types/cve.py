from dataclasses import dataclass

import datetime


@dataclass(frozen=True)
class CVE:
    id: str
    description: str
    create_time: datetime.datetime
