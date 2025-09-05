# SQLTalkAI: Conversational Database Assistant

🚀 Query your databases using natural language instead of writing SQL!
SQLTalkAI is an open-source Streamlit application that integrates LangChain with Groq LLaMA3 models to let you chat with your SQLite, PostgreSQL, or MySQL databases.

# 🔑 Key Features

💬 Chat with your database in plain English

🗄️ Works with SQLite, PostgreSQL, and MySQL

🤖 Built with LangChain SQL Agent for accurate query generation

🔒 Secure Groq API Key input for model authentication

# ⚡ Optimized with caching for faster responses

## ⚙️ Getting Started
1. Clone the Repository
```
git clone https://github.com/varanast/SQLTalkAI--Conversational-Database-Assistant.git
cd SQLTalkAI--Conversational-Database-Assistant
```


## 2. Create a Virtual Environment
```
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```


## 3. Install Requirements
```
pip install -r requirements.txt
```


## 4. Launch the App
```
streamlit run app.py
```

# 🛠️ Configuration
## Database Setup

SQLite → Uses student.db by default

PostgreSQL → Enter host, user, password, and database name via sidebar

MySQL → Provide connection details in the sidebar

# API Key Setup

You’ll need a Groq API Key to run LLaMA models:

Sign up at Groq Console

Generate an API Key from the Keys section

Paste it in the Streamlit sidebar

# 📖 How to Use

Select the database type from the sidebar

Provide database credentials (if applicable)

Enter your query in plain English (e.g., "List top 5 students by marks")

The app generates and executes the SQL query behind the scenes

Results are displayed in the chat interface instantly

# 🧑‍💻 Tech Stack

Streamlit → Interactive UI

LangChain → Natural language → SQL agent

Groq LLaMA3 → Query understanding and reasoning

SQLAlchemy → Database connection layer

SQLite, PostgreSQL, MySQL → Supported databases

# 🧩 Troubleshooting

❌ Error: No module named streamlit.cli
👉 Run with streamlit run app.py, not python streamlit app.py

❌ Error: Model decommissioned
👉 Update model name in code to llama-3.1-8b-instant or llama-3.3-70b-versatile

# 🤝 Contributing

Contributions are welcome! 🎉

Fork the repository

Create a new branch

Commit your changes

Open a pull request

# 📜 License

Currently, this project has no license. Please add one (MIT/Apache 2.0) before using in production.

# 🌟 Show Support

If you like this project, please star the repo ⭐ and share your feedback!
