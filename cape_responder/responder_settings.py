# Copyright 2018 BLEMUNDSBURY AI LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

# FILE configuration
THIS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__)))

def envint(varname: str, default: int) -> int:
   return int(os.getenv(varname, default))

CLUSTER_SCHEDULER_IP = os.getenv("CAPE_CLUSTER_SCHEDULER_IP", "127.0.0.1")
CLUSTER_SCHEDULER_PORT = envint("CAPE_CLUSTER_SCHEDULER_PORT", 8786)
NUM_WORKERS_PER_REQUEST = envint("CAPE_NUM_WORKERS_PER_REQUEST", 8)
