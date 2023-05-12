import json
import os
import time
from collections import deque
from pathlib import Path

import openai
from dotenv import load_dotenv, find_dotenv
from termcolor import colored

load_dotenv(find_dotenv())


def get_chat_response(system_prompt, user_prompt, model="gpt-3.5-turbo", temperature=0, max_tokens=2048, n=1,
                      patience=100,
                      sleep_time=0):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    while patience > 0:
        patience -= 1
        try:
            response = openai.ChatCompletion.create(model=model,
                                                    messages=messages,
                                                    temperature=temperature,
                                                    max_tokens=max_tokens,
                                                    n=n)
            if n == 1:
                prediction = response['choices'][0]['message']['content'].strip()
                if prediction != "" and prediction != None:
                    return prediction
            else:
                prediction = [choice['message']['content'].strip() for choice in response['choices']]
                if prediction[0] != "" and prediction[0] != None:
                    return prediction

        except Exception as e:
            print(e)
            if sleep_time > 0:
                time.sleep(sleep_time)
    return ""


# Find the Readme.md file from the code repo in the code_repo folder
def find_repo_folder(directory):
    # Find the name of the folder in the specified directory
    folder_name = None
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            folder_name = item
            break
    return os.path.join(directory, folder_name)


def find_readme(repo_folder):
    # Search for the README file within the found folder
    readme_path = os.path.join(repo_folder, "README.md")
    print(readme_path)
    if os.path.isfile(readme_path):
        print("README found in folder:", repo_folder)
        return readme_path
    else:
        print("README not found in folder:", repo_folder)
        return None


# summarize the README file
def summarize_readme(readme_path):
    if readme_path:
        system_prompt = """You are an expert developer and programmer. 
            Please infer the programming languages from the README.
            You are asked to summarize the README file of the code repository. 
            Please also mention the framework used in the code repository.
            """
        readme_content = open(readme_path, "r").read()
        user_prompt = f'Here is the README content: {readme_content}'
        return get_chat_response(system_prompt, user_prompt)


def bfs_folder_search(text_length_limit=4000, folder_path="./code_repo"):
    if not Path(folder_path).is_dir():
        return "Invalid directory path"

    root = Path(folder_path).resolve()
    file_structure = {str(root): {}}
    queue = deque([(root, file_structure[str(root)])])

    while queue:
        current_dir, parent_node = queue.popleft()
        try:
            for path in current_dir.iterdir():
                if path.is_dir():
                    if str(path.name) == ".git":
                        continue
                    parent_node[str(path.name)] = {"files": []}
                    queue.append((path, parent_node[str(path.name)]))
                else:
                    if "files" not in parent_node:
                        parent_node["files"] = []
                    parent_node["files"].append(str(path.name))

                # Check if we've exceeded the text length limit
                file_structure_text = json.dumps(file_structure)
                if len(file_structure_text) >= text_length_limit:
                    return file_structure_text

        except PermissionError:
            # This can happen in directories the user doesn't have permission to read.
            continue

    return json.dumps(file_structure)


def get_readme(code_repo_path="./code_repo"):
    repo_folder = find_repo_folder(code_repo_path)
    print(repo_folder)
    readme_path = find_readme(repo_folder)
    summary = summarize_readme(readme_path)
    print(colored(summary, "green"))
    return summary


def get_repo_structure(code_repo_path="./code_repo"):
    return bfs_folder_search(4000, code_repo_path)

def extract_function_name(input):
    system_prompt = """You are an expert developer and programmer. """
    user_prompt = """
        You will handle user questions about the code repository.
        Please extract the function name appeared in the question.
        Only response the function name without the parameters or any other words.

        Below are two examples:
        - Question: How to use the function extract_function_name?
        - Answer: extract_function_name

        - Question: How to use the function def supabase_vdb(query, knowledge_base):?
        - Answer: supabase_vdb 

        """ + f'Here is the user input: {input}'
    return get_chat_response(system_prompt, user_prompt)


if __name__ == "__main__":
    # Specify the path to the code_repo folder
    code_repo_path = "./code_repo"

    get_readme(code_repo_path)

    print(colored(bfs_folder_search(4000, code_repo_path), "yellow"))
