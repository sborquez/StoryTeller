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
├── notebooks          # Jupyter notebooks for experimenting
│   └── prompts.ipynb  # notebook for experimenting with the LangChain
└── story_teller
    ├── __init__.py
    ├── __main__.py  # main entry point
    ├── story        # story data structures
    │   ├── __init__.py 
    │   ├── page.py
    │   ├── tree.py
    │   └── path.py
    ├── app 
    │   ├── __init__.py
    │   ├── {ui}.py    # main entrypoint for the UI (e.g. cli for command line interface)
    │   ├── base.py    # defines the base UI class for UI independent code of the game
    │   └── states     # game state machine
    ├── teller  
    │   ├── __init__.py
    │   ├── learner.py  # RL agent for learning the best story
    │   └── chains.py   # Multimodal LLM chains for writing, drawing, and telling stories
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

- `STORYTELLER_LOGS_DIR`: The directory where the logs are stored
- `STORYTELLER_DATA_DIR`: The directory where the story data is stored
- `STORYTELLER_GUI_WIDTH`: The width of the GUI window (default: `800`)
- `STORYTELLER_GUI_HEIGHT`: The height of the GUI window (default: `600`)
- `STORYTELLER_GUI_FULLSCREEN`: Whether to run the GUI in fullscreen mode or not (default: `False`)
- `GOOGLE_APPLICATION_CREDENTIALS`: Credentials path for the Google Cloud API
- `OPENAI_API_KEY`: API key for the OpenAI API

Optionally, you can set the following variables:

- `STORYTELLER_DEBUG`: whether to run in debug mode or not (default: `false`)
- `STORYTELLER_LOG_LEVEL`: the log level (default: `INFO`)


### Testing

To run the tests, run the following command:

```bash
python -m pytest
```

### Running the GUI

To run the GUI, run the following command:

```bash
python -m story_teller
```

or for a specific UI:

```bash
python -m story_teller.cli
```


## How does it work?

### Story Data Structure

The story data structure is composed of three main components:

- `Page`: a page is a single node in the story tree. It contains an unique ID, the description text of the page, the image, the action that led to that page, and the karma points associated this page.
- `Path`: a path is a sequence of pages. It is used to store the current path in the story tree during a session. It contains the list of pages that have been visited. And the karma points associated with the path.
- `Tree`: a tree is a collection of pages. It contains the root page, and all the pages with the tree structure. It is used to store and access all the pages in the story.


### Teller Components

The project contains two teller components:

- `Learner`: This agent uses reinforcement learning to learn to generate the best story. It uses the Q-learning algorithm to learn the best paths that led to the best stories. It uses the players' feedback to update the Q-values.
- `Chains`: This component uses the LLM like OpenAI ChatGPT, and other APIs with a LangChain chain, to generate new pages for the story. It uses the `Learner` agent to select a previous generated page or generate a new one. It can write (text), draw (image), and tell (audio) stories.

### UI

We defined a UI agnostic interface for the game. The UI is composed of RenderData structure defined in `story_teller/app/base.py`. The UI is responsible for rendering the game, and for handling the user input. The UI is also responsible for handling the game state machine. The UI is defined in `story_teller/app/{ui}.py`.
