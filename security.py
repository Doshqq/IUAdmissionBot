import os

try:
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS").split(",")]
    OPERATOR_IDS = [int(x) for x in os.getenv("OPERATOR_IDS").split(",")]
except ValueError:
    print("ADMIN_IDS is not set in .env file")