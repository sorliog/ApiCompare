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
* Outputs a detailed comparison report, including:
    * Total API calls
    * Identical vs different responses
    * Summary of differences (formatted with color for readability)
* Handles errors gracefully if API requests fail.

## Requirements

* Python 3.x
* `requests` library for HTTP requests
* `deepdiff` library for deep comparison of JSON objects
* `termcolor` library for colored terminal output

You can install the required dependencies using pip:

```bash
pip install requests deepdiff termcolor
```

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

2. **Run the script**: From the command line, execute the script by providing the path to the CSV file as an argument.

```bash
python main.py <path_to_csv_file>
```

Example:

```bash
python main.py endpoints.csv
```

3. **View the output**: The script will print a detailed comparison report to the console. It will show:

* Total number of API calls made
* Number of identical responses
* Number of differing responses
* Detailed differences for any responses that don't match
