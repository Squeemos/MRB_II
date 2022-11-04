from setuptools import setup, find_packages

def main() -> int:
    # p = find_packages() # Maybe try and parse better?
    packages = ['yt_utils', 'ytdb', 'ytdb.reader', 'ytdb.load']

    setup(name = 'MRB', version = '1.0', packages = packages)

if __name__ == '__main__':
    SystemExit(main())
