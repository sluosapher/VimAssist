# define a function to update the assistant with documents in the working directory, return status
import os
import assistant_tools
import utilities as util


def update_docs(doc_dir:str, config_dir:str)->int:
    """
    Add all files in the working directory to the assistant.

    Args:
        doc_dir (str): The path of the working directory.

    Returns:
        int: 0 if successful, -1 if failed.
    """
    # check if config file exists. Create one if not exist
    config_file_path = os.path.join(config_dir, util.config_file_name)
    if not os.path.exists(config_file_path):
        util.create_configurations(config_dir)

    # read the config file
    config_data = util.read_configurations(config_file_path)

    # update the working directory in the config file
    config_data['doc_dir'] = doc_dir
    util.write_configurations(config_file_path, config_data)

    # create a new vector store if not exist, otherwise retrieve the existing one
    if ('vector_store_id' not in config_data) or (not config_data['vector_store_id']):
        try:
            vector_store_id = assistant_tools.create_vector_store()
            # print(f"Created a new vector store with ID {vector_store_id}.")
            config_data['vector_store_id'] = vector_store_id
            util.write_configurations(config_file_path, config_data)
        except Exception as e:
            print(e)
            return -1
    else:
        vector_store_id = config_data['vector_store_id']

    # update files in the vector store
    file_paths = util.list_files_in_directory(doc_dir)
    print(f"Found {len(file_paths)} files in the working directory.")

    status = assistant_tools.update_vector_store_files(vector_store_id, file_paths)
    if status != 0:
        print("Failed to update the vector store with the documents.")
        return -1

    # create a new assistant if not exist
    if 'assistant_id' not in config_data or config_data['assistant_id'] == "":
        try:
            assistant_id = assistant_tools.create_assistant("VimAssist", vector_store_id)
            # print(f"Created a new assistant with ID {assistant_id}.")
            config_data['assistant_id'] = assistant_id
            util.write_configurations(config_file_path, config_data)
        except Exception as e:
            print(e)
            return -1
    else:
        # try retrieve the assistant from openai
        assistant_id = config_data['assistant_id']
        assistant = assistant_tools.retrieve_assistant(assistant_id)
        if assistant is None:
            print(f"Failed to retrieve the assistant with ID {assistant_id}. Creating a new assistant.")
            # create a new assistant if failed to retrieve the old one
            assistant_id = assistant_tools.create_assistant("VimAssist", vector_store_id)
            if assistant_id is None:
                return -1
            print(f"Created a new assistant with ID {assistant_id}.")
            config_data['assistant_id'] = assistant_id

            # write the new assistant id to the config file
            util.write_configurations(config_file_path, config_data)
        else:
            pass

        assistant_id = config_data['assistant_id']

    # delete the old thread if exist
    if 'thread_id' in config_data and config_data['thread_id'] != "":
        try:
            assistant_tools.delete_thread(config_data['thread_id'])
            # print(f"Deleted the old thread with ID {config_data['thread_id']}.")
        except Exception as e:
            print(e) # if failed to delete the old thread, we continue to create a new thread
        
    config_data['thread_id'] = ""
    util.write_configurations(config_file_path, config_data)

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
    
    return 0

    # # list all files in the working directory
    # file_list = util.list_files_in_directory(doc_dir)
    # # print(f"Found {len(file_list)} files in the working directory.")

    # # TODO: create a new funtion to upload all files to the vector store

    # # create file objects in openai
    # file_id_list = assistant_tools.create_file_objects(file_list)
    # # print(f"Created {len(file_id_list)} file objects in openai.")

    # # check if file_id_list is None or empty
    # if file_id_list is None or len(file_id_list) == 0:
    #     return -1
    # else:
    #     # update the assistant with the new file list
    #     status = assistant_tools.update_files_of_assistant(assistant_id, file_id_list)
    #     if status == 0:
    #         # get all file names in the assistant, using function from assistant_tools
    #         file_name_list = assistant_tools.get_all_file_names(assistant_id)
    #         # print the file names to the console
    #         print("Updated the assistant with the following documents:")
    #         # print one file name per line
    #         for file_name in file_name_list:
    #             print(file_name)
    #         return 0
    #     else:
    #         print("Failed to update the assistant with the documents.")
    #         return -1
        
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
    message = 'Search attached documents, ' + message # force the assistant to search the attached documents
    status, answer = assistant_tools.sendMessage(assistant_id, thread_id, message)

    # print the answer to the console if successful
    if status == 0:
        return answer
    else:
        print(f"Failed to get answer: {answer}")
        return ""
    
# define a function to print out all file names in the knowledge base, using function from assistant_tools
def print_all_file_names(config_dir:str):
    """
    Print all file names in the knowledge base.

    Args:
        config_dir (str): The path of the config directory.
    """
    config_file_path = os.path.join(config_dir, util.config_file_name)

    # read doc dir from the config file
    doc_dir = util.read_configurations(config_file_path)['doc_dir']
    
    # read vector store id from the config file
    vector_store_id = util.read_configurations(config_file_path)['vector_store_id']
    file_name_list = assistant_tools.get_all_file_names(vector_store_id)

    # concantenate the doc dir to the file name
    file_name_list = [os.path.join(doc_dir, file_name) for file_name in file_name_list]

    print("The following documents are in the knowledge base:")
    for file_name in file_name_list:
        print(file_name)

# define a function to revise the content being edited in vim, return generated text. using function from assistant_tools
def revise_content(
        config_dir:str, 
        selected_text:str,
        text_at_top:str,
        text_at_bottom:str,
        user_request:str
        )->str:
    """
    Revise the content being edited in vim.

    """
    config_file_path = os.path.join(config_dir, util.config_file_name)

    # call the revise_content function from assistant_tools
    revised_text = assistant_tools.revise_content(
        selected_text=selected_text,
        text_before_selection=text_at_top,
        text_after_selection=text_at_bottom,
        user_request=user_request,
    )

    return revised_text
    
if __name__ == "__main__":
    # test update docs
    doc_dir = "/Users/sluo/Documents/Digital Assets/50-59 Work/51 blogs/51.02 tik-tok divestiment bill"
    config_dir = "/Users/sluo/development/vim-plugin/vimassist/scripts"

    status = update_docs(doc_dir, config_dir)
    if status == 0:
        print("Successfully updated the assistant with the documents.")
    else:
        print("Failed to update the assistant with the documents.")




