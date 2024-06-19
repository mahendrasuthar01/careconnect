import mongoengine
from mongoengine.connection import get_db, disconnect

# Configuration for MongoDB
DATABASE_NAME = 'coreconnect'
CONNECTION_STRING = 'mongodb://localhost:27017'
CONNECTION_ALIAS = 'default'

def connect_db():
    """Connect to the MongoDB database with MongoEngine."""
    try:
        disconnect(CONNECTION_ALIAS)  # Disconnect the existing connection if any.
        mongoengine.connect(db=DATABASE_NAME, host=CONNECTION_STRING, alias=CONNECTION_ALIAS)
        print(f"Connected to MongoDB database: {DATABASE_NAME}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

# Call the connect function
connect_db()