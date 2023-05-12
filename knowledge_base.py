import openai
from dotenv import load_dotenv, find_dotenv
import os
from supabase import create_client, Client
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS, SupabaseVectorStore
from langchain.document_loaders import TextLoader, PyPDFLoader
import requests
from bs4 import BeautifulSoup
import pickle
from langchain import OpenAI
from langchain.chains import VectorDBQAWithSourcesChain

def load_documents(filenames):
    text_splitter = CharacterTextSplitter(chunk_size=1500, chunk_overlap=0)
    docs = []
    for filename in filenames:
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filename)
        else:
            loader = TextLoader(filename)
        documents = loader.load()
        splits = text_splitter.split_documents(documents)
        docs.extend(splits)
        print(f"Split {filename} into {len(splits)} chunks")
    return docs


def load_urls(urls):
    text_splitter = CharacterTextSplitter(chunk_size=1500, separator="\n")
    docs, metadatas = [], []
    for url in urls:
        html = requests.get(url).text
        soup = BeautifulSoup(html, features="html.parser")
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        page_content = '\n'.join(line for line in lines if line)

        splits = text_splitter.split_text(page_content)
        docs.extend(splits)
        metadatas.extend([{"source": url}] * len(splits))
        print(f"Split {url} into {len(splits)} chunks")
    return docs, metadatas


def local_vdb(query, knowledge_base, store_vdb=True):
    faiss_store = FAISS.from_documents(knowledge_base["known_docs"], embedding=OpenAIEmbeddings())
    faiss_store.add_texts(knowledge_base["known_text"]["pages"], metadatas=knowledge_base["known_text"]["metadatas"])
    if store_vdb:
        with open("faiss_store.pkl", "wb") as f:
            pickle.dump(faiss_store, f)
    else:
        with open("faiss_store.pkl", "rb") as f:
            faiss_store = pickle.load(f)

    matched_docs = faiss_store.similarity_search_with_relevance_scores(query)

    for doc in matched_docs:
        print("------------------------\n", doc)

    return faiss_store

def supabase_vdb(query, knowledge_base):
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)

    vector_store = SupabaseVectorStore(client=supabase, embedding=OpenAIEmbeddings(), table_name="documents")
    vector_store.add_documents(knowledge_base["known_docs"])
    vector_store.add_texts(knowledge_base["known_text"]["pages"], metadatas=knowledge_base["known_text"]["metadatas"])
    matched_docs = vector_store.similarity_search_with_relevance_scores(query)

    for doc in matched_docs:
        print("------------------------\n", doc)

    return vector_store

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    query = "What protocols are supported by IoT GPT?"
    files = ["./config_template.yaml"]
    urls = ["https://github.com/JinghaoZhao/IoT-GPT"]

    known_docs = load_documents(files)
    known_pages, metadatas = load_urls(urls)

    knowledge_base = {
        "known_docs": known_docs,
        "known_text": {
            "pages": known_pages,
            "metadatas": metadatas
        }
    }

    faiss_store = local_vdb(query, knowledge_base)
    supabase_store = supabase_vdb(query, knowledge_base)

    chain = VectorDBQAWithSourcesChain.from_llm(
        llm=OpenAI(temperature=0), vectorstore=faiss_store)
    result = chain({"question": query})
    print("FAISS result", result)

    chain = VectorDBQAWithSourcesChain.from_llm(
        llm=OpenAI(temperature=0), vectorstore=supabase_store)
    result = chain({"question": query})
    print("Supabase result", result)
