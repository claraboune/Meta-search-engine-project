from abc import ABC


class AbstractEngine(ABC):
    """
    A class the represents an search engine.

    Methods
    -------
    search(user_request, nb_result)
    """

    def __init__(self) -> None:
        super().__init__()

    async def search(self, user_request, nb_result):
        pass
