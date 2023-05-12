# GPT-Code-Learner
Learn A Repo Interactively with GPT-4. Ask questions to let the GPT explain the code to you.

## Installation

1. Clone this repository and install the required packages:
```
git clone https://github.com/JinghaoZhao/GPT-Code-Learner.git
pip install -r requirements.txt
```
2. Create a `.env` file to put your API key:
```
OPENAI_API_KEY=sk-xxxxxx
```
3. clone the repo you want to learn into `code_repo` folder:
```
cd code_repo
git clone <repo_url>
```
4. Run the IoT-GPT:
```
python run.py
```
5. Open your web browser at http://127.0.0.1:7860 to ask any questions about your repo


## Knowledge Base
This feature is still under development.

GPT-Code-Learner supports using a knowledge base to answer repo-related questions. By default, it will use the source codes as the knowledge base. You can preload documents or provide URLs as background knowledge for the repo. More details can be found in [Knowledge Base](docs/KnowledgeBase.md).