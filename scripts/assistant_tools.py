import os
import time
from openai import OpenAI
import utilities as util

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
tools = [ 
    {"type": "code_interpreter"},
    {"type": "retrieval"}
]
model = "gpt-4-turbo-preview"


# define a function to create a new assistant, return the assistant id
def create_assistant(assistant_name:str)->str:
    assistant = client.beta.assistants.create(
        instructions="""
            You are a research assistant. 
            You answer user's questions using the knowledge from attached documents.
            Do not answer questions that are not relevant to attached documents.
            Do not use context from conversation history to generate answers.
        """,
        name=assistant_name,
        tools= tools,
        model= model,
    )

    return assistant.id

# define a function to create a file object in openai, return a list of file IDs
def create_file_objects(file_list: list[str])->list[str]:
    """
    Create file objects for each file in the given file list.

    Args:
        file_list (list[str]): A list of file paths.

    Returns:
        list[str]: A list of file IDs corresponding to the created file objects.
    """
    
    file_id_list = []
    for file_path in file_list:
        try:
            # print(f"Creating file object for {file_path}.")
            file = client.files.create(
                file=open(file_path, "rb"),
                purpose="assistants"
            )
        except Exception as e:
            print(f"Failed to create file object for {file_path}.{e}")
            # continue to the next file
            continue
        file_id_list.append(file.id)
    return file_id_list

# define a function to update files of the assistant, return status
def update_files_of_assistant(assistant_id:str, file_id_list: list[str])->int:
    """
    Add a list of file objects to the assistant.

    Args:
        assistant_id (str): The ID of the assistant to which the files will be added.
        file_id_list (list[str]): A list of file IDs to be added to the assistant.

    Returns:
        int: 0 if successful, -1 if failed.
    """
    # get the assistant
    assistant = client.beta.assistants.retrieve(
        assistant_id = assistant_id
    )

    # get the current file list
    old_file_ids = assistant.file_ids

    # update the assistant with the new file list
    try:
        assistant = client.beta.assistants.update(
            assistant_id = assistant_id,
            file_ids = file_id_list
        )
    except Exception as e:
        print(e)
        return -1
    
    # delete the old files from openai
    for file_id in old_file_ids:
        try:
            # print(f"Deleting file {file_id}")
            client.files.delete(file_id)
        except Exception as e:
            print(e)
            return -1
        
    return 0

# define a function to get all file names in the assistant, return a list of file names
def get_all_file_names(assistant_id:str)->list[str]:
    """
    Get all file names in the assistant.

    Args:
        assistant_id (str): The ID of the assistant.

    Returns:
        list[str]: A list of file names.
    """
    # get the assistant
    assistant = client.beta.assistants.retrieve(
        assistant_id = assistant_id
    )

    # get the current file list
    file_id_list = assistant.file_ids

    # get the file names
    file_names = []
    for file_id in file_id_list:
        file = client.files.retrieve(file_id)
        file_names.append(file.filename)
    return file_names

# define a function to create a thread object in openai.
def create_thread()->str:
    thread = client.beta.threads.create()
    return thread.id

# define a function to send a message to the assistant, return status and answer
def sendMessage(assistantId, threadId, message:str)->tuple[int, str]:
    # check if the assistant is set
    if assistantId is None:
        print
        return -1, "Assistant is not set"
    
    # check if the thread is set
    if threadId is None:
        return -1, "Thread is not set"
    

    # add a new message to the thread
    try:
        message = client.beta.threads.messages.create(
            thread_id=threadId,
            role = "user",
            content=message
        )
    except Exception as e:
        print(f"Error adding message to thread: {e}")
        return -1, f"Error adding message to thread: {e}"
    
    # run the assistant
    try:
        run = client.beta.threads.runs.create(
            thread_id=threadId,
            assistant_id=assistantId,
            instructions="Give concise answers to the user's questions."
        )
    except Exception as e:
        print(f"Error running assistant: {e}")
        return -1, f"Error running assistant: {e}"
    
    # check the status of the run with an loop
    while run.status != "completed":
        # wait for 0.05 seconds before checking the status again
        time.sleep(0.05)

        try:
            run = client.beta.threads.runs.retrieve(
                thread_id=threadId,
                run_id=run.id
            )
        except Exception as e:
            print(f"Error retrieving run: {e}")
            return -1, f"Error retrieving run: {e}"
    
    # get the messages from the thread
    try:
        messages = client.beta.threads.messages.list(
            thread_id=threadId
        )
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return -1, f"Error retrieving messages: {e}"
    
    # get the text value from the most recent message

    # TODO: need to consider getting other types of messages, such as images
    message = messages.data[0]
    # print(f"Message: {message}")

    # TODO: process annotations

    answer = message.content[0].text.value
    # print(f"Answer: {answer}")

    return 0, answer


if __name__ == "__main__":
    config_file_path = "/Users/sluo/development/vim-plugin/chatdocu/scripts/config.json"

    # read assistant id and thread id from the config file, using function from utilities
    assistant_id = util.read_configurations(config_file_path)['assistant_id']
    thread_id = util.read_configurations(config_file_path)['thread_id']

    # user message
    message = "What is the capital of France?"

    # send the message to the assistant
    status, answer = sendMessage(assistant_id, thread_id, message)

    # print the answer to the console if successful
    if status == 0:
        print(answer)
    else:
        print(f"Failed to get answer: {answer}")
    
