from ortools.sat.python import cp_model
from src.csv.csv_utils import CsvHeaders
import src.sbc_solver.exceptions as SolverExceptions
import time

from typing import List


class EaFcSbcSolver:
    _MAX_PLAYERS_IN_FORMATION = 11

    def __init__(self, ea_fc_cards_df, max_time_for_solution_s=100):
        self._model = cp_model.CpModel()
        self._solver = cp_model.CpSolver()
        self._solver.parameters.num_workers = 8
        self._solver.parameters.max_time_in_seconds = max_time_for_solution_s
        self._ea_fc_cards_df = ea_fc_cards_df

        self._no_cards = len(ea_fc_cards_df)
        self._cards_bools_vars = [self._model.NewBoolVar(f'{self._ea_fc_cards_df[CsvHeaders.ID].iloc[i]}') for i in
                                  range(self._no_cards)]
        self._no_players = None
        self._formation = None
        self._leagues_bools = None
        self._nationality_bools = None
        self._solved = False
        self._player_chemistry = [self._model.NewIntVar(0, 3, f"player_{i}_chemistry") for i in range(self._no_cards)]

    def set_formation(self, formation: List[str]):
        if len(formation) > self._MAX_PLAYERS_IN_FORMATION:
            raise SolverExceptions.IncorrectFormation(
                f"Too many players in formation. Max players per formation = {EaFcSbcSolver._MAX_PLAYERS_IN_FORMATION}")
        self._formation = formation
        self._no_players = len(formation)
        # Formation constraint
        self._add_constraint_to_formation()

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

        # NATIONALITY
        nation_arr = self._ea_fc_cards_df[CsvHeaders.Nationality].unique()
        nation_map_to_unique_id = self._get_map_attribute_to_number(nation_arr)
        nation_vars = [self._model.NewIntVar(0, self._no_players, f"Nation_{i}") for i in range(len(nation_arr))]
        nation_chemistry = [self._model.NewIntVar(0, self._no_players, f"Nation_Chem_{i}") for i in range(len(nation_arr))]

        plus_one_same_two_nation = []
        plus_two_same_five_nation = []
        plus_three_same_eight_or_more_nations = []

        for i in range(len(nation_arr)):
            plus_one_same_two_nation.append(self._model.NewBoolVar(f'plus_one_same_two_nation_{i}'))
            plus_two_same_five_nation.append(self._model.NewBoolVar(f'plus_two_same_five_nation_{i}'))
            plus_three_same_eight_or_more_nations.append(
                self._model.NewBoolVar(f'plus_three_same_eight_more_country_{i}'))

        # Calculate no. player in each nationality
        for nation_id in range(len(nation_arr)):
            self._model.Add(
                nation_vars[nation_id] == cp_model.LinearExpr.Sum([(1 if nation_id == nation_map_to_unique_id[
                    self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]] else 0) * self._cards_bools_vars[i] for i in
                                                                   range(self._no_cards)]))

            self._model.AddLinearConstraint(nation_vars[nation_id], 2, 4).OnlyEnforceIf(
                plus_one_same_two_nation[nation_id])
            self._model.Add(nation_vars[nation_id] < 2).OnlyEnforceIf(
                plus_one_same_two_nation[nation_id].Not())

            self._model.AddLinearConstraint(nation_vars[nation_id], 5, 7).OnlyEnforceIf(
                plus_two_same_five_nation[nation_id])
            self._model.Add(nation_vars[nation_id] < 5).OnlyEnforceIf(
                plus_two_same_five_nation[nation_id].Not())

            self._model.Add(nation_vars[nation_id] >= 8).OnlyEnforceIf(
                plus_three_same_eight_or_more_nations[nation_id])
            self._model.Add(nation_vars[nation_id] < 8).OnlyEnforceIf(
                plus_three_same_eight_or_more_nations[nation_id].Not())

            self._model.Add(nation_chemistry[nation_id] == 0).OnlyEnforceIf([
                plus_one_same_two_nation[nation_id].Not(),
                plus_two_same_five_nation[nation_id].Not(),
                plus_two_same_five_nation[nation_id].Not()
            ])

            self._model.Add(nation_chemistry[nation_id] == 1).OnlyEnforceIf(
                plus_one_same_two_nation[nation_id]
            )

            self._model.Add(nation_chemistry[nation_id] == 2).OnlyEnforceIf(
                plus_two_same_five_nation[nation_id]
            )

            self._model.Add(nation_chemistry[nation_id] == 3).OnlyEnforceIf(
                plus_two_same_five_nation[nation_id]
            )

        # LEAGUES
        leagues_arr = self._ea_fc_cards_df[CsvHeaders.League].unique()
        league_map_to_unique_id = self._get_map_attribute_to_number(leagues_arr)
        league_vars = [self._model.NewIntVar(0, self._no_players, f"League_{i}") for i in range(len(leagues_arr))]
        league_chemistry = [self._model.NewIntVar(0, self._no_players, f"League_Chem_{i}") for i in
                            range(len(leagues_arr))]

        plus_one_same_three_league = []
        plus_two_same_five_league = []
        plus_three_same_eight_more_league = []

        for i in range(len(leagues_arr)):
            plus_one_same_three_league.append(self._model.NewBoolVar(f'plus_one_same_three_league_{i}'))
            plus_two_same_five_league.append(self._model.NewBoolVar(f'plus_two_same_five_league_{i}'))
            plus_three_same_eight_more_league.append(self._model.NewBoolVar(f'plus_three_same_eight_more_league_{i}'))

        # Calculate no. player in each league
        for league_id in range(len(leagues_arr)):
            self._model.Add(
                league_vars[league_id] == cp_model.LinearExpr.Sum([(1 if league_id == league_map_to_unique_id[
                    self._ea_fc_cards_df[CsvHeaders.League].iloc[i]] else 0) * self._cards_bools_vars[i] for i in
                                                                   range(self._no_cards)]))

            self._model.AddLinearConstraint(league_vars[league_id], 3, 5).OnlyEnforceIf(
                plus_one_same_three_league[league_id])
            self._model.Add(league_vars[league_id] < 3).OnlyEnforceIf(
                plus_one_same_three_league[league_id].Not())

            self._model.AddLinearConstraint(league_vars[league_id], 5, 7).OnlyEnforceIf(
                plus_two_same_five_league[league_id])
            self._model.Add(league_vars[league_id] < 5).OnlyEnforceIf(
                plus_two_same_five_league[league_id].Not())

            self._model.Add(league_vars[league_id] >= 8).OnlyEnforceIf(
                plus_three_same_eight_more_league[league_id])
            self._model.Add(league_vars[league_id] < 8).OnlyEnforceIf(
                plus_three_same_eight_more_league[league_id].Not())

            self._model.Add(league_chemistry[league_id] == 0).OnlyEnforceIf([
                plus_one_same_three_league[league_id].Not(),
                plus_two_same_five_league[league_id].Not(),
                plus_three_same_eight_more_league[league_id].Not()
            ])
            self._model.Add(league_chemistry[league_id] == 1).OnlyEnforceIf(
                plus_one_same_three_league[league_id]
            )
            self._model.Add(league_chemistry[league_id] == 2).OnlyEnforceIf(
                plus_two_same_five_league[league_id]
            )
            self._model.Add(league_chemistry[league_id] == 3).OnlyEnforceIf(
                plus_three_same_eight_more_league[league_id]
            )

        # CLUBS
        clubs_arr = self._ea_fc_cards_df[CsvHeaders.Club].unique()
        clubs_map_to_unique_id = self._get_map_attribute_to_number(clubs_arr)
        clubs_vars = [self._model.NewIntVar(0, self._no_players, f"Club_{i}") for i in range(len(clubs_arr))]
        club_chemistry = [self._model.NewIntVar(0, self._no_players, f"Club_Chem_{i}") for i in range(len(clubs_arr))]

        plus_one_same_two_club = []
        plus_two_same_four_club = []
        plus_three_same_seven_club = []

        for i in range(len(clubs_arr)):
            plus_one_same_two_club.append(self._model.NewBoolVar(f'plus_one_same_two_club_{i}'))
            plus_two_same_four_club.append(self._model.NewBoolVar(f'plus_two_same_four_club_{i}'))
            plus_three_same_seven_club.append(self._model.NewBoolVar(f'plus_three_same_seven_club_{i}'))

        # Calculate no. player in each Club
        for club_id in range(len(clubs_arr)):
            self._model.Add(clubs_vars[club_id] == cp_model.LinearExpr.Sum([(1 if club_id == clubs_map_to_unique_id[
                self._ea_fc_cards_df[CsvHeaders.Club].iloc[i]] else 0) * self._cards_bools_vars[i] for i in
                                                                            range(self._no_cards)]))

            self._model.AddLinearConstraint(clubs_vars[club_id], 2, 4).OnlyEnforceIf(plus_one_same_two_club[club_id])
            self._model.Add(clubs_vars[club_id] < 2).OnlyEnforceIf(plus_one_same_two_club[club_id].Not())

            self._model.AddLinearConstraint(clubs_vars[club_id], 4, 6).OnlyEnforceIf(plus_two_same_four_club[club_id])
            self._model.Add(clubs_vars[club_id] < 4).OnlyEnforceIf(
                plus_two_same_four_club[club_id].Not())

            self._model.Add(clubs_vars[club_id] >= 7).OnlyEnforceIf(plus_three_same_seven_club[club_id])
            self._model.Add(clubs_vars[club_id] < 7).OnlyEnforceIf(
                plus_three_same_seven_club[club_id].Not())

            self._model.Add(club_chemistry[club_id] == 0).OnlyEnforceIf([plus_one_same_two_club[club_id].Not(),
                                                                         plus_two_same_four_club[club_id].Not(),
                                                                         plus_three_same_seven_club[club_id].Not()]
                                                                        )
            self._model.Add(club_chemistry[club_id] == 1).OnlyEnforceIf(plus_one_same_two_club[club_id])
            self._model.Add(club_chemistry[club_id] == 2).OnlyEnforceIf(plus_two_same_four_club[club_id])
            self._model.Add(club_chemistry[club_id] == 3).OnlyEnforceIf(plus_three_same_seven_club[club_id])

        for i in range(self._no_cards):

            if self._ea_fc_cards_df[CsvHeaders.Position].iloc[i] not in self._formation:
                self._model.add(self._player_chemistry[i] == 0)
            else:

                card_league_id = league_map_to_unique_id[self._ea_fc_cards_df[CsvHeaders.League].iloc[i]]
                card_nation_id = nation_map_to_unique_id[self._ea_fc_cards_df[CsvHeaders.Nationality].iloc[i]]
                card_club_id = clubs_map_to_unique_id[self._ea_fc_cards_df[CsvHeaders.Club].iloc[i]]

                # Player Chemistry
                self._model.Add(self._player_chemistry[i] == club_chemistry[card_club_id] + league_chemistry[card_league_id] + nation_chemistry[card_nation_id]).OnlyEnforceIf(self._cards_bools_vars[i])
                self._model.Add(self._player_chemistry[i] == 0).OnlyEnforceIf(self._cards_bools_vars[i].Not())

        self._model.Add(cp_model.LinearExpr.Sum(self._player_chemistry) >= chemistry)

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

        # Objective
        self._model.Minimize(
            sum(self._cards_bools_vars[i] * self._ea_fc_cards_df[CsvHeaders.Price].iloc[i] for i in
                range(self._no_cards))
        )

        # Find solutions
        start_time = time.time()
        self._solver.Solve(self._model)

        solution_players = None
        solution_players = [self._ea_fc_cards_df.iloc[i] for i in range(self._no_cards) if
                            self._solver.Value(self._cards_bools_vars[i])]
        if solution_players:
            print(f"SBC solved in: {time.time() - start_time}s")

        return solution_players


    def reset(self):
        ea_fc_cards_temp = self._ea_fc_cards_df
        del self._model
        del self._solver
        del self._ea_fc_cards_df
        del self._no_cards
        del self._cards_bools_vars
        self.__init__(ea_fc_cards_temp)

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
