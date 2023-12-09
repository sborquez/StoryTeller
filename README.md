# StoryTeller
Create interactive text-based stories with LangChain


## Project Structure

The project is structured as follows:

```
.
├── README.md
├── requirements.txt
├── LICENSE
├── .env
├── .gitignore
└── story_teller
    ├── __init__.py
    ├── __main__.py  # main entry point
    ├── story        # story data structures
    │   ├── __init__.py 
    │   ├── page.py
    │   ├── tree.py
    │   └── path.py
    ├── gui 
    │   ├── __init__.py
    │   ├── app.py    # main entrypoint for the GUI
    │   └── states.py # game state machine
    ├── agents  
    │   ├── __init__.py
    │   ├── learner.py  # RL agent for learning the best story
    │   ├── writer.py   # LLM agent for writing stories
    │   └── drawer.py   # Multimodal LLM agent for drawing stories
    └── tools.py   # utility functions
```

## Quickstart

### Installation

To install the project, run the following command:

```bash
conda create -n storyteller python=3.11
conda activate storyteller
pip install -r requirements.txt
```

### Setting up the environment variables

Use the `.env` file to set up the environment variables. The following variables are required:

- `STORYTELLER_LOGS_DIR`: the directory where the logs are stored
- `STORYTELLER_DATA_DIR`: the directory where the story data is stored
- `STORYTELLER_OPENAI_API_KEY`: the API key for the OpenAI API
- `STORYTELLER_GUI_WIDTH`: the width of the GUI window (default: `800`)
- `STORYTELLER_GUI_HEIGHT`: the height of the GUI window (default: `600`)
- `STORYTELLER_GUI_FULLSCREEN`: whether to run the GUI in fullscreen mode or not (default: `False`)

### Running the GUI

To run the GUI, run the following command:

```bash
python -m story_teller
```

## How does it work?

### Story Data Structure

The story data structure is composed of three main components:

- `Page`: a page is a single node in the story tree. It contains an unique ID, the description text of the page, the image, the action that led to that page, the karma points associated this page, and the list of possible pages that can be reached from this page.
- `Path`: a path is a sequence of pages. It is used to store the current path in the story tree during a session. It contains the list of pages that have been visited. And the karma points associated with the path.
- `Tree`: a tree is a collection of pages. It contains the root page, and a list of all the pages in the tree. It is used to store the story data and reuse it across sessions.


### Agents

The project contains three agents:

- `Learner`: this agent uses reinforcement learning to learn to generate the best story. It uses the Q-learning algorithm to learn the best paths that led to the best stories. It uses the players' feedback to update the Q-values.
- `Writer`: this agent uses the OpenAI API to generate new pages for the story. It uses the `Learner` agent to select a previous generated page or generate a new one.
- `Drawer`: this agent uses the OpenAI API to generate a image for a given page. It uses the `Writer` agent to generate the page text.


### GUI

The GUI is based on the Python library `PyGame`. It shows the current page text, the possible actions, the image, and the karma points.

