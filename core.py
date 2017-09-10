import cffi
import time
import threading
import asyncio

ffi = cffi.FFI()
ffi.cdef('''
typedef void * Resource;

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;

typedef void (*AsyncEndpointHandler) (int id, Resource call_info);
typedef void (*GetSessionItemCallback) (Resource data, const char *value);
typedef void (*SetSessionItemCallback) (Resource data);
typedef void (*KVStorageGetItemCallback) (Resource data, const char *value);
typedef void (*KVStorageSetItemCallback) (Resource data);
typedef void (*KVStorageRemoveItemCallback) (Resource data);
typedef void (*ReadStreamOnDataCallback) (Resource call_with, const u8 *data, u32 data_len);
typedef void (*ReadStreamOnEndCallback) (Resource call_with);
typedef void (*ReadStreamOnErrorCallback) (Resource call_with);

Resource ice_create_server();
Resource ice_server_listen(Resource handle, const char *addr);
Resource ice_server_router_add_endpoint(Resource handle, const char *p);

void ice_server_set_session_cookie_name(
    Resource server,
    const char *name
);

void ice_server_set_session_timeout_ms(
    Resource server,
    u64 ms
);

void ice_server_add_template(
    Resource server,
    const char *name,
    const char *content
);

void ice_server_set_max_request_body_size(
    Resource server,
    u32 size
);

void ice_server_disable_request_logging(
    Resource server
);

void ice_server_set_async_endpoint_cb(
    Resource server,
    AsyncEndpointHandler cb
);

void ice_server_set_endpoint_timeout_ms(
    Resource server,
    u64 t
);

void ice_server_set_custom_app_data(
    Resource server,
    Resource data
);

void ice_server_cervus_load_bitcode(
    Resource server,
    const char *name,
    const u8 *data,
    u32 len
);

void ice_server_set_session_storage_provider(
    Resource server,
    Resource provider // Type: KVStorage
);

const char * ice_glue_request_get_remote_addr(Resource req);
const char * ice_glue_request_get_method(Resource req);
const char * ice_glue_request_get_uri(Resource req);

void ice_glue_request_get_session_item_async(
    Resource req,
    const char *key,
    GetSessionItemCallback cb,
    Resource call_with
);

void ice_glue_request_set_session_item_async(
    Resource req,
    const char *key,
    const char *value,
    SetSessionItemCallback cb,
    Resource call_with
);

const char * ice_glue_request_get_header(Resource t, const char *k);
const u8 * ice_glue_request_get_headers(Resource t);
const char * ice_glue_request_get_cookie(Resource t, const char *key);
const u8 * ice_glue_request_get_cookies(Resource t);
const u8 * ice_glue_request_get_query(Resource t);
const u8 * ice_glue_request_get_body(Resource t, u32 *len);
const u8 * ice_glue_request_get_body_as_urlencoded(Resource t);
Resource ice_glue_request_render_template_to_owned(
    Resource req,
    const char *name,
    const char *data
);
Resource ice_glue_request_borrow_context(Resource t);
const u8 * ice_glue_request_get_url_params(Resource t);

Resource ice_glue_create_response();
void ice_glue_destroy_response(Resource t);
void ice_glue_response_set_body(
    Resource t,
    const u8 *body,
    u32 len
);
void ice_glue_response_set_file(
    Resource t,
    const char *path
);
void ice_glue_response_set_status(
    Resource t,
    u16 status
);
bool ice_glue_response_consume_rendered_template(
    Resource resp,
    Resource data
);
void ice_glue_response_add_header(
    Resource t,
    const char *k,
    const char *v
);
void ice_glue_response_set_cookie(
    Resource t,
    const char *k,
    const char *v
);

Resource ice_glue_response_create_wstream(
    Resource t
);

bool ice_core_fire_callback(
    Resource call_info,
    Resource resp
);

Resource ice_core_borrow_request_from_call_info(
    Resource call_info
);
int ice_core_endpoint_get_id(Resource ep);

void ice_core_endpoint_set_flag(
    Resource ep,
    const char *name,
    bool value
);

Resource ice_storage_kv_create_with_redis_backend(
    const char *conn_str
);

void ice_storage_kv_destroy(
    Resource handle
);

void ice_storage_kv_get(
    Resource handle,
    const char *k,
    KVStorageGetItemCallback cb,
    void *call_with
);

void ice_storage_kv_set(
    Resource handle,
    const char *k,
    const char *v,
    KVStorageSetItemCallback cb,
    void *call_with
);

void ice_storage_kv_remove(
    Resource handle,
    const char *k,
    KVStorageRemoveItemCallback cb,
    void *call_with
);

void ice_storage_kv_expire_sec(
    Resource handle,
    const char *k,
    u32 t,
    KVStorageSetItemCallback cb,
    void *call_with
);

Resource ice_storage_kv_get_hash_map_ext(
    Resource kv
);

void ice_storage_kv_hash_map_ext_get(
    Resource hm,
    const char *k,
    const char *map_key,
    KVStorageGetItemCallback cb,
    void *call_with
);

void ice_storage_kv_hash_map_ext_set(
    Resource hm,
    const char *k,
    const char *map_key,
    const char *v,
    KVStorageSetItemCallback cb,
    void *call_with
);

void ice_storage_kv_hash_map_ext_remove(
    Resource hm,
    const char *k,
    const char *map_key,
    KVStorageRemoveItemCallback cb,
    void *call_with
);

const char * ice_metadata_get_version();

''')

lib = ffi.dlopen("ice_core")

print("Core version: " + ffi.string(lib.ice_metadata_get_version()).decode())
