import os
import chardet
import openai
from termcolor import colored
from dotenv import load_dotenv, find_dotenv
from knowledge_base import load_documents, load_code_chunks, supabase_vdb, local_vdb, load_local_vdb


def split_file_content_by_function(filepath, file_ext):
    with open(filepath, 'rb') as file:
        rawdata = file.read()

    # Detect the file encoding
    result = chardet.detect(rawdata)
    encoding = result['encoding']

    # Decode the content using the detected encoding
    content = rawdata.decode(encoding)

    # TODO: Support more file types
    # Define the keyword for splitting based on the file extension
    if file_ext == '.py':
        keyword = 'def '
    elif file_ext == '.js':
        keyword = 'function '
    elif file_ext == '.java':
        keyword = 'static '
    elif file_ext == '.cpp':
        keyword = '::'
    else:
        print(f'Unsupported file extension: {file_ext}, return entire file content as one chunk')
        return [content]

    # Split the content by the keyword
    chunks = content.split(keyword)

    # Prepend the keyword to all chunks except the first one
    chunks = [chunks[0]] + [keyword + chunk for chunk in chunks[1:]]

    return chunks


def generate_knowledge_from_repo(dir_path, ignore_list):
    knowledge = {"known_docs": [], "known_text": {"pages": [], "metadatas": []}}
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in ignore_list]  # modify dirs in-place
        for file in files:
            if file in ignore_list:
                continue
            filepath = os.path.join(root, file)
            try:
                # Extract the file extension
                file_ext = os.path.splitext(filepath)[1]
                if file_ext not in {'.py', '.js', '.java', '.cpp'}:
                    knowledge["known_docs"].extend(load_documents([filepath]))
                else:
                    chunks = split_file_content_by_function(filepath, file_ext)
                    code_pieces, metadatas = load_code_chunks(chunks, filepath)
                    knowledge["known_text"]["pages"].extend(code_pieces)
                    knowledge["known_text"]["metadatas"].extend(metadatas)
            except Exception as e:
                print(f"Failed to process {filepath} due to error: {str(e)}")

    return knowledge


def get_folder_names(dir_path):
    folder_names = [name for name in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, name))]
    concatenated_names = "-".join(folder_names)
    return concatenated_names

def generate_or_load_knowledge_from_repo(dir_path="./code_repo"):
    vdb_path = "./vdb-" + get_folder_names(dir_path) + ".pkl"
    # check if vdb_path exists
    if os.path.isfile(vdb_path):
        vdb = load_local_vdb(vdb_path)
    else:
        ignore_list = ['.git', 'node_modules', '__pycache__', '.idea',
                       '.vscode']
        knowledge = generate_knowledge_from_repo(dir_path, ignore_list)
        vdb = local_vdb(knowledge, vdb_path=vdb_path)
    return vdb


def get_repo_context(query, vdb):
    matched_docs = vdb.similarity_search_with_relevance_scores(query, k=10)
    output = ""
    for idx, docs in enumerate(matched_docs):
        output += f"Context {idx}:\n"
        output += str(docs)
        output += "\n\n"
    return output


if __name__ == '__main__':
    print(get_folder_names("./code_repo"))

    load_dotenv(find_dotenv())
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    query = "How to use the knowledge base?"

    vdb = generate_or_load_knowledge_from_repo("./code_repo")

    context = get_repo_context(query, vdb)
    print(context)


