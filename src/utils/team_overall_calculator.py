from typing import List
from statistics import mean
from src.utils.team_overall_calculator_if import TeamOverallCalculatorIf


class TeamOverallCalculator(TeamOverallCalculatorIf):

    @staticmethod
    def calculate(squad: List[int]):
        avg_player_rating = mean(squad)
        belov_avg_player_ratings, above_avg_player_ratings = TeamOverallCalculator._split_to_players_above_and_belove_avg(
            squad, avg_player_rating)
        above_avg_player_ratings = [rating + (rating - avg_player_rating) for rating in above_avg_player_ratings]
        squad_overall = round((sum(belov_avg_player_ratings) + sum(above_avg_player_ratings)) / (
                    len(belov_avg_player_ratings) + len(above_avg_player_ratings)), 2)
        if (squad_overall - int(squad_overall)) >= 0.95:
            squad_overall += 1
        return squad_overall

    @staticmethod
    def _split_to_players_above_and_belove_avg(squad: List[int], avg_rating):
        belov_avg_player_ratings = []
        above_avg_player_ratings = []

        for player_overall_rating in squad:
            if player_overall_rating > avg_rating:
                above_avg_player_ratings.append(player_overall_rating)
            else:
                above_avg_player_ratings.append(player_overall_rating)

        return belov_avg_player_ratings, above_avg_player_ratings
