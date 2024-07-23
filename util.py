import os
from dotenv import load_dotenv, find_dotenv
from termcolor import colored
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import OpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv(find_dotenv())


def get_chat_response(system_prompt, user_prompt):
    # By default, use the local LLM
    llm_type = os.environ.get('LLM_TYPE', "local")
    if llm_type == "local":
        return get_local_llm_response(system_prompt, user_prompt)
    else:
        return get_openai_response(system_prompt, user_prompt)


def get_local_llm_response(system_prompt, user_prompt, model="ggml-gpt4all-j", temperature=0.9):
    base_path = os.environ.get('OPENAI_API_BASE', 'http://localhost:8080/v1')
    model_name = os.environ.get('MODEL_NAME', model)
    llm = OpenAI(temperature=temperature, openai_api_base=base_path, model_name=model_name, openai_api_key="null")
    text = system_prompt + "\n\n" + user_prompt + "\n\n"
    response = llm(text)
    print(response)
    return response


def get_openai_response(system_prompt, user_prompt, model="gpt-3.5-turbo", temperature=0):
    chat = ChatOpenAI(model_name=model, temperature=temperature)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    response = chat(messages)
    print(response)
    return response.content
