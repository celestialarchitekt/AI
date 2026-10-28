
"""
====================
fastAPI - request/response
===================
"""

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

class LoginRequest(BaseModel):
    email: EmailStr
    password : str


class LoginResponse(BaseModel):
    status:str
    access_token:str
    user_id:int


@app.post("/login", response_model = LoginResponse)
def login_user(credentials: LoginRequest):
    return {
        "status" : "authentication",
        "access_token" : "bearer_token",
        "user_id" : 1
    } 


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)



"""
1. Client Sends Payload (curl)
   │
   ▼
2. FastAPI Validates & Creates Instance
   credentials = LoginRequest(email="...", password="...")
   │
   ▼
3. Function Executes
   access email/password via credentials.email & credentials.password
   │
   ▼
4. Server Returns Raw Output
   {"status": "authenticated", "access_token": "...", "user_id": 42}
   │
   ▼
5. FastAPI Filters & Formats against Response Model
   LoginResponse enforces JSON structure ──► Sent to Client

"""