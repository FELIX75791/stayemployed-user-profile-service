import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class BeforeAfterLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path
        print(f"[START] {method} {path}")

        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        print(f"[END] {method} {path} - Completed in {process_time:.2f} seconds")

        response.headers["X-Process-Time"] = str(process_time)

        return response