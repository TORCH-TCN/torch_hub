from typing import Optional
from prefect.blocks.core import Block
from pydantic import SecretStr

class UploadCredentials(Block):
    host: Optional[str] = None
    type: Optional[str] = None
    username: Optional[str] = None
    password: Optional[SecretStr] = None
