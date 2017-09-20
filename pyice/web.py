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
    
    def route(self, dispatch_info, flags = []):
        if not isinstance(dispatch_info, DispatchInfo):
            raise Exception("DispatchInfo required")

        def this_target(ctx, req, call_with):
            req = Request(ctx, req)
            dispatch_info.call(req)
        
        handle = core.ffi.callback("IceHttpRouteCallback", this_target)
        self.callback_handles.append(handle)
        
        rt = core.lib.ice_http_server_route_create(
            dispatch_info.path.encode(),
            handle,
            core.ffi.NULL
        )
        core.lib.ice_http_server_add_route(self.inst, rt)
    
    def listen(self):
        self.require_not_started()
        self.started = True
        running_servers.append(self)
        core.lib.ice_http_server_start(self.inst)

    def default_endpoint(self, req):
        req.create_response().set_status(404).set_body("Not found").send()

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

class Response:
    def __init__(self, req):
        self.request = req
        self.inst = core.lib.ice_http_response_create()
    
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

    def send(self):
        self.request.send_response(self)
