import sqlite3
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
MONGODB_URI = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tcf_nlp_db")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in .env file")

client = MongoClient(MONGODB_URI)

# SQLite DB files
db_files = ["model.db", "complaints.db", "database.db"]

for db_file in db_files:

    print(f"\nProcessing: {db_file}")

    # SQLite connect
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # MongoDB database name
    mongo_db_name = DATABASE_NAME
    mongo_db = client[mongo_db_name]

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:

        table_name = table[0]
        print(f"Converting table: {table_name}")

        # Fetch rows
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Column names
        columns = [desc[0] for desc in cursor.description]

        documents = []

        for row in rows:
            doc = {}

            for i in range(len(columns)):
                doc[columns[i]] = row[i]

            documents.append(doc)

        # Insert into MongoDB
        if documents:
            mongo_db[table_name].insert_many(documents)

    conn.close()

print("\nAll databases converted successfully!")