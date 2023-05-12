from code_searcher import get_function_context
import util


def user_input_handler(input):
    # TODO: Replace it with an AI classifier to call tools
    # If users ask questions about a function, we use the code_searcher to get the context
    if "function" in input:
        # extract the function name from the input
        function_name = util.extract_function_name(input)
        print(function_name)
        if function_name:
            # search the function with context
            context = get_function_context(function_name)
            prompt = input + "\n\n" + \
                     f"Here are some the contexts of the function {function_name}: \n\n" + context
            return prompt
    else:
        return input


if __name__ == "__main__":
    results = user_input_handler("What is the usage of the function traffic_interval?")
    print(results)
