from data.dataset_factory import DatasetFactory, DatasetSources
from src.sbc_solver.ea_fc_sbc_solver import EaFcSbcSolver
from src.utils.formations import Formations
from src.solution_display.console_display import SbcSolutionConsoleDisplay


if __name__ == "__main__":

    dataset = DatasetFactory.create(DatasetSources.CSV)

    formation = Formations["4-4-2"]

    sbc_solver = EaFcSbcSolver(dataset, formation)
    sbc_solver.set_min_unique_leagues(5)
    sbc_solver.set_min_overall_of_squad(80)
    sbc_solver.set_min_rare_cards(2)
    sbc_solver.set_min_team_chemistry(5)
    sbc_solver.set_min_unique_nations(5)
    sbc_cards = sbc_solver.solve()

    solution_display = SbcSolutionConsoleDisplay(sbc_cards, formation)
    solution_display.display()
