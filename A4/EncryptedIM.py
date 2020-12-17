#!/usr/bin/python

#Original Author : Henry Tan
#Edit by Johnny Li
#EncryptedIM.py

import os
import sys
import argparse
import socket
import select
import logging
import signal #To kill the programs nicely
import random

#import hashlib 
from Crypto.Hash import HMAC, SHA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from collections import deque

############
#GLOBAL VARS
DEFAULT_PORT = 9999
s = None
server_s = None
logger = logging.getLogger('main')
###########

def parse_arguments():
  parser = argparse.ArgumentParser(description = 'A P2P IM service.')
  parser.add_argument('-c', dest='connect', metavar='HOSTNAME', type=str)
  parser.add_argument('-s', dest='server', action='store_true')
  parser.add_argument(dest = 'port', metavar = 'PORT', nargs = '?', type = int, default = DEFAULT_PORT)
  parser.add_argument('-confkey', dest='confkey', metavar='key1', type=str, required=True)
  parser.add_argument('-authkey', dest='authkey', metavar='key2', type=str, required=True)

  return parser.parse_args()

#def print_how_to():
#  print ("This program must be run with exactly ONE of the following options")
#  print ("-c <HOSTNAME> <PORT> -confkey <K1> -authkey <K2>  : to connect to <HOSTNAME> on tcp port <portnum> (default port 9990)")
#  print ("-s <PORT> -confkey <K1> -authkey <K2>             : to run a server listening on tcp port <portnum> (default port 9999)")

def sigint_handler(signal, frame):
#  logger.debug("SIGINT Captured! Killing")
  global s, server_s
  if s is not None:
    s.shutdown(socket.SHUT_RDWR)
    s.close()
  if server_s is not None:
    s.close()

  quit()

def init():
  global s, confkey, authkey
  args = parse_arguments()

  logging.basicConfig()
  logger.setLevel(logging.CRITICAL)

  #Catch the kill signal to close the socket gracefully
  signal.signal(signal.SIGINT, sigint_handler)

  #hashing key1
  #SHA: https://docs.python.org/2/library/sha.html
  key1 = SHA.new()
  key1.update(bytes(args.confkey, encoding='utf-8'))
  confkey = key1.digest() #string
  confkey = confkey[:16] #128 bits

  #hash key2
  key2 = SHA.new()
  key2.update(bytes(args.authkey, encoding='utf-8'))
  authkey = key2.digest() #string
  authkey = authkey[:16] #128 bits

#  if args.connect is None and args.server is False:
#    print_how_to()
#    quit()

#  if args.connect is not None and args.server is not False:
#    print_how_to()
#    quit()

  if args.connect is not None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    logger.debug('Connecting to ' + args.connect + ' ' + str(args.port))
    s.connect((args.connect, args.port))

  if args.server is not False:
    global server_s
    server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_s.bind(('', args.port))
    server_s.listen(1) #Only one connection at a time
    s, remote_addr = server_s.accept()
    server_s.close()
#    logger.debug("Connection received from " + str(remote_addr))

def main():
  global s
  datalen=64

  init()

  inputs = [sys.stdin, s]
  outputs = [s]

  output_buffer = deque()

  while s is not None:
    #Prevents select from returning the writeable socket when there's nothing to write
    if (len(output_buffer) > 0):
      outputs = [s]
    else:
      outputs = []

    readable, writeable, exceptional = select.select(inputs, outputs, inputs)

    if s in readable:
      get_iv = s.recv(16) #Send 16 bytes of IV
      get_hmac = s.recv(20) #HMAC send 20 bytes for sha1

      data = s.recv(datalen) #Get entire message
	  #print "received packet, length "+str(len(data))
	  
      if ((data is not None) and (len(data) > 0)):
		#Python hmac: https://docs.python.org/3/library/hmac.html
        #HMAC authkey with SHA1
        hkey = HMAC.new(authkey, digestmod=SHA)
        hkey.update(data)

		#Error output check
        if (hkey.digest() != get_hmac): #If HMAC and received authkey don't match
           sys.exit("HMAC is incorrect.")
		   
        #Encrypt HMAC with AES: https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html
        h = AES.new(confkey, AES.MODE_CBC,get_iv) #Mode CBC
        decrypt = h.decrypt(data) #Decrypt the given data

        #Padding
        pad = decrypt[-1]

        #Check padding length
        if (pad != 10):
           decrypt = decrypt[:-pad] #Add padding
        sys.stdout.write(decrypt.decode('utf-8')) #Assuming that stdout is always writeable

      else:
        #Socket was closed remotely
        s.close()
        s = None

    if sys.stdin in readable:
      data = sys.stdin.readline(1024)

      #Setup IV
	  #https://stackoverflow.com/questions/40961482/how-to-use-get-random-bytes-in-linux-kernel-module
      iv = get_random_bytes(AES.block_size)

	  #Setup encrypt mode
      if ((len(data)%16)!= 0): #16x byte encryption blocks
        data=data+(16-(len(data)%16))*chr(16-(len(data)%16)) #repeated length times

      #Encrypt
      t = AES.new(confkey, AES.MODE_CBC, iv)
      ciphertext = t.encrypt(data)

      #Build HMAC with SHA1
      hmac = HMAC.new(authkey, digestmod=SHA)
      hmac.update(ciphertext)

      msg = b"".join([iv, hmac.digest(), ciphertext]) #join everything to be sent together

      if(len(data) > 0):
        output_buffer.append(msg)

      else:
        #EOF encountered, close if the local socket output buffer is empty.
        if( len(output_buffer) == 0):
          s.shutdown(socket.SHUT_RDWR)
          s.close()
          s = None

    if s in writeable:
      if (len(output_buffer) > 0):
        data = output_buffer.popleft()
        bytesSent = s.send(data)
        #If not all the characters were sent, put the unsent characters back in the buffer
        if(bytesSent < len(data)):
          output_buffer.appendleft(data[bytesSent:])

    if s in exceptional:
      s.shutdown(socket.SHUT_RDWR)
      s.close()
      s = None

###########

if __name__ == "__main__":
  main()