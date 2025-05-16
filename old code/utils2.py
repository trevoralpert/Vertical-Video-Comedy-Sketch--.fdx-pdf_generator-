from langchain_community.chat_models import ChatOpenAI  # Updated import
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.tools import DuckDuckGoSearchRun  # Updated import

# Function to generate video script
def generate_script(prompt, video_length, creativity, api_key):
    # Template for generating 'Title'
    title_template = PromptTemplate(
        input_variables=['subject'],
        template='Please come up with a title for a YouTube video on the {subject}.'
    )

    # Template for generating 'Video Script' using search engine
    script_template = PromptTemplate(
        input_variables=['title', 'DuckDuckGo_Search', 'duration'],
        template=(
            'Create a script for a YouTube video based on this title. '
            'TITLE: {title} of duration {duration} minutes using this search data: {DuckDuckGo_Search}'
        )
    )

    # Setting up OpenAI LLM
    llm = ChatOpenAI(temperature=creativity, openai_api_key=api_key, model_name='gpt-3.5-turbo')

    # Creating chains for 'Title' & 'Video Script'
    title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True)
    script_chain = LLMChain(llm=llm, prompt=script_template, verbose=True)

    # DuckDuckGo Search Tool
    search = DuckDuckGoSearchRun()

    # Generate Title
    title = title_chain.run(prompt)

    # Generate Script using DuckDuckGo Search results
    search_result = search.run(prompt)
    script = script_chain.run(title=title, DuckDuckGo_Search=search_result, duration=video_length)

    return search_result, title, script
