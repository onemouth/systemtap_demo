from base64 import b64encode
import time


def main():
    while True:
        time.sleep(1)
        a = [1]*1000
        b64encode(b"testtest")

if __name__ == "__main__":
    main()
