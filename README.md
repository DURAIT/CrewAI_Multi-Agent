# News_Crew: A Two-Agent CrewAI Newsletter Generator

A small [CrewAI](https://docs.crewai.com/) project where two agents work in a line:

1. A **Researcher** searches the web (via `SerperDevTool`) and finds today's top 3 tech news stories.
2. A **Writer**, who has **no tools and cannot search**, turns the Researcher's findings into a **5-line newsletter**.

The tasks run **sequentially**, and the Writer only works because the Researcher's output is explicitly handed to it.

---

## How It Works

```
┌────────────────────┐    research output    ┌────────────────────┐
│     Researcher     │ ────────────────────► │       Writer       │
│  tools: Serper     │   (context handoff)   │    tools: none     │
│  finds top 3 news  │                       │  writes 5 lines    │
└────────────────────┘                       └────────────────────┘
        Task 1                                       Task 2
                  Process.sequential (1 → 2)
```

| Component | Details |
|-----------|---------|
| **Researcher agent** | Own role, goal and backstory. Carries `tools=[SerperDevTool()]`. |
| **Writer agent** | Own role, goal and backstory. Carries `tools=[]`, so it can't browse. |
| **`research_task`** | Finds today's top 3 tech stories (headline, short summary, source). |
| **`write_task`** | Writes the newsletter. Receives the research via `context=[research_task]`. |
| **Crew** | `process=Process.sequential`, `verbose=True`. |

### The handoff

Task outputs do not pass between tasks automatically. This line in `write_task` is what gives the Writer the Researcher's results:

```python
context=[research_task]
```

Remove it and the Writer has nothing to write from.

### The 5-line rule

The Writer's `expected_output` states the format explicitly:

> A newsletter of EXACTLY 5 lines: line 1 is a catchy title, lines 2-4 are one line per story, and line 5 is a short sign-off.

---

## Prerequisites

- **Python 3.10 or newer** (3.12 recommended)
- An **OpenAI API key** (CrewAI uses OpenAI models by default)
- A **Serper API key** for web search

### Getting the API keys

| Key | Where to get it |
|-----|-----------------|
| `OPENAI_API_KEY` | <https://platform.openai.com/api-keys> |
| `SERPER_API_KEY` | <https://serper.dev> (sign up, then copy the key from the dashboard; a free tier is available) |

---

## Setup

### 1. Put the project in a folder

```
CrewAI_Multi-Agent/
├── news_crew.py
├── README.md
└── .env              ← you will create this
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
cd path\to\CrewAI_Multi-Agent
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
cd path/to/CrewAI_Multi-Agent
python3 -m venv venv
source venv/bin/activate
```

If PowerShell blocks activation, run this once and try again:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install "crewai[tools]" python-dotenv
```

### 4. Create the `.env` file

In the same folder as `news_crew.py`, create a file named exactly `.env`:

```env
OPENAI_API_KEY=your-openai-key-here
SERPER_API_KEY=your-serper-key-here
```

Rules for this file:

- No quotes around the values and no spaces around `=`.
- Never commit it. If you use Git, add `.env` to your `.gitignore`.
- The script calls `load_dotenv()` at startup and exits with a clear message if a key is missing.

---

## Run It

```bash
python news_crew.py
```

With `verbose=True`, you'll see the full process in your terminal:

1. The Researcher starts, decides to use the search tool, and runs queries.
2. The Researcher returns its 3 stories.
3. The Writer starts and reads the Researcher's output.
4. The Writer produces the final newsletter.

The script finishes by printing the result under a **FINAL NEWSLETTER** banner.

### Example output (illustrative)

```
Tech Today: Your 60-Second Briefing
Company A unveils a new AI chip promising faster on-device inference.
Regulators open a review into Company B's latest acquisition.
Company C reports a security breach and urges users to reset passwords.
That's the wrap, see you tomorrow!
```

Your results will differ because they depend on the news of the day.

---

## Code Walkthrough

### 1. Setup and key loading
```python
load_dotenv()
```
Loads `OPENAI_API_KEY` and `SERPER_API_KEY` from `.env` into the environment. `SerperDevTool` reads `SERPER_API_KEY` automatically.

### 2. The date
```python
today = date.today().strftime("%B %d, %Y")
```
The current date is inserted into the Researcher's goal and task, so searches focus on **today's** news instead of whatever the model remembers.

### 3. Agents
```python
researcher = Agent(role=..., goal=..., backstory=..., tools=[search_tool], verbose=True)
writer     = Agent(role=..., goal=..., backstory=..., tools=[],            verbose=True)
```
The only structural difference is the `tools` list. That is what gives one agent web access and keeps the other offline.

### 4. Tasks
```python
research_task = Task(description=..., expected_output=..., agent=researcher)
write_task    = Task(description=..., expected_output=..., agent=writer,
                     context=[research_task])
```

### 5. Crew
```python
news_crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    verbose=True,
)
result = news_crew.kickoff()
```
`Process.sequential` runs the tasks in list order, so research always finishes before writing begins.

---

## Customization Ideas

| Want to... | Change this |
|------------|-------------|
| Cover a different topic (e.g. AI, crypto, space) | Edit the Researcher's `goal` and `research_task.description` |
| Get more or fewer stories | Change "top 3" in the Researcher's goal and task, and adjust the Writer's line rules to match |
| Change the newsletter length | Update the line count in `write_task.expected_output` |
| Change the tone (casual, formal, witty) | Edit the Writer's `backstory` and `goal` |
| Use a different LLM | Pass `llm=...` when creating each `Agent` |
| Save the newsletter to a file | Add `output_file="newsletter.txt"` to `write_task` |
| Search only recent results | Configure `SerperDevTool` (for example, `SerperDevTool(n_results=10)`) |

---

## Project Structure

```
CrewAI_Multi-Agent/
├── news_crew.py   # the crew: agents, tasks, and kickoff
├── .env           # API keys (not committed)
└── README.md      # this file
```

---

## Troubleshooting

| Problem | Likely cause and fix |
|---------|----------------------|
| `Missing SERPER_API_KEY` / `Missing OPENAI_API_KEY` | The key is not in `.env`, the file isn't next to the script, or it's named `.env.txt`. Check the filename and spelling. |
| `401 Unauthorized` or "invalid API key" | The key is wrong, expired, or has extra spaces or quotes. Re-copy it into `.env`. |
| OpenAI quota or billing error | Your OpenAI account has no credits or has hit a rate limit. Check your billing page. |
| Output is not exactly 5 lines | LLMs occasionally add a blank line or a preface. Re-run, or tighten the Writer's `expected_output` (for example, "No preface, no blank lines"). |
| Stories look old or generic | Make sure the date is in the task description and that the Researcher actually called the search tool (visible in verbose logs). |
| Nothing happens or it seems stuck | Web search plus two LLM calls can take 30-90 seconds. Watch the verbose output for progress. |
| `.env` changes are ignored | Restart the script, since the file is only read at startup. |

---

## Notes

- This project is a learning example of **sequential multi-agent workflows**: tool access per agent, and explicit context handoff between tasks.
- News quality depends on search results and the model. Verify important facts before publishing anything.
