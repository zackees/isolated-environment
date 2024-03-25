import sys

try:
    from isolated_environment import api

    print(api)
    print("Successfully imported IsolatedEnvironment")
    # print the path to find the isolated_environment module
    # print(api.__file__)
    print(f"IsolatedEnvironment path: {api.__file__}")
    # print out the python path
    # print(sys.path)
    # print out the python executable
    print(f"Python executable: {sys.executable}")
    sys.exit(0)
except ImportError:
    print("Failed to import IsolatedEnvironment")
    sys.exit(1)
