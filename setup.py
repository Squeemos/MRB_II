from setuptools import setup, find_packages

blacklisted = ["models", "etl"]

p = find_packages()
p = [x for x in p if not "online" in x]
p = [x for x in p if x not in blacklisted]

setup(name = 'MRB', version = '1.0', packages = p)
