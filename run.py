import hupper
import code_learner
from dotenv import load_dotenv, find_dotenv

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    reloader = hupper.start_reloader('code_learner.main')
    code_learner.main()