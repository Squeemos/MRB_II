from setuptools import setup, find_packages

p = find_packages()
p = [x for x in p if not "online" in x]

setup(name = 'MRB', version = '1.0', packages = p)
