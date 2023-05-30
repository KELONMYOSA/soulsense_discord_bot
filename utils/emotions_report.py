import pandas as pd


def _csv_to_pandas(file_path):
    file = pd.read_csv(file_path, header=None)
    file.columns = ["timestamp", "duration", "username", "emotion", "text"]

    return file


def visualize_report(file_path):
    df = _csv_to_pandas(file_path)
