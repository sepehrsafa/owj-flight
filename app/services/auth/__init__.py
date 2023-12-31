from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from typing import Annotated
from fastapi import Depends
from owjcommon.token import validate_token
from owjcommon.exceptions import OWJException, OWJPermissionException
from owjcommon.enums import UserTypeChoices, UserSet
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="https://account.owj.app/api/account/v1/auth/oauth2"
)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    return await validate_token(
        security_scopes,
        token,
        secret_key=settings.jwt.secret_key,
        algorithm=settings.jwt.algorithm,
    )


def check_user_set(user, user_set: UserSet):
    if user.type not in user_set.value:
        raise OWJException("E1030", 403)
