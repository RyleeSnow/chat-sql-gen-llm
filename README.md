# ChatSQLGenLLM - Intelligent SQL Query Generation System

> **Language**: [English](README.md) | [中文](README.zh.md)

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![FastAPI](https://img.shields.io/badge/fastapi-latest-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An AI-powered SQL query generation chatbot that converts natural language questions into SQL queries and executes them to retrieve data from databases. Built with advanced Large Language Models (LLM) and modern web technologies.

![Local Image](./interface.png)

<br>

## ✨ Features

- 🤖 **Intelligent Query Generation**: Convert natural language to SQL using state-of-the-art SQLCoder model
- 🔍 **Dual Output Modes**: Generate SQL code or directly return queried data
- 🖥️ **User-friendly Interface**: Interactive web interface built with Streamlit
- 🚀 **Flexible Architecture**: Multiple deployment options (direct integration or API-based)
- 📊 **Database Integration**: Support for SQLite and other SQL databases
- 🔧 **Customizable**: Configurable prompts, metadata, and model settings

<br>

## 🏗️ System Architecture

The system provides three different deployment architectures:

```
ChatSQLGenLLM/
├── locally_hosted_llm_directly_with_streamlit/     # Direct Integration
│   ├── config.json                                 # Configuration settings
│   ├── run_streamlit.py                            # Main application
│   ├── prompt.md                                   # Prompt template
│   ├── metadata.sql                                # Database schema
│   └── fewshots_examples.txt                       # Example queries
├── locally_hosted_llm_fastapi_with_streamlit/      # API-based Architecture
│   ├── s1_build_local_api.py                       # FastAPI server
│   ├── s2_chatbot_call_api.py                      # Streamlit client
│   └── [configuration files]
└── remote_llm_api_with_streamlit/                  # Remote API Integration
    ├── s1_call_remote_llm_api.php                  # PHP API client
    ├── s2_chatbot_call_api.py                      # Streamlit interface
    └── [configuration files]
```

<br>

## 🚀 Quick Start

### System Requirements

- **Operating System**: Ubuntu 20.04 (tested) / macOS
- **Python**: 3.9+
- **Hardware**: 
  - GPU RAM: 16GB × 2GPU (as tested in original setup)
  - CPU RAM: 8GB+
  - Storage: 20GB+ free space

### Core Dependencies

Based on the original system configuration:

```
streamlit
transformers
torch
fastapi
sqlite3 (built-in with Python)
pandas
uvicorn
```

### Model Setup

The system uses the **SQLCoder-7B-2** model from Hugging Face:

1. **Download the Model**:
   ```bash
   # Visit: https://huggingface.co/defog/sqlcoder-7b-2
   ```

2. **Model Information**:
   - **Model**: [defog/sqlcoder-7b-2](https://huggingface.co/defog/sqlcoder-7b-2)
   - **Architecture**: Fine-tuned Code Llama model optimized for SQL generation
   - **Performance**: High accuracy on complex SQL queries with natural language understanding

<br>

## 📖 Deployment Options

### 1. 🏠 Direct Integration (Recommended for Beginners)

**locally_hosted_llm_directly_with_streamlit** - Simple, all-in-one solution

Perfect for quick setup and testing. The LLM model runs directly within the Streamlit application.

#### Configuration

**Step 1: Configure Settings**

Edit `locally_hosted_llm_directly_with_streamlit/config.json`:

```json
{
    "model_path": "/path/to/sqlcoder-7b-2/",
    "prompt_file": "prompt.md",
    "metadata_file": "metadata.sql",
    "answer_mode": "code",
    "local_db_path": "/path/to/database.db"
}
```

- Configuration Options:
  - **`model_path`**: Absolute path to your downloaded SQLCoder model directory
  - **`prompt_file`**: Template file for structuring queries to the LLM (default: "prompt.md")
  - **`metadata_file`**: SQL file containing your database schema information (default: "metadata.sql")
  - **`answer_mode`**: 
    - `"code"`: Returns generated SQL query code only
    - `"dataframe"`: Returns actual query results as dataframe (requires database connection)
  - **`local_db_path`**: Path to local database file (required only when answer_mode is "dataframe")

#### Launch Application

**Step 2: Start the Service**

```bash
cd locally_hosted_llm_directly_with_streamlit
streamlit run run_streamlit.py --server.address 127.0.0.1 --server.port 6006
```

**Step 3: Access Interface**

Open your browser and navigate to: [http://127.0.0.1:6006](http://127.0.0.1:6006)

> **Note**: For remote server deployment, ensure proper port forwarding is configured. You can customize the port number as needed.

<br>

### 2. 🔌 API-Based Architecture (Recommended for Production)

**locally_hosted_llm_fastapi_with_streamlit** - Scalable, microservices approach

Ideal for production environments where you need flexibility and don't want to reload the model frequently.

#### Advantages:
- ⚡ **Performance**: Model stays loaded in memory between requests
- 🔄 **Flexibility**: Restart web interface without reloading model
- 🔧 **Integration**: Easy to integrate with other applications

#### Setup Process

**Step 1: Configure Settings**

Edit `locally_hosted_llm_fastapi_with_streamlit/config.json`:

```json
{
    "model_path": "/path/to/sqlcoder-7b-2/",
    "prompt_file": "prompt.md",
    "metadata_file": "metadata.sql",
    "answer_mode": "code",
    "local_db_path": "/path/to/database.db",
    "api_address": "http://127.0.0.1:8000"
}
```

- Configuration Options:
  - **`model_path`**: Absolute path to your downloaded SQLCoder model directory
  - **`prompt_file`**: Template file for structuring queries to the LLM (default: "prompt.md")
  - **`metadata_file`**: SQL file containing your database schema information (default: "metadata.sql")
  - **`answer_mode`**: Output format ("code" for SQL queries, "dataframe" for results)
  - **`local_db_path`**: Path to local database file (required for "dataframe" mode)
  - **`api_address`**: URL of the FastAPI server (must match the server port)


**Step 2: Start the API Server**

```bash
cd locally_hosted_llm_fastapi_with_streamlit
uvicorn s1_build_local_api:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
```

> **Important**: Ensure the port matches the `api_address` in your config.json

**Step 3: Launch the Web Interface**

```bash
streamlit run s2_chatbot_call_api.py --server.address 127.0.0.1 --server.port 6006
```

**Step 4: Access Application**

Open [http://127.0.0.1:6006](http://127.0.0.1:6006) in your browser

**Step 5: Stop Services**

To stop the API server:
```bash
lsof -ti:8000 | xargs kill
```

<br>

### 3. 🌐 Remote API Integration

**remote_llm_api_with_streamlit** - Connect to external LLM services

For integrating with cloud-based or remote LLM APIs when you want to use external services instead of hosting the model locally.

#### Use Cases:
- 🌩️ **Cloud Integration**: Connect to cloud-based LLM services
- 💰 **Cost Optimization**: Use external APIs to avoid local GPU costs
- 🔧 **Hybrid Architecture**: Combine local processing with remote AI services
- 📈 **Scalability**: Leverage cloud infrastructure for model inference

#### Setup Process

**Step 1: Configure Settings**

Edit `remote_llm_api_with_streamlit/config.json`:

```json
{
    "prompt_file": "prompt.md",
    "metadata_file": "metadata.sql",
    "answer_mode": "dataframe",
    "local_db_path": "/path/to/local/database.db"
}
```

**Step 2: Configure PHP API Client**

The system includes a PHP script (`s1_call_remote_llm_api.php`) that acts as a bridge between the Streamlit interface and remote APIs:

- Update the API endpoint in the PHP file
- Configure authentication if required
- Adjust timeout and error handling settings

**Step 3: Start the Service**

```bash
cd remote_llm_api_with_streamlit
# Start PHP server (if needed)
php -S localhost:8080 > php_server.log 2>&1 &

# Start Streamlit interface
streamlit run s2_chatbot_call_api.py --server.address 127.0.0.1 --server.port 6006
```

**Step 4: Access Application**

Open [http://127.0.0.1:6006](http://127.0.0.1:6006) in your browser

> **Note**: This architecture requires a running remote LLM API service and proper network connectivity.

<br>

## 🛠️ Advanced Configuration

### Database Schema Setup

The `metadata.sql` file should contain your database schema information:

```sql
-- Example metadata.sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product_name TEXT,
    quantity INTEGER,
    price DECIMAL(10,2),
    order_date DATE
);
```

### Prompt Engineering

Customize the `prompt.md` file to improve query generation:

```markdown
### Task
Generate a SQL query to answer questions.

{examples}

### Database Schema
The query will run on a database with the following schema:
{table_metadata_string}

### Answer
Given the database schema, here is the SQL query that [QUESTION]{user_question}[/QUESTION]
[SQL]
```

### Few-Shot Examples

Add examples in `fewshots_examples.txt` to improve model performance:

```
Question: How many users registered last month?
SQL: SELECT COUNT(*) FROM users WHERE created_at >= DATE('now', '-1 month');

Question: What are the top 5 selling products?
SQL: SELECT product_name, SUM(quantity) as total_sold FROM orders GROUP BY product_name ORDER BY total_sold DESC LIMIT 5;
```

<br>

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
