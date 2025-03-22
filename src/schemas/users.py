from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    login: EmailStr
    password: constr(strip_whitespace=True, min_length=4)
    first_name: constr(strip_whitespace=True, min_length=1)
    last_name: constr(strip_whitespace=True, min_length=1)


class UserLogin(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
