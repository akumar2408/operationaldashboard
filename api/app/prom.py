from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response

REQ_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method","path","status"])
REQ_LAT = Histogram("http_request_latency_seconds", "Request latency", ["method","path"])

async def metrics(request: Request):
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

class MetricsASGIMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        method = scope["method"]; path = scope["path"]
        import time
        start = time.time()
        status = {"code": "200"}
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status["code"] = str(message["status"])
            await send(message)
        await self.app(scope, receive, send_wrapper)
        REQ_COUNT.labels(method, path, status["code"]).inc()
        REQ_LAT.labels(method, path).observe(time.time()-start)
