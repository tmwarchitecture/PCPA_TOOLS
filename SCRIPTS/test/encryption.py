import hashlib

result = hashlib.md5(b'GeeksforGeeks') 
print result.digest()

print hashlib.sha224(b"Nobody inspects the spammish repetition").hexdigest()