# bi_crew.py
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, ScrapeWebsiteTool, SerperDevTool
from dotenv import load_dotenv

load_dotenv()

# --- ENVIRONMENT VARIABLES & TOOLS ---
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

file_read_tool = FileReadTool()
web_scrape_tool = ScrapeWebsiteTool()
search_tool = SerperDevTool()

# =====================================================================
# AGENT DEFINITIONS: The Professional BI & Data Team
# =====================================================================

# 1. The Project Manager: Business Requirements Analyst
requirements_analyst = Agent(
    role='Business Requirements Analyst',
    goal=(
        "To meticulously analyze the client's initial request and the provided dataset's structure. "
        "Your primary objective is to transform a vague question into a set of specific, answerable analytical queries "
        "and to create a clear, actionable plan for your team."
    ),
    backstory=(
        "You are a seasoned consultant who bridges the gap between business stakeholders and the technical data team. "
        "You excel at listening to a client's needs and identifying the underlying business problem. "
        "Your analytical plans are legendary for their clarity and precision, ensuring the team is always focused on what truly matters."
    ),
    tools=[],
    allow_delegation=False,
    verbose=True
)

# 2. The Data Engineer: Data Cleaning & Preparation Specialist
data_engineer = Agent(
    role='Data Engineer',
    goal='To take raw data from any source and render it immaculately clean, structured, and ready for analysis. You are the guardian of data quality.',
    backstory=(
        "You are a detail-oriented data engineer with a passion for order and quality. You believe that no meaningful analysis can happen "
        "without a pristine dataset. You are an expert in handling missing values, correcting data types, and ensuring data integrity."
    ),
    tools=[file_read_tool],
    allow_delegation=False,
    verbose=True
)

# 3. The Data Scientist: Deep-Dive Quantitative Analyst
quantitative_analyst = Agent(
    role='Quantitative Data Scientist',
    goal='To perform a deep and rigorous statistical analysis of the clean data. You uncover the hidden stories, correlations, and statistically significant patterns that are not visible on the surface.',
    backstory=(
        "You are a PhD-level data scientist with a deep love for numbers. You go beyond simple descriptive statistics. "
        "You employ methods like regression, correlation analysis, and segmentation to extract the deepest possible insights from a dataset. "
        "Your findings form the factual bedrock of any business strategy."
    ),
    tools=[],
    allow_delegation=False,
    verbose=True
)

# 4. The BI Strategist: Market & Business Context Analyst
market_strategist = Agent(
    role='Market Intelligence Strategist',
    goal="To place the quantitative findings into a real-world business context. You answer the 'so what?' question by researching market trends, competitor activities, and industry benchmarks.",
    backstory=(
        "You are a strategic thinker who connects the dots between internal data and the external market. You live and breathe industry news "
        "and can instantly see how a competitor's product launch or a new market trend might explain the numbers. You provide the crucial 'why' behind the 'what'."
    ),
    tools=[web_scrape_tool, search_tool],
    allow_delegation=False,
    verbose=True
)

# 5. The BI Communicator: Reporting & Visualization Specialist
reporting_specialist = Agent(
    role='BI Reporting and Visualization Specialist',
    goal='To synthesize all technical findings and strategic insights into a single, compelling, and easily understandable report for a non-technical executive audience.',
    backstory=(
        "You are a master of communication and data storytelling. You can take a dense statistical report and a complex market analysis and "
        "weave them into a clear narrative with beautiful visualizations. Your reports are known for driving action and clarifying complex decisions for leadership."
    ),
    tools=[],
    allow_delegation=False,
    verbose=True
)

# =====================================================================
# TASK DEFINITIONS: The Professional Workflow
# =====================================================================

