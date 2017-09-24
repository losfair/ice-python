import cffi

ffi = cffi.FFI()
ffi.cdef('''
typedef unsigned char ice_uint8_t;
typedef unsigned short ice_uint16_t;
typedef unsigned int ice_uint32_t;
typedef char * ice_owned_string_t;

typedef char ice_int8_t;
typedef short ice_int16_t;
typedef int ice_int32_t;

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

struct vIceRpcServerConfig {
    char _[0];
};
typedef struct vIceRpcServerConfig * IceRpcServerConfig;

struct vIceRpcServer {
    char _[0];
};
typedef struct vIceRpcServer * IceRpcServer;

struct vIceRpcCallContext {
    char _[0];
};
typedef struct vIceRpcCallContext * IceRpcCallContext;

struct vIceRpcParam {
    char _[0];
};
typedef struct vIceRpcParam * IceRpcParam;

struct vIceRpcClient {
    char _[0];
};
typedef struct vIceRpcClient * IceRpcClient;

struct vIceRpcClientConnection {
    char _[0];
};
typedef struct vIceRpcClientConnection * IceRpcClientConnection;

typedef void (*IceRpcMethodCallback)(
    IceRpcCallContext,
    void *
);

typedef void (*IceRpcClientConnectCallback)(
    IceRpcClientConnection,
    void *
);

typedef void (*IceRpcClientConnectionCallCallback)(
    const IceRpcParam,
    void *
);

IceRpcServerConfig ice_rpc_server_config_create();
void ice_rpc_server_config_destroy(IceRpcServerConfig config);
void ice_rpc_server_config_add_method(
    IceRpcServerConfig config,
    const char *name,
    IceRpcMethodCallback cb,
    void *call_with
);

IceRpcServer ice_rpc_server_create(IceRpcServerConfig config);
void ice_rpc_server_start(IceRpcServer server, const char *addr);

ice_uint32_t ice_rpc_call_context_get_num_params(IceRpcCallContext ctx);
IceRpcParam ice_rpc_call_context_get_param(IceRpcCallContext ctx, ice_uint32_t pos);
void ice_rpc_call_context_end(IceRpcCallContext ctx, IceRpcParam ret);

IceRpcParam ice_rpc_param_build_i32(ice_int32_t v);
IceRpcParam ice_rpc_param_build_f64(double v);
IceRpcParam ice_rpc_param_build_string(const char *v);
IceRpcParam ice_rpc_param_build_error(IceRpcParam from);
IceRpcParam ice_rpc_param_build_bool(ice_uint8_t v);
IceRpcParam ice_rpc_param_build_null();

ice_int32_t ice_rpc_param_get_i32(IceRpcParam p);
double ice_rpc_param_get_f64(IceRpcParam p);
ice_owned_string_t ice_rpc_param_get_string_to_owned(IceRpcParam p);
ice_uint8_t ice_rpc_param_get_bool(IceRpcParam p);
IceRpcParam ice_rpc_param_get_error(IceRpcParam p);
ice_uint8_t ice_rpc_param_is_null(IceRpcParam p);
void ice_rpc_param_destroy(IceRpcParam p);
IceRpcParam ice_rpc_param_clone(IceRpcParam p);

IceRpcClient ice_rpc_client_create(const char *addr);
void ice_rpc_client_destroy(IceRpcClient client);
void ice_rpc_client_connect(
    IceRpcClient client,
    IceRpcClientConnectCallback cb,
    void *call_with
);
void ice_rpc_client_connection_destroy(
    IceRpcClientConnection conn
);
void ice_rpc_client_connection_call(
    IceRpcClientConnection conn,
    const char *method_name,
    const IceRpcParam *params,
    ice_uint32_t num_params,
    IceRpcClientConnectionCallCallback cb,
    void *call_with
);
''')

lib = ffi.dlopen("ice_core")

print("Core version: " + ffi.string(lib.ice_metadata_get_version()).decode())
