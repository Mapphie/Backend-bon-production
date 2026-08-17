
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel
from sqlalchemy import text

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.database.database import SyncSession


router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = None

class UserOut(BaseModel):
    id:str
    username: str
    role: Optional[str] = None
    is_active: bool
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
@router.post("/register", response_model=UserOut)
def register(user: UserCreate):
    with SyncSession() as db:
        stmt = text("SELECT id from dbo.users WHERE username = :username")
        existing = db.execute(stmt, {"username": user.username}).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Cet utilisateur existe déjà")
        
        insert_query = text("""
            INSERT INTO dbo.users (username, password, role)
            OUTPUT INSERTED.id, INSERTED.username, INSERTED.role, INSERTED.is_active 
            values (:username, :password, :role)                   
        """)
        row = db.execute(insert_query, {
            "username": user.username,
            "password": hash_password(user.password),
            "role": user.role,
        }).mappings().first()
        
        db.commit()
        
        return {
            "id": str(row["id"]),
            "username": row["username"],
            "role": row["role"],
            "is_active": bool(row["is_active"]),
        }
        
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with SyncSession() as db:
        query = text("SELECT id, username, password, role, is_active FROM dbo.users WHERE username = :username")
        row = db.execute(query, {"username": form_data.username}).mappings().first()
        
    if not row or not verify_password(form_data.password, row["password"]):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not row["is_active"]:
        raise HTTPException(status_code=403, detail="Utilisateur désactivé")
    
    token = create_access_token(
        data = {"sub": str(row["id"]), "username": row["username"], "role": ["role"]}
    )
    
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str= Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_access_token(token)        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role"),
    }
        
@router.get("/me", response_model=UserOut)
def me(current_user: dict = Depends(get_current_user)):
    with SyncSession() as db:
        query = text("SELECT id, username, role, is_active from dbo.users WHERE id = :id")
        result = db.execute(query, {"id": current_user["id"]}).mappings().first()
        
    if not result:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    return {
        "id": str(result["id"]),
        "username": result["username"],
        "role": result["role"],
        "is_active": bool(result["is_active"]),
    }