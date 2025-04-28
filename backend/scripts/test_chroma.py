from app.core.config import settings

def test_chroma_connection():
    try:
        # Get ChromaDB client
        client = settings.get_chroma_client()
        
        # Test heartbeat
        client.heartbeat()
        print("✅ ChromaDB heartbeat successful")
        
        # Create a test collection
        collection = client.create_collection(
            name="test_collection",
            metadata={"description": "Test collection"}
        )
        print("✅ Created test collection")
        
        # Add a test document
        collection.add(
            documents=["This is a test document"],
            metadatas=[{"source": "test"}],
            ids=["test1"]
        )
        print("✅ Added test document")
        
        # Query the collection
        results = collection.query(
            query_texts=["test"],
            n_results=1
        )
        print("✅ Query successful:", results)
        
        # Clean up
        client.delete_collection("test_collection")
        print("✅ Cleaned up test collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_chroma_connection() 