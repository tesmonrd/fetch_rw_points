# Fetch Rewards - Points Assignment
Authored: Rick Tesmond\
Contact: tesmonrd@gmail.com



## Overview
Our users have points in their accounts. Users only see a single balance in their accounts. But for reporting purposes we actually track their points per
payer/partner. In our system, each transaction record contains: payer (string), points (integer), timestamp (date).
For earning points it is easy to assign a payer, we know which actions earned the points. And thus which partner should be paying for the points.
When a user spends points, they don't know or care which payer the points come from. But, our accounting team does care how the points are spent.

There are two rules for determining what points to "spend" first:
* We want the oldest points to be spent first (oldest based on transaction timestamp, not the order they’re received)
* We want no payer's points to go negative.


### Technology
* **Python 3.9** - important for use of "f-strings"
* FastAPI Framework
* sqlalchemy (sqlite) - database file is created when the application runs for the first time. Can delete the db file to clear it easily.


## How to run it
Ensure you have a Python 3.9 version installed and `python` defaults to version 3.9, or else replace the python commands with `python3.9`.

* Navigate to a new project directory
* `git clone` from repo: https://github.com/tesmonrd/fetch_rw_points.git
* initialize you virtual environment of choice and activate it... i use `python -m venv yourenvname`. 
* `cd` into the project directory, and load the requirements from requirements.txt using `pip install -r requirements.txt`.
* Run `uvicorn app.main:app` from your command line and you're off! Defaults to run on `http://127.0.0.1:8000`.


## Interacting with the Web App
The FastAPI config page is the default home page. You can examine and run API queries directly from the page. Otherwise, you can execute queries using `curl`

### Curl commands
#### Balances:
`curl -X 'GET' 'http://127.0.0.1:8000/balances/' -H 'accept: application/json'`
#### Spend:
`curl -X 'POST' 'http://127.0.0.1:8000/spend/?spend_amt=5000' -H 'accept: application/json'`
#### Add transactions:
`curl -X 'POST' 'http://127.0.0.1:8000/transaction/add/' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{ "payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z"
}'`
#### Transactions:
`curl -X 'GET' 'http://127.0.0.1:8000/transactions/' -H 'accept: application/json'`
#### Bulk add:
`curl -X 'POST' 'http://127.0.0.1:8000/transaction/add/bulk' -H 'accept: application/json' -H 'Content-Type: application/json' -d '[
    { "payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z" },
    { "payer": "UNILEVER", "points": 200, "timestamp": "2022-10-31T11:00:00Z" },
    { "payer": "DANNON", "points": -200, "timestamp": "2022-10-31T15:00:00Z" },
    { "payer": "MILLER COORS", "points": 10000, "timestamp": "2022-11-01T14:00:00Z" },
    { "payer": "DANNON", "points": 1000, "timestamp": "2022-11-02T14:00:00Z" }
]'`

## How to test

Simply run `pytest` from the project's root directory!
