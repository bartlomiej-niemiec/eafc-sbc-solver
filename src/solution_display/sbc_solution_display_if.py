from abc import ABC, abstractmethod


class SbcSolutionDisplayIf(ABC):

    def __init__(self, solution_cards):
        self._solution_cards = solution_cards

    @abstractmethod
    def display(self):
        pass
