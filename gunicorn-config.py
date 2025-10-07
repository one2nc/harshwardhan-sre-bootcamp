import os
# from opentelemetry import trace
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# # from opentelemetry.instrumentation.wsgi import WSGIMiddleware
# from opentelemetry.sdk.resources import Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor

# def post_fork(server, worker):
#     # Initialize OpenTelemetry SDK within each worker process
#     resource = Resource.create({
#         "service.name": os.environ.get("OTEL_SERVICE_NAME", "my-gunicorn-app"),
#         "service.version": os.environ.get("OTEL_SERVICE_VERSION", "1.0.0"),
#         "environment": os.environ.get("OTEL_ENVIRONMENT", "development"),
#     })
#     provider = TracerProvider(resource=resource)
#     processor = BatchSpanProcessor(OTLPSpanExporter())
#     provider.add_span_processor(processor)
#     trace.set_tracer_provider(provider)

#     # Apply WSGI middleware for automatic instrumentation if needed
#     # server.app = WSGIMiddleware(server.app) # Uncomment if using WSGI middleware

statsd_host= "observability-prometheus-statsd-exporter.observability-ns.svc.cluster.local:9125"
statsd_prefix= "student-api"
# Other Gunicorn settings
workers = os.cpu_count() * 2 + 1

# print(os.cpu_count())

# bind = ['0.0.0.0:80']
bind = ['0.0.0.0:5000']
# Timeout for worker processes (in seconds)
timeout = 30

# Log level
loglevel = "info"

preload_app=True

worker_class="sync" # use Uvicorn class for async apps

accesslog = '-'
errorlog = '-'