# Task 1: Define the Project Scope
requirements_task = Task(
    description=(
        "Analyze the user's request: '{user_question}' and the schema of the data at '{file_path}'. "
        "Your first step is to read only the first 5 rows to understand the columns. "
        "Then, formulate a concise 'Project Goal' and a list of 3-5 specific 'Key Analytical Questions' that will guide the entire analysis. "
        "This plan will be the foundation for all subsequent work."
    ),
    expected_output="A structured markdown document with a 'Project Goal' section and a bulleted list under 'Key Analytical Questions'.",
    agent=requirements_analyst
)

# Task 2: Clean and Prepare the Data
data_engineering_task = Task(
    description=(
        "Based on the project plan, load the full dataset from '{file_path}'. "
        "Perform a comprehensive data cleaning process. "
        "Your final output MUST be a summary of the cleaning actions performed (e.g., 'Removed 25 duplicate rows', 'Filled 88 missing values in the Sales column with the mean') "
        "and a description of the final, clean dataset's structure."
    ),
    expected_output="A markdown report detailing all data cleaning steps and the final state of the data.",
    agent=data_engineer,
    context=[requirements_task]
)

# Task 3: Perform Deep Statistical Analysis
quantitative_analysis_task = Task(
    description=(
        "Using the clean data and guided by the 'Key Analytical Questions' from the project plan, perform a deep statistical analysis. "
        "Go beyond simple averages. Look for correlations, segment the data, and identify any statistically significant findings. "
        "Focus on answering the analytical questions with hard numbers."
    ),
    expected_output="A detailed technical report of quantitative findings, with statistical evidence supporting each point.",
    agent=quantitative_analyst,
    context=[data_engineering_task]
)

# Task 4: Gather External Business Context
market_strategy_task = Task(
    description=(
        "Take the key quantitative findings from the previous step and investigate the external context. "
        "Use your web search tools to find relevant industry news, competitor actions, or market trends that could explain these findings. "
        "For example, if a product's sales are down, find out if a competitor launched a new product."
    ),
    expected_output="A concise business context report linking the internal data findings to external market factors, with supporting URLs.",
    agent=market_strategist,
    context=[quantitative_analysis_task]
)

# Task 5: Create the Final Client-Ready Report
# In bi_crew.py

# In bi_crew.py

final_report_task = Task(
    description=(
        "This is the final and most important step. Synthesize all the information from the previous tasks (Project Plan, Data Cleaning Summary, Quantitative Analysis, and Market Context) into a single, cohesive client-facing report. "
        "The report MUST be structured with the following sections in markdown:\n\n"
        "### Executive Summary\nA brief, high-level summary of the most critical findings and recommendations.\n\n"
        "### Key Insights & Visualizations\nA section detailing the main discoveries. For each insight, first write the textual explanation, then embed the chart data using the required format: [CHART_DATA]...[END_CHART_DATA]\n\n"
        "### Actionable Recommendations\nA numbered list of clear, strategic recommendations that the client can act upon.\n\n"
        "### Appendix: Data & Methodology\nA brief summary of the data cleaning process and the analytical methods used.\n\n"
        "**CRITICAL FORMATTING RULE: When you create any markdown tables in your report, you MUST ensure that all date-related columns (like a column named 'DATE' or 'Year') contain only text strings. For example, a year should be '2023', not the number 2023. A full date must be a string like '2023-04-15'. This is to prevent display errors.**"
    ),
    expected_output=(
        "A comprehensive, beautifully formatted markdown report ready to be presented to a business executive. "
        "All tables within the report must have their date-like columns formatted as text strings."
    ),
    agent=reporting_specialist,
    output_file='final_client_report.md',
    context=[requirements_task, data_engineering_task, quantitative_analysis_task, market_strategy_task]
)

# =====================================================================
# CREW DEFINITION
# =====================================================================

bi_crew = Crew(
    agents=[requirements_analyst, data_engineer, quantitative_analyst, market_strategist, reporting_specialist],
    tasks=[requirements_task, data_engineering_task, quantitative_analysis_task, market_strategy_task, final_report_task],
    process=Process.sequential,
    verbose=True
)