import json
import random
import sqlite3
import time

import pandas as pd
import requests
import streamlit as st
from fastapi import FastAPI

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

app = FastAPI()


@app.get('/fetch_data')
def fetch_data(input_question, fewshots_examples):
    """
    Fetch data from the PHP API.
    """

    try:
        api_address = config['api_address']
        response = requests.post(
            api_address, json={
                'question': input_question,
                'examples': fewshots_examples,
                'prompt_file': config['prompt_file'],
                'metadata_file': config['metadata_file']
            })

        if response.status_code == 200:
            return response.json()['query']
        else:
            # Improved error message with response content
            raise RuntimeError(f'HTTP error {response.status_code}: {response.text}')
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'Error fetching data from the API: {str(e)}')
    except ValueError as e:
        raise RuntimeError(f'Error decoding JSON: {str(e)}')


def random_greetings():
    """Generate a random greeting."""

    response = random.choice([
        'Hello there! This is Catbot. How can I assist you today?', 'Hi! Is there anything I can help you with?',
        'This is Catbot. Do you need any help?',
    ])
    for word in response.split():
        yield word + ' '
        time.sleep(0.05)


# Build the UI
with st.sidebar:
    # Build the few-shots examples input box. Here you can input your few-shots examples which may help you improve the model's performance.
    # If you don't have any few-shots examples, you can leave it empty.
    with st.form(key='fs_examples_form'):
        fewshots_examples_text_input = st.text_area('Few-shots Examples 👇', height=680,
                                                    placeholder='Enter your few-shots examples here',
                                                    key='fewshots_examples_text_input')
        submit_button = st.form_submit_button('Submit')
        if submit_button:
            st.write('submitted')
    st.write('')

# Here is a file to store the historic few-shots examples. Every time you submit the few-shots examples, it will be stored in this file.
# If you don't want to use few-shots examples, you should leave it empty.
with open('fewshots_examples.txt', 'r') as f:
    historic_fs_examples = [line for line in f.readlines() if line.strip()]
    if len(historic_fs_examples) == 0:
        last_time_fs_examples = ''
    else:
        last_time_fs_examples = historic_fs_examples[-1].strip().split(',')[1].strip()

if len(fewshots_examples_text_input) > 0:
    # If the user inputs content in the few-shots examples input box.

    if fewshots_examples_text_input != last_time_fs_examples:
        # If the user inputs content is different from the last time saved, save the new content and the time to the historic file.
        with open('fewshots_examples.txt', 'a+') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S') + ', ' + fewshots_examples_text_input + '\n')

    # Use the new few-shots examples as the current few-shots examples.
    fs_examples = fewshots_examples_text_input
else:
    # If the user doesn't input content in the few-shots examples input box, use the last time saved few-shots examples as the current few-shots examples.
    fs_examples = last_time_fs_examples

# Title and caption
st.title('🐱 ChatSQLGenLLM')
st.caption('💭 Help you generate SQL queries / Get the queried data based on your questions')
st.caption('--------------------------------')

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

# if the user inputs content in the chat input box, execute the following operations
if user_input := st.chat_input():
    # display the user's input in the chat interface
    st.chat_message('user').write(user_input)

    # fetch the data from the PHP API
    sqlcode = fetch_data(input_question=user_input, fewshots_examples=fs_examples)

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
