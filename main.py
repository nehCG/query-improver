import run
import sys


def main():
    # receive user input
    # format: <google api key> <google engine id> <precision> <query>
    run.search(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

if __name__ == "__main__":
    main()
