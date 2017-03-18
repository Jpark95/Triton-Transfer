#!/bin/bash

# Check the parameters provided
if [ "$#" -ne 1 ]
then
	echo "Wrong arguments, usage :"
	echo "./build.sh <build or clean>"
	exit
fi

BUILD_OR_CLEAN=$1

if [ $BUILD_OR_CLEAN == "build" ]
then
	# Enter your build code here, think about make
	# thrift --gen py -r metadataServer.thrift
	# thrift --gen py -r blockServer.thrift

	# Fill in the build part, see comments below
	thrift --gen py blockServer.thrift
	thrift --gen py metadataServer.thrift
	thrift --gen py shared.thrift
	exit

elif [ $BUILD_OR_CLEAN == "clean" ]
then
	echo "Cleaning"
	# Do the cleaning part here, think of make clean
	rm -rf gen-py

	# Fill in code specific cleanup similar to what you would do in make clean
else
	echo "Wrong build command"
	echo "Either ./build.sh build or ./build.sh clean"
	exit
fi
