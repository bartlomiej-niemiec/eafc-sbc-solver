import pathlib
from src.csv.csv_utils import get_csv_content, preprocess_csv_data
from src.sbc_solver.ea_fc_sbc_solver import EaFcSbcSolver


if __name__ == "__main__":
    CSV_FILENAME = "fut_players.csv"
    CSV_FILEPATH = pathlib.Path(__file__).parent.parent.resolve().joinpath('data').joinpath(CSV_FILENAME)

    players_df = get_csv_content(CSV_FILEPATH)
    preprocess_csv_data(players_df)

    # model = cp_model.CpModel()
    #
    # no_cards = len(players_df)
    # no_players_in_squad = 11
    # max_leagues_in_squad = 3
    #
    # cards_vars = [model.NewBoolVar(f'card_{i}') for i in range(no_cards)]
    #
    # # No. players searched
    # model.add(sum(cards_vars) == 11)
    #
    # club_map = get_map_attribute_to_number(players_df[CsvHeaders.Club])
    # nationality_map = get_map_attribute_to_number(players_df[CsvHeaders.Nationality])
    #
    # # Exactly no. players from particular team
    # model.add(sum((1 if players_df[CsvHeaders.Club].iloc[i] == "FC Barcelona" else 0) * cards_vars[i] for i in
    #              range(no_cards)) == 5)
    #
    # # Max leagues allowed for challenge
    # leagues_arr = players_df[CsvHeaders.League].unique()
    # league_map = get_map_attribute_to_number(leagues_arr)
    # league_vars = [model.NewIntVar(0, len(leagues_arr) - 1, f"League_{i}") for i in range(max_leagues_in_squad)]
    # for i in range(no_cards):
    #     is_league = [model.NewBoolVar(f'Not_League_{i}') for j in range(max_leagues_in_squad)]
    #     for j in range(max_leagues_in_squad):
    #         model.add(league_vars[j] == league_map[players_df[CsvHeaders.League].iloc[i]]).OnlyEnforceIf(is_league[j])
    #     model.AddBoolOr(is_league).OnlyEnforceIf(cards_vars[i])
    #
    # model.Minimize(
    #     sum(cards_vars[i] * players_df[CsvHeaders.Price].iloc[i] for i in range(len(cards_vars)))
    # )
    #
    # # Find solutions
    # solver = cp_model.CpSolver()
    # solver.Solve(model)
    #
    # for i in range(no_cards):
    #     if solver.Value(cards_vars[i]):
    #         print_player_date(players_df.iloc[i])
    #
    # print("Done")

    sbc_solver = EaFcSbcSolver(players_df)
    sbc_solver.set_formation([0] * 11)
    sbc_solver.set_max_leagues_for_solution(1)
    sbc_solver.set_how_many_rare_cards(5)
    sbc_solver.set_how_many_players_from_version("SILVER RARE", 3)
    sbc_solver.solve()
    sbc_solver.print_solution()
