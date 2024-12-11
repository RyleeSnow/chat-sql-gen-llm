# ChatSQLGenLLM
A chatbot to generate SQL code / Get the queried data based on LLM model

![Local Image](./interface.png)

&nbsp;

## Model Used:
**SQLCoder** Model from Huggingface. Details and Dowload: https://huggingface.co/defog/sqlcoder-7b-2

&nbsp;

## Interface Builder:
**Streamlit**. Details: https://streamlit.io/

&nbsp;

## Basic Information of System:
- Python 3.9
- Unbantu 20.4
- Cuda Version 11.4
- Basic Python Package: `streamlit`, `transformers`, `torch`, `sqlite3`, `pandas`

&nbsp;

## Contents of this repository
![GitHub Repo stars](https://img.shields.io/github/stars/RyleeSnow/ChatSQLGenLLM) Please kindly support if you think this repo is helpful! Thx!

### 1. locally_hosted_llm_directly_with_streamlit
Codes for you to direcly use Streamlit module to build a chatbot. Quick and Easy!

- Step 1: Adjust configurations in `config.json`
    - `model_path`: path of local LLM model.
    - `prompt_file`: path of prompt template markdown file. The template in this repo is based on SQLCoder model, if you want to use another model, you may need to change the template.
    - `metadata_file`: path of SQL database's metadata (table name, column names, and column types). The current metadata file in this repo is just a placeholder, you may need to change it to your own metadata.
    - `answer_mode`:
        - "code": the chatbot will answer you with the SQL query code.
        - "dataframe": the chat will answer you with the queried dataframe (connected database is required).
    - `local_db_path`: only use when you want it to answer with "dataframe" and have a local database, otherwise you should leave it as empty.

- Step 2: Use your browser and start to chat.
    - Run the following command in your terminal:
        ```bash
        streamlit run main.py --server.address 127.0.0.1 --server.port 6006
        ```
    - Open your brower: http://127.0.0.1:6006
        - Note: if you are using a server and want to open the browser locally, make sure you have the port forwarded. And of course, you can use other port instead of 6006.

