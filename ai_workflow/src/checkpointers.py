import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

sqlite_connection = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)

sqlite_checkpointer = SqliteSaver(conn=sqlite_connection)