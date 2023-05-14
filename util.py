import os
import time

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
