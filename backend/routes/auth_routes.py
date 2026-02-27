from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from models.user import LoginRequest, LoginResponse, UserResponse
from auth import verify_password
from jwt_handler import create_token, verify_token
from utils.db_utils import users_collection

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user."""
    user_id = verify_token(creds.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Authenticate user and return access token."""
    user = await users_collection.find_one({"email": credentials.email})

    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(str(user["_id"]))

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user.get("role", "appeals_manager")
        }
    )

@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)):
    """Get current authenticated user."""
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        role=user.get("role", "appeals_manager")
    )
