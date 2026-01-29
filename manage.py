from fastapi import FastAPI
from feeds.views import feed_router
import uvicorn

app = FastAPI(title="Instagram App Backend", version="1.0.0")

app.include_router(feed_router)


@app.get("/")
def root():
    return {"message": "Instagram App Backend API"}



if __name__ == "__main__":
    uvicorn.run(
        "manage:app",
        host="localhost",
        port=8000,
        reload=True,
    )
