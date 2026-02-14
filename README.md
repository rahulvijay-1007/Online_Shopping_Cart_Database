# Online Shopping Cart Backend

A production-focused e-commerce backend built with FastAPI and MySQL, designed to handle
authentication, admin control, and concurrency-safe checkout.

---

## Why this project exists

Most e-commerce tutorials ignore real-world problems like:
- concurrent checkouts
- inventory overselling
- admin-only write access
- transactional guarantees

This project solves those problems deliberately.

---

## Features

- JWT-based authentication (OAuth2 password flow)
- Role-based access control (admin vs user)
- Admin control plane:
  - add products
  - update price
  - update stock
- Cart → Order flow with atomic checkout
- Concurrency-safe stock handling using row-level locking
- Analytics endpoint for top-selling products
- Fully Dockerized setup

---

## Tech Stack

- **Backend:** FastAPI
- **Database:** MySQL (InnoDB)
- **Auth:** JWT (role embedded in token)
- **Infra:** Docker Compose

---

## Architecture Highlights

- Stateless authentication using JWT
- Admin-only routes protected via dependency injection
- Checkout runs inside a single DB transaction
- `SELECT ... FOR UPDATE` prevents overselling under concurrency
- Rollback on failure guarantees consistency

---

## Concurrency Safety (Key Part)

Checkout logic:
1. Starts a DB transaction
2. Locks cart + product rows
3. Validates stock
4. Creates order and order_items
5. Deducts stock
6. Clears cart
7. Commits atomically

Stress-tested with concurrent checkout requests:
- Only one order succeeds
- Others fail cleanly
- No negative stock
- No partial orders

---

## How to Run

```bash
docker compose up --build


##Backend runs at:
http://<IP ADDRESS>:8000

##API docs
http://<IP ADDRESS>:8000/docs

##IP ADDRESS
Go to linux and type ip a----this will give the ip address of the system
