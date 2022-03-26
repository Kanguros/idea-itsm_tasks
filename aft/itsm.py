"""
Module for class which represents ITSM web application.

Assumption:
- No API available.
- Access to website with the usage of Selenium.
-
"""
from typing import Callable, Dict, Optional, Tuple, List

from aft.task import Task


class ITSM:
    TASK_MAP: Dict[str, Callable] = {
        'add': '',
        'analysis': lambda s: "Perform analysis of" in s,
        'lookup': lambda s: "Remove entry XYZ from" in s
    }

    def __init__(self,
                 url,
                 proxy: Optional[Tuple[str, str]],
                 **kwargs):
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
        """Create a WebDriver along with provided additional options:
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

    def get_tasks(self, **kwargs) -> List[Task]:
        """
        Get all or filtered (kwargs) Tasks.
        :param kwargs: Find only the desire ones. Place for somekind of filtering.
        :return: List of Tasks
        """
        return [task for task in self._find_tasks()]

    def _find_tasks(self) -> List[Task]:
        self.driver.get(self.url + "unique_url_for_page_with_task_table")
        page_table = self.driver.find_element()

        tasks = []
        for row in page_table:
            tasks.append(
                self._evaluate_entry(row))
        return tasks

    def _evaluate_entry(self, row) -> Task:
        entry_title = row.find_element()
        entry_url = row.find_element()
        entry_state = row.find_element()

        task = None
        for task_type, check_call in self.TASK_MAP.items():
            if not check_call(entry_title):
                continue
            if task is not None:
                raise ValueError(f"Task was already evaluated as: {task}")
            task = Task(name=entry_title,
                        url=entry_url,
                        kind=task_type,
                        status=entry_state)
        return task
