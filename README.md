# FC24 Ultimate Team SBC solver
This repository contains script for solving SBC (Squad Building Challenges) in optimize way by selecting cards which they overall price is the lowest.
Squad Building Challenges consist in building squad of ultimate team cards that fulfill given requirements.
For solving SBC challenges player can earn rewards to use in ultimate team - cards, packs etc.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
pip install -r requirements.txt
```

## Usage
To run the script you need to:
* create dataset from csv file or db - input data is provided by project [fc24-ultimate-team-players](https://github.com/bartlomiej-niemiec/fc24-ultimate-team-players) 
* create EaFcSbcSolver instance and use it's interface to provide requirements for your SBC and set desired formation of squad,
* run solve and display output data

Code Example:
```python
from data.dataset_factory import DatasetFactory, DatasetSources
from src.sbc_solver.ea_fc_sbc_solver import EaFcSbcSolver
from src.utils.formations import Formations
from src.solution_display.console_display import SbcSolutionConsoleDisplay

if __name__ == "__main__":

    dataset = DatasetFactory.create(DatasetSources.CSV)

    formation = Formations["4-1-3-2"]

    sbc_solver = EaFcSbcSolver(dataset, formation)
    sbc_cards = sbc_solver.solve()

    solution_display = SbcSolutionConsoleDisplay(sbc_cards, formation)
    solution_display.display()

```

Example Output:
```console
SBC solved in: 19.32286834716797s
+-----------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                        SBC solution cards, Total Price = 2200                                                       |
+-------------------+----------+--------+---------+-------+-----------+---------------+---------------------------------------------------------------+
| Name              | Position | Rating | Version | Price | League    | Nationality   | Futwiz                                                        |
+-------------------+----------+--------+---------+-------+-----------+---------------+---------------------------------------------------------------+
| Dani Martin       | GK       | 68     | SILVER  | 200   | ESP 2     | Spain         | https://www.futwiz.com/en/fc24/player/dani-martin/7576        |
| Chase Gasper      | LB       | 64     | BRONZE  | 200   | MLS       | United States | https://www.futwiz.com/en/fc24/player/chase-gasper/20618      |
| Christopher McVey | CB       | 64     | BRONZE  | 200   | MLS       | Sweden        | https://www.futwiz.com/en/fc24/player/christopher-mcvey/20628 |
| Lucas Lissens     | CB       | 64     | BRONZE  | 200   | DEN 1     | Belgium       | https://www.futwiz.com/en/fc24/player/lucas-lissens/20616     |
| Peter Therkildsen | RB       | 64     | BRONZE  | 200   | SWE 1     | Denmark       | https://www.futwiz.com/en/fc24/player/peter-therkildsen/20647 |
| Maria Diaz        | RM       | 73     | SILVER  | 200   | D1 Arkema | Spain         | https://www.futwiz.com/en/fc24/player/maria-diaz/3048         |
| Rai Marchan       | CDM      | 64     | BRONZE  | 200   | ESP 2     | Spain         | https://www.futwiz.com/en/fc24/player/rai-marchan/20665       |
| Gabriel Lunetta   | LM       | 64     | BRONZE  | 200   | ITA 2     | Italy         | https://www.futwiz.com/en/fc24/player/gabriel-lunetta/20630   |
| Nelson Palacio    | CM       | 71     | SILVER  | 200   | MLS       | Colombia      | https://www.futwiz.com/en/fc24/player/nelson-palacio/4897     |
| Jonathan Leko     | ST       | 64     | BRONZE  | 200   | ENG 3     | England       | https://www.futwiz.com/en/fc24/player/jonathan-leko/20623     |
| Tom Nichols       | ST       | 64     | BRONZE  | 200   | ENG 4     | England       | https://www.futwiz.com/en/fc24/player/tom-nichols/20614       |
+-------------------+----------+--------+---------+-------+-----------+---------------+---------------------------------------------------------------+
```

## What requirements can be input to the solver?

+ set_min_overall_of_squad() - minimum overall rating of squad,
+ set_min_cards_with_overall() - mininum no. players with given rating,
+ set_min_team_chemistry() - minimum squad chemistry,
+ set_exact_unique_nations() - exact number of unique nations of players in solution,
+ set_max_unique_nations() - maximum number of unique nations of players in solution,
+ set_min_unique_nations() - minimumn number of unique nations of players in solution,
+ set_exact_unique_leagues() - exact number of unique leagues of players in solution,
+ set_max_unique_leagues() - maximum number of unique leagues of players in solution,
+ set_min_unique_leagues() - minimumn number of unique leagues of players in solution,
+ set_max_nations_for_solution() - maximum number of nations used for solution,
+ set_max_leagues_for_solution() - maximum number of leagues used for solution,
+ set_min_rare_cards() - minimum number of rare cards used for solution,
+ set_min_cards_with_version() - minimum number of cards in specific version used for solution,
+ set_min_cards_with_league() - minimum number of cards in specific league used for solution,
+ set_min_cards_with_nation() - minimum number of cards in specific nationality used for solution,
+ set_min_cards_with_club() - minimum number of cards in specific club used for solution,
