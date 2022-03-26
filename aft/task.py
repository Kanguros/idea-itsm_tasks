"""
Module for representation of a single ITSM task.

It may be defined using various structures:
- simple dict
- named tuple
- regular class
- dataclass
- third-party library as:
    - pydantic
"""


from dataclasses import dataclass

from enum import StrEnum

class Status(StrEnum):
    success: str
    failure: str
    unknown: str
    not_applicable: str

@dataclass
class Task:
    name: str
    url: str
    kind: str
    status: Status = Status.unknown
    desc: str = ""

