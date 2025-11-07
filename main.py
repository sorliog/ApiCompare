import argparse
from dotenv import load_dotenv
import requests
import csv
from deepdiff import DeepDiff
from deepdiff.helper import SetOrdered
from termcolor import colored
import re
import os

MAX_DIFF_PRINT_LENGTH = 50
ROWSET_NESTED_DIFF_REGEX_PATTERN = r"root\[\'RowSet\'\]\[\'Row\']\[\d+\]"


def get_headers_from_env(api_key):
    api_key = api_key.upper().strip()
    if api_key.endswith("."):
        api_key = api_key[:-1]
    load_dotenv()
    headers_list = [e for e in os.environ.keys() if e.startswith(f"{api_key}.HEADERS.")]
    if len(headers_list) > 0:
        headers = {}
        for header in headers_list:
            value = os.environ[header]

            headers[header[header.rindex(".") + 1:]] = value
        return headers
    return None


def get_closing_chars_from_string(value):
    stack = []
    for c in value[:MAX_DIFF_PRINT_LENGTH]:
        if c == "{":
            stack.append("}")
        elif c == "[":
            stack.append("]")
        elif c == "(":
            stack.append(")")
    return "".join(stack)


def print_diff_summary(diff, minimal_output=False, verbose_output=False, indent=0):
    """
    Prints a readable summary of the differences between two JSON files.
    Takes a DeepDiff object as input.
    """
    if not diff:
        print(colored(f"{'    ' * indent}The two files are identical!", 'green'))
        return

    if minimal_output and not verbose_output:
        print(colored(f"{'    ' * indent}The two files are different!", 'red'))
        return

    if "values_changed" in diff and "root['RowSet']['Row'][0]" in diff['values_changed']:
        matching_strings = []
        if 'iterable_item_removed' in diff:
            matching_strings = matching_strings + [s for s in diff['iterable_item_removed'] if
                                                   re.search(ROWSET_NESTED_DIFF_REGEX_PATTERN, s)]
        if 'iterable_item_added' in diff:
            matching_strings = matching_strings + [s for s in diff['iterable_item_added'] if
                                                   re.search(ROWSET_NESTED_DIFF_REGEX_PATTERN, s)]
        if len(matching_strings) > 0:
            print(colored(f"\n{'    ' * indent}Detected differing nested list structures in ", 'red') + colored(
                "root['RowSet']['Row']",
                'yellow'))

    # Added keys
    if 'dictionary_item_added' in diff:
        print(colored(f"\n{'    ' * indent}Added keys:", 'green'))
        added_items = diff['dictionary_item_added']

        # If it's a set, just iterate over its items (paths)
        if isinstance(added_items, set) or isinstance(added_items, list) or isinstance(added_items, SetOrdered):
            for item in added_items:
                print(f"{'    ' * indent}  - {colored(item, 'blue')}")

        # If it's a dict, iterate over key/value pairs
        elif isinstance(added_items, dict):
            for item, value in added_items.items():
                print(f"{'    ' * indent}  - {colored(item, 'blue')}: {value}")

        # (Optional) Catch other types just in case
        else:
            print(f"{'    ' * indent}  - Unexpected type: {type(added_items)}")

    # Removed keys
    if 'dictionary_item_removed' in diff:
        print(colored(f"\n{'    ' * indent}Removed keys:", 'red'))
        for item in diff['dictionary_item_removed']:
            print(f"{'    ' * indent}  - {colored(item, 'red')}")

    # Changed values
    if 'values_changed' in diff:
        print(colored(f"\n{'    ' * indent}Changed values:", 'magenta'))
        for item, change in diff['values_changed'].items():
            old_value = str(change['old_value'])
            new_value = str(change['new_value'])

            if len(old_value) > MAX_DIFF_PRINT_LENGTH:
                old_value = old_value[:MAX_DIFF_PRINT_LENGTH] + '... ' + get_closing_chars_from_string(old_value)
            if len(new_value) > MAX_DIFF_PRINT_LENGTH:
                new_value = new_value[:MAX_DIFF_PRINT_LENGTH] + '... ' + get_closing_chars_from_string(new_value)

            print(
                f"{'    ' * indent}  - {colored(item, 'yellow')} changed from {colored(old_value, 'red')} to {colored(new_value, 'green')}")

            if type(change['old_value']) is dict and type(
                    change['new_value']) is dict and indent < 1 and verbose_output:
                deeper_diff = compare_json(change['old_value'], change['new_value'])
                if deeper_diff is not None:
                    print(colored(f"\n{'    ' * indent}Detailed changes:", 'magenta'))
                    print_diff_summary(deeper_diff, minimal_output=minimal_output, verbose_output=verbose_output,
                                       indent=indent + 1)

    # Type changes (if any)
    if 'type_changes' in diff:
        print(colored("\nType changes:", 'cyan'))
        for item, change in diff['type_changes'].items():
            print(
                f"{'    ' * indent}  - {colored(item, 'white')}: type changed from {colored(change['old_type'], 'red')} to {colored(change['new_type'], 'green')}")

    # Dictionary item moved (if any)
    if 'dictionary_item_moved' in diff:
        print(colored("\nMoved items:", 'blue'))
        for item in diff['dictionary_item_moved']:
            print(f"  - {colored(item, 'magenta')}")

    # Any other differences (items added or removed from lists)
    if 'iterable_item_added' in diff:
        print(colored("\nAdded items in lists:", 'green'))
        for item, value in diff['iterable_item_added'].items():
            print(f"  - {colored(item, 'blue')}: {value}")

    if 'iterable_item_removed' in diff:
        print(colored("\nRemoved items in lists:", 'red'))
        for item in diff['iterable_item_removed']:
            print(f"  - {colored(item, 'red')}")


