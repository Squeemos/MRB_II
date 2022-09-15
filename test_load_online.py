import os
import json
import string
from urllib.request import urlopen

if __name__ == '__main__':
    my_url = "https://raw.githubusercontent.com/Squeemos/MRB_II/main/data/2022_09_12_output.json"

    response = urlopen(my_url)
    data = json.loads(response.read())
