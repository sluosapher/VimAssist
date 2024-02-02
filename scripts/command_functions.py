# define a function to update the assistant with documents in the working directory, return status
import os
import assistant_tools
import utilities as util


def update_docs(working_dir:str, config_dir:str)->int:
    """
    Add all files in the working directory to the assistant.

    Args:
        working_dir (str): The path of the working directory.

    Returns:
        int: 0 if successful, -1 if failed.
    """
    # read the config file
    config_file_path = os.path.join(config_dir, util.config_file_name)
    config_data = util.read_configurations(config_file_path)

    # update the working directory in the config file
    config_data['working_dir'] = working_dir
    util.write_configurations(config_file_path, config_data)

    # create a new assistant if not exist
    if 'assistant_id' not in config_data or config_data['assistant_id'] == "":
        try:
            assistant_id = assistant_tools.create_assistant("My Writting Assistant")
            # print(f"Created a new assistant with ID {assistant_id}.")
            config_data['assistant_id'] = assistant_id
            util.write_configurations(config_file_path, config_data)
        except Exception as e:
            print(e)
            return -1
    else:
        assistant_id = config_data['assistant_id']

    # create a new thread if not exist
    if 'thread_id' not in config_data or config_data['thread_id'] == "":
        try:
            thread_id = assistant_tools.create_thread()
            # print(f"Created a new thread with ID {thread_id}.")
            config_data['thread_id'] = thread_id
            util.write_configurations(config_file_path, config_data)
        except Exception as e:
            print(e)
            return -1
    else:
        thread_id = config_data['thread_id']

    # list all files in the working directory
    file_list = util.list_files_in_directory(working_dir)
    # print(f"Found {len(file_list)} files in the working directory.")

    # create file objects in openai
    file_id_list = assistant_tools.create_file_objects(file_list)
    # print(f"Created {len(file_id_list)} file objects in openai.")

    # check if file_id_list is None or empty
    if file_id_list is None or len(file_id_list) == 0:
        return -1
    else:
        # update the assistant with the new file list
        status = assistant_tools.update_files_of_assistant(assistant_id, file_id_list)
        if status == 0:
            # get all file names in the assistant, using function from assistant_tools
            file_name_list = assistant_tools.get_all_file_names(assistant_id)
            # print the file names to the console
            print("Updated the assistant with the following documents:")
            # print one file name per line
            for file_name in file_name_list:
                print(file_name)
            return 0
        else:
            print("Failed to update the assistant with the documents.")
            return -1
        
# define a function to send a message to the assistant, return answer. using function from assistant_tools
def send_message_to_assistant(message:str, config_dir:str)->str:
    """
    Send a message to the assistant.

    Args:
        message (str): The message to send.
    Returns:
        str: The answer from the assistant.
    """

    # check if message is empty
    if message == "":
        print("Message is empty.")
        return ""

    config_file_path = os.path.join(config_dir, util.config_file_name)

    # read assistant id and thread id from the config file, using function from utilities
    assistant_id = util.read_configurations(config_file_path)['assistant_id']
    thread_id = util.read_configurations(config_file_path)['thread_id']

    # send the message to the assistant
    status, answer = assistant_tools.sendMessage(assistant_id, thread_id, message)

    # print the answer to the console if successful
    if status == 0:
        return answer
    else:
        print(f"Failed to get answer: {answer}")
        return ""
        
if __name__ == "__main__":
    # # get the current directory
    # dir = "/Users/sluo/tmp"
    # update_docs(dir)

    # send a message to the assistant
    message = "What is the capital of China?"

    answer = send_message_to_assistant(message)
    print(answer)




