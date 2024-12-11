import json
import random
import sqlite3
import time

import pandas as pd
import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Read config from json file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)


def random_greetings():
    """Generate a random greeting message"""

    response = random.choice([
        'Hello there! This is Catbot. How can I assist you today?',
        'Hi! Is there anything I can help you with?',
        'This is Catbot. Do you need any help?',
    ])
    for word in response.split():
        yield word + ' '
        time.sleep(0.05)


def generate_prompt(question, examples, prompt_file, metadata_file):
    """
    Generate a prompt for the LLM model.
    Args:
        question (str): The question to generate a prompt for.
        examples (str): The few-shots examples to generate a prompt for.
        prompt_file (str): The path to the prompt file. Prompt file is a markdown file that contains the prompt template.
        metadata_file (str): The path to the metadata file. Metadata file is a SQL file that contains the table metadata (table name, column names, and column types).
    Returns:
        str: The generated prompt.
    """

    # Read the prompt template.
    # NOTE! This template is based on SQLCoder model, if you want to use other model, you may need to change the template.
    with open(prompt_file, 'r') as f:
        prompt = f.read()

    # Read the metadata file. This file contains the SQL database's metadata (table name, column names, and column types).
    # NOTE! This current content is just a placeholder, you may need to change it to your own metadata.
    with open(metadata_file, 'r') as f:
        table_metadata_string = f.read()

    # Format the prompt with the question and table metadata
    return prompt.format(user_question=question,
                         examples=examples,
                         table_metadata_string=table_metadata_string)


# Build the UI
with st.sidebar:
    # Build the few-shots examples input box. Here you can input your few-shots examples which may help you improve the model's performance.
    # If you don't have any few-shots examples, you can leave it empty.
    with st.form(key='fs_examples_form'):
        fewshots_examples_text_input = st.text_area(
            'Few-shots Examples 👇',
            height=680,
            placeholder='Enter your few-shots examples here',
            key='fewshots_examples_text_input')
        submit_button = st.form_submit_button('Submit')
        if submit_button:
            st.write('submitted')
    st.write('')

    # Build the max length slider. This is the maximum length of the generated SQL query.
    max_length = st.slider('max_length', 128, 4096, 1024, step=128)

# Here is a file to store the historic few-shots examples. Every time you submit the few-shots examples, it will be stored in this file.
# If you don't want to use few-shots examples, you should leave it empty.
with open('fewshots_examples.txt', 'r') as f:
    historic_fs_examples = [line for line in f.readlines() if line.strip()]
    if len(historic_fs_examples) == 0:
        last_time_fs_examples = ''
    else:
        last_time_fs_examples = historic_fs_examples[-1].strip().split(
            ',')[1].strip()

if len(fewshots_examples_text_input) > 0:
    # If the user inputs content in the few-shots examples input box.

    if fewshots_examples_text_input != last_time_fs_examples:
        # If the user inputs content is different from the last time saved, save the new content and the time to the historic file.
        with open('fewshots_examples.txt', 'a+') as f:
            f.write(
                time.strftime('%Y-%m-%d %H:%M:%S') + ', ' +
                fewshots_examples_text_input + '\n')

    # Use the new few-shots examples as the current few-shots examples.
    fs_examples = fewshots_examples_text_input
else:
    # If the user doesn't input content in the few-shots examples input box, use the last time saved few-shots examples as the current few-shots examples.
    fs_examples = last_time_fs_examples

# Title and caption
st.title('🐱 ChatSQLGenLLM')
st.caption(
    '💭 Help you generate SQL queries / Get the queried data based on your questions'
)
st.caption('--------------------------------')


# Load the model and the tokenizer, and initialize the pipeline.
# Cache the model to improve the performance.
@st.cache_resource
def get_model():
    model_path = config['model_path']  # change this to the path of the model

    # NOTE! If you want to use other model, you may need to change the way of loading the model and the tokenizer.
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map='auto',
        use_cache=True)  # Load the model
    tokenizer = AutoTokenizer.from_pretrained(
        model_path)  # Load the tokenizer.
    pipe = pipeline('text-generation',
                    model=model,
                    tokenizer=tokenizer,
                    max_new_tokens=max_length,
                    do_sample=False,
                    return_full_text=False,
                    num_beams=5)  # Initialize the pipeline
    return tokenizer, pipe


tokenizer, pipe = get_model()

# If the session_state does not have 'messages', create a list with default messages
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if not st.session_state.messages:
    response = ''.join(
        random_greetings())  # Generate a random greeting message
    st.session_state.messages.append({
        'role': 'assistant',
        'content': response
    })

# Iterate through all messages in the session_state and display them in the chat interface
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.write(msg['content'])

# If the user inputs content in the chat input box, execute the following operations
if user_input := st.chat_input():
    # Display the user's input in the chat interface
    st.chat_message('user').write(user_input)

    messages = [{'role': 'user', 'content': user_input}]

    prompt = generate_prompt(question=user_input,
                             examples=fs_examples,
                             prompt_file=config['prompt_file'],
                             metadata_file=config['metadata_file'])
    eos_token_id = tokenizer.eos_token_id

    # Extract the query from the generated text
    # NOTE! The current code is based on SQLCoder model, if you want to use other model, you may need to change the way of extracting the query from the generated text.
    outputs = (pipe(prompt,
                    num_return_sequences=1,
                    eos_token_id=eos_token_id,
                    pad_token_id=eos_token_id)[0]['generated_text'].split(
                        ';')[0].split('```')[0].strip() + ';'
               )
    sqlcode = outputs.split(';')[0].strip().split(':')[-1].strip()

    if config['answer_mode'] == 'code':
        # If the answer mode is 'code', display the generated SQL code in the chat interface
        st.chat_message('assistant').write(sqlcode)
    elif config['answer_mode'] == 'dataframe':
        # If the answer mode is 'dataframe', display the queried data in the chat interface

        # ======= Query the database START =======
        # NOTE! Feel free to change the way of querying the database.
        conn = sqlite3.connect(config['local_db_path'])
        cursor = conn.cursor()
        cursor.execute(sqlcode)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        df = pd.DataFrame(rows, columns=column_names)
        df = df.head(5)  # NOTE! For better visualization, only show the first 5 rows.
        # ======= Query the database END =======

        # Display the queried data in the chat interface
        st.chat_message('assistant').write(df)

    # Add the user's input and the model's output to the messages list in the session_state
    st.session_state.messages.append({'role': 'user', 'content': user_input})
    st.session_state.messages.append({'role': 'assistant', 'content': sqlcode})
