EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
CHAT_MODEL_ID = 'Qwen/Qwen2.5-1.5B-Instruct'
TEMPLATE = ''' Answer the query only from the following context if the context is insufficient or answer is not available in context just say you don't know
            context:
            {context}\n

            question:
            {question}''',