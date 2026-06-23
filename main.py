from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
from models import User, Course
from typing import List
from schemas import CourseCreate, CourseOut, UserRegister, UserOut, Token
import models
from sqlalchemy.orm import joinedload
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token, verify_password, hash_password, get_current_user, require_any_role
from pagination import pagination_params
from exceptions import ForbiddenException,NotFoundException
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/register", response_model=UserOut, status_code=201)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    uname = user.name.strip()
    umail = user.email.strip()
    password = user.password
    user_role = user.role
    if not uname or not umail or not password:
        raise HTTPException(status_code=422, detail="Name, Email and password cannot be empty")
    chkmail = db.query(User).filter(User.email == umail).first()
    if chkmail is not None:
        raise HTTPException(status_code=400, detail="Email already registered")
    encr_pass = hash_password(password)
    new_user = User(name=uname, email=umail, hashed_password=encr_pass,role=user_role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    data = {"sub": str(user.id)}
    token = create_access_token(data)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/dashboard",response_model=UserOut)
def supervisory_dashboard(current_user: User = Depends(require_any_role("teacher","admin"))):
    return current_user


@app.post("/courses", response_model=CourseOut, status_code=201)
def create_course(course: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_any_role("teacher"))):
    ncourse = course.title.strip()
    if not ncourse:
        raise HTTPException(status_code=422, detail="Course Title cannot be empty")
    new_course = Course(title=ncourse, owner_id=current_user.id)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@app.get("/users/{user_id}", response_model=UserOut)
def get_user_details_byid(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed_roles = {"teacher", "admin"}
    if current_user.id != user_id and current_user.role.lower() not in allowed_roles:
        raise ForbiddenException("You do not have permission to view this user.")
    fetchuser = db.query(User).options(joinedload(User.courses)).filter(User.id == user_id).first()
    if not fetchuser:
        raise NotFoundException()
    return fetchuser


@app.get("/users", response_model=List[UserOut])
def get_all_users(db: Session = Depends(get_db),current_user: User = Depends(require_any_role("teacher", "admin")),pagination: dict=Depends(pagination_params)):
    users= db.query(User).offset(pagination["offset"]).limit(pagination["limit"]).all()
    return users


@app.get("/courses",response_model=List[CourseOut])
def get_courses(db: Session = Depends(get_db),current_user: User = Depends(get_current_user),pagination: dict=Depends(pagination_params)):
    courses = db.query(Course).offset(pagination["offset"]).limit(pagination["limit"]).all()
    return courses


@app.delete("/users/{user_id}")
def delete_user_byid(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    allowed_roles = {"admin"}
    if current_user.id != user_id and current_user.role.lower() not in allowed_roles:
        raise ForbiddenException("You do not have permission to delete this user.")
    fetchuser = db.query(User).filter(User.id == user_id).first()
    if not fetchuser:
        raise NotFoundException()
    db.delete(fetchuser)
    db.commit()
    return {"message": "User deleted successfully"}
