import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

defaults = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

yaml_layer = {"port": 8285}

env_file = {"APP_LOG_LEVEL": "warning"}

os_env = {
    "APP_WORKERS": "8",
    "APP_DEBUG": "false",
    "APP_LOG_LEVEL": "warning",
    "APP_API_KEY": "key-4ivzq45vag",
}


def to_bool(v):
    return str(v).strip().lower() in ("true", "1", "yes", "on")


def convert(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)


def clean_env(d):
    out = {}
    for k, v in d.items():
        k = k.lower()
        if k.startswith("app_"):
            k = k[4:]
        if k == "num_workers":
            k = "workers"
        out[k] = v
    return out


@app.get("/effective-config")
def effective_config(request: Request):
    cfg = dict(defaults)
    cfg.update(yaml_layer)
    cfg.update(clean_env(env_file))
    cfg.update(clean_env(os_env))

    for item in request.query_params.getlist("set"):
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        k = k.strip().lower()
        if k == "num_workers":
            k = "workers"
        cfg[k] = v

    result = {k: convert(k, v) for k, v in cfg.items()}
    result["api_key"] = "****"
    return result