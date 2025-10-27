# Project 2 – Extending the JWKS Server (Flask)

**Student:** Tanchhopa Limbu Sanba  
**Course:** CSCE 3550  
**Assignment:** Project 2 – Persistent JWKS Server with SQLite and Key Expiry  

---

## Overview
This project extends the JWKS (JSON Web Key Set) server built in Project 1 by adding **persistent RSA key storage**, **key expiry logic**, and **secure database practices**.  

### Key Features
- RSA key generation and storage in a local SQLite database  
- Automatic seeding of one **expired** and one **valid** key  
- `/auth` endpoint issues JWTs using valid or expired keys  
- `/.well-known/jwks.json` serves only **non-expired** public keys  
- Secure parameterized SQL queries (SQL injection safe)  
- Unit tests achieving **93% coverage**  
- Verified through **Gradebot (65/65 points)**  

Built using **Python 3.13**, **Flask 3.x**, **PyJWT**, and **JWCrypto**.

---

## Prerequisites
- Python 3.10+ (tested on 3.13.1)  
- `pip` package manager  
- macOS / Linux / Windows  
- Virtual environment (`venv`) recommended  
- Gradebot client (provided by professor)

---

## Project Structure

```
jwks-sqlite/
├── tests/
│   └── test_app.py
├── app.py
├── db.py
├── crypto_utils.py
├── gradebot
├── requirements.txt
├── totally_not_my_privateKeys.db
└── README.md
```
---

##  Installation

Clone the repository:
```
git clone https://github.com/chhopa/jwks-sqlite.git
cd jwks-sqlite
```

Create and activate a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows PowerShell
```

Install dependencies:
```
pip install -r requirements.txt
```

## Running the Server

Start Flask:
```
flask run -p 8080
```
By default, the server runs at:
  http://127.0.0.1:8080

## Endpoints

| # | Method | Endpoint | Description |
|:-:|:--|:--|:--|
| 1 | GET | `/healthz` | Returns `{"ok": true}` |
| 2 | POST | `/auth` | Issues JWT signed with a **valid** key |
| 3 | POST | `/auth?expired` | Issues JWT signed with an **expired** key |
| 4 | GET | `/.well-known/jwks.json` | Returns only non-expired public keys |

Example Curl Commands:
```
curl http://127.0.0.1:8080/healthz
curl -XPOST http://127.0.0.1:8080/auth
curl -XPOST “http://127.0.0.1:8080/auth?expired”
curl http://127.0.0.1:8080/.well-known/jwks.json
```
---

##  Database Schema
**Database File:** `totally_not_my_privateKeys.db`

| Column | Type | Description |
|:--|:--|:--|
| `kid` | INTEGER PRIMARY KEY AUTOINCREMENT | Unique key ID |
| `key` | BLOB | PEM-encoded RSA private key |
| `exp` | INTEGER | Unix timestamp expiration time |

Auto-seeded Records:
| Type | Expiration Condition |
|:--|:--|
| Expired Key | `exp < now()` |
| Valid Key | `exp > now()` |

---

##  Testing & Coverage
```
coverage run -m pytest
coverage report -m
```
```
=================================================================================
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
app.py                 45      5    89%   30-31, 35-36, 93
crypto_utils.py        18      0   100%
db.py                  21      3    86%   32-34
tests/test_app.py      38      0   100%
-------------------------------------------------
TOTAL                 122      8    93%
```
 All tests passed!
 Coverage exceeds 80 % requirement!

 ### Manual Endpoint Testing
```
 # Valid JWT
curl -XPOST http://127.0.0.1:8080/auth
# Expired JWT
curl -XPOST "http://127.0.0.1:8080/auth?expired"
# Public JWKS
curl http://127.0.0.1:8080/.well-known/jwks.json
```
---

## Run the Test Client(Gradebot)
```
./gradebot project2
```

## Gradebot Output
```
╭────────────────────────────────┬────────┬──────────┬─────────╮
│ RUBRIC ITEM                    │ ERROR? │ POSSIBLE │ AWARDED │
├────────────────────────────────┼────────┼──────────┼─────────┤
│ /auth valid JWT authN          │        │       15 │      15 │
│ Valid JWK found in JWKS        │        │       20 │      20 │
│ Database exists                │        │       15 │      15 │
│ Database query uses parameters │        │       15 │      15 │
├────────────────────────────────┼────────┼──────────┼─────────┤
│                                │  TOTAL │       65 │      65 │
╰────────────────────────────────┴────────┴──────────┴─────────╯
```

