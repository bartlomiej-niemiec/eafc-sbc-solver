from ortools.sat.python import cp_model
from src.csv.csv_utils import CsvHeaders
import src.sbc_solver.exceptions as SolverExceptions

from typing import List


class EaFcSbcSolver:
    _MAX_PLAYERS_IN_FORMATION = 11

    def __init__(self, ea_fc_cards_df):
        self._model = cp_model.CpModel()
        self._solver = cp_model.CpSolver()
        self._solver.parameters.num_workers = 4
        self._ea_fc_cards_df = ea_fc_cards_df
        self._no_cards = len(ea_fc_cards_df)
        self._cards_bools_vars = [self._model.NewBoolVar(f'{self._ea_fc_cards_df[CsvHeaders.ID].iloc[i]}') for i in
                                  range(self._no_cards)]
        self._no_players = None
        self._formation = None
        self._leagues_bools = None
        self._nationality_bools = None
        self._solved = True
        self._player_chemistry = [self._model.NewIntVar(0, 3, f"player_{i}_chemistry") for i in range(self._no_cards)]

    def set_formation(self, formation: List[str]):
        if len(formation) > self._MAX_PLAYERS_IN_FORMATION:
            raise SolverExceptions.IncorrectFormation(
                f"Too many players in formation. Max players per formation = {EaFcSbcSolver._MAX_PLAYERS_IN_FORMATION}")
        self._formation = formation
        self._no_players = len(formation)

    def set_min_cards_with_club(self, club: str, no_players):
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

    def set_min_cards_with_nation(self, nation: str, no_players):
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

    def set_min_cards_with_league(self, league: str, no_players):
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

    def set_min_cards_with_version(self, version: str, no_players):
        version_arr = self._ea_fc_cards_df[CsvHeaders.Version].unique()
        version_map_to_unique_id = self._get_map_attribute_to_number(version_arr)
        if not version_map_to_unique_id.get(version):
            raise SolverExceptions.IncorrectVersion(f"Version: {version} is not on the list")

        self._model.add(
            sum(
                (1 if self._ea_fc_cards_df[CsvHeaders.Version].iloc[i].strip() == version else 0) *
                self._cards_bools_vars[i] for
                i in range(self._no_cards)
            ) >= no_players
        )

    def set_min_rare_cards(self, no_players):
        self._model.add(
            sum(
                (1 if self._is_card_version_rare(self._ea_fc_cards_df[CsvHeaders.Version].iloc[i].strip()) else 0) *
                self._cards_bools_vars[i] for
                i in range(self._no_cards)
            ) >= no_players
        )

    def set_min_cards_with_overall(self, no_players, overall):
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
                self._model.add(league_vars[j] == league_map_to_unique_id[
                    self._ea_fc_cards_df[CsvHeaders.League].iloc[i]]).OnlyEnforceIf(is_league[j])
            self._model.AddBoolOr(is_league).OnlyEnforceIf(self._cards_bools_vars[i])

    def set_max_nations_for_solution(self, max_nations):
        nation_arr = self._ea_fc_cards_df[CsvHeaders.Nationality].unique()
        nation_map_to_unique_id = self._get_map_attribute_to_number(nation_arr)

        nation_vars = [self._model.NewIntVar(0, len(nation_arr) - 1, f"Nation_{i}") for i in range(max_nations)]

        for i in range(self._no_cards):
            is_nation = [self._model.NewBoolVar(f'Is_Nation_{i}') for i in range(max_nations)]
            for j in range(max_nations):
                self._model.add(nation_vars[j] == nation_map_to_unique_id[
                    self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]]).OnlyEnforceIf(is_nation[j])
            self._model.AddBoolOr(is_nation).OnlyEnforceIf(self._cards_bools_vars[i])

    def set_min_unique_leagues(self, no_leagues):
        if not self._leagues_bools:
            self._init_unique_leagues()

        self._model.add(sum(self._leagues_bools) >= no_leagues)

    def set_max_unique_leagues(self, no_leagues):
        if not self._leagues_bools:
            self._init_unique_leagues()

        self._model.add(sum(self._leagues_bools) < no_leagues)

    def set_exact_unique_leagues(self, no_leagues):
        if not self._leagues_bools:
            self._init_unique_leagues()

        self._model.add(sum(self._leagues_bools) == no_leagues)

    def set_min_unique_nations(self, no_nations):
        if not self._nationality_bools:
            self._init_unique_nations()

        self._model.add(sum(self._nationality_bools) >= no_nations)

    def set_max_unique_nations(self, no_nations):
        if not self._nationality_bools:
            self._init_unique_nations()

        self._model.add(sum(self._nationality_bools) < no_nations)

    def set_exact_unique_nations(self, no_nations):
        if not self._nationality_bools:
            self._init_unique_nations()

        self._model.add(sum(self._nationality_bools) == no_nations)

    def set_min_team_chemistry(self, chemistry):

        nation_arr = self._ea_fc_cards_df[CsvHeaders.Nationality].unique()
        nation_map_to_unique_id = self._get_map_attribute_to_number(nation_arr)
        nation_vars = [self._model.NewIntVar(0, self._no_players, f"Nation_{i}") for i in range(len(nation_arr))]

        # Calculate no. player in each nationality
        for nation_id in range(len(nation_arr)):
            self._model.Add(nation_vars[nation_id] == cp_model.LinearExpr.Sum([(1 if nation_id == nation_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]] else 0) * self._cards_bools_vars[i] for i in
                                                           range(self._no_cards)]))

        leagues_arr = self._ea_fc_cards_df[CsvHeaders.League].unique()
        league_map_to_unique_id = self._get_map_attribute_to_number(leagues_arr)
        league_vars = [self._model.NewIntVar(0, self._no_players, f"League_{i}") for i in range(len(leagues_arr))]

        # Calculate no. player in each league
        for league_id in range(len(leagues_arr)):
            self._model.Add(league_vars[league_id] == cp_model.LinearExpr.Sum([(1 if league_id == league_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.League].iloc[i]] else 0) * self._cards_bools_vars[i] for i in
                                                           range(self._no_cards)]))

        clubs_arr = self._ea_fc_cards_df[CsvHeaders.Club].unique()
        clubs_map_to_unique_id = self._get_map_attribute_to_number(clubs_arr)
        clubs_vars = [self._model.NewIntVar(0, self._no_players, f"Club_{i}") for i in range(len(clubs_arr))]

        # Calculate no. player in each Club
        for club_id in range(len(clubs_arr)):
            self._model.Add(clubs_vars[club_id] == cp_model.LinearExpr.Sum([(1 if club_id == clubs_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Club].iloc[i]] else 0) * self._cards_bools_vars[i] for i in
                                                        range(self._no_cards)]))

        plus_one_same_two_club = [self._model.NewBoolVar(f'plus_one_same_two_club_{i}') for i in range(self._no_cards)]
        plus_one_same_two_nation = [self._model.NewBoolVar(f'plus_one_same_two_nation_{i}') for i in range(self._no_cards)]
        plus_one_same_three_league = [self._model.NewBoolVar(f'plus_one_same_three_league_{i}') for i in range(self._no_cards)]
        plus_two_same_four_club = [self._model.NewBoolVar(f'plus_two_same_four_club_{i}') for i in range(self._no_cards)]
        plus_two_same_five_nation = [self._model.NewBoolVar(f'plus_two_same_five_nation_{i}') for i in range(self._no_cards)]
        plus_two_same_five_league = [self._model.NewBoolVar(f'plus_two_same_five_league_{i}') for i in range(self._no_cards)]
        plus_three_same_seven_club = [self._model.NewBoolVar(f'plus_three_same_seven_club_{i}') for i in range(self._no_cards)]
        plus_three_same_eight_more_country = [self._model.NewBoolVar(f'plus_three_same_eight_more_country_{i}') for i in range(self._no_cards)]
        plus_three_same_eight_more_league = [self._model.NewBoolVar(f'plus_three_same_eight_more_league_{i}') for i in range(self._no_cards)]

        for i in range(self._no_cards):
            # ----------------------------1---------------------------------
            self._model.Add(clubs_vars[clubs_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Club].iloc[i]]] >= 2).OnlyEnforceIf([self._cards_bools_vars[i], plus_one_same_two_club[i]])

            self._model.Add(clubs_vars[clubs_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Club].iloc[i]]] < 2).OnlyEnforceIf(plus_one_same_two_club[i].Not())

            # ---------------------------2---------------------------------
            self._model.Add(nation_vars[nation_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]]] >= 2).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_two_nation[i]])


            self._model.Add(nation_vars[nation_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]]] < 2).OnlyEnforceIf(
                plus_one_same_two_nation[i].Not())

            # ---------------------------3---------------------------------
            self._model.Add(league_vars[league_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.League].iloc[i]]] >= 3).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_three_league[i]])


            self._model.Add(league_vars[league_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.League].iloc[i]]] < 3).OnlyEnforceIf(
                plus_one_same_three_league[i].Not())

            # ---------------------------4---------------------------------

            self._model.Add(clubs_vars[clubs_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Club].iloc[i]]] >= 4).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_two_same_four_club[i]])


            self._model.Add(clubs_vars[clubs_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Club].iloc[i]]] < 4).OnlyEnforceIf(
                plus_two_same_four_club[i].Not())

            # ---------------------------5---------------------------------
            self._model.Add(nation_vars[nation_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]]] >= 5).OnlyEnforceIf([self._cards_bools_vars[i], plus_two_same_five_nation[i]])


            self._model.Add(nation_vars[nation_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]]] < 5).OnlyEnforceIf(plus_two_same_five_nation[i].Not())

            # ---------------------------6---------------------------------
            self._model.Add(league_vars[league_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.League].iloc[i]]] >= 5).OnlyEnforceIf([self._cards_bools_vars[i], plus_two_same_five_league[i]])


            self._model.Add(league_vars[league_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.League].iloc[i]]] < 5).OnlyEnforceIf(
                plus_two_same_five_league[i].Not())

            # ---------------------------7---------------------------------
            self._model.Add(clubs_vars[clubs_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Club].iloc[i]]] >= 7).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_three_same_seven_club[i]])

            self._model.Add(clubs_vars[clubs_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Club].iloc[i]]] < 7).OnlyEnforceIf(
                plus_three_same_seven_club[i].Not())

            # ---------------------------8---------------------------------
            self._model.Add(nation_vars[nation_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]]] >= 8).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_three_same_eight_more_country[i]])

            self._model.Add(nation_vars[nation_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]]] < 8).OnlyEnforceIf(
                plus_three_same_eight_more_country[i].Not())

            # ---------------------------9---------------------------------
            self._model.Add(league_vars[league_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.League].iloc[i]]] >= 8).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_three_same_eight_more_league[i]])

            self._model.Add(league_vars[league_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.League].iloc[i]]] < 8).OnlyEnforceIf(
                plus_three_same_eight_more_league[i].Not())

            add_one_boolean = self._model.NewBoolVar(f"add_one_{i}")
            add_two_boolean = self._model.NewBoolVar(f"add_two_{i}")
            add_three_boolean = self._model.NewBoolVar(f"add_three_{i}")

            self._model.AddBoolOr([plus_one_same_three_league[i], plus_one_same_two_club[i], plus_one_same_two_nation[i]]).OnlyEnforceIf(add_one_boolean)
            self._model.AddBoolAnd([plus_one_same_three_league[i].Not(), plus_one_same_two_club[i].Not(), plus_one_same_two_nation[i].Not()]).OnlyEnforceIf(add_one_boolean.Not())

            self._model.AddBoolOr([plus_two_same_four_club[i], plus_two_same_five_league[i], plus_two_same_five_nation[i]]).OnlyEnforceIf(add_two_boolean)
            self._model.AddBoolAnd([plus_two_same_four_club[i].Not(), plus_two_same_five_league[i].Not(), plus_two_same_five_nation[i].Not()]).OnlyEnforceIf(add_two_boolean.Not())

            self._model.AddBoolOr([plus_three_same_eight_more_country[i], plus_three_same_seven_club[i], plus_three_same_eight_more_league[i]]).OnlyEnforceIf(add_three_boolean)
            self._model.AddBoolAnd([plus_three_same_eight_more_country[i].Not(), plus_three_same_seven_club[i].Not(), plus_three_same_eight_more_league[i].Not()]).OnlyEnforceIf(add_three_boolean.Not())

            # 0 CHEMISTRY
            self._model.add(self._player_chemistry[i] == 0).OnlyEnforceIf(self._cards_bools_vars[i].Not())
            self._model.add(self._player_chemistry[i] == 0).OnlyEnforceIf([self._cards_bools_vars[i], add_one_boolean.Not(), add_two_boolean.Not(), add_three_boolean.Not()])

            # 1 CHEMISTRY
            self._model.add(self._player_chemistry[i] == 1).OnlyEnforceIf(
                [self._cards_bools_vars[i], add_one_boolean, add_two_boolean.Not(), add_three_boolean.Not()]
            )

            # 2 CHEMISTRY
            self._model.add(self._player_chemistry[i] == 2).OnlyEnforceIf(
                [self._cards_bools_vars[i], add_one_boolean.Not(), add_two_boolean, add_three_boolean.Not()])

            self._model.add(self._player_chemistry[i] == 2).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_three_league[i], plus_one_same_two_club[i], add_two_boolean.Not(), add_three_boolean.Not()])

            self._model.add(self._player_chemistry[i] == 2).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_two_club[i], plus_one_same_two_nation[i],
                 add_two_boolean.Not(), add_three_boolean.Not()])

            self._model.add(self._player_chemistry[i] == 2).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_two_club[i], plus_one_same_three_league[i],
                 add_two_boolean.Not(), add_three_boolean.Not()])

            # 3 CHEMISTRY
            self._model.add(self._player_chemistry[i] == 3).OnlyEnforceIf(
                [self._cards_bools_vars[i], add_one_boolean.Not(), add_two_boolean.Not(), add_three_boolean])

            self._model.add(self._player_chemistry[i] == 3).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_three_league[i], plus_two_same_four_club[i], add_three_boolean.Not()])

            self._model.add(self._player_chemistry[i] == 3).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_three_league[i], plus_two_same_five_nation[i], add_three_boolean.Not()])

            self._model.add(self._player_chemistry[i] == 3).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_two_club[i], plus_two_same_five_nation[i],
                 add_three_boolean.Not()])

            self._model.add(self._player_chemistry[i] == 3).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_two_club[i], plus_two_same_five_league[i],
                 add_three_boolean.Not()])

            self._model.add(self._player_chemistry[i] == 3).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_two_nation[i], plus_two_same_five_league[i],
                 add_three_boolean.Not()])

            self._model.add(self._player_chemistry[i] == 3).OnlyEnforceIf(
                [self._cards_bools_vars[i], plus_one_same_two_nation[i], plus_two_same_four_club[i],
                 add_three_boolean.Not()])

        self._model.add(sum(self._player_chemistry) >= chemistry)

    def set_min_overall_of_squad(self, overall):
        if not (0 <= overall <= 99):
            raise SolverExceptions.IncorrectOverallValue("Overall should be in range 0 - 99")

        if self._no_players is None:
            raise SolverExceptions.IncorrectFormation("Formation has to be set")

        players_with_min_overall = int(0.64 * self._no_players)

        overall_player = [self._model.NewIntVar(0, 99, f"player_{i}_overall") for i in range(self._no_cards)]

        for i in range(self._no_cards):
            self._model.Add(overall_player[i] == self._ea_fc_cards_df[CsvHeaders.OverallRating].iloc[i]).OnlyEnforceIf(
                self._cards_bools_vars[i])
            self._model.Add(overall_player[i] == 0).OnlyEnforceIf(self._cards_bools_vars[i].Not())

        self._model.Add(
            sum(overall_player) >= ((int(overall) * players_with_min_overall) + (
                    (self._no_players - players_with_min_overall) * (overall - 1)))
        )

    def solve(self):
        if not self._formation:
            raise SolverExceptions.IncorrectFormation("Formation is not set!")

        # No. players searched
        self._model.Add(sum(self._cards_bools_vars) == self._no_players)

        # Formation constraint
        self._add_constraint_to_formation()

        # Objective
        self._model.Minimize(
            sum(self._cards_bools_vars[i] * self._ea_fc_cards_df[CsvHeaders.Price].iloc[i] for i in
                range(self._no_cards))
        )

        # Find solutions
        self._solver.Solve(self._model)

    def print_solution(self):
        sum_price = 0
        if self._solved:
            for i in range(self._no_cards):
                if self._solver.Value(self._cards_bools_vars[i]):
                    sum_price += self._ea_fc_cards_df[CsvHeaders.Price].iloc[i]
                    self._print_player(self._ea_fc_cards_df.iloc[i])
                    print(f"Chemistry: {self._solver.Value(self._player_chemistry[i])}")
                    print('++++++++++++++++++++++++++++++++')
            print(f"Final Price: {sum_price}")

    def get_players_in_solution(self):
        solution_players = None
        if self._solved:
            solution_players = [self._ea_fc_cards_df.iloc[i] for i in range(self._no_cards) if
                                self._solver.Value(self._cards_bools_vars[i])]

        return solution_players

    def reset(self):
        ea_fc_cards_temp = self._ea_fc_cards_df
        del self._model
        del self._solver
        del self._ea_fc_cards_df
        del self._no_cards
        del self._cards_bools_vars
        self.__init__(ea_fc_cards_temp)

    def _print_player(self, player_df):
        print(f"Futwiz Link: {player_df[CsvHeaders.FutwizLink]}")
        print(f"Player Name: {player_df[CsvHeaders.Name]}")
        print(f"Player Overall Rating: {player_df[CsvHeaders.OverallRating]}")
        print(f"Card Price: {player_df[CsvHeaders.Price]}")
        print(f"Card Version: {player_df[CsvHeaders.Version]}")
        print(f"League: {player_df[CsvHeaders.League]}")
        print(f"Nationality: {player_df[CsvHeaders.Nationality]}")

    def _get_map_attribute_to_number(self, attribute_list):
        map = {}
        val = 0
        for attr in attribute_list:
            if attr.strip() not in map:
                map[attr.strip()] = val
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

    def _add_constraint_to_formation(self):
        position_to_no_players_map = {}
        for position in self._formation:
            if not position_to_no_players_map.get(position):
                position_to_no_players_map[position] = 1
            else:
                position_to_no_players_map[position] += 1

        for key, value in position_to_no_players_map.items():
            self._model.add(
                sum(
                    (1 if self._ea_fc_cards_df[CsvHeaders.Position].iloc[i] == key else 0) * self._cards_bools_vars[i]
                    for
                    i in
                    range(self._no_cards)
                ) == value
            )

    def _init_unique_leagues(self):
        leagues_arr = self._ea_fc_cards_df[CsvHeaders.League].unique()
        league_map_to_unique_id = self._get_map_attribute_to_number(leagues_arr)
        self._leagues_bools = [self._model.NewBoolVar(f"Is_League_{i}") for i in range(len(leagues_arr))]

        for i in range(len(self._leagues_bools)):
            self._model.add(sum([(1 if league_map_to_unique_id[
                                           self._ea_fc_cards_df[CsvHeaders.League].iloc[j]] == i else 0) *
                                 self._cards_bools_vars[j] for j in range(self._no_cards)]) > 0).OnlyEnforceIf(
                self._leagues_bools[i])
            self._model.add(sum([(1 if league_map_to_unique_id[
                                           self._ea_fc_cards_df[CsvHeaders.League].iloc[j]] == i else 0) *
                                 self._cards_bools_vars[j] for j in range(self._no_cards)]) == 0).OnlyEnforceIf(
                self._leagues_bools[i].Not())

    def _init_unique_nations(self):
        nation_arr = self._ea_fc_cards_df[CsvHeaders.Nationality].unique()
        nation_map_to_unique_id = self._get_map_attribute_to_number(nation_arr)
        self._nationality_bools = [self._model.NewBoolVar(f"Is_Nation_{i}") for i in range(len(nation_arr))]
        for i in range(len(self._nationality_bools)):
            self._model.add(sum([(1 if nation_map_to_unique_id[
                                           self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[j]] == i else 0) *
                                 self._cards_bools_vars[j] for j in range(self._no_cards)]) > 0).OnlyEnforceIf(
                self._nationality_bools[i])
            self._model.add(sum([(1 if nation_map_to_unique_id[
                                           self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[j]] == i else 0) *
                                 self._cards_bools_vars[j] for j in range(self._no_cards)]) == 0).OnlyEnforceIf(
                self._nationality_bools[i].Not())
