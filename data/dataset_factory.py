import pathlib
from enum import IntEnum
from data.csv.csv_utils import get_csv_content, preprocess_csv_data


class DatasetSources(IntEnum):
    CSV = 1
    DB = 2


class DatasetFactory:
    @classmethod
    def create(cls, source: DatasetSources):
        dataset = None
        if source == DatasetSources.CSV:
            dataset = cls._get_dataset_from_csv()
        elif source == DatasetSources.DB:
            pass  # TO DO

        return dataset

    @classmethod
    def _get_dataset_from_csv(cls):
        CSV_FILENAME = "csv/fut_players.csv"
        CSV_FILEPATH = pathlib.Path(__file__).parent.joinpath(CSV_FILENAME)
        dataset = get_csv_content(CSV_FILEPATH)
        preprocess_csv_data(dataset)

        return dataset
