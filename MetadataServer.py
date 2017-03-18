#!/usr/bin/env python

import sys, os, hashlib, logging
logging.basicConfig()
sys.path.append('gen-py')

# Thrift specific imports
from thrift import Thrift
from thrift.transport import TSocket
from thrift.server import TServer
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

# Protocol specific imports
from metadataServer import MetadataServerService
from shared.ttypes import *
from blockServer import  *
from blockServer.ttypes import *

def getBlockServerPort(config_path):
    # This function reads config file and gets the port for block server

    print "Checking validity of the config path"
    if not os.path.exists(config_path):
        print "ERROR: Config path is invalid"
        exit(1)
    if not os.path.isfile(config_path):
        print "ERROR: Config path is not a file"
        exit(1)

    print "Reading config file"
    with open(config_path, 'r') as conffile:
        lines = conffile.readlines()
        for line in lines:
            if 'block' in line:
                # Important to make port as an integer
                return int(line.split()[1].lstrip().rstrip())

    # Exit if you did not get blockserver information
    print "ERROR: blockserver information not found in config file"
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
    print "Connecting to block server on port", port
    try:
        transport.open()
    except Exception as e:
        print "ERROR: Exception while connecting to block server, check if server is running on port", port
        print e
        exit(1)

    return client

class MetadataServerHandler():

    def __init__(self, config_path, my_id):
        # Initialize block
	self.config_path = config_path
	self.port = self.readServerPort()
	s = getBlockServerPort(config_path)
	self.sock = getBlockServerSocket(s)
	self.hashBlocks = {}

    def getFile(self, filename):
        # Function to handle download request from file
	if self.hashBlocks.has_key(filename):
	    return self.hashBlocks[filename]
	else:
	    returnFile = file()
	    returnFile.status = responseType.ERROR
	    return returnFile
	'''
	f = open(filename, 'rb')
	data = f.read()
	m = hashlib.sha256()
	m.update(data)
	hashString = m.hexdigest()
	hb = hashBlock()
	hb.hash = hashString
	hb.block = data
	hb.status = "OK"
	try resp = sock.storeBlock'''

    def storeFile(self, filename):
        # Function to handle upload request
	#s = getBlockServerPort(config_path)
	#sck = getBlockServerSocket(s)
	uResponse = uploadResponse()
	missingHash = []
	
	# LOOP through each block
	for hString in filename.hashList:
	    #m = hashlib.sha256()
	    #m.update(bString)
	    #hashString = m.hexdigest()
	    hBlock = self.sock.hasBlock(hString)
	    if hBlock == False:
		missingHash.append(hString)

	uResponse.hashList = missingHash
	if len(missingHash) == 0:
	    uResponse.status = uploadResponseType.FILE_ALREADY_PRESENT
	    self.hashBlocks[filename.filename] = filename
	else:
	    uResponse.status = uploadResponseType.MISSING_BLOCKS
	return uResponse

    def deleteFile(self, filename):
        # Function to handle download request from file
	if self.hashBlocks.has_key(filename) == False:
	    r = response()
	    r.message = responseType.ERROR
	    return r
        self.hashBlocks[filename] = None
        self.hashBlocks.pop(filename,None);
	r = response()
	r.message = responseType.OK
	return r

    def readServerPort(self):
        # Get the server port from the config file.
        # id field will determine which metadata server it is 1, 2 or n
        # Your details will be then either metadata1, metadata2 ... metadatan
        # return the port
	print "Checking validity of config path"
	if not os.path.exists(config_path):
	    print "ERROR: Config path is invalid"
	    exit(1)
	if not os.path.isfile(config_path):
	    print "ERROR: Config path is not a file"
	    exit(1)
	
	print "Reading config file"
	with open(config_path, 'r') as conffile:
            lines = conffile.readlines()
            for line in lines:
                if 'metadata1' in line:
                    # Important to make port as an integer
                    return int(line.split()[1].lstrip().rstrip())

        # Exit if you did not get blockserver information
        print "ERROR: blockserver information not found in config file"
        exit(1)

    # Add other member functions if needed

# Add additional classes and functions here if needed

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "Invocation <executable> <config_file> <id>"
        exit(-1)

    config_path = sys.argv[1]
    my_id = sys.argv[2]

    print "Initializing metadata server"
    handler = MetadataServerHandler(config_path, my_id)
    port = handler.readServerPort()
    # Define parameters for thrift server
    processor = MetadataServerService.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    # Create a server object
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print "Starting server on port : ", port

    try:
        server.serve()
    except (Exception, KeyboardInterrupt) as e:
        print "\nExecption / Keyboard interrupt occured: ", e
        exit(0)
