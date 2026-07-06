from typing import Literal

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from src.app.config import settings
from src.app.deps import get_db
from src.app.middleware.auth import create_access_token
from src.app.schemas.user import UserOut
from src.models.device import Device
from src.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()

if settings.OAUTH_GOOGLE_CLIENT_ID:
    oauth.register(
        name="google",
        client_id=settings.OAUTH_GOOGLE_CLIENT_ID,
        client_secret=settings.OAUTH_GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

if settings.OAUTH_APPLE_CLIENT_ID:
    oauth.register(
        name="apple",
        client_id=settings.OAUTH_APPLE_CLIENT_ID,
        client_secret=settings.OAUTH_APPLE_CLIENT_SECRET,
        authorize_url="https://appleid.apple.com/auth/authorize",
        access_token_url="https://appleid.apple.com/auth/token",
        client_kwargs={"scope": "name email"},
    )

if settings.OAUTH_FACEBOOK_CLIENT_ID:
    oauth.register(
        name="facebook",
        client_id=settings.OAUTH_FACEBOOK_CLIENT_ID,
        client_secret=settings.OAUTH_FACEBOOK_CLIENT_SECRET,
        authorize_url="https://www.facebook.com/v18.0/dialog/oauth",
        access_token_url="https://graph.facebook.com/v18.0/oauth/access_token",
        client_kwargs={"scope": "email public_profile"},
    )

PROVIDERS = ["google", "apple", "facebook"]


@router.get("/login/{provider}")
async def login(provider: str, request: Request):
    if provider not in PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown provider: {provider}",
        )
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{provider} OAuth is not configured",
        )
    redirect_uri = request.url_for("callback", provider=provider)
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/callback/{provider}", name="callback")
async def callback(
    provider: str, request: Request, db: Session = Depends(get_db)
):
    if provider not in PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown provider: {provider}",
        )

    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)

    if provider == "google":
        resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            token=client.token,
        )
        profile = resp.json()
        email = profile.get("email", "")
        first_name = profile.get("given_name", "")
        last_name = profile.get("family_name", "")
    elif provider == "apple":
        userinfo = token.get("userinfo", {})
        email = userinfo.get("email", "")
        name_info = userinfo.get("name", {})
        first_name = name_info.get("firstName", "")
        last_name = name_info.get("lastName", "")
    elif provider == "facebook":
        resp = await client.get(
            "https://graph.facebook.com/me?fields=id,email,first_name,last_name",
            token=client.token,
        )
        profile = resp.json()
        email = profile.get("email", "")
        first_name = profile.get("first_name", "")
        last_name = profile.get("last_name", "")
    else:
        email = ""
        first_name = ""
        last_name = ""

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve email from provider",
        )

    user = db.query(User).filter_by(
        email=email, social_provider=provider
    ).first()

    if user is None:
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            social_provider=provider,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        device = db.query(Device).filter(
            Device.user_id == None
        ).order_by(Device.d_id).first()
        if device:
            device.user_id = user.id
            db.commit()

    access_token = create_access_token(user.id)
    user_out = UserOut(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        social_provider=user.social_provider,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )

    import urllib.parse
    params = urllib.parse.urlencode({
        "access_token": access_token,
        "user": user_out.model_dump_json(),
    })
    redirect_url = f"{settings.FRONTEND_URL}/login?{params}"
    return RedirectResponse(url=redirect_url)
