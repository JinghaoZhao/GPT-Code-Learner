from code_searcher import get_function_context
import util
import repo_parser


def tool_selection(input):
    system_prompt = """You are an expert developer and programmer. """
    user_prompt = """
        You need to act as a tool recommender according to the user's questions.
        You are giving a user question about the code repository.
        You choose one of the following tools to help you answer the question.
        Your answer should be the name of the tool. No any other words or symbol are allowed.

        The tools are defined as follows:

        - Code_Searcher: This tool searches keywords extracted from user input in the code repository. We consider using "Code_Searcher" when the user question specifies specific functions or variables. For example, this tool is used to handle questions such as “How to use the function extract_function_name?”, “How to use the function def supabase_vdb():”, etc.

        - Repo_Parser: This tool performs a fuzzy search on the code repo. It provides contexts for questions about the general procedures in the repo. The question could be high-level and involves multiple source code files and documents. For example, this tool is used to handle questions such as “What function processes the incoming message?”, “How does the code store the knowledge base?”, etc.

        - No_Tool: This is the default tool when the question does not specific to the code repository. You should use this tool when you cannot find use any tools above to answer the question. For example, this tool is used to handle questions such as “What is the programming language of this repo?”, “What is the framework used in this repo?”, etc.


        Below are some example questions and answers:

        - Question: How to use the function extract_function_name?
        - Code_Searcher

        - Question: How to use the function def supabase_vdb(knowledge_base):?
        - Code_Searcher 

        - Question: How to create a knowledge base?
        - Repo_Parser 

        - Question: How to use the knowledge base?
        - Repo_Parser 

        - Question: How does this repo generate the UI interface?
        - Repo_Parser 

        - Question: How to use the python asyncio library?
        - No_Tool

        """ + f'Here is the user input: {input}'
    return util.get_chat_response(system_prompt, user_prompt)


def extract_function_name(input):
    system_prompt = """You are an expert developer and programmer. """
    user_prompt = """
        You will handle user questions about the code repository.
        Please extract the function or variable name appeared in the question.
        Only response the one name without the parameters or any other words.
        If both function and variable names are mentioned, only extract the function name.

        Below are two examples:
        - Question: How to use the function extract_function_name?
        - Answer: extract_function_name

        - Question: How to use the function def supabase_vdb(query, knowledge_base):?
        - Answer: supabase_vdb 

        - Question: What is the usage of vdb?
        - Answer: vdb 

        """ + f'Here is the user input: {input}'
    return util.get_chat_response(system_prompt, user_prompt)


def user_input_handler(input):
    tool = tool_selection(input)
    print(tool)
    if tool == "Code_Searcher":
        # extract the function or variable name from the input
        function_name = extract_function_name(input)
        print(function_name)
        if function_name:
            # search the function with context
            context = get_function_context(function_name)
            prompt = input + "\n\n" + \
                     f"Here are some the contexts of the function or variable {function_name}: \n\n" + context
            return prompt
    elif tool == "Repo_Parser":
        vdb = repo_parser.generate_or_load_knowledge_from_repo()
        context = repo_parser.get_repo_context(input, vdb)
        prompt = input + "\n\n" + \
                 f"Here are some contexts about the question, which are ranked by the relevance to the question: \n\n" + context
        return prompt
    else:
        print("No tool is selected.")
        return input


if __name__ == "__main__":
    # results = user_input_handler("What is the usage of the function traffic_interval?")
    # print(results)

    results = user_input_handler("How to build a knowledge base?")
    print(results)
