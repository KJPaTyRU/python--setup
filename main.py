import sys

from app_name.config import get_settings
import uvicorn


def run_uvicorn(run_args: dict):
    uvicorn.run("app_name.main:create_app", **run_args)


def main():
    run_uvicorn(get_settings().uvicorn_kwargs)


if __name__ == "__main__":
    sys.exit(main())
