"""
Vector store for RAG memory using ChromaDB.
Stores and retrieves conversation context and facts.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from loguru import logger


class VectorMemory:
    """
    Vector-based memory store using ChromaDB.
    Supports semantic search and context retrieval.
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "jarvis_memory"
    ):
        """
        Initialize vector memory.
        
        Args:
            persist_directory: Directory to persist vector database
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.collection = None
        self._initialize_db()
        logger.info(f"VectorMemory initialized: {collection_name}")

    def _initialize_db(self) -> None:
        """Initialize ChromaDB."""
        try:
            import chromadb
            
            # Use new ChromaDB API (non-deprecated)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Jarvis memory and context store"}
            )
            
            logger.info("ChromaDB initialized (PersistentClient)")
        except ImportError:
            logger.warning(
                "ChromaDB not installed. "
                "Run: pip install chromadb"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")

    def store(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """
        Store text in memory.
        
        Args:
            text: Text to store
            metadata: Optional metadata
            memory_id: Optional custom ID
            
        Returns:
            Memory ID
        """
        if not self.collection:
            logger.error("Vector store not initialized")
            return ""

        if memory_id is None:
            memory_id = str(uuid.uuid4())

        if metadata is None:
            metadata = {}
        
        # Add timestamp
        metadata["timestamp"] = datetime.now().isoformat()
        
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[memory_id]
            )
            logger.debug(f"Stored memory: {memory_id}")
            return memory_id
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return ""

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memory for relevant content.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of matching memories
        """
        if not self.collection:
            logger.error("Vector store not initialized")
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            memories = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    memory = {
                        "text": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0,
                        "id": results['ids'][0][i] if results['ids'] else ""
                    }
                    memories.append(memory)
            
            logger.debug(f"Found {len(memories)} memories for query: {query}")
            return memories
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: Memory ID
            
        Returns:
            Memory data or None
        """
        if not self.collection:
            return None

        try:
            result = self.collection.get(ids=[memory_id])
            if result['documents']:
                return {
                    "text": result['documents'][0],
                    "metadata": result['metadatas'][0] if result['metadatas'] else {},
                    "id": memory_id
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get memory: {e}")
            return None

    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: Memory ID
            
        Returns:
            True if successful
        """
        if not self.collection:
            return False

        try:
            self.collection.delete(ids=[memory_id])
            logger.debug(f"Deleted memory: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False

    def clear_all(self) -> bool:
        """
        Clear all memories from the collection.
        
        Returns:
            True if successful
        """
        if not self.collection:
            return False

        try:
            # Delete and recreate collection
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Jarvis memory and context store"}
            )
            logger.info("Cleared all memories")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memories: {e}")
            return False

    def get_recent_context(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation context.
        
        Args:
            n: Number of recent items
            
        Returns:
            List of recent memories sorted by timestamp
        """
        if not self.collection:
            return []

        try:
            # Get all and sort by timestamp
            # This is a simplified version - production would use better querying
            all_items = self.collection.get()
            
            if not all_items['documents']:
                return []
            
            memories = []
            for i, doc in enumerate(all_items['documents']):
                metadata = all_items['metadatas'][i] if all_items['metadatas'] else {}
                memories.append({
                    "text": doc,
                    "metadata": metadata,
                    "id": all_items['ids'][i] if all_items['ids'] else "",
                    "timestamp": metadata.get('timestamp', '')
                })
            
            # Sort by timestamp (descending)
            memories.sort(key=lambda x: x['timestamp'], reverse=True)
            return memories[:n]
        except Exception as e:
            logger.error(f"Failed to get recent context: {e}")
            return []

    def count(self) -> int:
        """
        Count total memories in collection.
        
        Returns:
            Number of memories
        """
        if not self.collection:
            return 0

        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to count memories: {e}")
            return 0


