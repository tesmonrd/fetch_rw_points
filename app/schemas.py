from pydantic import BaseModel


class TransactionBase(BaseModel):
    payer: str
    points: int
    timestamp: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "payer": "DANNON",
                "points": 300,
                "timestamp": "2022-10-31T10:00:00Z"
            }
        }


class Transaction(TransactionBase):
    id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "payer": "DANNON",
                "points": 300,
                "timestamp": "2022-10-31T10:00:00Z"
            }
        }
