# define a function to list all files in a given directory, return a list of file paths. Do not include subdirectories.
import os
import json

config_file_name = 'config.json'
# config_file_name = 'config-test.json'

def list_files_in_directory(directory:str)->list[str]:
    """
    List all files in a given directory.

    Args:
        directory (str): The path of the directory.

    Returns:
        list[str]: A list of file paths.
    """
    file_list = []
    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path):
            # skip hidden files starting with '.'
            if file[0] == '.':
                continue
            # print(full_path)
            file_list.append(full_path)
    return file_list


def read_configurations(config_file_path:str):
    with open(config_file_path, 'r') as file:
        config_data = json.load(file)
    return config_data

def write_configurations(config_file_path, config_data):
    with open(config_file_path, 'w') as file:
        json.dump(config_data, file, indent=4)

# define a function to compare a given path string with the working_dir in the config file
def compare_path_with_working_dir(path:str, config_file_path:str):
    config_data = read_configurations(config_file_path)
    working_dir = config_data['working_dir']
    if path==working_dir:
        return True
    else:
        return False

if __name__ == "__main__":
    pass
