import hashlib
str2hash = "Hello, World!"

def encoding(string):
    # Create a new sha256 hash object
    return str(hashlib.sha256(string.encode()).hexdigest())

if __name__ == "__main__":
    print(encoding(str2hash))