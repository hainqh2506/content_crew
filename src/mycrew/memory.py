from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory, UserMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.memory.storage.rag_storage import RAGStorage
from llm import gg_embedder
long_term_memory = LongTermMemory(
        storage=LTMSQLiteStorage(
            db_path="db/long_term_memory.db" # Đường dẫn tùy chỉnh
            #db_path="/my_crew_memory/long_term_memory.db" # Đường dẫn tùy chỉnh
        )
    )

# Short-term memory for current context using RAG
short_term_memory = ShortTermMemory(
    storage = RAGStorage(
            embedder_config=gg_embedder,
            type="short_term",
            path="db/"
        )
    )