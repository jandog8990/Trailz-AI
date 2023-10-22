from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from routes import router as book_router

config = dotenv_values(".env")
app = FastAPI()

#@app.get("/")
#async def root():
#    return {"message": "Welcome, bitch."}

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

# Register all of the /book endpoints
app.include_router(book_router, tags=["books"], prefix="/book")
