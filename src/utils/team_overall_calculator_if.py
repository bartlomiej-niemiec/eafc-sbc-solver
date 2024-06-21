from typing import List
from abc import ABC, abstractmethod


class TeamOverallCalculatorIf(ABC):

    @abstractmethod
    def calculate(squad: List[int]):
        pass
