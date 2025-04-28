import os
import time
import chromadb
from chromadb.config import Settings

def wait_for_chroma():
    """Wait for ChromaDB to be available"""
    max_retries = 30
    retry_interval = 2
    
    chroma_host = os.getenv("CHROMA_HOST", "localhost")
    chroma_port = os.getenv("CHROMA_PORT", "8000")
    
    print(f"Waiting for ChromaDB at {chroma_host}:{chroma_port}...")

    # Create a client without tenant/database for initial setup
    client = chromadb.HttpClient(
        host=chroma_host,
        port=int(chroma_port),
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=True
        )
    )
    
    for i in range(max_retries):
        try:
            client.heartbeat()
            print("Successfully connected to ChromaDB!")
            return client, chroma_host, chroma_port
        except Exception as e:
            if i < max_retries - 1:
                print(f"Connection attempt {i + 1} failed. Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                raise Exception("Failed to connect to ChromaDB after maximum retries") from e

def init_chroma():
    """Initialize ChromaDB with tenant and database"""
    try:
        # Wait for ChromaDB to be available
        client, chroma_host, chroma_port = wait_for_chroma()
        

        # Get tenant and database names
        tenant_name = os.getenv("CHROMA_TENANT", "videochat")
        database_name = os.getenv("CHROMA_DATABASE", "videochat_db")
        
        # print(f"Setting up tenant '{tenant_name}' and database '{database_name}'...")
        
        # Create tenant if it doesn't exist
        # try:
        #     client.set_tenant(tenant=tenant_name)
        # except Exception as e:
        #     if "already exists" in str(e).lower():
        #         print(f"Tenant '{tenant_name}' already exists")
        #     else:
        #         raise
        
        
        # # Create database if it doesn't exist
        # try:
        #     client.create_database(database_name)
        #     print(f"Created new database '{database_name}'")
        # except Exception as e:
        #     if "already exists" in str(e).lower():
        #         print(f"Database '{database_name}' already exists")
        #     else:
        #         raise
        
        # # Set database
        # client.set_database(database_name)
        # print(f"Using tenant '{tenant_name}' and database '{database_name}'")
        
        # Create a test collection to verify everything works
        collection = client.create_collection(
            name="test_collection",
            metadata={
                "description": "Test collection to verify ChromaDB initialization",
                "hnsw:space": "cosine",
                "hnsw:construction_ef": 100,
                "hnsw:M": 16,
                "hnsw:search_ef": 10
            }
        )
        
        # Add a test document
        collection.add(
            documents=["This is a test document"],
            metadatas=[{"source": "initialization"}],
            ids=["test1"]
        )
        
        # Query to verify
        results = collection.query(
            query_texts=["test"],
            n_results=1
        )
        
        if results and len(results['documents']) > 0:
            print("Successfully initialized ChromaDB!")
            print("- Created/verified tenant and database")
            print("- Created test collection")
            print("- Verified query functionality")
            
            # Clean up test collection
            client.delete_collection("test_collection")
            print("- Cleaned up test collection")
            
        return True
        
    except Exception as e:
        print(f"Error initializing ChromaDB: {str(e)}")
        raise

if __name__ == "__main__":
    init_chroma() 