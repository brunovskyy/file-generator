import csv
from typing import Union, List

def parse_input_data(input_data: Union[dict, List[dict], str]) -> List[dict]:
    """
    Converts the input into a list of dictionaries.

    Parameters:
        input_data (dict | list[dict] | str):
            - A dictionary containing input data.
            - A list of dictionaries.
            - A string with the path to a CSV file.

    Returns:
        list[dict]: List of dictionaries with the processed data.

    Raises:
        ValueError: If the input type is not supported.

    Usage:
        - If a dict is provided, it is wrapped in a list.
        - If a list of dicts is provided, it is returned as is.
        - If a CSV file path is provided, the file is read and each row is converted to a dict.
    """
    # If input is a dictionary, wrap it in a list
    if isinstance(input_data, dict):
        return [input_data]
    # If input is already a list of dictionaries, return it directly
    elif isinstance(input_data, list):
        return input_data
    # If input is a CSV file path, read and convert each row to a dictionary
    elif isinstance(input_data, str) and input_data.lower().endswith('.csv'):
        with open(input_data, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]
    # If input type is not supported, raise an exception
    else:
        raise ValueError("input_data must be a dict, list of dicts, or path to a CSV file.")