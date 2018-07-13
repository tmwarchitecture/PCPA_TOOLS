def encrypt(plaintext):
    key = 'abcdefghijklmnopqrstuvwxyz'
    """Encrypt the string and return the ciphertext"""
    def secondaryEncrypt(n, plaintext):
        newSuffix = ''
        for l in plaintext.lower():
            i = (key.index(l) + n+1) % 26
            newSuffix += key[i]
        return newSuffix
    result = ''
    n = 3
    endLength = 20
    
    newSuffix = ''
    for i in range(2,10):
        newSuffix += secondaryEncrypt(n**i, plaintext)
    
    plaintext += newSuffix[:(endLength - len(plaintext))]
    
    for j, l in enumerate(plaintext.lower()):
        try:
            i = (key.index(l) + n + j) % 26
            result += key[i]
        except ValueError:
            result += l

    return result.lower()[:endLength]

def decrypt(n, ciphertext):
    key = 'abcdefghijklmnopqrstuvwxyz'
    """Decrypt the string and return the plaintext"""
    result = ''
    
    for j, l in enumerate(ciphertext):
        try:
            i = (key.index(l) - n - j) % 26
            result += key[i]
        except ValueError:
            result += l

    return result