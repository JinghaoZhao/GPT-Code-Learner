# Using Local LLM Models

GPT-Code-Learner uses [LocalAI](https://github.com/go-skynet/LocalAI) to run the LLM models locally. 

## Installation
Here are general steps for installation on Mac. Please refer to [LocalAI](https://github.com/go-skynet/LocalAI) for more details.

```shell
# install build dependencies
brew install cmake
brew install go

# clone the repo
git clone https://github.com/go-skynet/LocalAI.git

cd LocalAI

# build the binary
make build

# Download gpt4all-j to models/
wget https://gpt4all.io/models/ggml-gpt4all-j.bin -O models/ggml-gpt4all-j

# Use a template from the examples
cp -rf prompt-templates/ggml-gpt4all-j.tmpl models/

# Run LocalAI
./local-ai --models-path ./models/ --debug

# Now API is accessible at localhost:8080
curl http://localhost:8080/v1/models

curl http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d '{
     "model": "ggml-gpt4all-j",
     "messages": [{"role": "user", "content": "How are you?"}],
     "temperature": 0.9 
   }'
```

## Running GPT-Code-Learner with Local LLM Models
Before running GPT-Code-Learner, please make sure the LocalAI is running at localhost:8080.

```shell
./local-ai --models-path ./models/ --debug
```

Then, change the following line in the `.env` file:
```
LLM_TYPE="local"
```

Finally, run the GPT-Code-Learner:
```
python run.py
```

## Known Issues
- The accuracy of the local LLM models is not as good as the online version. We are still working on improving the performance of the local LLM models.
- Also, the first message of the conversation are usually blocked in the local LLM models. Restarting the GPT-Code-Learner may solve this issue.