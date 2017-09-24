from . import core

running_servers = []

class ServerConfig:
    def __init__(self):
        self.inst = core.lib.ice_http_server_config_create()
    
    def __del__(self):
        if self.inst != None:
            core.lib.ice_http_server_config_destroy(self.inst)
    
    def take(self):
        inst = self.inst
        self.inst = None
        return inst
    
    def set_num_executors(self, n):
        core.lib.ice_http_server_config_set_num_executors(self.inst, n)
        return self
    
    def set_listen_addr(self, addr):
        core.lib.ice_http_server_config_set_listen_addr(self.inst, addr.encode())
        return self

class Server:
    def __init__(self, cfg):
        if not isinstance(cfg, ServerConfig):
            raise Exception("Invalid server config")

        self.inst = core.lib.ice_http_server_create(cfg.take())
        self.started = False
        self.callback_handles = [];

    def __del__(self):
        if self.started == False:
            print("Warning: Server leaked")
    
    def require_not_started(self):
        if self.started:
            raise Exception("Server already started")
    
    def route(self, dispatch_info):
        if not isinstance(dispatch_info, DispatchInfo):
            raise Exception("DispatchInfo required")

        def this_target(ctx, req, call_with):
            req = Request(ctx, req)
            dispatch_info.call(req)
        
        handle = core.ffi.callback("IceHttpRouteCallback", this_target)
        self.callback_handles.append(handle)

        if dispatch_info.path != None:
            path = dispatch_info.path.encode()
        else:
            path = "".encode()
        
        rt = core.lib.ice_http_server_route_create(
            path,
            handle,
            core.ffi.NULL
        )

        if dispatch_info.path != None:
            core.lib.ice_http_server_add_route(self.inst, rt)
        else:
            core.lib.ice_http_server_set_default_route(
                self.inst,
                rt
            )

    def define_route(self, path):
        def decorator(func):
            try:
                import asyncio
                from . import web_async
                if asyncio.iscoroutinefunction(func):
                    self.route(
                        web_async.AsyncDispatchInfo(
                            path,
                            func
                        )
                    )
                    return func
            except:
                pass
            self.route(DispatchInfo(path, func))
            return func

        return decorator

    def listen(self):
        self.require_not_started()
        self.started = True
        running_servers.append(self)
        core.lib.ice_http_server_start(self.inst)

class DispatchInfo:
    def __init__(self, path, cb):
        if not callable(cb):
            raise Exception("Callable required")

        self.path = path
        self.callback = cb
    
    def call(self, req):
        try:
            self.callback(req)
        except Exception as e:
            req.create_response().set_status(500).set_body(str(e)).send()

class Request:
    def __init__(self, ctx, req):
        self.context = ctx
        self.inst = req
    
    def __del__(self):
        if self.inst != None:
            self.create_response().set_status(500).send()

    def create_response(self):
        return Response(self)
    
    def send_response(self, resp):
        core.lib.ice_http_server_endpoint_context_end_with_response(self.context, resp.take())
        self.context = None
        self.inst = None
    
    def get_uri(self):
        return ffi.string(
            core.lib.ice_http_request_get_uri(self.inst)
        )
    
    def get_method(self):
        return ffi.string(
            core.lib.ice_http_request_get_method(self.inst)
        )

    def get_remote_addr(self):
        return ffi.string(
            core.lib.ice_http_request_get_remote_addr(self.inst)
        )
    
    def get_header(self, k):
        ret = core.lib.ice_http_request_get_header(
            self.inst,
            k.encode()
        )
        if ret == ffi.NULL:
            return None
        return ffi.string(ret)

class Response:
    def __init__(self, req):
        self.request = req
        self.inst = core.lib.ice_http_response_create()
        self.set_header("X-Powered-By", "Ice-python")
    
    def __del__(self):
        if self.inst != None:
            core.lib.ice_http_response_destroy(self.inst)
    
    def take(self):
        inst = self.inst
        self.inst = None
        return inst
    
    def set_status(self, status):
        core.lib.ice_http_response_set_status(self.inst, status)
        return self
    
    def set_body(self, body):
        if type(body) == str:
            body = body.encode()
        
        core.lib.ice_http_response_set_body(self.inst, body, len(body))
        return self
    
    def set_header(self, k, v):
        core.lib.ice_http_response_set_header(
            self.inst,
            k.encode(),
            v.encode()
        )
        return self
    
    def append_header(self, k, v):
        core.lib.ice_http_response_append_header(
            self.inst,
            k.encode(),
            v.encode()
        )
        return self

    def send(self):
        self.request.send_response(self)