def print_comparison_report(differences, total_calls, error_calls, identical_count, different_count,
                            minimal_output=False, verbose_output=False):
    # Print the final comparison report in a clean, structured format
    print("\n" + colored("Comparison Report", 'yellow'))
    print(f"Total calls made: {colored(total_calls, 'cyan')}")
    print(f"Error calls received: {colored(error_calls, 'red')}")
    print(f"Identical JSON responses: {colored(identical_count, 'green')}")
    print(f"Different JSON responses: {colored(different_count, 'red')}")

    if not minimal_output or verbose_output:
        print(colored("\nDifferences found:", 'yellow'))
    for diff in differences:
        print(
            f"\n{colored(diff['api_a_endpoint'], 'blue')} ({colored(diff['api_a_method'], 'blue')}) vs {colored(diff['api_b_endpoint'], 'blue')} ({colored(diff['api_b_method'], 'blue')})")
        print_diff_summary(diff['differences'], minimal_output=minimal_output, verbose_output=verbose_output)
        print("-" * 100)


# Function to make API request and fetch the JSON data
def fetch_json(endpoint, method='GET', headers=None, data=None):
    try:
        if method.upper() == 'POST':
            response = requests.post(endpoint, headers=headers, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(endpoint, headers=headers, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(endpoint, headers=headers)
        else:
            # Default to GET if method is not specified or is GET
            response = requests.get(endpoint, headers=headers)

        response.raise_for_status()  # Will raise an exception for 4xx/5xx errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {endpoint} with {method}: {e}")
        return None


# Function to compare JSON responses
def compare_json(json_a, json_b):
    # Use DeepDiff to find the differences
    diff = DeepDiff(json_a, json_b, ignore_order=True,
                    ignore_numeric_type_changes=True)
    return diff


# Function to read CSV file containing API endpoints and methods
def read_csv(file_name):
    with open(file_name, mode='r') as file:
        reader = csv.reader(file)
        endpoints = []
        for row in reader:
            if row is not None and len(row) > 0 and not row[0].strip().startswith("#"): # Ignore comments
                endpoints.append(row)
    return endpoints


# Main function to perform the comparison
def compare_apis(csv_file, api_a_headers, api_b_headers, minimal_output=False, verbose_output=False):
    # Read the CSV file containing the endpoint pairs and methods
    endpoints = read_csv(csv_file)

    # Statistics
    total_calls = 0
    identical_count = 0
    different_count = 0
    differences = []
    error_calls = 0

    # Iterate through each row of the CSV
    for row in endpoints:
        if len(row) != 4:
            continue
        api_a_endpoint = row[0]
        api_a_method = row[1]
        api_b_endpoint = row[2]
        api_b_method = row[3]

        api_a_endpoint = api_a_endpoint.strip()
        api_a_method = api_a_method.strip()
        api_b_endpoint = api_b_endpoint.strip()
        api_b_method = api_b_method.strip()
        total_calls += 1
        if not minimal_output:
            print(f"Comparing: {api_a_endpoint} ({api_a_method}) with {api_b_endpoint} ({api_b_method})")

        # Fetch the JSON responses from both APIs
        json_a = fetch_json(api_a_endpoint, api_a_method, headers=api_a_headers)
        json_b = fetch_json(api_b_endpoint, api_b_method, headers=api_b_headers)

        if json_a is not None and json_b is not None:
            # Compare the two JSON responses
            diff = compare_json(json_a, json_b)

            if diff:  # If there are differences
                different_count += 1
                differences.append({
                    "api_a_endpoint": api_a_endpoint,
                    "api_b_endpoint": api_b_endpoint,
                    "api_a_method": api_a_method,
                    "api_b_method": api_b_method,
                    "differences": diff
                })
            else:
                identical_count += 1
                differences.append({
                    "api_a_endpoint": api_a_endpoint,
                    "api_b_endpoint": api_b_endpoint,
                    "api_a_method": api_a_method,
                    "api_b_method": api_b_method,
                    "differences": None
                })
        else:
            error_calls += 1
            print(f"Skipping comparison for {api_a_endpoint} and {api_b_endpoint} due to error in fetching responses")

    print_comparison_report(differences, total_calls, error_calls, identical_count, different_count,
                            minimal_output=minimal_output, verbose_output=verbose_output)


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-?", "-h", "--help", action="help", help="show this help message and exit")
parser.add_argument("-m", "--minimal", help="Minimal output.", action=argparse.BooleanOptionalAction)
parser.add_argument("-v", "--verbose", help="Verbose output ie Show detailed changes). Overrides --minimal",
                    action=argparse.BooleanOptionalAction)
parser.add_argument("csv_file", help="CSV file that contains URLS and methods for calls.")
args = parser.parse_args()

api_a_headers = get_headers_from_env("api_a")
api_b_headers = get_headers_from_env("api_b")

csv_file = args.csv_file
compare_apis(csv_file, api_a_headers, api_b_headers, minimal_output=args.minimal == True,
             verbose_output=args.verbose == True)
