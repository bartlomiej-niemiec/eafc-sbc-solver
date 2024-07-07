import pathlib
from src.csv.csv_utils import get_csv_content, preprocess_csv_data
from src.sbc_solver.ea_fc_sbc_solver import EaFcSbcSolver
from src.utils.formations import Formations
from src.csv.csv_utils import CsvHeaders


def print_card(card):
    print("====================================================")
    print(f"| Name    : {card[CsvHeaders.Name]}                |")
    print(f"| Rating  : {card[CsvHeaders.OverallRating]}       |")
    print(f"| Position: {card[CsvHeaders.Position]}            |")
    print(f"| Nationality: {card[CsvHeaders.Nationality]}      |")
    print(f"| League: {card[CsvHeaders.League]}                |")
    print("====================================================")


if __name__ == "__main__":
    CSV_FILENAME = "fut_players.csv"
    CSV_FILEPATH = pathlib.Path(__file__).parent.parent.resolve().joinpath('data').joinpath(CSV_FILENAME)

    players_df = get_csv_content(CSV_FILEPATH)
    preprocess_csv_data(players_df)

    sbc_solver = EaFcSbcSolver(players_df)
    sbc_solver.set_formation(Formations["4-1-3-2"])
    sbc_solver.set_min_team_chemistry(22)
    sbc_cards = sbc_solver.solve()
    for card in sbc_cards:
        print_card(card)
