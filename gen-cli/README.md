# RAG Cli using LlamaIndex with Amazon Bedrock
This project customizes [LlamaIndex RAG CLI](https://docs.llamaindex.ai/en/stable/getting_started/starter_tools/rag_cli/) for Amazon Bedrock. It uses [chroma](https://www.trychroma.com/) backed by local filesystem as the vector DB.
## AWS Credentials setup
The CLI uses credentials which are set using -
```shell
export AWS_PROFILE=<profile>

## or environment variables 
export AWS_REGION=<region>
export AWS_ACCESS_KEY_ID=<your_access_key_id>
export AWS_SECRET_ACCESS_KEY=<your_secret_access_key>
## or session key along with three above for temp credentials
# export AWS_SESSION_TOKEN=your_session_token

```
## Customized embedding and query models
The default version uses following parameters. Ensure that you have access to models defined below along with API access to call Amazon Bedrock API - 
<li>Region - us-east-1 </li>
<li>Embedding Model - amazon.titan-embed-image-v1 </li>
<li>LLM - anthropic.claude-3-sonnet-20240229-v1:0 </li>


To customize set following environment variables - 
```shell
export AWS_REGION=<region>
export EMBEDDING_MODEL=<model_id>
export LLM=<model_id>
```
## Build and run
### Python installation
The implementation requires Python 3.10 or higher. Following are the installation instructions for Cloud9 on Amazon Linux.
```shell
### Python installation
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
cat << 'EOT' >> ~/.bashrc
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
EOT
source ~/.bashrc
sudo yum -y update
sudo yum -y install bzip2-devel
sudo yum -y install xz-devel

## Install python
pyenv install 3.10.10
pyenv global 3.10.10
```
### Poetry
Clone the repository and go to `ml-experiments/gen-cli`
```shell
cd ml-experiments/gen-cli
poetry install
```
```shell
## Prints help
./.venv/bin/python gen_cli/main.py rag -h
```
```shell
### Ask questions from a file using REPL interface
./.venv/bin/python gen_cli/main.py rag -f <local-file-path> -c
./.venv/bin/python gen_cli/main.py rag -f /Users/<home>/Documents/Databricks-docs/The-Delta-Lake-Series-Lakehouse-012921.pdf -c
```
```shell

```
### Without Poetry
```shell
cd ml-experiments/gen-cli
pip install -r requirements.txt 
```
```shell
## Print helps
python gen_cli/main.py rag -h
```
