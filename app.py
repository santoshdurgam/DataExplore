from flask import Flask, render_template, request, jsonify
from flask.cli import load_dotenv
from langchain.chains import LLMChain
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.prompts.prompt import PromptTemplate
from langchain.chat_models import ChatOpenAI
from bs4 import BeautifulSoup
import os

app = Flask(__name__)



def setup():
    load_dotenv()
    db = SQLDatabase.from_uri(os.getenv('DATABASE_HOST'))
    openai_api_key = os.getenv('OPENAI_API_KEY')
    llm = ChatOpenAI(temperature=0, model_name=os.getenv('OPEN_API_MODEL_NAME'),openai_api_key=openai_api_key)
    return llm, db


llm, db = setup()

def create_chart_using_vega(input_data):
    # This is an LLMChain to write a synopsis given a title of a play and the era it is set in.
    template = """You are data analyst. read the input and generate a valid JSON in which each element is an object. Strictly using this FORMAT and naming required for Vega as per github https://github.com/vega/vega . Instead of naming value field value in JSON, \n Make sure the format use double quotes and property names are string literals. \n Provide JSON data only. `;

    Question: {input}
    Answer: Result """

    prompt_template = PromptTemplate(input_variables=["input"], template=template)
    data_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="Result")

    # This is an LLMChain to write a review of a play given a synopsis.
    vega_viz_template = """you are UI developer who generates appropriate charts html using vega github  https://github.com/vega/vega-embed. Strictly follow the examples to create the appropriate HTML. Also use the latest src tags in strictly script as below
        <script src="https://cdn.jsdelivr.net/npm/vega@5.25.0"></script>
        <script src="https://cdn.jsdelivr.net/npm/vega-lite@5.9.1"></script>
        <script src="https://cdn.jsdelivr.net/npm/vega-embed@6.22.1"></script>

    Question: create appropriate charts for data input {Result}. Strictly it should be in dimension of width by 800 and hieght by 600 pixels. Also use different shade of colors for charts in x axis. Along with this, create html table borders and well formatted to render the input {Result} data.
    Answer: generate the formatted code here"""
    vega_viz_prompt_template = PromptTemplate(input_variables=["Result"], template=vega_viz_template)
    viz_chain = LLMChain(llm=llm, prompt=vega_viz_prompt_template, output_key="code")

    # This is the overall chain where we run these two chains in sequence.
    from langchain.chains import SequentialChain

    overall_chain = SequentialChain(
        chains=[data_chain, viz_chain],
        input_variables=["input"],
        # Here we return multiple variables
        output_variables=["Result", "code"],
        verbose=False)

    chart_html = overall_chain({"input": input_data})
    file_written_flag = write_output_to_html(chart_html, 'vega')
    return input_data
def create_chart_using_highchart(input_data):

    # This is an LLMChain to write a synopsis given a title of a play and the era it is set in.
    template = """You are data analyst. read the input and generate a valid JSON in which each element is an object. Strictly using this FORMAT and naming required for highcharts as in https://www.highcharts.com/docs/index . Instead of naming value field value in JSON, \n Make sure the format use double quotes and property names are string literals. \n Provide JSON data only. `;

    Question: {input}
    Answer: Result """

    prompt_template = PromptTemplate(input_variables=["input"], template=template)
    data_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="Result")

    # This is an LLMChain to write a review of a play given a synopsis.
    vega_viz_template = """you are UI developer who generates appropriate highchart html using the documentation samples in https://www.highcharts.com/docs/index.  

    Question: create appropriate charts for data input {Result}. Strictly it should be in dimension of width by 800 and hieght by 600 pixels. Strictly use different colors in x axis. Along with this, create html table borders and well formatted to render the input {Result} data.  
    Answer: generate the formatted code here"""
    vega_viz_prompt_template = PromptTemplate(input_variables=["Result"], template=vega_viz_template)
    viz_chain = LLMChain(llm=llm, prompt=vega_viz_prompt_template, output_key="code")

    # This is the overall chain where we run these two chains in sequence.
    from langchain.chains import SequentialChain

    overall_chain = SequentialChain(
        chains=[data_chain, viz_chain],
        input_variables=["input"],
        # Here we return multiple variables
        output_variables=["Result", "code"],
        verbose=False)

    chart_html = overall_chain({"input": input_data})
    file_written_flag = write_output_to_html(chart_html, 'highchart')
    return input_data
def convert_question_to_charts(query):
    '''
    This takes an input of natural language to question the db, convert this into sql dialect and get the response and converts it into natural language output
    :param query: question for db
    :return: response as html supported by all charts
    '''

    # overriding db default prompt template
    _DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    Use the following format:

    Question: "Question here"
    SQLQuery: "SQL Query to run"
    SQLResult: "Result of the SQLQuery with appropriate friendly column names"
    Answer: "Final answer here with values"

    Only use the following tables:

    {table_info}

    If someone asks for the table foobar, they really mean the employee table.

    Question: {input}"""

    PROMPT = PromptTemplate(
        input_variables=["input", "table_info", "dialect"], template=_DEFAULT_TEMPLATE
    )

    db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=PROMPT, verbose=True)

    # Querying the db with natural language
    nl_db_response = db_chain.run(query = query)

    # # natural language db response
    print(nl_db_response)

    output_vega = create_chart_using_vega(nl_db_response)
    ouput_hc = create_chart_using_highchart(nl_db_response)

    return nl_db_response

def write_output_to_html(html_text, chart_type):
    soup = BeautifulSoup(html_text["code"], 'html.parser')
    with open("templates/chart_" + chart_type +".html", "w", encoding='utf-8') as file:
        file.write(str(soup))
    return True

@app.route('/home')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/vega')
def vega_charts():
    return render_template('chart_vega.html')

@app.route('/hc')
def high_charts():
    return render_template('chart_highchart.html')

@app.route('/', methods=['POST'])
def handle_form():
    if request.method == 'POST':
        # Call the API method here and get the response content
        # response_content = convert_question_to_chart_html(request.form['text'])
        # response_content = convert_question_to_hcchart_html(request.form['text'])
        response_content = convert_question_to_charts(request.form['text'])
        return render_template('home.html', response=response_content)


if __name__ == '__main__':
    app.run()


