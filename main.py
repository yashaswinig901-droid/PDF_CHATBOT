# main.py
from langchain_community.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
from utils.pdf_loader import load_and_split_pdf
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_or_load_vectorstore(pdf_path, index_path="faiss_index"):
    documents = load_and_split_pdf(pdf_path)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    if os.path.exists(index_path):
        vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    else:
        vectorstore = FAISS.from_documents(documents, embeddings)
        vectorstore.save_local(index_path)

    return vectorstore

def get_qa_chain(vectorstore):
    llm = Ollama(model="llama3")
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        return_source_documents=True
    )
    return chain
