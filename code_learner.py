import gradio as gr
import json
import requests
import os
from termcolor import colored
from repo_parser import clone_repo, generate_or_load_knowledge_from_repo
import tool_planner

llm_type = os.environ.get('LLM_TYPE', "local")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "null")
if llm_type == "local":
    API_URL = "http://localhost:8080/v1/chat/completions"
    model = "ggml-gpt4all-j"
else:
    API_URL = "https://api.openai.com/v1/chat/completions"
    model = "gpt-3.5-turbo"

code_repo_path = "./code_repo"

init_system_prompt = """Now you are an expert programmer and teacher of a code repository. 
    You will be asked to explain the code for a specific task in the repo.
    You will be provided with some related code snippets or documents related to the question.
    Please think the explanation step-by-step.
    Please answer the questions based on your knowledge, and you can also refer to the provided related code snippets.
    The README.md file and the repo structure are also available for your reference.
    If you need any details clarified, please ask questions until all issues are clarified. \n\n
"""
system_prompt = init_system_prompt


def generate_response(system_msg, inputs, top_p, temperature, chat_counter, chatbot=[], history=[]):
    orig_inputs = inputs

    # Inputs are pre-processed with extra tools
    inputs = tool_planner.user_input_handler(inputs)

    print("Inputs Length: ", len(inputs))
    # Add checker for the input length to fitin the GPT model window size
    if llm_type == "local":
        token_limit = 2000
    else:
        token_limit = 8000
    if len(inputs) > token_limit:
        inputs = inputs[:token_limit]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    if system_msg.strip() == '':
        initial_message = [{"role": "user", "content": f"{inputs}"}]
        multi_turn_message = []
    else:
        initial_message = [{"role": "system", "content": system_msg},
                           {"role": "user", "content": f"{inputs}"}]
        multi_turn_message = [{"role": "system", "content": init_system_prompt}]

    if chat_counter == 0:
        payload = {
            "model": model,
            "messages": initial_message,
            "temperature": temperature,
            "top_p": top_p,
            "n": 1,
            "stream": True,
            "presence_penalty": 0,
            "frequency_penalty": 0,
        }
    else:
        messages = multi_turn_message
        for data in chatbot:
            user = {"role": "user", "content": data[0]}
            assistant = {"role": "assistant", "content": data[1]}
            messages.extend([user, assistant])
        temp = {"role": "user", "content": inputs}
        messages.append(temp)

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "n": 1,
            "stream": True,
            "presence_penalty": 0,
            "frequency_penalty": 0, }

    chat_counter += 1
    history.append(orig_inputs)
    print(colored("Orig input from the user: ", "green"), colored(orig_inputs, "green"))
    print(colored("Input with tools: ", "blue"), colored(inputs, "blue"))
    response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    token_counter = 0
    partial_words = ""

    response_complete = False

    counter = 0
    for chunk in response.iter_lines():
        if counter == 0:
            counter += 1
            continue

        if response_complete:
            print(colored("Response: ", "yellow"), colored(partial_words, "yellow"))

        if chunk.decode():
            chunk = chunk.decode()
            if chunk.startswith("error:"):
                print(colored("Chunk: ", "red"), colored(chunk, "red"))

            # Check if the chatbot is done generating the response
            try:
                if len(chunk) > 12 and "finish_reason" in json.loads(chunk[6:])['choices'][0]:
                    response_complete = json.loads(chunk[6:])['choices'][0].get("finish_reason", None) == "stop"
            except:
                print("Error in response_complete check")
                pass

            try:
                if len(chunk) > 12 and "content" in json.loads(chunk[6:])['choices'][0]['delta']:
                    partial_words = partial_words + json.loads(chunk[6:])['choices'][0]["delta"]["content"]
                    if token_counter == 0:
                        history.append(" " + partial_words)
                    else:
                        history[-1] = partial_words
                    chat = [(history[i], history[i + 1]) for i in range(0, len(history) - 1, 2)]
                    token_counter += 1
                    yield chat, history, chat_counter, response
            except:
                print("Error in partial_words check")
                pass


