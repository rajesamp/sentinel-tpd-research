# Wolfi/Chainguard distroless Python runtime (non-root by default, zero shell/apk)
FROM cgr.dev/chainguard/python:latest
WORKDIR /app
COPY --chown=nonroot:nonroot . /app
USER nonroot
ENTRYPOINT ["python", "reproduce.py", "--offline", "--quick", "--output", "/tmp/reproduced"]
