include "shared.thrift"

namespace cpp metadataServer
namespace py metadataServer
namespace java metadataServer

/* we can use shared.<datatype>, instead we could also typedef them for
	convenience */
typedef shared.response response
typedef shared.file file
typedef shared.uploadResponse uploadResponse

service MetadataServerService {

	file getFile(1: string filename),
	uploadResponse storeFile(1: file f),
	response deleteFile(1: string filename)
}
