from pydantic import BaseModel
from typing import List,Optional,Literal
class CourseOut(BaseModel):
    id: int
    title: str
    model_config = {"from_attributes": True}# Pydantic v2 (was orm_mode in v1)
class CourseCreate(BaseModel):
    title:str
class UserRegister(BaseModel):
        name: str
        email: str
        password: str
        role: Literal["student", "teacher", "admin"] = "student"
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    courses: List[CourseOut] = [] # nested list of courses
    model_config = {"from_attributes": True}
class Token(BaseModel):
        access_token: str
        token_type: str
class TokenData(BaseModel):
        id: Optional[int] = None