#!/usr/bin/env python3
""" Authentication
"""
from bcrypt import hashpw, gensalt, checkpw
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from uuid import uuid4
from typing import Union


def _hash_password(password: str) -> str:
    """ This func takes in a string argument, converts it to unicode
    and returns salted, hashed password as bytestring
    """
    return hashpw(password.encode('utf-8'), gensalt())


def _generate_uuid() -> str:
    """ This func generates UUID
    and Returns string representation of new UUID
    """
    return str(uuid4())


class Auth:
    """An Auth class to interact with the authentication database.
    """

    def __init__(self):
        """ Initialization """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """ This func registers and returns a new user if email isn't listed"""
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            hashed_password = _hash_password(password)
            new_user = self._db.add_user(email, hashed_password)
            return new_user

    def valid_login(self, email: str, password: str) -> bool:
        """ This func checks if user password is valid, locates by email """
        try:
            found_user = self._db.find_user_by(email=email)
            return checkpw(
                password.encode('utf-8'),
                found_user.hashed_password
                )
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """ This func creates session ID using UUID, finds user by email """
        try:
            found_user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None

        session_id = _generate_uuid()
        self._db.update_user(found_user.id, session_id=session_id)
        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[str, None]:
        """ This func finds user by session_id """
        if session_id is None:
            return None
        try:
            found_user = self._db.find_user_by(session_id=session_id)
            return found_user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: str) -> None:
        """ This func updates user's session_id to None"""
        if user_id is None:
            return None
        try:
            found_user = self._db.find_user_by(id=user_id)
            self._db.update_user(found_user.id, session_id=None)
        except NoResultFound:
            return None

    def get_reset_password_token(self, email: str) -> str:
        """ This func finds user by email, updates user's reset_toke with UUID """
        try:
            found_user = self._db.find_user_by(email=email)
        except NoResultFound:
            raise ValueError

        reset_token = _generate_uuid()
        self._db.update_user(found_user.id, reset_token=reset_token)
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """ This func uses the reset_token to find the corresponding user.
            If it does'nt exist, raises a ValueError exception.
        """
        if reset_token is None or password is None:
            return None

        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            raise ValueError

        hashed_password = _hash_password(password)
        self._db.update_user(user.id,
                             hashed_password=hashed_password,
                             reset_token=None)
