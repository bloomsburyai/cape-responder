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

from package_settings import NAME, VERSION, PACKAGES, DESCRIPTION
from setuptools import setup
from pathlib import Path
import json
import urllib.request
from functools import lru_cache


@lru_cache(maxsize=50)
def _get_github_sha(github_install_url: str):
    """From the github_install_url get the hash of the latest commit"""
    repository = Path(github_install_url).stem.split('#egg', 1)[0]
    organisation = Path(github_install_url).parent.stem
    with urllib.request.urlopen(f'https://api.github.com/repos/{organisation}/{repository}/commits/master') as response:
        return json.loads(response.read())['sha']


setup(
    name=NAME,
    version=VERSION,
    long_description=DESCRIPTION,
    author='Bloomsbury AI',
    author_email='contact@bloomsbury.ai',
    packages=PACKAGES,
    include_package_data=True,
    install_requires=['dask==0.15.4',
                      'distributed==1.19.2',
                      'numpy==1.15.0',
                      'pytest==3.6.4',
                      'cape_machine_reader==' + _get_github_sha(
                          'git+https://github.com/bloomsburyai/cape-machine-reader#egg=cape_machine_reader'),
                      'cape_document_manager==' + _get_github_sha(
                          'git+https://github.com/bloomsburyai/cape-document-manager#egg=cape_document_manager'),
                      'cape_document_qa==' + _get_github_sha(
                          'git+https://github.com/bloomsburyai/cape-document-qa#egg=cape_document_qa')
                      ],
    dependency_links=[
        'git+https://github.com/bloomsburyai/cape-machine-reader#egg=cape_machine_reader-' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-machine-reader#egg=cape_machine_reader'),
        'git+https://github.com/bloomsburyai/cape-document-manager#egg=cape_document_manager-' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-document-manager#egg=cape_document_manager'),
        'git+https://github.com/bloomsburyai/cape-document-qa#egg=cape_document_qa-' + _get_github_sha(
            'git+https://github.com/bloomsburyai/cape-document-qa#egg=cape_document_qa')
    ],
    package_data={
        '': ['*.*'],
    },
)
