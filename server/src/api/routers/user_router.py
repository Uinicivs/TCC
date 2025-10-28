from fastapi import APIRouter, Depends, status

from src.api.dtos import user_dtos
from src.app.services import UserService
from src.app.models.user_model import User
from src.api.dependencies import is_admin, get_current_user, get_user_service


router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post(
    '/',
    dependencies=[Depends(is_admin)],
    status_code=status.HTTP_201_CREATED,
    response_model=user_dtos.ReadUserOutDTO
)
async def create_user(user_in: user_dtos.CreateUserInDTO, service: UserService = Depends(get_user_service)):
    return await service.create_user(
        name=user_in.name,
        email=user_in.email,
        password=user_in.password,
        role=user_in.role
    )


@router.get(
    '/me',
    response_model=user_dtos.ReadUserOutDTO
)
async def get_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.get(
    '/',
    dependencies=[Depends(is_admin)],
    response_model=list[user_dtos.ReadUsersOutDTO]
)
async def get_users(service: UserService = Depends(get_user_service)):
    return await service.get_users()


@router.delete(
    '/{id}',
    dependencies=[Depends(is_admin)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(id: str, service: UserService = Depends(get_user_service)):
    return await service.delete_user(id)
