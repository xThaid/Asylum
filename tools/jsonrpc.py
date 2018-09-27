import inspect
import json


class JsonRpcError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get('code'),
            data.get('message'))

    @classmethod
    def from_json(cls, json_str):
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        return {'code': self.code, 'message': self.message}

    def json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return "JsonRpcError({code}): {message}".format(
            code=self.code, message=str(self.message))


JsonRpcParseError = JsonRpcError(
    -32700, "Invalid JSON was received by the server.")
JsonRpcInvalidRequest = JsonRpcError(
    -32600, "The JSON sent is not a valid Request object.")
JsonRpcMethodNotFound = JsonRpcError(
    -32601, "The method does not exist / is not available.")
JsonRpcInvalidParams = JsonRpcError(
    -32602, "Invalid method parameter(s).")
JsonRpcInternalError = JsonRpcError(
    -32603, "Internal JSON-RPC error.")


class JsonRpcRequest:
    def __init__(self, method, params=None, id=None):
        self.method = method
        self.params = params
        self.id = id

    @property
    def is_notification(self):
        return self.id is None

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(
            data.get('method'),
            data.get('params'),
            data.get('id'))

    def json(self):
        data = {
            'jsonrpc': '2.0',
            'method': self.method
        }

        if self.params is not None:
            data['params'] = self.params

        if self.id is not None:
            data['id'] = self.id

        return json.dumps(data)


class JsonRpcResponse:
    def __init__(self, result=None, error=None, id=None):
        self.result = result if not error else None
        self.error = error
        self.id = id

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        err = data.get('error')
        return cls(
            data.get('result'),
            None if err is None else JsonRpcError.from_dict(err),
            data.get('id'))

    def json(self):
        data = {
            'jsonrpc': '2.0'
        }

        if self.result is not None:
            data['result'] = self.result
        if self.error is not None:
            data['error'] = self.error.to_dict()

        data['id'] = self.id

        return json.dumps(data)


def is_invalid_params(func, *args, **kwargs):
    if not inspect.isfunction(func):
        return True

    try:
        funcargs, varargs, varkwargs, defaults = inspect.getargspec(func)
    except ValueError:
        argspec = inspect.getfullargspec(func)
        funcargs, varargs, varkwargs, defaults = argspec[:4]

    if defaults:
        funcargs = funcargs[:-len(defaults)]

    if args and len(args) != len(funcargs):
            return True
    if kwargs and set(kwargs.keys()) != set(funcargs):
        return True

    if not args and not kwargs and funcargs:
        return True

    return False


class JsonRpcService:
    def __init__(self):
        self.method_map = {}

    def add_method(self, f, func_name=None):
        if func_name is None:
            func_name = f.__name__
        self.method_map[func_name] = f

    def handle(self, request_data):
        if isinstance(request_data, bytes):
            request_data = request_data.decode('utf-8')
        try:
            request = JsonRpcRequest.from_json(request_data)
        except ValueError:
            return JsonRpcResponse(error=JsonRpcParseError)

        return self.handle_request(request)

    def handle_request(self, request):
        def make_response(result=None, error=None):
            return None if request.is_notification else JsonRpcResponse(
                result=result,
                error=error,
                id=request.id)

        if request.method is None:
            return make_response(error=JsonRpcInvalidRequest)

        try:
            method = self.method_map[request.method]
        except KeyError:
            return make_response(error=JsonRpcMethodNotFound)

        args = tuple(request.params) if isinstance(request.params, list)\
            else ()
        kwargs = request.params if isinstance(request.params, dict) else {}
        try:
            result = method(*args, **kwargs)
        except JsonRpcError as e:
            return make_response(error=e)
        except Exception as e:
            if isinstance(e, TypeError) and is_invalid_params(
                    method, *args, **kwargs):
                return make_response(error=JsonRpcInvalidParams)
            else:
                return make_response(error=JsonRpcInternalError)

        return make_response(result=result)
