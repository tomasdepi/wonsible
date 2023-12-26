import yaml

def parse_yaml_file(file_path: str, open_mode: str='r') -> dict:
    with open(file_path, open_mode) as file:
        data = yaml.safe_load(file)

    return data

def get_missing_mandatory_keys(mandatory_keys: list, dict_to_check: dict) -> list:
    return [key for key in mandatory_keys if key not in dict_to_check]
