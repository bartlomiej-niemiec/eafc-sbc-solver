import pandas as pd
from src.csv.player_data_template import PlayerDataTemplateFactory, does_file_include_player_stats, GeneralPlayerData, \
    GkPosStats, CommonPosStats


def get_csv_content(filepath, delimiter=';'):
    with_player_stats = does_file_include_player_stats(filepath)
    names = [key for key in PlayerDataTemplateFactory().create(with_player_stats).keys()]
    dtypes = {key: str for key in PlayerDataTemplateFactory().create(with_player_stats).keys()}
    return pd.read_csv(filepath, delimiter=delimiter, names=names, dtype=dtypes, skiprows=[0])


class CsvHeaders(GeneralPlayerData, CommonPosStats, GkPosStats):
    pass


class CsvRowAttributeIndex:
    ADDED = 0
    AGE = 1
    ALTERNATIVE_POS = 2
    ATT_WR = 3
    BODY_TYPE = 4
    CLUB = 5
    DEF_WR = 6
    FOOT = 7
    FUTWIZ_LINK = 8
    HEIGHT = 9
    ID = 10
    LEAGUE = 11
    FULLNAME = 12
    NATIONALITY = 13
    OVERALL_RATING = 14
    POSITION = 15
    PRICE = 16
    SKILL_MOVE = 17
    VERSION = 18
    WEAK_FOOT = 19
    WEIGHT = 20
    ACCELERATE = 21
    ACCELERATION = 22
    AGGRESSION = 23
    AGILITY = 24
    BALANCE = 25
    BALL_CONTROL = 26
    COMPOSURE = 27
    CROSSING = 28
    CURVE = 29
    DEF = 30
    DRI = 31
    DEF_AWARENESS = 32
    DRIBBLING = 33
    FK_ACC = 34
    FINISHING = 35
    HEADING = 36
    INTERCEPTION = 37
    JUMPING = 38
    LONG_PASS = 39
    LONG_SHOTS = 40
    PAC = 41
    PAS = 42
    PHY = 43
    PENALTIES = 44
    PLAYSTYLES = 45
    PLAYSTYLES_PLUS = 46
    POSITIONING = 47
    REACTIONS = 48
    SHO = 49
    SHORT_PASS = 50
    SHOT_POWER = 51
    SLIDE_TACKLE = 52
    SPRINT_SPEED = 53
    STAMINA = 54
    STAND_TACKLE = 55
    STRENGTH = 56
    VISION = 57
    VOLLEYS = 58
    DIV = 59
    GK_DIVING = 60
    GK_HANDLING = 61
    GK_KICKING = 62
    GK_POS = 63
    GK_REFLEXES = 64
    HAN = 65
    KIC = 66
    POS = 67
    REF = 68
    SPD = 69


def preprocess_csv_data(players_df):
    string_columns = [
        CsvHeaders.Added,
        CsvHeaders.AltPos,
        CsvHeaders.Club,
        CsvHeaders.AttWR,
        CsvHeaders.BodyType,
        CsvHeaders.DefWR,
        CsvHeaders.Foot,
        CsvHeaders.FutwizLink,
        CsvHeaders.Height,
        CsvHeaders.League,
        CsvHeaders.Name,
        CsvHeaders.Nationality,
        CsvHeaders.Position,
        CsvHeaders.Version,
        CsvHeaders.Weight,
        CsvHeaders.AcceleRATE,
        CsvHeaders.PlayStyles,
        CsvHeaders.PlayStyles,
        CsvHeaders.PlayStylesPlus,
    ]

    for column in players_df:
        if column in string_columns:
            players_df[column] = players_df[column].astype(str)
        else:
            players_df[column] = players_df[column].fillna(0)
            players_df[column] = players_df[column].astype(int)

    for i in range(len(players_df)):
        players_df.at[i, CsvHeaders.Club] = players_df[CsvHeaders.Club].iloc[i].strip()
        players_df.at[i, CsvHeaders.Nationality] = players_df[CsvHeaders.Nationality].iloc[i].strip()
        players_df.at[i, CsvHeaders.Version] = players_df[CsvHeaders.Version].iloc[i].strip()
        players_df.at[i, CsvHeaders.League] = players_df[CsvHeaders.League].iloc[i].strip()

    players_df.drop(players_df[(players_df[CsvHeaders.Price] == 0)].index, inplace=True)
