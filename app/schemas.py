from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8, max_length=255)

class UserList(BaseModel):
    id: int
    name: str
    email: str

    model_config = {
        'from_attributes': True
    }

class UserLogin(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=255)