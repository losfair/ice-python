from . import core

class ServerConfig:
    def __init__(self):
        self.inst = core.lib.ice_rpc_server_config_create()
        self.callbacks = []

    def __del__(self):
        if self.inst != None:
            core.lib.ice_rpc_server_config_destroy(self.inst)

    def add_method(self, name, m):
        def caller(ctx, call_with):
            m(CallContext(ctx))

        cb = core.ffi.callback("IceRpcMethodCallback", caller)
        self.callbacks.append(cb)

        core.lib.ice_rpc_server_config_add_method(
            self.inst,
            name.encode(),
            cb,
            core.ffi.NULL
        )

class Server:
    def __init__(self, config):
        if not isinstance(config, ServerConfig):
            raise TypeError("ServerConfig required")

        cfg_inst = config.inst
        config.inst = None
        self.config = config # Preserve callback handles

        self.inst = core.lib.ice_rpc_server_create(
            cfg_inst
        )

    def start(self, addr):
        core.lib.ice_rpc_server_start(self.inst, addr.encode())

class CallContext:
    def __init__(self, inst):
        self.inst = inst

    def get_num_params(self):
        return core.lib.ice_rpc_call_context_get_num_params(self.inst)

    def get_param(self, pos):
        p = core.lib.ice_rpc_call_context_get_param(self.inst, pos)
        if p == core.ffi.NULL:
            return None
        else:
            return Param(p, True)

    def end(self, ret):
        if not isinstance(ret, Param):
            raise TypeError("Param needed for return value")

        if ret.borrowed:
            raise Exception("The param to return must be owned")

        inst = self.inst
        self.inst = None

        retInst = ret.inst
        ret.inst = None

        core.lib.ice_rpc_call_context_end(inst, retInst)

class Client:
    def __init__(self, addr):
        self.inst = core.lib.ice_rpc_client_create(addr.encode())
        self.pending_connect_callbacks = []

    def __del__(self):
        if self.inst != None:
            core.lib.ice_rpc_client_destroy(self.inst)

    def connect(self, cb):
        cb_ctx = {}
        def target(conn, call_with):
            handle = cb_ctx["handle"]
            self.pending_connect_callbacks.remove(handle)
            if conn == core.ffi.NULL:
                cb(None)
            else:
                cb(ClientConnection(conn))

        handle = core.ffi.callback(
            "IceRpcClientConnectCallback",
            target
        )
        cb_ctx["handle"] = handle
        self.pending_connect_callbacks.append(handle)

        core.lib.ice_rpc_client_connect(
            self.inst,
            handle,
            core.ffi.NULL
        )

class ClientConnection:
    def __init__(self, inst):
        self.inst = inst
        self.pending_callbacks = set([])
        self.conn_call_cb_handle = core.ffi.callback(
            "IceRpcClientConnectionCallCallback",
            self.conn_call_cb
        )

    def __del__(self):
        if self.inst != None:
            core.lib.ice_rpc_client_connection_destroy(self.inst)

    def destroy(self):
        core.lib.ice_rpc_client_connection_destroy(self.inst)
        self.inst = None

    def call(self, method_name, params, cb):
        raw_params = core.ffi.new("IceRpcParam[" + str(len(params)) + "]")
        for i in range(len(params)):
            if params[i].borrowed or params[i].inst == None:
                raise Exception("Invalid param(s)")
            raw_params[i] = params[i].inst
            params[i].inst = None

        cb_handle = core.ffi.new_handle(cb)
        self.pending_callbacks.add(cb_handle)

        core.lib.ice_rpc_client_connection_call(
            self.inst,
            method_name.encode(),
            raw_params,
            len(params),
            self.conn_call_cb_handle,
            cb_handle
        )

    def conn_call_cb(self, raw_borrowed_ret, cb_handle):
        cb = core.ffi.from_handle(cb_handle)
        self.pending_callbacks.remove(cb_handle)
        if raw_borrowed_ret == core.ffi.NULL:
            cb(None)
        else:
            cb(Param(raw_borrowed_ret, True).to_owned())

class Param:
    def __init__(self, inst, borrowed = False):
        self.inst = inst
        self.borrowed = borrowed

    def __del__(self):
        if self.inst != None and not self.borrowed:
            core.lib.ice_rpc_param_destroy(self.inst)

    def to_owned(self):
        if not self.borrowed:
            raise Exception("Already owned")

        self.inst = core.lib.ice_rpc_param_clone(self.inst)
        self.borrowed = False

        return self

    def get_i32(self):
        return core.lib.ice_rpc_param_get_i32(self.inst)

    def get_f64(self):
        return core.lib.ice_rpc_param_get_f64(self.inst)

    def get_string(self):
        raw_s = core.lib.ice_rpc_param_get_string_to_owned(self.inst)
        if raw_s == core.ffi.NULL:
            return None

        s = core.ffi.string(raw_s)
        core.lib.ice_glue_destroy_cstring(raw_s)

        return s.decode()

    def get_bool(self):
        return bool(core.lib.ice_rpc_param_get_bool(self.inst))

    def get_error(self):
        e = core.lib.ice_rpc_param_get_error(self.inst)
        if e == core.ffi.NULL:
            return None
        else:
            return Param(e, True)

    def is_null(self):
        return bool(core.lib.ice_rpc_param_is_null(self.inst))

    @staticmethod
    def build_i32(v):
        return Param(core.lib.ice_rpc_param_build_i32(v))

    @staticmethod
    def build_f64(v):
        return Param(core.lib.ice_rpc_param_build_f64(v))

    @staticmethod
    def build_string(v):
        return Param(core.lib.ice_rpc_param_build_string(v.encode()))

    @staticmethod
    def build_error(other):
        if not isinstance(other, Param):
            raise TypeError("Param required")
        if other.borrowed or other.inst == None:
            raise Exception("Invalid error source")

        other_inst = other.inst
        other.inst = None
        return Param(core.lib.ice_rpc_param_build_error(other_inst))

    @staticmethod
    def build_bool(v):
        return Param(core.lib.ice_rpc_param_build_bool(int(v)))

    @staticmethod
    def build_null():
        return Param(core.lib.ice_rpc_param_build_null())
