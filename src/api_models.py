from pydantic import BaseModel
from typing import List

class Package(BaseModel):
    package_list: List[str]
    transitive_stack: List[str] = []

class Packages(BaseModel):
    packages: List[Package]
