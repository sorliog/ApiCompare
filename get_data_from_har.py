import sys
import json

if len(sys.argv) != 2:
    print("Usage: python get_data_from_har.py <har_file>")
    exit(1)


with open(sys.argv[1]) as har_file:
    json_data = json.load(har_file)


for entry in json_data['log']['entries']:
    rq = entry['request']
    method = rq['method']
    url = rq['url']
    print(url + "," + method)