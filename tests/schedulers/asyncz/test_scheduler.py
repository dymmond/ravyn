from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from unittest.mock import MagicMock

import pytest
from asyncz.executors.base import BaseExecutor
from asyncz.schedulers import AsyncIOScheduler
from asyncz.schedulers.base import BaseScheduler, default_loggers_class
from asyncz.schedulers.datastructures import TaskDefaultStruct
from asyncz.stores.base import BaseStore
from asyncz.tasks.types import TaskType
from asyncz.triggers import IntervalTrigger
from asyncz.triggers.base import BaseTrigger
from loguru import logger

from ravyn import Ravyn
from ravyn.contrib.schedulers.asyncz.config import AsynczConfig
from ravyn.contrib.schedulers.asyncz.decorator import scheduler
from ravyn.exceptions import ImproperlyConfigured


class DummyScheduler(BaseScheduler):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wakeup = MagicMock()

    def shutdown(self, wait=True):
        super().shutdown(wait)

    def wakeup(self): ...


class DummyTrigger(BaseTrigger):  # pragma: no cover
    def __init__(self, **args):
        super().__init__(**args)
        self.args = args

    def get_next_trigger_time(
        self, previous_time: datetime, now: Optional[datetime] = None
    ) -> Union[datetime, None]: ...


class DummyExecutor(BaseExecutor):  # pragma: no cover
    def __init__(self, **args):
        super().__init__(**args)
        self.args = args
        self.start = MagicMock()
        self.shutdown = MagicMock()
        self.send_task = MagicMock()

    def do_send_task(self, task: "TaskType", run_times: List[datetime]) -> Any:
        return super().do_send_task(task, run_times)


class DummyStore(BaseStore):  # pragma: no cover
    def __init__(self, **args):
        super().__init__(**args)
        self.args = args
        self.start = MagicMock()
        self.shutdown = MagicMock()

    def get_due_tasks(self, now: datetime) -> List["TaskType"]: ...

    def lookup_task(self, task_id: Union[str, int]) -> "TaskType": ...

    def delete_task(self, task_id: Union[str, int]): ...

    def remove_all_tasks(self): ...

    def get_next_run_time(self) -> datetime: ...

    def get_all_tasks(self) -> List["TaskType"]: ...

    def add_task(self, task: "TaskType"): ...

    def update_task(self, task: "TaskType"): ...


def scheduler_tasks() -> Dict[str, str]:
    return {
        "task_one": "tests.schedulers.asyncz.test_scheduler",
        "task_two": "tests.schedulers.asyncz.test_scheduler",
    }


@scheduler(name="task1", trigger=IntervalTrigger(seconds=1), max_instances=3, is_enabled=True)
def task_one():  # pragma: no cover
    value = 3
    logger.info(value)
    return 3


@scheduler(name="task2", trigger=IntervalTrigger(seconds=3), max_instances=3, is_enabled=True)
def task_two():  # pragma: no cover
    value = 8
    logger.info(value)
    return 8


scheduler_config = AsynczConfig(tasks=scheduler_tasks())


def test_access_original_function() -> None:
    assert task_one.original.__name__ == "task_one"
    assert task_two.original.__name__ == "task_two"


def test_ravyn_starts_scheduler():
    app = Ravyn(scheduler_config=scheduler_config)
    assert app.scheduler_config.tasks == scheduler_tasks()
    assert app.scheduler_config.scheduler_class == AsyncIOScheduler


@pytest.fixture
def scheduler_class(monkeypatch):
    scheduler_class = AsyncIOScheduler
    scheduler_class._setup = MagicMock()
    # by patching out _setup task_defaults are not initialized anymore
    scheduler_class.task_defaults = TaskDefaultStruct()
    scheduler_class.timezone = timezone.utc
    scheduler_class.loggers = default_loggers_class()
    scheduler_class.logger_name = "asyncz.schedulers"
    return scheduler_class


@pytest.mark.parametrize(
    "global_config",
    [
        {
            "asyncz.timezone": "UTC",
            "asyncz.task_defaults.mistrigger_grace_time": "5",
            "asyncz.task_defaults.coalesce": "false",
            "asyncz.task_defaults.max_instances": "9",
            "asyncz.executors.default.class": "%s:DummyExecutor" % __name__,
            "asyncz.executors.default.arg1": "3",
            "asyncz.executors.default.arg2": "a",
            "asyncz.executors.alter.class": "%s:DummyExecutor" % __name__,
            "asyncz.executors.alter.arg": "true",
            "asyncz.stores.default.class": "%s:DummyStore" % __name__,
            "asyncz.stores.default.arg1": "3",
            "asyncz.stores.default.arg2": "a",
            "asyncz.stores.bar.class": "%s:DummyStore" % __name__,
            "asyncz.stores.bar.arg": "false",
        },
        {
            "asyncz.timezone": "UTC",
            "asyncz.task_defaults": {
                "mistrigger_grace_time": "5",
                "coalesce": "false",
                "max_instances": "9",
            },
            "asyncz.executors": {
                "default": {"class": "%s:DummyExecutor" % __name__, "arg1": "3", "arg2": "a"},
                "alter": {"class": "%s:DummyExecutor" % __name__, "arg": "true"},
            },
            "asyncz.stores": {
                "default": {"class": "%s:DummyStore" % __name__, "arg1": "3", "arg2": "a"},
                "bar": {"class": "%s:DummyStore" % __name__, "arg": "false"},
            },
        },
    ],
    ids=["ini-style", "yaml-style"],
)
def test_ravyn_scheduler_configurations(scheduler_class, global_config):
    scheduler_config = AsynczConfig(
        tasks=scheduler_tasks(), scheduler_class=scheduler_class, configurations=global_config
    )
    app = Ravyn(
        scheduler_config=scheduler_config,
        enable_scheduler=True,
    )

    app.scheduler_config.scheduler_class._setup.assert_called_once_with(
        {
            "timezone": "UTC",
            "task_defaults": {
                "mistrigger_grace_time": "5",
                "coalesce": "false",
                "max_instances": "9",
            },
            "executors": {
                "default": {"class": "%s:DummyExecutor" % __name__, "arg1": "3", "arg2": "a"},
                "alter": {"class": "%s:DummyExecutor" % __name__, "arg": "true"},
            },
            "stores": {
                "default": {"class": "%s:DummyStore" % __name__, "arg1": "3", "arg2": "a"},
                "bar": {"class": "%s:DummyStore" % __name__, "arg": "false"},
            },
        }
    )


def test_raise_exception_on_tasks_key(scheduler_class):
    """
    Raises Ravyn ImproperlyConfigured if task passed has not a format Dict[str, str]
    """
    tasks = {
        1: "tests.schedulers.asyncz.test_scheduler",
        2: "tests.schedulers.asyncz.test_scheduler",
    }

    with pytest.raises(ImproperlyConfigured):
        scheduler_config = AsynczConfig(scheduler_class=scheduler_class, tasks=tasks)
        Ravyn(
            scheduler_config=scheduler_config,
            enable_scheduler=True,
        )


def test_raise_exception_on_tasks_value(scheduler_class):
    """
    Raises Ravyn ImproperlyConfigured if task passed has not a format Dict[str, str]
    """
    tasks = {
        "task_one": 1,
        "task_two": 2,
    }

    with pytest.raises(ImproperlyConfigured):
        scheduler_config = AsynczConfig(scheduler_class=scheduler_class, tasks=tasks)
        Ravyn(
            scheduler_config=scheduler_config,
            enable_scheduler=True,
        )
