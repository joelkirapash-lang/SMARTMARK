from functools import wraps

from flask import g, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app.models import User


def load_current_user():
    """Populates g.current_user / g.school_id from the JWT. The school_id
    ALWAYS comes from the verified token, never from request params/body -
    this is what makes cross-tenant access impossible even if a client
    tries to pass a different school_id."""
    verify_jwt_in_request()
    claims = get_jwt()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user is None:
        return None
    g.current_user = user
    g.school_id = claims.get("school_id")
    g.role = claims.get("role")
    return user


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = load_current_user()
        if user is None:
            return jsonify({"error": "Not authenticated"}), 401
        return fn(*args, **kwargs)

    return wrapper


def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = load_current_user()
            if user is None:
                return jsonify({"error": "Not authenticated"}), 401
            if user.role.value not in roles:
                return jsonify({"error": "Forbidden: insufficient role"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def scoped(model):
    """Returns a query for `model` pre-filtered to the current request's
    school_id. Use this instead of `Model.query` everywhere in routes so
    tenant isolation can never accidentally be skipped."""
    return model.query.filter_by(school_id=g.school_id)
