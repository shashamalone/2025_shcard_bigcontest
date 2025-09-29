from langchain.tools import tool
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "my-index")

embeddings = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")
vectorstore = PineconeVectorStore.from_existing_index(PINECONE_INDEX_NAME, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

@tool("rag_search")
def rag_search(query: str):
    """Pinecone RAG를 통해 관련 문서 3개를 검색한다"""
    docs = retriever.get_relevant_documents(query)
    return [{"content": d.page_content, "metadata": d.metadata} for d in docs]
