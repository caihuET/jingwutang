"""商城与背包 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.service.shop_service import ShopService

router = APIRouter()


@router.get("/shop/list")
def shop_list(category: int = 0, db: Session = Depends(get_db)):
    return {"code": 0, "data": ShopService(db).get_shop(category), "message": "ok"}


class BuyRequest(BaseModel):
    item_id: int
    quantity: int = 1


@router.post("/shop/buy")
def shop_buy(req: BuyRequest, player_id: int = 1, db: Session = Depends(get_db)):
    result = ShopService(db).buy(player_id, req.item_id, req.quantity)
    return {"code": 0, "data": result, "message": "购买成功"}


@router.get("/inventory/list")
def inventory_list(player_id: int = 1, db: Session = Depends(get_db)):
    return {"code": 0, "data": ShopService(db).get_inventory(player_id), "message": "ok"}


class UseRequest(BaseModel):
    item_id: int
    quantity: int = 1


@router.post("/inventory/use")
def inventory_use(req: UseRequest, player_id: int = 1, db: Session = Depends(get_db)):
    result = ShopService(db).use_item(player_id, req.item_id, req.quantity)
    return {"code": 0, "data": result, "message": "使用成功"}