def reset_textbox():
    return gr.update(value='')


def set_visible_false():
    return gr.update(visible=False)


def set_visible_true():
    return gr.update(visible=True)


def analyze_repo(repo_url, progress=gr.Progress()):
    progress(0, desc="Starting")
    repo_information = clone_repo(repo_url, progress)

    progress(0.6, desc="Building Knowledge Base")
    generate_or_load_knowledge_from_repo()

    if repo_information is not None:
        return init_system_prompt + repo_information, "Analysis completed"
    else:
        return init_system_prompt, "Analysis failed"

def main():
    title = """<h1 align="center">GPT-Code-Learner</h1>"""

    system_msg_info = """A conversation could begin with a system message to gently instruct the assistant."""

    theme = gr.themes.Soft(text_size=gr.themes.sizes.text_md)

    with gr.Blocks(
            css="""#col_container { margin-left: auto; margin-right: auto;} #chatbot {height: 520px; overflow: auto;}""",
            theme=theme,
            title="GPT-Code-Learner",
    ) as demo:
        gr.HTML(title)

        with gr.Column(elem_id="col_container"):
            with gr.Accordion(label="System message:", open=False):
                system_msg = gr.Textbox(
                    label="Instruct the AI Assistant to set its beaviour",
                    info=system_msg_info,
                    value=system_prompt
                )
                accordion_msg = gr.HTML(
                    value="Refresh the app to reset system message",
                    visible=False
                )
            # Add text box for the repo link with submit button
            with gr.Row():
                with gr.Column(scale=6):
                    repo_url = gr.Textbox(
                        placeholder="Repo Link",
                        lines=1,
                        label="Repo Link"
                    )
                with gr.Column(scale=2):
                    repo_link_btn = gr.Button("Analyze Code Repo")
                with gr.Column(scale=2):
                    analyze_progress = gr.Textbox(label="Status")

            repo_link_btn.click(analyze_repo, [repo_url], [system_msg, analyze_progress])

            with gr.Row():
                with gr.Column(scale=10):
                    chatbot = gr.Chatbot(
                        label='GPT-Code-Learner',
                        elem_id="chatbot"
                    )

            state = gr.State([])
            with gr.Row():
                with gr.Column(scale=8):
                    inputs = gr.Textbox(
                        placeholder="What questions do you have for the repo?",
                        lines=1,
                        label="Type an input and press Enter"
                    )
                with gr.Column(scale=2):
                    b1 = gr.Button()

            with gr.Accordion(label="Examples", open=True):
                gr.Examples(
                    examples=[
                        ["What is the usage of this repo?"],
                        ["Which function launches the application in the repo?"],
                    ],
                    inputs=inputs)

            with gr.Accordion("Parameters", open=False):
                top_p = gr.Slider(minimum=-0, maximum=1.0, value=0.5, step=0.05, interactive=True,
                                  label="Top-p (nucleus sampling)", )
                temperature = gr.Slider(minimum=-0, maximum=5.0, value=0.5, step=0.1, interactive=True,
                                        label="Temperature", )
                chat_counter = gr.Number(value=0, visible=True, precision=0)

        inputs.submit(generate_response, [system_msg, inputs, top_p, temperature, chat_counter, chatbot, state],
                      [chatbot, state, chat_counter], )
        b1.click(generate_response, [system_msg, inputs, top_p, temperature, chat_counter, chatbot, state],
                 [chatbot, state, chat_counter], )

        inputs.submit(set_visible_false, [], [system_msg])
        b1.click(set_visible_false, [], [system_msg])
        inputs.submit(set_visible_true, [], [accordion_msg])
        b1.click(set_visible_true, [], [accordion_msg])

        b1.click(reset_textbox, [], [inputs])
        inputs.submit(reset_textbox, [], [inputs])

    demo.queue(max_size=99).launch(debug=True)


if __name__ == "__main__":
    main()
