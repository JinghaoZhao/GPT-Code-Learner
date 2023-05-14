from code_searcher import get_function_context
import util
import repo_parser


def user_input_handler(input):
    tool = util.tool_selection(input)
    print(tool)
    if tool == "Code_Searcher":
        # extract the function or variable name from the input
        function_name = util.extract_function_name(input)
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
                 f"Here are some the contexts about the question, which are ranked by the relevance to the question: \n\n" + context
        return prompt
    else:
        print("No tool is selected.")
        return input


if __name__ == "__main__":
    # results = user_input_handler("What is the usage of the function traffic_interval?")
    # print(results)

    results = user_input_handler("How to build a knowledge base?")
    print(results)
