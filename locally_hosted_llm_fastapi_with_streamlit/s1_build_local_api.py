import json

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Read config from json file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

app = FastAPI()

# Load the model and tokenizer once at startup
model_path = config['model_path']  # change this to the path of the model

# NOTE! If you want to use other model, you may need to change the way of loading the model and the tokenizer.
model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True, torch_dtype=torch.float16,
                                             device_map='auto', use_cache=True)  # Load the model
tokenizer = AutoTokenizer.from_pretrained(model_path)  # Load the tokenizer.
pipe = pipeline('text-generation', model=model, tokenizer=tokenizer, max_new_tokens=3000, do_sample=False,
                return_full_text=False, num_beams=5)  # Initialize the pipeline


class QueryRequest(BaseModel):
    """
    Request body for the generate endpoint.
    """

    # The question to generate a prompt for.
    question: str
    # Few-shots examples.
    examples: str
    # The path to the prompt file. Prompt file is a markdown file that contains the prompt template.
    prompt_file: str
    # The path to the metadata file. Metadata file is a SQL file that contains the table metadata (table name, column names, and column types).
    metadata_file: str


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
    return prompt.format(user_question=question, examples=examples, table_metadata_string=table_metadata_string)


@app.post('/generate')
async def generate(request: QueryRequest):
    """
    Generate a query from the prompt and return the query.
    """
    try:
        # Generate the prompt
        prompt = generate_prompt(question=request.question, examples=request.examples, prompt_file=request.prompt_file,
                                 metadata_file=request.metadata_file)
        # Generate the query
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
        return {'query': sqlcode}
    except Exception as e:
        # If an error occurs, raise an HTTP exception with a 500 status code and the error message
        raise HTTPException(status_code=500, detail=str(e))
