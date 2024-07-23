import openai
from dotenv import load_dotenv, find_dotenv
import os
from supabase import create_client, Client
import requests
from bs4 import BeautifulSoup
import pickle
from langchain_community.llms.openai import OpenAI
from langchain.chains import VectorDBQAWithSourcesChain
from sentence_transformers import SentenceTransformer
from termcolor import colored
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS, SupabaseVectorStore
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
import shutil

class LocalHuggingFaceEmbeddings(Embeddings):
    def __init__(self, model_id="all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_id)

    def embed_documents(self, texts):
        embeddings = self.model.encode(texts)
        return embeddings

    def embed_query(self, text):
        embedding = self.model.encode(text)
        return list(map(float, embedding))


def load_documents(filenames):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        length_function=len,
    )
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


def load_code_chunks(chunks, filepath):
    text_splitter = CharacterTextSplitter(chunk_size=1500, separator="\n")
    docs, metadatas = [], []
    for chunk in chunks:
        splits = text_splitter.split_text(chunk)
        docs.extend(splits)
        metadatas.extend([{"source": filepath}] * len(splits))
    print(f"Split {filepath} into {len(docs)} pieces")
    return docs, metadatas


def local_vdb(knowledge, vdb_path=None):
    embedding_type = os.environ.get('EMBEDDING_TYPE', "local")
    if embedding_type == "local":
        embedding = LocalHuggingFaceEmbeddings()
    else:
        embedding = OpenAIEmbeddings(disallowed_special=())
    print(colored("Embedding documents...", "green"))
    faiss_store = FAISS.from_documents(knowledge["known_docs"], embedding=embedding)
    if vdb_path is not None:

        faiss_store.save_local(vdb_path)
        # path = "./vdb/index.pkl"
        # shutil.copyfile(path, vdb_path)
    return faiss_store


def load_local_vdb(vdb_path):
    if os.path.getsize(vdb_path) > 0:
        with open(vdb_path, "rb") as f:
            try:
                faiss_store = FAISS.load_local(vdb_path, OpenAIEmbeddings,allow_dangerous_deserialization=True)
                return faiss_store
            except EOFError:
                print("File is broken or wrong format.")
    else:
        print("File content is empty.")
    return None


def supabase_vdb(knowledge):
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)

    vector_store = SupabaseVectorStore(client=supabase, embedding=OpenAIEmbeddings(), table_name="documents")
    vector_store.add_documents(knowledge["known_docs"])
    vector_store.add_texts(knowledge["known_text"]["pages"], metadatas=knowledge["known_text"]["metadatas"])

    return vector_store


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    openai.api_key = os.environ.get("OPENAI_API_KEY", "null")

    query = "What is the usage of this repo?"
    files = ["./README.md"]
    urls = ["https://github.com/JinghaoZhao/GPT-Code-Learner"]

    known_docs = load_documents(files)
    known_pages, metadatas = load_urls(urls)

    knowledge_base = {"known_docs": known_docs, "known_text": {"pages": known_pages, "metadatas": metadatas}}

    faiss_store = local_vdb(knowledge_base)
    matched_docs = faiss_store.similarity_search(query)
    for doc in matched_docs:
        print("------------------------\n", doc)

    supabase_store = supabase_vdb(knowledge_base)
    matched_docs = supabase_store.similarity_search(query)
    for doc in matched_docs:
        print("------------------------\n", doc)

    chain = VectorDBQAWithSourcesChain.from_llm(llm=OpenAI(temperature=0), vectorstore=faiss_store)
    result = chain({"question": query})
    print("FAISS result", result)

    chain = VectorDBQAWithSourcesChain.from_llm(llm=OpenAI(temperature=0), vectorstore=supabase_store)
    result = chain({"question": query})
    print("Supabase result", result)
