import os
from pathlib import Path
import urllib.parse
import sqlite3
import streamlit as st
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
from langchain.sql_database import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_types import AgentType

# -----------------------------
# Page & Sidebar Configuration
# -----------------------------
st.set_page_config(page_title="SQLTalkAI", page_icon="🦜", layout="wide")
st.title("🦜 LangChain + SQL: Natural Language to Queries")

DB_CHOICES = ("SQLite (local student.db)", "PostgreSQL", "MySQL")

with st.sidebar:
    st.subheader("Connection Settings")
    db_choice = st.radio("Choose a database", DB_CHOICES, index=0)

    st.markdown("### Model Settings")
    api_key = st.text_input("Groq API Key", type="password", value=os.environ.get("GROQ_API_KEY", ""))

    st.caption("Tip: You can set GROQ_API_KEY as an environment variable to avoid typing it here.")

# -----------------------------
# Helpers
# -----------------------------
def get_llm(groq_key: str):
    """Return a streaming LLM client (Groq Llama3)."""
    if not groq_key:
        st.error("Groq API key is required.")
        st.stop()
    return ChatGroq(groq_api_key=groq_key, model_name="llama-3.3-70b-versatile", streaming=True)

def build_sqlite_db() -> SQLDatabase:
    """Open a read-only SQLite connection to student.db colocated with the app."""
    db_path = (Path(__file__).parent / "student.db").resolve()
    if not db_path.exists():
        st.error(f"student.db not found at: {db_path}")
        st.stop()

    # Read-only SQLite connection via URI
    def _creator():
        return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)

    engine = create_engine("sqlite:///", creator=_creator)
    return SQLDatabase(engine)

def build_engine_from_url(url: str):
    """Create a SQLAlchemy engine from a DSN URL and validate connectivity."""
    try:
        engine = create_engine(url)
        # Basic connectivity check
        with engine.connect() as _:
            pass
        return engine
    except Exception as exc:
        st.error(f"Connection failed: {exc}")
        st.stop()

def build_pg_engine(host: str, user: str, password: str, dbname: str):
    """Create a Postgres engine with safe URL encoding."""
    if not all([host, user, password, dbname]):
        st.error("Please provide all PostgreSQL fields.")
        st.stop()

    user_q = urllib.parse.quote_plus(user)
    pwd_q = urllib.parse.quote_plus(password)
    host_q = host.strip()
    db_q = urllib.parse.quote_plus(dbname)
    dsn = f"postgresql+psycopg2://{user_q}:{pwd_q}@{host_q}/{db_q}"
    return build_engine_from_url(dsn)

def build_mysql_engine(host: str, user: str, password: str, dbname: str):
    """Create a MySQL engine with safe URL encoding (mysql-connector)."""
    if not all([host, user, password, dbname]):
        st.error("Please provide all MySQL fields.")
        st.stop()

    user_q = urllib.parse.quote_plus(user)
    pwd_q = urllib.parse.quote_plus(password)
    host_q = host.strip()
    db_q = urllib.parse.quote_plus(dbname)
    dsn = f"mysql+mysqlconnector://{user_q}:{pwd_q}@{host_q}/{db_q}"
    return build_engine_from_url(dsn)

@st.cache_resource(ttl=2 * 60 * 60)  # cache for 2 hours
def build_sql_database(source: str, **kwargs) -> SQLDatabase:
    """Return a SQLDatabase for the chosen backend."""
    if source == "sqlite":
        return build_sqlite_db()

    if source == "postgres":
        engine = build_pg_engine(
            host=kwargs.get("host", ""),
            user=kwargs.get("user", ""),
            password=kwargs.get("password", ""),
            dbname=kwargs.get("dbname", ""),
        )
        return SQLDatabase(engine)

    if source == "mysql":
        engine = build_mysql_engine(
            host=kwargs.get("host", ""),
            user=kwargs.get("user", ""),
            password=kwargs.get("password", ""),
            dbname=kwargs.get("dbname", ""),
        )
        return SQLDatabase(engine)

    st.error("Unsupported database type.")
    st.stop()

def init_sql_agent(db: SQLDatabase, llm: ChatGroq):
    """Instantiate a SQL Agent wired to our database/toolkit."""
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )
    return agent

def show_schema_preview(db: SQLDatabase):
    """Optional quick look at tables for usability."""
    try:
        tables = db.get_usable_table_names()
        if tables:
            with st.expander("🔎 Tables discovered (click to expand)"):
                st.write(sorted(list(tables)))
        else:
            st.info("No tables discovered or the user lacks permissions.")
    except Exception as exc:
        st.warning(f"Could not list tables: {exc}")

# -----------------------------
# Collect DB Credentials (Forms)
# -----------------------------
db_params = {}
if db_choice == "SQLite (local student.db)":
    backend = "sqlite"

elif db_choice == "PostgreSQL":
    backend = "postgres"
    with st.sidebar.form("pg_form"):
        pg_host = st.text_input("PostgreSQL Host", value="127.0.0.1").strip()
        pg_user = st.text_input("PostgreSQL User", value="postgres").strip()
        pg_pass = st.text_input("PostgreSQL Password", type="password")
        pg_db = st.text_input("PostgreSQL Database").strip()
        submitted = st.form_submit_button("Save PostgreSQL Settings")
    if submitted:
        st.toast("PostgreSQL settings saved.", icon="✅")
    db_params.update(dict(host=pg_host, user=pg_user, password=pg_pass, dbname=pg_db))

elif db_choice == "MySQL":
    backend = "mysql"
    with st.sidebar.form("mysql_form"):
        my_host = st.text_input("MySQL Host", value="127.0.0.1").strip()
        my_user = st.text_input("MySQL User", value="root").strip()
        my_pass = st.text_input("MySQL Password", type="password")
        my_db = st.text_input("MySQL Database").strip()
        submitted = st.form_submit_button("Save MySQL Settings")
    if submitted:
        st.toast("MySQL settings saved.", icon="✅")
    db_params.update(dict(host=my_host, user=my_user, password=my_pass, dbname=my_db))

# -----------------------------
# Initialize LLM, DB, and Agent
# -----------------------------
llm = get_llm(api_key)
db = build_sql_database(backend, **db_params)
agent = init_sql_agent(db, llm)

# Optional: quick schema peek to guide users
show_schema_preview(db)

# -----------------------------
# Chat State & UI
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Hi! Ask me anything about your database."}]

# Render history
for m in st.session_state.chat_history:
    st.chat_message(m["role"]).write(m["content"])

# Chat input
prompt = st.chat_input("e.g., Top 5 customers by revenue last quarter")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        callback = StreamlitCallbackHandler(st.container())
        try:
            # Using .run keeps compatibility across langchain versions
            reply = agent.run(prompt, callbacks=[callback])
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.write(reply)
        except Exception as exc:
            st.error(f"Something went wrong while processing your query: {exc}")

with st.sidebar:
    if st.button("Clear Conversation"):
        st.session_state.chat_history = [{"role": "assistant", "content": "History cleared. How can I help you now?"}]
        st.experimental_rerun()
