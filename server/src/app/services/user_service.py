from typing import Any
from bson import ObjectId
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.core.security import hash_password, verify_password
from src.app.core.auth import create_access_token, decode_access_token
from src.app.models.user_model import User, UserRole, AuthUser, RefreshUser
from src.app.core.exceptions import (
    translate_mongo_error,

    NotFoundException,
    UpdateFailedException,
    InvalidObjectIdException,
)


class UserService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    async def create_user(self, name: str, email: str, password: str, role: UserRole) -> User:
        try:
            existing = await self.database.users.find_one({"email": email})
            if existing:
                raise ValueError("Email already registered")

            hashed = hash_password(password)
            new_user = User(
                name=name,
                email=email,
                password=hashed,
                role=role,
            )
            user_dict = new_user.model_dump(by_alias=True, exclude={'id'})
            user = await self.database.users.insert_one(user_dict)
            new_user.id = user.inserted_id

            return new_user
        except Exception as e:
            raise translate_mongo_error(e)

    async def get_user_by_email(self, email: str) -> User:
        try:
            user = await self.database.users.find_one({"email": email})
            if not user:
                raise NotFoundException("User not found")
            return User.model_validate(user)
        except Exception as e:
            raise translate_mongo_error(e)

    async def get_user(self, id: str) -> User:
        try:
            if not ObjectId.is_valid(id):
                raise InvalidObjectIdException()

            user_from_db = await self.database.users.find_one({'_id': ObjectId})
        except Exception as e:
            raise translate_mongo_error(e)

        if not user_from_db:
            raise NotFoundException()

        return User.model_validate(user_from_db)

    async def get_users(self) -> list[User]:
        try:
            user_cursor = self.database.users.find({})
            users_from_db = await user_cursor.to_list(length=None)

            return [User.model_validate(user) for user in users_from_db]
        except Exception as e:
            raise translate_mongo_error(e)

    async def increment_flow_count(self, id: str) -> None:
        try:
            if not ObjectId.is_valid(id):
                raise InvalidObjectIdException()

            user = await self.get_user(id)

            update_user: dict[str, Any] = {}
            update_user['flowCount'] = user.flowCount + 1
            update_user['updatedAt'] = datetime.now(timezone.utc)

            result = await self.database.users.update_one(
                {'_id': ObjectId(id)},
                {'$set': update_user}
            )
        except Exception as e:
            raise translate_mongo_error(e)

        if result.matched_count == 0:
            raise NotFoundException()

        if result.modified_count == 0:
            raise UpdateFailedException()

    async def delete_user(self, user_id: str) -> None:
        try:
            if not ObjectId.is_valid(user_id):
                raise InvalidObjectIdException()

            result = await self.database.users.delete_one({"_id": ObjectId(user_id)})
        except Exception as e:
            raise translate_mongo_error(e)

        if result.deleted_count == 0:
            raise NotFoundException("User not found")

    async def login(self, email: str, password: str) -> AuthUser:
        user = await self.get_user_by_email(email)

        if not verify_password(password, user.password):
            raise Exception('Invalid credentials')

        payload = {'sub': user.email, 'role': user.role}
        access_token, access_exp = create_access_token(payload, 'access')
        refresh_token, _ = create_access_token(payload, 'refresh')

        return AuthUser(
            accessToken=access_token,
            refreshToken=refresh_token,
            tokenType='bearer',
            tokenExpires=access_exp
        )

    async def refresh(self, refresh_token: str) -> RefreshUser:
        payload = decode_access_token(refresh_token, expected_type='refresh')

        email = payload.get('sub')
        role = payload.get('role')

        new_access, access_exp = create_access_token(
            {'sub': email, 'role': role},
            'access'
        )
        return RefreshUser(
            accessToken=new_access,
            tokenType='bearer',
            tokenExpires=access_exp
        )
