import importlib
import logging

from fastapi import HTTPException, APIRouter, status
from src.cloud.routers.model.ActionRequest import ActionRequest

app = APIRouter()

logger = logging.getLogger("defualt-logger")
logger.setLevel(logging.DEBUG)

action_instances_cache = {}

@app.get("/action/perform", response_model=None)
async def perform_action(request: ActionRequest):
    actionName = request.action.capitalize() + "Action"
    action_module_path = f"src.cloud.actions.{request.action.lower()}.{actionName}"
    try:
        if actionName not in action_instances_cache:
            print("Loading action module: ", action_module_path)
            module = importlib.import_module(action_module_path)
            ActionClass = getattr(module, actionName)
            action_instances_cache[actionName] = ActionClass()
        return action_instances_cache[actionName].handle(request.parameters)
    except ImportError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Action '{request.action}' not found")
    except AssertionError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
