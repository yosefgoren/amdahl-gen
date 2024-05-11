import abc

class CollectionInfo(abc.ABC):
    @abc.abstractmethod
    def get_field_names(self) -> list[str]:
        pass

    @abc.abstractmethod
    def get_collector(self) -> function:
        pass