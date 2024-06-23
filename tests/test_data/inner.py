import sys

try:
    import static_ffmpeg

    print(static_ffmpeg)
    print("Successfully imported static_ffmpeg")
    # print the path to find the isolated_environment module
    # print(api.__file__)
    print(f"IsolatedEnvironment path: {static_ffmpeg.__file__}")
    # print out the python path
    # print(sys.path)
    # print out the python executable
    print(f"Python executable: {sys.executable}")
    sys.exit(0)
except ImportError:
    print("Failed to import static_ffmpeg")
    sys.exit(1)
