import os

# FILE configuration
THIS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__)))

CLUSTER_SCHEDULER_IP = os.getenv("CAPE_CLUSTER_SCHEDULER_IP", "127.0.0.1")
CLUSTER_SCHEDULER_PORT = int(os.getenv("CAPE_CLUSTER_SCHEDULER_PORT", 8786))
NUM_WORKERS_PER_REQUEST = int(os.getenv("CAPE_NUM_WORKERS_PER_REQUEST", 8))
