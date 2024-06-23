import pathlib
from src.csv.csv_utils import get_csv_content, preprocess_csv_data
from src.sbc_solver.ea_fc_sbc_solver import EaFcSbcSolver


if __name__ == "__main__":
    CSV_FILENAME = "fut_players.csv"
    CSV_FILEPATH = pathlib.Path(__file__).parent.parent.resolve().joinpath('data').joinpath(CSV_FILENAME)

    players_df = get_csv_content(CSV_FILEPATH)
    preprocess_csv_data(players_df)

    sbc_solver = EaFcSbcSolver(players_df)
    sbc_solver.set_formation([0] * 11)
    sbc_solver.set_min_overall_of_squad(82)
    sbc_solver.set_how_many_cards_with_overall(3, 86)
    sbc_solver.solve()
    sbc_solver.print_solution()
