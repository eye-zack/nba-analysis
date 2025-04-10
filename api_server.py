from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import predict, auth_routes

app = FastAPI()

origins = [
    "http://localhost:3000",  # React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(auth_routes.router)