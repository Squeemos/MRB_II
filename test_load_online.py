import os
import json
import string
from urllib.request import urlopen

if __name__ == '__main__':
    my_url = "https://squeemos.pythonanywhere.com/static/2022_09_07_output.json"

    response = urlopen(my_url)
    data = json.loads(response.read())
    print(data)
