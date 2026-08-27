import win32crypt
import pickle

def protect(data):
    blob = win32crypt.CryptProtectData(data, "FolderGuard face data", None, None, None, 0)
    return blob

def unprotect(blob):
    description, data = win32crypt.CryptUnprotectData(blob, None, None, None, 0)
    return data

def save_encodings(path, encodings):
    raw = pickle.dumps(encodings)
    protected = protect(raw)
    with open(path, "wb") as f:
        f.write(protected)

def load_encodings(path):
    with open(path, "rb") as f:
        protected = f.read()
    raw = unprotect(protected)
    return pickle.loads(raw)

if __name__ == "__main__":
    test_data = [1, 2, 3, "some encoding placeholder"]
    save_encodings("test.bin", test_data)
    loaded = load_encodings("test.bin")
    print(loaded)