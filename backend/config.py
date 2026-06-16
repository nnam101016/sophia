import os
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)


print("Loading env from:", ENV_PATH)


load_dotenv(ENV_PATH)



HELIUS_API_KEY = os.getenv(
    "HELIUS_API_KEY"
)



GMGN_CONFIG = {

    "device_id":
    os.getenv("GMGN_DEVICE_ID"),

    "fp_did":
    os.getenv("GMGN_FP_DID"),

    "client_id":
    os.getenv("GMGN_CLIENT_ID")

}



print("GMGN CONFIG:")
print(GMGN_CONFIG)

print("HELIUS:")
print(
    HELIUS_API_KEY[:5]
    if HELIUS_API_KEY
    else None
)