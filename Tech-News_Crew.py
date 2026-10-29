"""
News_Crew: a two-agent sequential CrewAI crew.
 
Researcher (can search the web via SerperDevTool) -> Writer (no tools)
 
Setup:
    pip install crewai crewai-tools python-dotenv
 
    Create a .env file next to this script:
        OPENAI_API_KEY=your-openai-key
        SERPER_API_KEY=your-serper-key
 
Run:
    python Tech-News_Crew.py
"""

import os
import sys
from datetime import date

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# --- Load API keys from the .env file ---------------------------------------
load_dotenv()

for key in ("SERPER_API_KEY", "OPENAI_API_KEY"):
    if not os.getenv(key):
        sys.exit(f"Missing {key}. Add it to your .env file.")

today = date.today().strftime("%B %d, %Y")

# --- Tool: only the Researcher gets this -------------------------------------
search_tool = SerperDevTool()

# --- Agents ------------------------------------------------------------------
researcher = Agent(
    role="Tech News Researcher",
    goal=f"Find the 3 most important tech news stories published today ({today}).",
    backstory=(
        "You are a sharp tech journalist who lives in the news cycle. "
        "You verify stories through web search, favour recent and credible "
        "sources, and always report the facts accurately."
    ),
    tools=[search_tool],  # can search the web
    verbose=True,
)

writer = Agent(
    role="Newsletter Writer",
    goal="Turn researched tech stories into a punchy, readable 5-line newsletter.",
    backstory=(
        "You are a newsletter editor known for crisp, engaging writing. "
        "You never research on your own; you work only with the material "
        "your researcher hands you."
    ),
    tools=[],  # cannot search at all
    verbose=True,
)

# --- Tasks -------------------------------------------------------------------
research_task = Task(
    description=(
        f"Search the web for today's ({today}) top 3 tech news stories. "
        "For each story, give the headline, a 1-2 sentence summary, and the source."
    ),
    expected_output=(
        "A list of exactly 3 tech stories, each with a headline, "
        "a short summary and a source."
    ),
    agent=researcher,
)

write_task = Task(
    description=(
        "Using ONLY the stories provided by the researcher, write a short "
        "tech newsletter. Do not add stories or facts that are not in the "
        "researcher's output."
    ),
    expected_output=(
        "A newsletter of EXACTLY 5 lines, no more and no less: "
        "line 1 is a catchy title, lines 2-4 are one line per story, "
        "and line 5 is a short sign-off. No blank lines, no extra text."
    ),
    agent=writer,
    context=[research_task],  # hands the Researcher's output to the Writer
)

# --- Crew --------------------------------------------------------------------
news_crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,  # research first, then write
    verbose=True,
)

if __name__ == "__main__":
    result = news_crew.kickoff()
    print("\n" + "=" * 60)
    print("FINAL NEWSLETTER")
    print("=" * 60)
    print(result)