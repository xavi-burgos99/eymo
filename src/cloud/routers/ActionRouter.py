import importlib
import logging

from typing import Annotated
from fastapi import HTTPException, APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.cloud.routers.model.ActionRequest import ActionRequest
from src.cloud.routers.Security import Eymo_sec, User, Token, get_current_active_user


app = APIRouter()

logger = logging.getLogger("default-logger")
logger.setLevel(logging.DEBUG)

action_instances_cache = {}

@app.get("/action/perform", response_model=None)
async def perform_action(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: ActionRequest
    ):
    actionName = request.action.capitalize() + "Action"
    action_module_path = f"src.cloud.actions.{request.action.lower()}.{actionName}"
    try:
        if actionName not in action_instances_cache:
            print("Loading action module: ", action_module_path)
            module = importlib.import_module(action_module_path)
            ActionClass = getattr(module, actionName)
            action_instances_cache[actionName] = ActionClass()
        return action_instances_cache[actionName].handle(request.parameters)
    except ImportError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Action '{request.action}' not found with error: {e}")
    except AssertionError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/authentication")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    Es = Eymo_sec()
    user = Es.authenticate_user(form_data.username, form_data.password)
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
    access_token = Es.create_access_token(
        data={"sub": user.get('username')}
    )
    return Token(access_token=access_token, token_type="bearer")

