from pydantic import BaseModel

class SignUp(BaseModel):
    code1:int
    first_name: str
    last_name: str
    code2:int
    company: str
    position: str
    code3:int
    email: str
    password: str
    code4:int

class Login(BaseModel):
    email: str
    password: str

class Verify_SignUp(BaseModel):
    verification_code:str
    first_name: str
    last_name: str
    company: str
    position: str
    email: str
    password: str