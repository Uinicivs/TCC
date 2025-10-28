from fastapi import APIRouter, Depends

from src.api.dtos import user_dtos
from src.app.services import UserService
from src.api.dependencies import get_user_service


router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post('/login', response_model=user_dtos.LoginUserOutDTO)
async def login(user_in: user_dtos.LoginUserInDTO, service: UserService = Depends(get_user_service)):
    return await service.login(
        email=user_in.email,
        password=user_in.password
    )


@router.post('/refresh', response_model=user_dtos.RefreshUserOutDTO)
async def refresh(refresh_token: str, service: UserService = Depends(get_user_service)):
    return await service.refresh(refresh_token=refresh_token)
