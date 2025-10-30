from bson import ObjectId
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from src.app.core.auth import decode_access_token
from src.app.models.user_model import User, UserRole
from src.app.services import UserService, FlowService
from src.api.dependencies.service import get_user_service, get_flow_service


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/auth/login',
    scheme_name="BearerAuth"
)


async def get_current_user(token: str = Depends(oauth2_scheme),
                           service: UserService = Depends(get_user_service)) -> User:
    try:
        try:
            payload = decode_access_token(token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )

        if (email := payload.get('sub')) is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )

        user = await service.get_user_by_email(email)

        assert user.id is not None

        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


async def get_authorized_user(id: str,
                              current_user: User = Depends(get_current_user),
                              service: FlowService = Depends(get_flow_service)) -> User:
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid flow ID'
        )

    flow = await service.get_flow(id)

    if flow.ownerId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You do not have access to this flow {id}'
        )

    return current_user


def is_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admins only'
        )

    return current_user
