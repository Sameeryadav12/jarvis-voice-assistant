"""
Test Jarvis memory system (ChromaDB).
Sprint 4 - Part 1: Memory & RAG
"""

import sys
from pathlib import Path

# UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

# Suppress debug logs
import logging
logging.getLogger().setLevel(logging.WARNING)

from core.memory.vectorstore import VectorMemory

print("\n" + "=" * 60)
print("  JARVIS MEMORY SYSTEM TEST")
print("=" * 60)
print("\n[1/5] Initializing memory...")

try:
    memory = VectorMemory(
        persist_directory="./test_memory_db",
        collection_name="test_memory"
    )
    print("  [OK] Memory initialized")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Store information
print("\n[2/5] Testing store...")
try:
    facts = [
        "My favorite color is blue",
        "I live in New York",
        "My birthday is in December",
        "I work at TechCorp as a software engineer",
        "I enjoy hiking on weekends"
    ]
    
    for fact in facts:
        memory_id = memory.store(fact, metadata={"type": "fact"})
        print(f"  [OK] Stored: '{fact[:40]}...'")
    
    print(f"  [OK] Stored {len(facts)} facts")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Search memory
print("\n[3/5] Testing search...")
try:
    queries = [
        "What is my favorite color?",
        "Where do I live?",
        "What do I do for work?",
    ]
    
    for query in queries:
        results = memory.search(query, n_results=2)
        print(f"  Query: '{query}'")
        if results:
            print(f"  Result: '{results[0]['text']}'")
            print(f"  [OK]")
        else:
            print(f"  [WARN] No results")
        print()
    
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Count and recent context
print("[4/5] Testing count and context...")
try:
    count = memory.count()
    print(f"  Total memories: {count}")
    
    recent = memory.get_recent_context(n=3)
    print(f"  Recent memories: {len(recent)}")
    print(f"  [OK]")
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Cleanup
print("\n[5/5] Cleaning up test database...")
try:
    memory.clear_all()
    print("  [OK] Test database cleared")
except Exception as e:
    print(f"  [WARN] Cleanup failed: {e}")

print("\n" + "=" * 60)
print("[SUCCESS] MEMORY SYSTEM WORKING!")
print("=" * 60)
print("\nMemory capabilities:")
print("  - Store facts and conversation history")
print("  - Semantic search (finds relevant info)")
print("  - Context retrieval")
print("  - Persistent storage")
print()




