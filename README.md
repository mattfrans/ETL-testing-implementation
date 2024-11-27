# My submission for the following task:

Documentation of the tests aswell as instructions for how to run the program can be found in TESTING_DOCUMENTATION.md. 

Instructions for running with docker:

```bash
Build the Docker image
docker build . -t etl-tests

Run all tests in container
docker run --rm -v $(pwd):/etl etl-tests pytest tests/ -v
```

# Preliminary Task: Junior Test Engineer

Thank you for applying and showing interest for the position in the Junior Test Engineer at Reagle!

This task is designed to evaluate your approach to testing a simple Extract-Transform-Load (ETL) data pipeline.

## Task Overview

In this task, your objective is to review a data pipeline that was put together in a hurry by a somewhat lazy data engineer. Your job is to ensure everything works as expected. To do this, write the most relevant test cases for this example. The tests can be unit tests, end-to-end tests, or data validations, depending on what makes the most sense for the pipeline.

The implementation details are entirely up to you. For instance, you can decide whether to write the tests inside the pipeline module or as standalone scripts and choose whichever testing libraries you prefer. Feel free to make reasonable modifications to the existing code to align with your testing strategy.

That said, don’t feel pressured to cover every possible test case. We’re more interested in your approach, so don’t spend too much time on this. After all, we didn’t spend much time writing this task either!

### Requirements
- python3.10 or later
- SQLite3 (While completing this task does not require installing the SQLite3 CLI, it provides a convenient and straightforward way to access the database.)

## How to Get Started

### 1. Clone the Repository

Begin by cloning this repository to your local machine:

```
git clone https://github.com/reaglecode/test-case-preliminary-task.git
cd test-case-preliminary-task
```

### 2. Install Requirements

Next, install the required dependencies. It’s recommended to use a virtual environment for this step. **Remember to install testing libraries you wish to use or add them into requirements.txt file**.

```
pip install -r requirements.txt
```

Install SQLite3 if not installed yet. Refer to documentation in https://www.sqlite.org/index.html.

### 3. Initialise the Database and run the ETL

Once the dependencies are installed and you’ve verified that your Python version is compatible, you’re good to go.

Start by initializing the database

```
python main.py --method init
```

Then, run the pipeline to fetch open job applications provided by the city of Vantaa and load them into a local SQLite database:

```
python main.py
```


## Tips

### Sqlite3 CLI

To quickly verify that the pipeline has executed correctly, you can use the SQLite command-line interface:

```
sqlite3 db/reagle_test.db
```

Use the following command to check the tables in the database:

```
.tables
```

You can query the database with standard SQL commands, such as:

```
SELECT COUNT(*) FROM vantaa_open_applications;
```

### Database Connection String

The ```run_etl``` function accepts one parameter, which is the database connection string. For SQLite, the format is ```sqlite:///path/to/database/file```. You can also specify a different file path for a test database. While not mandatory, using a separate test database might simplify your workflow.

The pipeline provided does not necessarily need to pass your tests. Your job in this assignment is simply to implement the testing routines, not fix possible issues.

## Running into issues

### Run in Docker

If you encounter compatibility issues but have Docker installed, you can run the code inside a Docker container with the correct Python interpreter. Using Docker is definetely not required but it might help in certain scenarios.

You can build and enter a container with the following commands:

```
docker build . -t <container-name>
docker run -it <container-name> /bin/bash
```

For efficiency, you can mount a volume to your local test folder, so you don’t need to rebuild the container every time you update your code:

```
docker run -v $(pwd)/path/to/your/tests:/etl/path/to/your/tests -it <ontainer-name> /bin/bash
```

### For Windows Users

If you are running on Windows and run into issues, we recommend that you use the wsl extension and try to run code in linux enviroment.

Installation documentation fow wsl can be found here https://learn.microsoft.com/en-us/windows/wsl/install

## Good Luck!

Feel free to ask if you have any questions about the assignment or run into any issues.
