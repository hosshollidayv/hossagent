from fastapi import APIRouter
from hossagent.route_hygiene import route_inventory

router = APIRouter()

@router.get("/api/route-inventory")
async def api_route_inventory():
    from hoss_core import app
    return {
        "status": "ok",
        "routes": route_inventory(app),
    }
