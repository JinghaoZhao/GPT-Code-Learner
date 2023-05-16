# GPT-Code-Learner
Learn A Repo Interactively with GPT. Ask questions to let the GPT explain the code to you.

![GPT-Code-Learner.jpg](docs%2FGPT-Code-Learner.jpg)

### Try it out in your browser
![GUI.jpg](docs%2FGUI.jpg)


## Local LLM Support (Experimental)
GPT-Code-Learner supports running the LLM models locally. In general, GPT-Code-Learner uses [LocalAI](https://github.com/go-skynet/LocalAI) for local private LLM and [Sentence Transformers](https://huggingface.co/sentence-transformers) for local embedding.

Please refer to [Local LLM](docs/LocalLLM.md) for more details.

<span style="color:red">Note: Due to the current capability of local LLM, the performance of GPT-Code-Learner is not as good as the online version. </span>

## Installation

1. Clone this repository and install the required packages:
```
git clone https://github.com/JinghaoZhao/GPT-Code-Learner.git
pip install -r requirements.txt
```
2. Create a `.env` file to put your API key:
```
OPENAI_API_KEY=sk-xxxxxx
LLM_TYPE="OpenAI"
```
If you want to run the whole program locally, please change the following line in the `.env` file:
```
LLM_TYPE="local"
```
3. clone the repo you want to learn into `code_repo` folder:
```
cd code_repo
git clone <repo_url>
```
4. Run the GPT-Code-Learner. If you use local LLM models, please run the local model before running the GPT-Code-Learner. Please refer to [Local LLM](docs/LocalLLM.md) for more details.
```
python run.py
```

5. Open your web browser at http://127.0.0.1:7860 to ask any questions about your repo


## Knowledge Base
GPT-Code-Learner generates vector database from the code repo as a knowledge base to answer repo-related questions. By default, it will use the source codes as the knowledge base. More details can be found in [Knowledge Base](docs/KnowledgeBase.md).

## Tool Planner
The core of the GPT-Code-Learner is the tool planner. It leverages available tools to process the input to provide contexts.

Currently, the tool planner supports the following tools:

- **Code_Searcher**: This tool searches keywords (e.g., specific functions or variables) extracted from user query in the code repository

- **Repo_Parser**: This tool performs a fuzzy search with vector database of the code repo. It provides contexts for questions about the general procedures in the repo.

More tools are under development. Feel free to contribute to this project!