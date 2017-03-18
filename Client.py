#!/usr/bin/env python

import sys, os, hashlib, logging
import glob
logging.basicConfig()
sys.path.append('gen-py')

from blockServer import *
from blockServer.ttypes import *
from shared import *
from shared.ttypes import *
from metadataServer import *
from metadataServer.ttypes import *

# Thrift specific imports
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Add classes / functions as required here

def getBlockServerPort(config_path):
    # This function reads config file and gets the port for block server

    if not os.path.exists(config_path):
        print "ERROR"
        exit(1)
    if not os.path.isfile(config_path):
        print "ERROR"
        exit(1)

    with open(config_path, 'r') as conffile:
        lines = conffile.readlines()
        for line in lines:
            if 'block' in line:
                # Important to make port as an integer
                return int(line.split()[1].lstrip().rstrip())

    # Exit if you did not get blockserver information
    print "ERROR"
    exit(1)

def getMetaServerPort(config_path):
    # This function reads config file and gets the port for block server

    if not os.path.exists(config_path):
        print "ERROR"
        exit(1)
    if not os.path.isfile(config_path):
        print "ERROR"
        exit(1)

    with open(config_path, 'r') as conffile:
        lines = conffile.readlines()
        for line in lines:
            if 'metadata1' in line:
                # Important to make port as an integer
                return int(line.split()[1].lstrip().rstrip())

    # Exit if you did not get blockserver information
    print "ERROR"
    exit(1)


def getBlockServerSocket(port):
    # This function creates a socket to block server and returns it

    # Make socket
    transport = TSocket.TSocket('localhost', port)
    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)
    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    # Create a client to use the protocol encoder
    client = BlockServerService.Client(protocol)

    # Connect!
    try:
        transport.open()
    except Exception as e:
        print "ERROR", port
        print e
        exit(1)

    return client

def getMetaServerSocket(port):
    transport = TSocket.TSocket('localhost', port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = MetadataServerService.Client(protocol)
    try:
	transport.open()
    except Exception as e:
	print "ERROR", port
	print e
	exit(1)
    return client

if __name__ == "__main__":

    if len(sys.argv) < 4:
        print "ERROR"
        exit(-1)
    
    config_path = sys.argv[1]
    base_dir = sys.argv[2]
    command = sys.argv[3]
    filename = sys.argv[4]
    base_dir_files = {}
    myBlocks = {}
    # keep track of existing files
    for fname in os.listdir(base_dir):
	f = open(base_dir + "/" + fname, 'rb')
	myFile = file()
	myFile.filename = fname
	myList = []
	#data = f.read(4000000)

	while True:
	    data = f.read(4194304)
	    if data == "":
		break
	    m = hashlib.sha256()
	    m.update(data)
	    hashString = m.hexdigest()
	    myList.append(hashString)
	    myBlocks[hashString] = data
	myFile.hashList = myList
	myFile.status = responseType.OK
	myFile.version = 1
        base_dir_files[fname] = myFile
	
    servPort = getBlockServerPort(config_path)
    sock = getBlockServerSocket(servPort)
    metaPort = getMetaServerPort(config_path)
    mSock = getMetaServerSocket(metaPort)

    if command == "upload":
	if base_dir_files.has_key(filename) == True:
	    try:
		uResp = mSock.storeFile(base_dir_files[filename])
	    except Exception as e:
		print "ERROR"
		exit(1)
	else:
	    print "ERROR"
	    exit(1)
	if uResp.status == uploadResponseType.FILE_ALREADY_PRESENT:
            print "ERROR"
	    exit(1)
        else:
            for s in uResp.hashList:
		hb = hashBlock()
		hb.hash = s
		hb.block = myBlocks[s]
		hb.status = "OK"
		try:
		    resp = sock.storeBlock(hb)
		except Exception as e:
		    print "ERROR"
		    exit(1)
		if resp.message != responseType.OK:
		    print "ERROR"
		    exit(1)
	    try:
		uResp = mSock.storeFile(base_dir_files[filename])
	    except Exception as e:
		print "ERROR"
		exit(1)
	    if uResp.status == uploadResponseType.FILE_ALREADY_PRESENT:
		print "OK"
		exit(1)
	    else:
		print "ERROR"
		exit(1)

    elif command == "download":
        try:
	    tempFile = mSock.getFile(base_dir_files[filename].filename)
	except Exception as e:
	    print "ERROR"
	    exit(1)
	if tempFile.status == responseType.OK:
	    base_dir_files[filename] = tempFile
	    f = open(base_dir + '/' + filename, 'w+')
	    for hString in tempFile.hashList:
		if myBlocks.has_key(hString) == False:
		    try:
			hb = sock.getBlock(hString)
		    except Exception as e:
			print "ERROR"
			exit(1)
		    if hb.status == "OK":
			myBlocks[hString] = hb.block
			f.write(hb.block)
		    else:
			print "ERROR"
			exit(1)
		else:
		    f.write(myBlocks[hString])
	    print "OK"
	else:
	    print "ERROR"
	    exit(1)
	
    elif command == "delete":
	try:
	    resp = mSock.deleteFile(filename)
	except Exception as e:
            print "ERROR"
            print e
	    exit(1)

        if resp.message == responseType.OK:
            print "OK"
        else:
            print "ERROR"

    '''
    Server information can be parsed from the config file

    connections can be created as follows

    Eg:

    # Make socket
    transport = TSocket.TSocket('serverip', serverport)

    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Create a client to use the protocol encoder
    client = HelloService.Client(protocol)

    # Connect!
    try:
        transport.open()
    except Exception as e:
        print "Error while opening socket to server\n", e
        exit(1)

    # Create custom data structure object
    m = message()

    # Fill in data
    m.data = "Hello From Client!!!"

    # Call via RPC
    try:
        dataFromServer = client.HelloServiceMethod(m)
    except Exception as e:
        print "Caught an exception while calling RPC"
        # Add handling code
        exit(1)

    '''
