"""
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
"""

from setuptools import setup, find_packages

setup(
    name="clutrr",
    version="1.2.0",
    description="Compositional Language Understanding with Text-based Relational Reasoning",
    packages=find_packages(exclude=("data", "mturk")),
    include_package_data=True,
)
