import dotenv
import os
dotenv.load_dotenv()
ORG_DID=os.getenv("NILLION_DID")
ORG_SECRET_KEY=os.getenv("NILLION_SECRET_KEY")

NODE_CONFIG = {
    'node_a': {
        'url': os.getenv("NODE_A_URL"),
        'did': os.getenv("NODE_A_DID")
    },
    'node_b': {
        'url': os.getenv("NODE_B_URL"),
        'did':  os.getenv("NODE_B_DID")
    },
    'node_c': {
        'url': os.getenv("NODE_C_URL"),
        'did': os.getenv("NODE_C_DID")
    },
}