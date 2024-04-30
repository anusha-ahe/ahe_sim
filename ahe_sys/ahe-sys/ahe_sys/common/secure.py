from Crypto.Cipher import AES
import binascii
import argparse
import sys

key = b"AHEsecret321#312"


def encrypt(plain_text):
    cipher = AES.new(key, AES.MODE_CBC)
    b = plain_text.ljust(16).encode("UTF-8")
    iv = binascii.hexlify(cipher.iv).decode()
    encr = binascii.hexlify(cipher.encrypt(b)).decode()
    return iv + encr


def decrypt(code):
    iv = binascii.unhexlify(code[:32].encode())
    enc_text = binascii.unhexlify(code[32:].encode())
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return cipher.decrypt(enc_text).decode("UTF-8").rstrip()


def main(args):
    parser = argparse.ArgumentParser(description='encrypt password')
    parser.add_argument('password', help='password')
    parser.add_argument('-d', '--decode', action='store_true')
    args_p = parser.parse_args(args)
    if not args_p.decode:
        if len(args_p.password) != 16:
            print("length should be 16")
            return
        code = encrypt(args_p.password)
        print(code)
    else:
        if len(args_p.password) != 64:
            print("length should be 64")
            return
        code = decrypt(args_p.password)
        print(code)


if __name__ == "__main__":
    main(sys.argv[1:])
