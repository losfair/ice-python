import cffi

ffi = cffi.FFI()
ffi.cdef('''
typedef unsigned char ice_uint8_t;
typedef unsigned short ice_uint16_t;
typedef unsigned int ice_uint32_t;
typedef char * ice_owned_string_t;

const char * ice_metadata_get_version();

void ice_glue_destroy_cstring(ice_owned_string_t s);

struct vIceReadStream {
    char _[0];
};
typedef struct vIceReadStream * IceReadStream;

typedef ice_uint8_t (*IceReadStreamRecvCallbackOnData) (
    void *call_with,
    const ice_uint8_t *data,
    ice_uint32_t data_len
);

typedef void (*IceReadStreamRecvCallbackOnEnd) (
    void *call_with
);

typedef void (*IceReadStreamRecvCallbackOnError) (
    void *call_with
);

void ice_stream_rstream_begin_recv(
    IceReadStream target,
    IceReadStreamRecvCallbackOnData cb_on_data,
    IceReadStreamRecvCallbackOnEnd cb_on_end,
    IceReadStreamRecvCallbackOnError cb_on_error,
    void *call_with
);

void ice_stream_rstream_destroy(
    IceReadStream target
);

struct vIceWriteStream {
    char _[0];
};
typedef struct vIceWriteStream * IceWriteStream;

void ice_stream_wstream_write(
    IceWriteStream target,
    const ice_uint8_t *data,
    ice_uint32_t data_len
);

void ice_stream_wstream_destroy(
    IceWriteStream target
);

struct IceStreamTxRxPair {
    IceWriteStream tx;
    IceReadStream rx;
};

void ice_stream_create_pair(struct IceStreamTxRxPair *out);

struct vIceHttpServerConfig {
    char _[0];
};
typedef struct vIceHttpServerConfig * IceHttpServerConfig;

struct vIceHttpServer {
    char _[0];
};
typedef struct vIceHttpServer * IceHttpServer;

struct vIceHttpServerExecutionContext {
    char _[0];
};
typedef struct vIceHttpServerExecutionContext * IceHttpServerExecutionContext;

struct vIceHttpRouteInfo {
    char _[0];
};
typedef struct vIceHttpRouteInfo * IceHttpRouteInfo;

struct vIceHttpEndpointContext {
    char _[0];
};
typedef struct vIceHttpEndpointContext * IceHttpEndpointContext;

struct vIceHttpRequest {
    char _[0];
};
typedef struct vIceHttpRequest * IceHttpRequest;

struct vIceHttpResponse {
    char _[0];
};
typedef struct vIceHttpResponse * IceHttpResponse;

typedef void (*IceHttpRouteCallback) (
    IceHttpEndpointContext,
    IceHttpRequest,
    void *
);

typedef ice_uint8_t (*IceHttpReadBodyCallbackOnData) (
    const ice_uint8_t *data,
    ice_uint32_t len,
    void *call_with
);

typedef void (*IceHttpReadBodyCallbackOnEnd) (
    ice_uint8_t ok,
    void *call_with
);

typedef void (*IceHttpKeyValueIterInstantCallback) (
    const char *key,
    const char *value,
    void *call_with
);

IceHttpServerConfig ice_http_server_config_create();
void ice_http_server_config_destroy(IceHttpServerConfig cfg);
void ice_http_server_config_set_listen_addr(
    IceHttpServerConfig cfg,
    const char *addr
);
void ice_http_server_config_set_num_executors(
    IceHttpServerConfig cfg,
    ice_uint32_t n
);
IceHttpServer ice_http_server_create(
    IceHttpServerConfig cfg
);
IceHttpServerExecutionContext ice_http_server_start(
    IceHttpServer server
);
IceHttpRouteInfo ice_http_server_route_create(
    const char *path,
    IceHttpRouteCallback cb,
    void *call_with
);
void ice_http_server_route_destroy(
    IceHttpRouteInfo rt
);
void ice_http_server_add_route(
    IceHttpServer server,
    IceHttpRouteInfo rt
);
void ice_http_server_set_default_route(
    IceHttpServer server,
    IceHttpRouteInfo rt
);
IceHttpResponse ice_http_response_create();
void ice_http_response_destroy(
    IceHttpResponse resp
);
void ice_http_response_set_body(
    IceHttpResponse resp,
    const ice_uint8_t *data,
    ice_uint32_t len
);
void ice_http_response_set_status(
    IceHttpResponse resp,
    ice_uint16_t status
);
void ice_http_response_set_header(
    IceHttpResponse resp,
    const char *k,
    const char *v
);
void ice_http_response_append_header(
    IceHttpResponse resp,
    const char *k,
    const char *v
);
void ice_http_response_attach_rstream(
    IceHttpResponse resp,
    IceReadStream stream
);
void ice_http_server_endpoint_context_end_with_response(
    IceHttpEndpointContext ctx,
    IceHttpResponse resp
);
IceHttpRequest ice_http_server_endpoint_context_take_request(
    IceHttpEndpointContext ctx
);
void ice_http_request_destroy(
    IceHttpRequest req
);
ice_owned_string_t ice_http_request_get_uri_to_owned(
    IceHttpRequest req
);
ice_owned_string_t ice_http_request_get_method_to_owned(
    IceHttpRequest req
);
ice_owned_string_t ice_http_request_get_remote_addr_to_owned(
    IceHttpRequest req
);
ice_owned_string_t ice_http_request_get_header_to_owned(
    IceHttpRequest req,
    const char *k
);
void ice_http_request_iter_headers(
    IceHttpRequest req,
    IceHttpKeyValueIterInstantCallback cb,
    void *call_with
);
void ice_http_request_take_and_read_body(
    IceHttpRequest req,
    IceHttpReadBodyCallbackOnData cb_on_data,
    IceHttpReadBodyCallbackOnEnd cb_on_end,
    void *call_with
);
ice_uint8_t ice_storage_file_http_response_begin_send(
    IceHttpRequest req,
    IceHttpResponse resp,
    const char *path
);

struct vIceKVStorage {
    char _[0];
};
typedef struct vIceKVStorage * IceKVStorage;

struct vIceKVStorageHashMapExt {
    char _[0];
};
typedef struct vIceKVStorageHashMapExt * IceKVStorageHashMapExt;

typedef void (*IceKVStorageGetItemCallback) (void *data, const char *value);
typedef void (*IceKVStorageSetItemCallback) (void *data);
typedef void (*IceKVStorageRemoveItemCallback) (void *data);

IceKVStorage ice_storage_kv_create_with_redis_backend(
    const char *conn_str
);
void ice_storage_kv_destroy(IceKVStorage handle);
void ice_storage_kv_get(
    IceKVStorage handle,
    const char *k,
    IceKVStorageGetItemCallback cb,
    void *call_with
);
void ice_storage_kv_set(
    IceKVStorage handle,
    const char *k,
    const char *v,
    IceKVStorageSetItemCallback cb,
    void *call_with
);
void ice_storage_kv_remove(
    IceKVStorage handle,
    const char *k,
    IceKVStorageRemoveItemCallback cb,
    void *call_with
);
void ice_storage_kv_expire_sec(
    IceKVStorage handle,
    const char *k,
    ice_uint32_t t,
    IceKVStorageSetItemCallback cb,
    void *call_with
);

IceKVStorageHashMapExt ice_storage_kv_get_hash_map_ext(
    IceKVStorage handle
);

void ice_storage_kv_hash_map_ext_get(
    IceKVStorageHashMapExt hm,
    const char *k,
    const char *map_key,
    IceKVStorageGetItemCallback cb,
    void *call_with
);

void ice_storage_kv_hash_map_ext_set(
    IceKVStorageHashMapExt hm,
    const char *k,
    const char *map_key,
    const char *v,
    IceKVStorageSetItemCallback cb,
    void *call_with
);


void ice_storage_kv_hash_map_ext_remove(
    IceKVStorageHashMapExt hm,
    const char *k,
    const char *map_key,
    IceKVStorageRemoveItemCallback cb,
    void *call_with
);
''')

lib = ffi.dlopen("ice_core")

print("Core version: " + ffi.string(lib.ice_metadata_get_version()).decode())
