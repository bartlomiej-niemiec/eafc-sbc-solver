from data.dataset_factory import DatasetFactory, DatasetSources
from src.sbc_solver.ea_fc_sbc_solver import EaFcSbcSolver
from src.utils.formations import Formations
from src.solution_display.console_display import SbcSolutionConsoleDisplay


if __name__ == "__main__":

    dataset = DatasetFactory.create(DatasetSources.CSV)

    formation = Formations["4-1-3-2"]

    sbc_solver = EaFcSbcSolver(dataset)
    sbc_solver.set_formation(formation)
    sbc_cards = sbc_solver.solve()

    solution_display = SbcSolutionConsoleDisplay(sbc_cards, formation)
    solution_display.display()
