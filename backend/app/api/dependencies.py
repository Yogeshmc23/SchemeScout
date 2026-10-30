from typing import Annotated

from fastapi import Depends, Request

from ..services.runtime import Services


def get_services(request: Request) -> Services:
    return request.app.state.services


ServiceDependency = Annotated[Services, Depends(get_services)]
