import os
import time
from openai import OpenAI
import utilities as util

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
tools = [ 
    {"type": "code_interpreter"},
    {"type": "file_search"}
]
model = "gpt-4-turbo-preview"
vector_store_name = "vimassist_vector_store" # name for the vector store used by vimassist agent

def create_vector_store()->str:
    try:
        vector_store = client.beta.vector_stores.create(
            name=vector_store_name
        )
    except Exception as e:
        print(e)
        return None
    return vector_store.id

def update_vector_store_files(vector_store_id:str, file_paths: list[str])->int:
    """
    Add a list of file objects to the vector store.

    Args:
        vector_store_id (str): The ID of the vector store to which the files will be added.
        file_paths (list[str]): A list of file paths to be added to the vector store.

    Returns:
        int: 0 if successful, -1 if failed.
    """
    # delete current files in the vector store
    try:
        vector_store_files = client.beta.vector_stores.files.list(
            vector_store_id = vector_store_id
        )
    except Exception as e:
        print(e)
        return -1
    
    old_file_ids = []
    for file in vector_store_files.data:
        old_file_ids.append(file.id)

    print(f"To be deleted file ids: {old_file_ids}")

    try:
        # remove the old files from the vector store and delete them
        for file_id in old_file_ids:
            client.beta.vector_stores.files.delete(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
            client.files.delete(file_id)
    except Exception as e:
        print(e)
        return -1
    
    # # Ready the files for upload to OpenAI 
    # file_streams = [open(path, "rb") for path in file_paths]
    
    # # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # # and poll the status of the file batch for completion.
    # file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    #     vector_store_id=vector_store_id, files=file_streams
    # )

    # # print the status of the file batch every 0.1 seconds
    # while file_batch.status != "completed":
    #     print(file_batch.status)
    #     print(file_batch.file_counts)
    #     time.sleep(0.1)

    # upload files to openai
    new_file_ids = create_file_objects(file_paths)
    if not new_file_ids:
        return -1

    # add the new files to the vector store
    try:
        for file_id in new_file_ids:
            client.beta.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
    except Exception as e:
        print(e)
        return -1

    print(f"Added {len(new_file_ids)} files to the vector store.")

    # list files in the vector store
    try:
        vector_store_files = client.beta.vector_stores.files.list(
            vector_store_id = vector_store_id
        )
    except Exception as e:
        print(e)
        return -1
    
    new_file_ids = []
    for file in vector_store_files.data:
        new_file_ids.append(file.id)

    print(f"New file ids: {new_file_ids}")

    return 0


def retrieve_vector_store(vector_store_id:str)->object:
    try:
        vector_store = client.beta.vector_stores.retrieve(
            vector_store_id = vector_store_id
        )

        # check if the name of the vector store is the same as the expected name
        if vector_store.name != vector_store_name:
            print("The vector store name is not the expected name.")
            return None
        
    except Exception as e:
        print(e)
        return None
    return vector_store

# define a function to create a new assistant, return the assistant id
def create_assistant(assistant_name:str, vector_store_id:str)->str:
    try:
        assistant = client.beta.assistants.create(
            instructions="""
                You are a research assistant with fabulous writing skills.

                You answer user's questions by searching from the attached documents, and organize the information into a well-written response. 
            """,
            name=assistant_name,
            model= model,
            tools= tools,
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
        )
    except Exception as e:
        print(e)
        return None

    return assistant.id

# define a function to retrieve the assistant, return the assistant object
def retrieve_assistant(assistant_id:str)->object:
    try:
        assistant = client.beta.assistants.retrieve(
            assistant_id = assistant_id
        )
    except Exception as e:
        print(e)
        return None
    return assistant


# define a function to create a file object in openai, return a list of file IDs
def create_file_objects(file_list: list[str])->list[str]: # TODO: delete this function once the new function is implemented
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
    try:
        assistant = client.beta.assistants.retrieve(
            assistant_id = assistant_id
        )
    except Exception as e:
        print(e)
        return -1

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

# delete a thread object in openai.
def delete_thread(thread_id:str):
    client.beta.threads.delete(thread_id)

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


# define a function to revise the content based on user's request
def revise_content(
        selected_text:str, 
        text_before_selection:str,
        text_after_selection:str,
        user_request:str
)->str:
    """
    Revise the content based on user's request.

    Args:
        selected_text (str): The text selected by the user. It can be empty, means no text is selected.
        text_before_selection (str): The text before the selected text in the article.
        text_after_selection (str): The text after the selected text in the article.
        user_request (str): The user's request.

    Returns:
        str: The revised content.
    """

    # check if the user request is empty
    if user_request == "":
        print("User request is empty.")
        return ""
    
    # check if the selected text is empty
    if selected_text == "":
        user_selectin = True

    # Prepare the system prompt for openai chat completion
    system_msg = f"""
    You are a text content editor with great logic and writing skills. You are revising the content based on the user's request.
    Instructions:
    * If the selected text is not empty, you only rewrite the selected text. Otherwise, you are adding new content based on the user's request.
    * Write concise and clear sentences to fulfill the user's request. 
    * Make your writing logically consistent with the context, by consdering the text before and after the selected text. 
    * Make your writing following the original language style, and keep the tone consistent.
    * Only return the revised text, do not include your own comments or explanations.
    """

    user_msg = f"""
    The text before the selected text:
    {text_before_selection}

    The selected text by user:
    {selected_text}

    The text after the selected text:
    {text_after_selection}

    User's request is:
    {user_request}

    Your revision is:
    """

    # combine the system message and user message
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]

    # call openai's chat completion API
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
    except Exception as e:
        print(e)
        return ""
    
    # get the revised text from the response
    revised_text = response.choices[0].message.content

    return revised_text

if __name__ == "__main__":
    # create a new vector store
    # vector_store_id = create_vector_store()
    vector_store_id = "vs_PFWnzlYL6BRNJCMMj7V3IKde"

    print(f"Vector store ID: {vector_store_id}")

    # update the vector store with the files
    # file_paths = [
    #     "/Users/sluo/Documents/Digital Assets/50-59 Work/51 blogs/51.02 tik-tok divestiment bill/House Passes Bill to Force TikTok Sale From Chinese Owner or Ban the App - The New York Times.pdf",
    #     "/Users/sluo/Documents/Digital Assets/50-59 Work/51 blogs/51.02 tik-tok divestiment bill/The TikTok bill passes.pdf",
    # ]
    file_paths = [
        "/Users/sluo/Documents/Digital Assets/50-59 Work/51 blogs/51.03 human-centered-ML-in-Cyber/human-centered-machine-learning-in-cyber-blogpost.md",
    ]

    status = update_vector_store_files(vector_store_id, file_paths)
    print(f"Update vector store status: {status}")

