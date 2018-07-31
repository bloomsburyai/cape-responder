import os
from dask.distributed import Client
from cape_responder.responder_settings import CLUSTER_SCHEDULER_IP, CLUSTER_SCHEDULER_PORT
from logging import info

CLUSTER_CLIENT = None
ENABLE_PARALLELIZATION = os.getenv('ENABLE_PARALLELIZATION', 'false').lower() == 'true'


def connect():
    global CLUSTER_CLIENT
    if CLUSTER_CLIENT is None:
        if ENABLE_PARALLELIZATION:
            info("Parallelization ENABLED")
            CLUSTER_CLIENT = Client(f'{CLUSTER_SCHEDULER_IP}:{CLUSTER_SCHEDULER_PORT}')  # Connect to the cluster
        else:
            info("Parallelization DISABLED")
            CLUSTER_CLIENT = DummyClient()
    return CLUSTER_CLIENT


class DummyResult:
    def __init__(self, value):
        self.value = value

    def result(self):
        return self.value


class DummyClient:
    def submit(self, funct, *args, **kwargs):
        if args and isinstance(args[0], list) and getattr(args[0][0], 'result', False):
            args = ([arg.result() for arg in args[0]],) + args[1:]
        return DummyResult(funct(*args, **kwargs))

    def map(self, funct, args):
        if args and getattr(args[0], 'result', False):
            args = [arg.result() for arg in args]
        return [DummyResult(funct(arg)) for arg in args]

    def gather(self, funct, *args, **kwargs):
        return [DummyResult(funct(arg)) for arg in args]
