import abc
from typing import Callable

class Collector(abc.ABC):
    @abc.abstractmethod
    def get_field_names(self) -> list[str]:
        pass

    @abc.abstractmethod
    def get_collector(self) -> Callable:
        pass