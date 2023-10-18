# Contributing Guidelines

Fork the repo and submit a PR. No specific format is required for PRs at this points...as long as its reasonable/understandble and focuses on the core development areas needed (discussed below) it will be integrated.

## TODOs
Until a first version is released, we are using inline TODO tags to track issues and work to be done. 

If you want to discuss anything with us though feel free to use the issues tab.

**Contributing in places with TODO tags is preferred (but not reqd).**

In addition to TODOs found in the codebase, the following are areas need development work:

- **Tests**: 
    + unit tests: only some unit tests are complete, some are scaffolded, and some are missing.
    + evals: evals are partially complete and need to be finished

- **Linting**: Started a Makefile to make it easy for devs (and later github actions) to run linting and things but didn't finish this. This needs to be robust before release.

- **Usage Scripts**: Currently the main scripts that the user runs are generate-ws, fillout-ws, generate-report and generate-annots (see pyproject.toml). However it would be nice to have a script for preprocessing the data for the ```ReadDesignChain``` and ```ReadSubmittalChain``` in case users want to just run those individually and not wait for the whole generate-ws/fillout-ws/etc workflow. (Also fillout-ws can take a while depending on the size of the submittal so it would be nice to have a way to run that separately as well)

- Docs: We need to write documentation for the codebase. This should be done using Jupyter Notebooks and Sphinx (on readthedocs). The docs should be written in a way that allows for easy contribution from the community.

- **Data**: More data to populate the equipment template database is helpful

- **Graphical User Interface**: we decided to just use a CLI for the MVP but if you feel like building out a simple GUI that would be cool.

## Directory Structure

```sh
# START: EXPLAINER FILES/FOLDERS
├── CONTRIBUTING.md # 🎯 you are here
├── README.md # entry point for the repo
├── LICENSE.md # available to use by anyone for anything
├── docs # docs for the codebase (TODO: currently just scaffolded)
├── images # for images in README or other top-level .md files
# END: EXPLAINER FILES/FOLDERS

# START: USER FACING FILES/FOLDERS
├── data # the only folder users should ever touch (they put their projects designs and submittals here)
│   ├── demo-01 # the demo project folder with 3 things (designs, submittals, and scope)
│   ├── demo1-ws-answers.xlsx # only here during development to make sure the agent retreives the correct data (the answers the agent should return in its filled out worksheet)
│   └── templates # equipment templates (used to determine what specs to look for)
├── cli-config.yaml # ...
├── session-config.yaml # ...
├── .env # ...
# END: USER FACING FILES/FOLDERS


# START: MECHE COPILOT CODE
├── meche_copilot # all the meche_copilot code
│   ├── chains
│   ├── cli
│   ├── get_comparison_results.py
│   ├── get_eq_specs_and_comps.py
│   ├── get_equipment_results.py
│   ├── pdf_helpers
│   ├── schemas.py
│   └── utils
├── tests
│   ├── _test_data
│   ├── data.py
│   ├── evals # agent evals (partially complete -- needs work)
│   ├── foo_test.py
│   ├── helpers 
│   ├── integration_tests # TODO: need to write integration tests
│   └── unit_tests # all unit tests (main file name with _test.py suffix)
# END: MECHE COPILOT CODE

# START: DEV CONTAINER/DEVELOPMENT FILES/FOLDERS
├── .devcontainer # ...
├── Dockerfile # ...
├── dev.Dockerfile # 
├── Makefile # ...
├── poetry.toml # poetry config
├── pyproject.toml # poetry config
```

## Contributing Instructions

### 1) Fork the repo
[Here are some instructions](https://docs.github.com/en/get-started/quickstart/fork-a-repo) on how to do that if you are unfamiliar

### 2) Start docker daemon
Dev container is configured to run docker so it will throw an error if you try to launch the dev container before starting the docker daemon. To launch either run docker gui or run ```docker info``` in terminal

### 3) Launch dev container
From VS-code make sure you have the [DevContainers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension intalled then launch the dev container like this or by clicking the green button in the bottom left of the VS-code window
![launch dev container](images/launch_dev_container.png)

At this point all dev dependencies have been installed and you can start running code, tests, making changes, etc.

### 4) Contribute
Probably wise to start by running unit tests to wrap your head around how things work and are called and unitized. But do whatever suits your fancy.

For example, now your terminal in VS-code will be running in the dev container so you can make sure poetry successfully installed all deps by running ```poetry show``` in the terminal

![terminal in dev container](images/terminal_in_container.png)

OR you can launch ipython by running ```ipython``` in the terminal

![ipython usage](images/ipython_usage.png)

OR you can run unit tests like this

```sh
poetry run pytest tests/unit_tests/copilot/generate_ws_test.py
```

![pytest usage](images/pytest_usage.png)

OR you can run any of the scripts by typing copi (tab completion to get the copilot-bla scripts)

![copilot scripts](images/copilot_scripts.png)

Running the `generate-ws` script looks like this 
![generate-ws](images/generate-ws.png)

and outputs a worksheet in the data/ dir which has sources, specs definitions and results for each piece of equipment scoped in the scope excel file (specified in session-config.yaml)
![ws1](images/ws1.png)

![ws2](images/ws2.png)

![ws3](images/ws3.png)

Running the `copilot-fillout-ws` script looks like this - UNFINISHED
Running the `copilot-generate-report` script looks like this - UNFINISHED
Running the `copilot-generate-annots` script looks like this - UNFINISHED


### 5) Submit PR
Once you are done making changes and want to submit a PR you can do so by clicking the "create pull request" button in the github UI

## Development Design Decisions

**1) Why'd you use pdf parsing instead of OCR?**
At the time OCR seemed like a potential rabbit hole/time sink so we tried using pdf parsing (via python's camelot) and its seemed effective so we went with it while acknowleding that a combination of OCR and pdf parsing would be ideal for future releases and if/when a more robust solution is needed.

Towards the end we realized that camelot had trouble parsing tables that were complex multi-line engineering tables like below so we were working on implementing a little postprocessor (see postprocess_camelot_df) where we cleaned up the DF and made a decision about what to use based on what the LLM got for metadata and what camelot extracted. You were in the middle of testing this in nbs (see camelot eval ipynb) and then gonna go through and tie everything together (all the chains and CLI scripts) for the demo. You'd prob have to modify the worksheet depending on how you decide to have the llm do the final lookup/analyze part. 

![erv_schedule](images/erv_schedule.png)

**2) Why didn't you use langchain's prebuilt document retreival chains?**
We tried using various langchain prebuilt document retreival chains (see LookupChain) but its wasn't doing a good/consistent job so we decided to write a custom retreiver for reading designs and submittals (see ```ReadDesignChain``` and ```ReadSubmittalChain```). 

these are basically implemented but you didn't finish testing them and tieing them back into the LookupSpecsChain. Actually you weren't sure if you were gonna do that or ditch the LookupSpecsChain in favor of AnalyzeSpecsChain which would ask the LLM on a per spec basis. Perhaps that is overkill and there is a good balance you can find where you have it do a few+ specs at a time....maybe update the chunker to handle this.


- Oh...and you need to write the generate engineering callout/annotations but are waiting on some examples of how that should look stylistically...once you have that its a few hrs of work with MuPDF and done.


