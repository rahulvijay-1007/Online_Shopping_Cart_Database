from pydantic import BaseModel, Field

class CartCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
