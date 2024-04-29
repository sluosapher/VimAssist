# define a function to list all files in a given directory, return a list of file paths. Do not include subdirectories.
import os
import json

# config_file_name = 'config.json'
config_file_name = 'config.json'

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

def create_configurations(config_dir:str):
    """
    create an empty config file in the given directory.
    :param config_dir: The path of the directory.
    :return: None
    """
    # create a new config file
    config_file_path = os.path.join(config_dir, config_file_name)
    config_data = {
        "assistant_id": "",
        "thread_id": "",
        "vector_store_id": "",
        "doc_dir": "",

    }
    with open(config_file_path, 'w') as file:
        json.dump(config_data, file, indent=4)

def read_configurations(config_file_path:str):
    with open(config_file_path, 'r') as file:
        config_data = json.load(file)
    return config_data

def write_configurations(config_file_path, config_data):
    with open(config_file_path, 'w') as file:
        json.dump(config_data, file, indent=4)

# define a function to compare a given path string with the doc_dir in the config file
def compare_path_with_doc_dir(path:str, config_file_path:str):
    config_data = read_configurations(config_file_path)
    doc_dir = config_data['doc_dir']
    if path==doc_dir:
        return True
    else:
        return False

if __name__ == "__main__":
    pass
