import importlib

from fastapi import HTTPException, APIRouter, status
from src.cloud.routers.model.ActionRequest import ActionRequest

app = APIRouter()


@app.get("/action/perform", response_model=None)
async def perform_action(request: ActionRequest):
    try:
        actionName = request.action.capitalize() + "Action"
        module = importlib.import_module(f"src.cloud.actions.{request.action.lower()}.{actionName}")
        ActionClass = getattr(module, actionName)
        action_instance = ActionClass()
        result = action_instance.handle(request.parameters)
        return result
    except ImportError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Action '{request.action}' not found")
    except AssertionError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
