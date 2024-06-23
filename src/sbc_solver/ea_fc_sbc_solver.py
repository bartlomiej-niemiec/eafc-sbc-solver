from ortools.sat.python import cp_model
from src.csv.csv_utils import CsvHeaders
import src.sbc_solver.exceptions as SolverExceptions
from src.utils.team_overall_calculator import TeamOverallCalculator

from typing import List


class EaFcSbcSolver:
    _MAX_PLAYERS_IN_FORMATION = 11

    def __init__(self, ea_fc_cards_df):
        self._model = cp_model.CpModel()
        self._solver = cp_model.CpSolver()
        self._ea_fc_cards_df = ea_fc_cards_df
        self._no_cards = len(ea_fc_cards_df)
        self._cards_bools_vars = [self._model.NewBoolVar(f'{self._ea_fc_cards_df[CsvHeaders.ID].iloc[i]}') for i in
                                  range(self._no_cards)]
        self._no_players = None
        self._formation = None
        self._solved = True

    def set_formation(self, list_of_position: List[str]):
        if len(list_of_position) > self._MAX_PLAYERS_IN_FORMATION:
            raise SolverExceptions.IncorrectFormation(
                f"Too many players in formation. Max players per formation = {EaFcSbcSolver._MAX_PLAYERS_IN_FORMATION}")
        self._formation = list_of_position
        self._no_players = len(list_of_position)

    def set_how_many_players_from_club(self, club: str, no_players):
        club_arr = self._ea_fc_cards_df[CsvHeaders.Club].unique()
        club_map_to_unique_id = self._get_map_attribute_to_number(club_arr)
        if not club_map_to_unique_id.get(club):
            raise SolverExceptions.IncorrectClubName(f"Club name: {club} is not on the list")

        self._model.add(
            sum(
                (1 if self._ea_fc_cards_df[CsvHeaders.Club].iloc[i] == club else 0) * self._cards_bools_vars[i] for i in
                range(self._no_cards)
            ) >= no_players
        )

    def set_how_many_players_from_nation(self, nation: str, no_players):
        nation_arr = self._ea_fc_cards_df[CsvHeaders.Nationality].unique()
        nation_map_to_unique_id = self._get_map_attribute_to_number(nation_arr)
        if not nation_map_to_unique_id.get(nation):
            raise SolverExceptions.IncorrectNationName(f"Nation name: {nation} is not on the list")

        self._model.add(
            sum(
                (1 if self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i] == nation else 0) * self._cards_bools_vars[i]
                for i in range(self._no_cards)
            ) >= no_players
        )

    def set_how_many_players_from_league(self, league: str, no_players):
        league_arr = self._ea_fc_cards_df[CsvHeaders.League].unique()
        league_map_to_unique_id = self._get_map_attribute_to_number(league_arr)
        if not league_map_to_unique_id.get(league):
            raise SolverExceptions.IncorrectLeagueName(f"Nation name: {league} is not on the list")

        self._model.add(
            sum(
                (1 if self._ea_fc_cards_df[CsvHeaders.League].iloc[i] == league else 0) * self._cards_bools_vars[i] for
                i in range(self._no_cards)
            ) >= no_players
        )

    def set_how_many_players_from_version(self, version: str, no_players):
        version_arr = self._ea_fc_cards_df[CsvHeaders.Version].unique()
        version_map_to_unique_id = self._get_map_attribute_to_number(version_arr)
        if not version_map_to_unique_id.get(version):
            raise SolverExceptions.IncorrectVersion(f"Version: {version} is not on the list")

        self._model.add(
            sum(
                (1 if self._ea_fc_cards_df[CsvHeaders.Version].iloc[i] == version else 0) * self._cards_bools_vars[i] for
                i in range(self._no_cards)
            ) >= no_players
        )

    def set_how_many_rare_cards(self, no_players):
        self._model.add(
            sum(
                (1 if self._is_card_version_rare(self._ea_fc_cards_df[CsvHeaders.Version].iloc[i]) else 0) *
                self._cards_bools_vars[i] for
                i in range(self._no_cards)
            ) >= no_players
        )

    def set_how_many_cards_with_overall(self, no_players, overall):
        self._model.add(
            sum(
                (1 if self._ea_fc_cards_df[CsvHeaders.OverallRating].iloc[i] == overall else 0) *
                self._cards_bools_vars[i] for
                i in range(self._no_cards)
            ) >= no_players
        )

    def set_max_leagues_for_solution(self, max_leagues):
        leagues_arr = self._ea_fc_cards_df[CsvHeaders.League].unique()
        league_map_to_unique_id = self._get_map_attribute_to_number(leagues_arr)

        league_vars = [self._model.NewIntVar(0, len(leagues_arr) - 1, f"League_{i}") for i in range(max_leagues)]

        for i in range(self._no_cards):
            is_league = [self._model.NewBoolVar(f'Is_League_{i}') for i in range(max_leagues)]
            for j in range(max_leagues):
                self._model.add(league_vars[j] == league_map_to_unique_id[self._ea_fc_cards_df[CsvHeaders.League].iloc[i]]).OnlyEnforceIf(is_league[j])
            self._model.AddBoolOr(is_league).OnlyEnforceIf(self._cards_bools_vars[i])

    def set_max_nations_for_solution(self, max_nations):
        nation_arr = self._ea_fc_cards_df[CsvHeaders.Nationality].unique()
        nation_map_to_unique_id = self._get_map_attribute_to_number(nation_arr)

        nation_vars = [self._model.NewIntVar(0, len(nation_arr) - 1, f"Nation_{i}") for i in range(max_nations)]

        for i in range(self._no_cards):
            is_nation = [self._model.NewBoolVar(f'Is_Nation_{i}') for i in range(max_nations)]
            for j in range(max_nations):
                self._model.add(nation_vars[j] == nation_map_to_unique_id[self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]]).OnlyEnforceIf(is_nation[j])
            self._model.AddBoolOr(is_nation).OnlyEnforceIf(self._cards_bools_vars[i])

    def set_min_overall_of_squad(self, overall):
        if not (0 <= overall <= 99):
            raise SolverExceptions.IncorrectOverallValue("Overall should be in range 0 - 99")

        if self._no_players is None:
            raise SolverExceptions.IncorrectFormation("Formation has to be set")

        players_with_min_overall = int(0.64 * self._no_players)

        for i in range(self._no_cards):

            overall_player = [self._model.NewIntVar(0, 99, f"player_{i}_overall") for i in range(self._no_players)]

            for j in range(len(overall_player)):

                self._model.Add(overall_player[j] == self._ea_fc_cards_df[CsvHeaders.OverallRating].iloc[i]).OnlyEnforceIf(self._cards_bools_vars[i])

            self._model.Add(
                sum(overall_player) >= ((int(overall) * players_with_min_overall) + ((self._no_players - players_with_min_overall) * (overall - 2)))
            )

    def solve(self):
        if not self._formation:
            raise SolverExceptions.IncorrectFormation("Formation is not set!")

        # No. players searched
        self._model.Add(sum(self._cards_bools_vars) == self._no_players)

        # Formation constraint: TO DO
        self._add_constraint_to_formation()

        # Objective
        self._model.Minimize(
            sum(self._cards_bools_vars[i] * self._ea_fc_cards_df[CsvHeaders.Price].iloc[i] for i in
                range(self._no_cards))
        )

        # Find solutions
        self._solver.Solve(self._model)

    def print_solution(self):
        if self._solved:
            for i in range(self._no_cards):
                if self._solver.Value(self._cards_bools_vars[i]):
                    self._print_player(self._ea_fc_cards_df.iloc[i])

    def get_players_in_solution(self):
        solution_players = None
        if self._solved:
            solution_players = [self._ea_fc_cards_df.iloc[i] for i in range(self._no_cards) if
                                self._solver.Value(self._cards_bools_vars[i])]

        return solution_players

    def _print_player(self, player_df):
        print('++++++++++++++++++++++++++++++++')
        print(f"Futwiz Link: {player_df[CsvHeaders.FutwizLink]}")
        print(f"Player Name: {player_df[CsvHeaders.Name]}")
        print(f"Player Overall Rating: {player_df[CsvHeaders.OverallRating]}")
        print(f"Card Price: {player_df[CsvHeaders.Price]}")
        print(f"Card Version: {player_df[CsvHeaders.Version]}")
        print(f"League: {player_df[CsvHeaders.League]}")
        print(f"Nationality: {player_df[CsvHeaders.Nationality]}")
        print('++++++++++++++++++++++++++++++++')

    def _get_map_attribute_to_number(self, attribute_list):
        map = {}
        val = 0
        for attr in attribute_list:
            if attr not in map:
                map[attr] = val
                val += 1
        return map

    def _is_card_version_rare(self, card_version):
        rare = True
        standard_versions = ["BRONZE", "SILVER", "GOLD"]
        is_standard_version = False

        for version in standard_versions:
            if version in card_version:
                is_standard_version = True
                break

        if is_standard_version and "RARE" not in card_version:
            rare = False

        return rare

    def _is_formation_valid(self):
        pass

    def _add_constraint_to_formation(self):
        pass