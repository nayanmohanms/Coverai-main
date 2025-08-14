# clear_pinecone.py
import sys
import os

# Add the project root directory to the Python path to resolve the import error
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app import pinecone_client
from pinecone.exceptions import NotFoundException

def clear_all_data():
    """
    Deletes all vectors from the Pinecone index to allow for a fresh start.
    """
    try:
        index = pinecone_client.index
        print(f"Clearing all data from Pinecone index '{pinecone_client.INDEX_NAME}'...")
        
        # The 'delete_all=True' parameter without a namespace clears the entire index.
        # However, to be safe and clear all potential namespaces from previous runs,
        # we can list them and delete one by one if needed, or just delete the whole index.
        # For serverless, deleting the index and recreating is often fastest.
        
        print(f"Deleting index '{pinecone_client.INDEX_NAME}'...")
        pinecone_client.pc.delete_index(pinecone_client.INDEX_NAME)
        print("Index deleted successfully.")
        
        print("Re-initializing index...")
        pinecone_client.init_pinecone()
        print("Index re-initialized. It is now empty.")

    except NotFoundException:
        print("Index not found. Nothing to clear.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    confirm = input("Are you sure you want to delete all data from the Pinecone index? This cannot be undone. (y/n): ")
    if confirm.lower() == 'y':
        clear_all_data()
    else:
        print("Operation cancelled.")
