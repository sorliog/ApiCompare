# API Comparison Script

This Python script compares the responses from two different APIs by fetching JSON data from their endpoints and
performing a detailed comparison to identify differences. It outputs a summary of the differences, including added,
removed, and changed keys, values, or types. The script can be run from the command line and uses a CSV file containing
pairs of API endpoints and methods (GET, POST, etc.).

## Features

* Fetches JSON data from two APIs (specified in a CSV file) using different HTTP methods (GET, POST, PUT, DELETE).
* Compares JSON responses using the DeepDiff library.
* Identifies differences such as:
    * Added/removed keys
    * Changed values
    * Type changes
    * Moved dictionary items
    * Differences in nested lists

* Flexible output modes:
    * Minimal → Just shows if APIs differ.
    * Verbose → Displays deep nested differences.
* Uses environment-based header management via .env for secure configuration.
* Outputs a detailed comparison report, including:
    * Total API calls
    * Identical vs different responses
    * Summary of differences (formatted with color for readability)
* Handles errors gracefully if API requests fail.

## Requirements

* Python 3.x
* `requests`
* `dotenv`
* `python-dotenv`
* `deepdiff`
* `termcolor`
  You can install the required dependencies using pip:

You can install python using `winget` or the [official website](https://www.python.org/downloads/)

* With `winget `
  ```bash
  winget install Python.Python.3.14 
  ```
  or
* Download and Install the Python Interpreter from https://www.python.org/downloads/. Make sure the version is above Python3.

# Installation

1. **Clone or download the repository:**

```bash
git clone https://github.com/sorliog/ApiCompare
cd ApiCompare
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Create a .env file in the same directory as the script.**

```bash
touch .env
```

4. **Configure you environment (see Next Section)**

# Environment Configuration (.env)

The script loads HTTP headers for each API from environment variables in your .env file.
The headers should follow this format:

```txt
api_a.headers.AccountNumber=123456
api_a.headers.UserId=myuser
api_a.headers.Cookie="session_cookie_value"
api_a.headers.Authorization="Bearer token123"

api_b.headers.AccountNumber=123456
api_b.headers.UserId=myuser
api_b.headers.Cookie="session_cookie_value"
api_b.headers.Authorization="Bearer token456"

```

> **Tip:**
> The prefix must be lowercase (api_a.headers. or api_b.headers.), but the script automatically converts it to uppercase
> internally.

## Usage

1. **Prepare the CSV file**: The CSV file should contain four columns for each comparison:

* API A endpoint (URL)
* API A method (GET, POST, etc.)
* API B endpoint (URL)
* API B method (GET, POST, etc.)

Example `endpoints.csv`:

```csv
https://api.example.com/data,GET,https://api.another.com/data,GET
https://api.example.com/create,POST,https://api.another.com/create,POST
```

> **Tip:** Lines beginning with # are ignored as comments.
>

2. **Run the script**: From the command line, execute the script by providing the path to the CSV file as an argument.

```bash
python main.py <path_to_csv_file>
```

Example:

```bash
python main.py endpoints.csv
```

## Optional Arguments

| Flag                 | Description                                                              |
|----------------------|--------------------------------------------------------------------------|
| `-?`, `-h`, `--help` | Show help message.                                                       |
| `-m`, `--minimal`    | Minimal output mode (only show whether responses differ).                |
| `-v`, `--verbose`    | Verbose mode (show full nested JSON differences). Overrides `--minimal`. |

3. **View the output**: The script will print a detailed comparison report to the console. It will show:

* Total number of API calls made
* Number of identical responses
* Number of differing responses
* Detailed differences for any responses that don't match
