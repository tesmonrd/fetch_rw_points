from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from . import models, schemas, utils
from .database import SessionLocal, engine


description = """
API application that conforms to the base requirements of the Fetch Rewards assignment.

The base cases for the assignment are all met. Users can submit transactions and spend interchangeably, and check
balance. I also included additional endpoints for bulk adding transactions, and reading all transactions.

See the README for deployment instructions.
"""

tags_metadata = [
    {
        "name": "required methods",
        "description": "Operations required for the Fetch API assignment.",
    },
    {
        "name": "additional methods",
        "description": "Operations not required, but helped in development.",
    },
]

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rick Tesmond's Fetch Rewards Assignment",
    description=description,
    openapi_tags=tags_metadata
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["get", "post"],
    allow_headers=["*"],
    allow_credentials=True,
)


def get_db():
    """Generates DB session for application."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
def main():
    """Establish landing page, directs to API docs."""
    return RedirectResponse(url="/docs/")


@app.get("/balances/", tags=["required methods"])
def show_balances(db: Session = Depends(get_db)):
    """Shows balances of all transactions."""
    all_transactions = db.query(models.Transaction).all()
    return utils.calculate_balances(all_transactions, db)


@app.post("/spend/", response_model=List[dict], tags=["required methods"])
def spend_points(spend_amt: int, db: Session = Depends(get_db)):
    """Executes spend on account."""
    if spend_amt <= 0:
        return []
    transactions = db.query(models.Transaction).all()
    return utils.handle_spend(transactions, spend_amt, db)


@app.post("/transaction/add/", response_model=schemas.Transaction, tags=["required methods"])
def add_transaction(transaction: schemas.TransactionBase, db: Session = Depends(get_db)):
    """Creates a new transaction."""
    if transaction.payer and transaction.points and transaction.timestamp:
        try:
            res = utils.create_transaction(transaction, db)
            return res
        except Exception as e:
            return e
    else:
        raise HTTPException(
            status_code=422,
            detail=f"Transaction missing data: {transaction}"
        )


@app.get("/transactions/", response_model=List[schemas.Transaction], tags=["additional methods"])
def show_transactions(db: Session = Depends(get_db)):
    """Returns list of all transactions from DB."""
    transactions = db.query(models.Transaction).all()
    return transactions


@app.post("/transaction/add/bulk/", response_model=List[schemas.Transaction], tags=["additional methods"])
def add_bulk_transactions(transactions: List[schemas.TransactionBase], db: Session = Depends(get_db)):
    """Creates bulk transactions. Accepts a list of dicts that conform to TransactionBase schema."""
    resp = []
    for transaction in transactions:
        if transaction.payer and transaction.points and transaction.timestamp:
            try:
                res = utils.create_transaction(transaction, db)
                resp.append(res)
            except Exception as e:
                return e
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Transaction missing data: {transaction}"
            )
    return resp
