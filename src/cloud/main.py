from fastapi import FastAPI
from src.cloud.routers import ActionRouter

app = FastAPI()

app.include_router(ActionRouter.app)


@app.get("/")
async def root():
    return {"message": "Server is running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
