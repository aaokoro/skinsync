if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "prepare":
        from skinsync.prepare import main as prepare_main

        prepare_main(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        import uvicorn

        from skinsync.api import app

        uvicorn.run(app, host="0.0.0.0", port=43173)
