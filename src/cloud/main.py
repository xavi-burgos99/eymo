from fastapi import FastAPI
from src.cloud.routers import ActionRouter

import ssl

PORT = 7125
app = FastAPI()
app.include_router(ActionRouter.app)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('./src/cloud/static/cert_tst.pem', keyfile='./src/cloud/static/key_tst.pem')


@app.get("/")
async def root():
    return {"message": "Server is running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT, ssl=ssl_context)
