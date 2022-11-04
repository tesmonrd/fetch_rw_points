from dateutil import parser
from datetime import datetime
from . import models, schemas
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List


def create_transaction(transaction: schemas.TransactionBase, db: Session):
    """Creates a transaction and saves it to the DB."""
    if _validate_datetime(transaction.timestamp):
        new_transaction = models.Transaction(**transaction.dict())
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return new_transaction


def calculate_balances(
        transactions: List[schemas.Transaction],
        db: Session
):
    """Calculates the balance using all transactions."""
    res_list = []
    unique_payers = set(trans.payer for trans in transactions)
    for payer in unique_payers:
        score_balance = 0
        trans_list = db.query(models.Transaction).filter(models.Transaction.payer == payer).all()
        for action in trans_list:
            score_balance += action.points
        res_list.append({"payer": payer, "points": score_balance})
    return res_list


def handle_spend(transactions:List[schemas.Transaction], spend_amt: int, db: Session):
    """Executes the spend logic on our DB, returns spending actions taken."""
    curr_balances = {payer_bal["payer"]: payer_bal["points"] for payer_bal in calculate_balances(transactions, db)}
    # Sort transactions by timestamp to conform to assignment requirements
    ordered_trans = _sort_data(transactions)
    actions = []
    trans_counter = {}
    current_spend = spend_amt
    for entry in ordered_trans:
        # Skip any entry where payer balance is 0
        if curr_balances[entry.payer] == 0:
            continue
        if current_spend - entry.points <= 0 or curr_balances[entry.payer] - current_spend <= 0:
            # Case where payer balance would be 0
            if curr_balances[entry.payer] - current_spend < 0:
                total_spent = -entry.points
            # Case where spend amount would be 0
            else:
                total_spent = -current_spend
            actions.append({"payer": entry.payer, "points": total_spent})
            current_spend -= total_spent
        # Any case where points balance or spend amount is not 0
        else:
            total_spent = -entry.points
            actions.append({"payer": entry.payer, "points": total_spent})
            current_spend -= entry.points

        curr_balances[entry.payer] -= total_spent
        if current_spend <= 0:
            break

    # Build return values and submit spending transaction
    for action in actions:
        if trans_counter.get(action["payer"]):
            trans_counter[action["payer"]] += action["points"]
        else:
            trans_counter[action["payer"]] = action["points"]
        action["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        _new_trans = create_transaction(schemas.TransactionBase(**action), db)
    return [{"payer": k, "points": v} for k, v in trans_counter.items()]


def _sort_data(transactions: List[schemas.Transaction]):
    """Helper method to sort list of transactions for spending logic."""
    return sorted(transactions, key=lambda x: parser.isoparse(x.timestamp))


def _validate_datetime(timestamp):
    """Ensures consistent datetime format."""
    try:
        parser.isoparse(timestamp)
        return True
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Timestamp is not in ISO format: {timestamp}"
        )