import pathlib
from src.csv.csv_utils import get_csv_content, preprocess_csv_data
from src.sbc_solver.ea_fc_sbc_solver import EaFcSbcSolver
from src.utils.formations import Formations
import time

if __name__ == "__main__":
    CSV_FILENAME = "fut_players.csv"
    CSV_FILEPATH = pathlib.Path(__file__).parent.parent.resolve().joinpath('data').joinpath(CSV_FILENAME)

    players_df = get_csv_content(CSV_FILEPATH)
    preprocess_csv_data(players_df)

    sbc_solver = EaFcSbcSolver(players_df)
    start_time = time.time()
    sbc_solver.set_formation(Formations["4-4-2"])
    sbc_solver.set_min_team_chemistry(25)
    sbc_solver.solve()
    sbc_solver.print_solution()
    print(f"Solution have been found in time: {time.time() - start_time}")
