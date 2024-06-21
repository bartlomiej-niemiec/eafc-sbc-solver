from typing import List
from abc import ABC, abstractmethod


class TeamOverallCalculatorIf(ABC):
    @staticmethod
    @abstractmethod
    def calculate(squad: List[int]):
        avg_player_rating = mean(squad)
