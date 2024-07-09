from src.solution_display.sbc_solution_display_if import SbcSolutionDisplayIf
from prettytable import PrettyTable
from data.csv.csv_utils import CsvHeaders


class SbcSolutionConsoleDisplay(SbcSolutionDisplayIf):

    def __init__(self, sbc_cards, formation):
        super().__init__(sbc_cards)
        self._cards_table = PrettyTable()
        self._total_price = 0
        self._formation = formation
        self._add_fieldnames()
        self._add_alignment()
        self._add_rows()
        self._add_title(self._total_price)

    def set_cards_to_display(self, sbc_cards, formation):
        self._solution_cards = sbc_cards
        self._total_price = 0
        self._formation = formation
        self._cards_table.clear_rows()
        self._add_rows()
        self._add_title(self._total_price)

    def display(self):
        print(self._cards_table)

    def _add_rows(self):
        position_added_map = {}
        for position in self._formation:
            if position_added_map.get(position) is None:
                cards_at_position = self._solution_cards.loc[self._solution_cards[CsvHeaders.Position] == position]
                for i in range(cards_at_position.shape[0]):
                    self._cards_table.add_row([
                        cards_at_position[CsvHeaders.Name].iloc[i],
                        cards_at_position[CsvHeaders.Position].iloc[i],
                        cards_at_position[CsvHeaders.OverallRating].iloc[i],
                        cards_at_position[CsvHeaders.Version].iloc[i],
                        cards_at_position[CsvHeaders.Price].iloc[i],
                        cards_at_position[CsvHeaders.League].iloc[i],
                        cards_at_position[CsvHeaders.Nationality].iloc[i],
                        cards_at_position[CsvHeaders.FutwizLink].iloc[i]
                    ])
                    self._total_price += cards_at_position[CsvHeaders.Price].iloc[i]
                position_added_map[position] = True

    def _add_title(self, price):
        self._cards_table.title = f"SBC solution cards, Total Price = {price}"

    def _add_fieldnames(self):
        self._cards_table.field_names = [
            "Name",
            "Position",
            "Rating",
            "Version",
            "Price",
            "League",
            "Nationality",
            "Futwiz"
        ]

    def _add_alignment(self):
        self._cards_table.align["Name"] = "l"
        self._cards_table.align["Position"] = "l"
        self._cards_table.align["Rating"] = "l"
        self._cards_table.align["Version"] = "l"
        self._cards_table.align["Price"] = "l"
        self._cards_table.align["League"] = "l"
        self._cards_table.align["Nationality"] = "l"
        self._cards_table.align["Futwiz"] = "l"
