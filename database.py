import os
from dotenv import load_dotenv
from mongoengine import connect, disconnect
from pymongo.errors import ConnectionFailure

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = "tcf_nlp_db"

def init_mongodb():
    """Initialize MongoDB connection"""
    if not MONGO_URL:
        raise ValueError("MONGO_URL is not set in the environment variables.")
        
    try:
        disconnect()  # Disconnect any existing connections
        connect(
            db=DB_NAME,
            host=MONGO_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True
        )
        print("✅ MongoDB connected successfully")
        return True
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        raise

def close_mongodb():
    """Close MongoDB connection"""
    try:
        disconnect()
        print("✅ MongoDB disconnected")
    except Exception as e:
        print(f"❌ Error closing MongoDB: {e}")