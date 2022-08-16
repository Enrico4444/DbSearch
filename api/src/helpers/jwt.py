from flask_jwt_extended import create_access_token, get_jwt_identity
from helpers.user_role_management import get_permissions

def refresh_token():
    """
        Get a new access token without requiring username and password—only the "refresh token"
        provided in the /login endpoint.

        Note that refreshed access tokens have a `fresh=False`, which means that the user may have not
        given us their username and password for potentially a long time (if the token has been
        refreshed many times over).
    """
    user = get_jwt_identity()
    # get permissions as additional claim
    permissions = {"permissions": get_permissions(user)}
    return create_access_token(identity=user, fresh=False, additional_claims=permissions)
            
        