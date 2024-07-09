import webbrowser
from data.csv.csv_utils import CsvHeaders
from src.solution_display.sbc_solution_display_if import SbcSolutionDisplayIf


class SbcSolutionWebBrowserDisplay(SbcSolutionDisplayIf):

    def __init__(self, sbc_cards):
        super().__init__(sbc_cards)

    def display(self):
        webbrowser_controller = webbrowser.get()
        for i in range(self._solution_cards.shape[0]):
            if i == 0:
                webbrowser_controller.open_new(self._solution_cards[CsvHeaders.FutwizLink].iloc[i])
            else:
                webbrowser_controller.open_new_tab(self._solution_cards[CsvHeaders.FutwizLink].iloc[i])
