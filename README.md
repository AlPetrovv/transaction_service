# Transaction Service

A Django-based microservice for handling financial transactions with asynchronous processing capabilities using Celery and Redis.

## Features
- RESTful API for transaction management
- PostgreSQL database for data persistence
- Redis for message brokering and caching
- Containerized with Docker

## Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Poetry (Python dependency management)
- PostgreSQL
- Redis

## Getting Started

### Local Development Setup

1. Clone the repository:
2. make build && make run 
3. create wallets from db
4. request POST `http://localhost:8000/api/stransfer`
```python 
data={"from_wallet_id": "some_number", "to_wallet_id": "some_number", "amount": "100"}
```