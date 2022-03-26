"""
Module for class which represents ITSM web application.

Assumption:
- No API available.
- Access to website with the usage of Selenium.
-
"""
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Dict, Optional, Tuple, List


class Status(StrEnum):
    open: str = 'open'
    closed: str = 'closed'
    wip: str = 'in_progress'
    unknown: str = 'unknown'


@dataclass
class Task:
    name: str
    url: str
    kind: str
    status: Status = Status.unknown
    desc: str = ""


class ITSM:

    TASK_CALL: Dict[str, Callable] = {
        'add': '',
        'analysis': lambda s: "Perform analysis of" in s,
        'lookup': lambda s: "Remove entry XYZ from" in s
    }

    def __init__(self,
                 username,
                 password,
                 url,
                 headless: bool,
                 proxy: Optional[Tuple[str, str]],
                 **kwargs):
        """
        Represents ITSM application. Interacted through Web GUI

        :param username:
        :param password:
        :param url: Url for ITSM. There is no reason to not hardcode that url in the class.
        :param headless: Run WebDriver in headless mode.
        :param proxy: Proxy IP's if reqired.
        :param kwargs: Additional params for WebDriver
        """
        self.username = username
        self.password = password
        self.url = url
        self.proxy = proxy
        self._options = kwargs or {}
        self._driver = None

    @property
    def driver(self):
        if self._driver is None:
            self._driver = self._load_driver()

        return self._driver

    def _load_driver(self):
        """
        Create a WebDriver along with provided additional options:
            - self.proxy and
            - self._options
        """
        capabilities = []
        if self.proxy:
            capabilities.append(self.proxy)
        if self._options:
            capabilities.append(self._options)
        driver = WebDriver(capabilities)
        # Specific actions executed alread on initiated driver
        driver.implicit_wait()
        return driver

    def get_tasks(self) -> List[Task]:
        """
        Get all Tasks.
        """
        self.driver.get(self.url + "unique_url_for_page_with_task_table")
        page_table = self.driver.find_element()

        tasks = []
        for row in page_table:
            tasks.append(
                self._extract_task(row))
        return tasks

    def get_active_tasks(self):
        """
        Get all Tasks with Status `open` and `wip`.
        """
        return [task
                for task in self.get_tasks()
                if task.status in (Status.open, Status.wip)]

    def _extract_task(self, row) -> Task:
        """From `tr` element of a table, extract task's details."""
        entry_title = row.find_element()
        entry_url = row.find_element()
        entry_state = row.find_element()

        task = None
        for task_type, type_call in self.TASK_CALL.items():
            if not type_call(entry_title):
                continue
            if task is not None:
                raise ValueError(f"Task was already evaluated as: {task}")
            task = Task(name=entry_title,
                        url=entry_url,
                        kind=task_type,
                        status=entry_state)
        return task
