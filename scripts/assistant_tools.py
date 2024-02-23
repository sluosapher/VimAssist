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
    try:
        assistant = client.beta.assistants.create(
            instructions="""
                You are a research assistant with fabulous writing skills.

                You answer user's questions by searching from the attached documents, and organize the information into a well-written response. 
            """,
            name=assistant_name,
            tools= tools,
            model= model,
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
    # test the revsie_content function
    selected_text = ""
    text_before_selection = """
# Some highlights of my career experiences

## Director of Cyber Machine Learing and AI

* cyber machine learning strategy: I worked with Cyber's senior leadership and other stakeholders to identify and prioritize opportunities for applying machine learning to address cyber security challenges. I have identified four major opportunities of applying ML in cyber: 1) soley relying on rule-based detectoins; 2)cyber operations still involve many manual operations which can be automated; 3) the detection pipeline is not stable enough 4) need upskill training Cyber's associates with ML knowledge and skills. Then I made a strategy to address these opportunities, which includes a security service part, a engineering improvement part, and a training part. I also made a 2-year roadmap to implement the strategy. At last, I presented the strategy to Cyber's senior leadership and got their buy-in.

* Cyber GenAI initiatives: I poineered in the Cyber GenAI initiatives, and prepared several key use cases with parters within Cyber. We did PoC for these use cases and got some promising results. GenAI initiatives include text-to-sql translation, automated cyber intel anlysis, anomaly detection in crowdstrike logs. These use cases are critical to Cyber's operation and can save a lot of manual work. I also made a roadmap for these use cases.

* anomaly detection: I worked with Vendor (mixmode) to introuce their anomaly detection product to Cyber. I led the engineering, product, and architecture teams to integrate the product into Cyber's environment, and started the real-time anomaly detection in Cyber's environment. I also led the effort to build the in-house anomaly detection capability, and we have made some progress in this area.

## Founder of chatdocu.ai

Song Luo's experience with building ChatDocu.AI and ChatEssay.AI is characterized by hands-on involvement and transformative innovation. As the Founder and Developer from March 2023 to the present, Luo was responsible for transforming the concepts into fully operational products, beginning with architecture design through hands-on development, and deploying the products across both AWS and Azure platforms. ChatDocu.AI is an intelligent chatbot that answers questions without hallucination. ChatEssay.AI is an AI assistant designed to craft personalized college admission essays. These projects illustrate Luo's profound capability in leveraging advanced Generative AI technologies to address practical needs, displaying an impressive blend of technical acumen and innovative vision in AI application development.

## Director of big data innovation at Tencent

* Privacy computing product: I led the tencent security's big data team to develop a privacy computing product, called federated learning. This is the first privacy computing prodeuct in Tencent. This product played a key part in Tencent's privacy computing strategy. It not only supports Tencent's internal use cases, but also supports Tencent's external partners as one of Tencent Security's most innovative products.

* Using the federated learning product, we developed use cases for tencent's anti-fraud and advertising business. It has made a significant impact on Tencent's business.
"""
    selected_text = """
### What is the one thing you would want people to know about you?

I am a passionate and innovative leader in AI and machine learning, and I want to make people's life secure, efficient, and happy.
"""

    text_after_selection = """
### What is one of your proudest accomplishments from the past year?

I transformed the concepts of ChatDocu.AI and ChatEssay.AI from ideas to fully operational products that can be readily used by the public.

### What are you most passionate about in your current career path?

I am passionate about leveraging AI and machine learning to address practical needs, particularly in the areas of cyber security and education.

### What would your coworkers say about you?

My coworkers would say that I am a passionate technical leader with a strong vision and a lot of great ideas.

## My Future self

### What kind of roles do you see yourself in moving forward?

A technical leadership role in AI and machine learning, with a focus improve efficiency in people's work and life.

### What have you done recently to grow professionally?

I learned a lot on the journey of building ChatDocu.AI and ChatEssay.AI. From programming with LLM to deploying the products on AWS and Azure, and from understanding the business needs to designing the products, I have grown a lot professionally.
"""

    user_request = "can you enrich this part with more details?"

    revised_text = revise_content(selected_text, text_before_selection, text_after_selection, user_request)
    print(revised_text)
    
