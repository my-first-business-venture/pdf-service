import os
from llama_index.core import GPTVectorStoreIndex, Document, Settings
from llama_index.llms.openai import OpenAI
from config import OPENAI_KEY, LLM_MODEL

class LlamaIndexService:
    def __init__(self, pdf_text: str):
        os.environ["OPENAI_API_KEY"] = OPENAI_KEY
        self.document = Document(text=pdf_text)
        llm = OpenAI(model=LLM_MODEL)
        Settings.llm = llm
        self.index = GPTVectorStoreIndex.from_documents([self.document])

    def get_relevant_context(self, query: str, top_k: int = 5) -> str:
        query_engine = self.index.as_query_engine(similarity_top_k=top_k)
        response = query_engine.query(query)
        return str(response)
