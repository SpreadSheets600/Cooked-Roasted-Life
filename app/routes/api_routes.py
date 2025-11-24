from . import api_bp
from ..models import CombinedUserData
from ..models.database import db, Roast, RecentRoast
from ..services import SpotifyService, ValorantService, AnimeService, GeminiRoaster

import uuid
from datetime import datetime
from flask import jsonify, request, session


@api_bp.get("/ping")
def ping():
    return jsonify({"ok": True})


@api_bp.post("/roast")
def generate_roast():
    body = request.get_json(force=True) if request.is_json else request.form
    valorant_name = body.get("valorant_name")
    valorant_tag = body.get("valorant_tag")
    anilist_user = body.get("anilist_user")

    spotify_service = SpotifyService()
    if spotify_service.is_ready():
        spotify_data = spotify_service.get_roast_profile_data()
    else:
        spotify_data = {}
        # Remove Spotify token if present
        if session.get("spotify_token_info"):
            session.pop("spotify_token_info", None)

    valorant_data = {}
    if valorant_name and valorant_tag:
        valorant_data = ValorantService().get_roast_data(
            valorant_name, valorant_tag, region=body.get("valorant_region", "na")
        )

    anime_data = {}
    if anilist_user:
        anime_data = AnimeService().get_roast_data(anilist_user)

    combined = CombinedUserData(
        spotify=spotify_data, valorant=valorant_data, anime=anime_data
    )
    prompt_block = combined.prompt_block()

    roast_text = ""
    try:
        gemini = GeminiRoaster()
        roast_text = gemini.roast(prompt_block)
    except Exception as e:
        roast_text = f"Failed To Generate Roast: {e}"

    roast_id = str(uuid.uuid4())[:8]

    user_id = session.get("user_id")
    roast = Roast(
        id=roast_id,
        user_id=user_id,
        roast_text=roast_text,
        sources=combined.as_dict()["sources"],
        raw_data=combined.as_dict(),
        inputs={
            "valorant_name": valorant_name,
            "valorant_tag": valorant_tag,
            "anilist_user": anilist_user,
        },
        is_public=True,
    )
    db.session.add(roast)

    if user_id:
        track_recent_roast(user_id, roast_id)

    db.session.commit()

    session.pop("spotify_token_info", None)

    return jsonify(
        {
            "id": roast_id,
            "sources": combined.as_dict()["sources"],
            "roast": roast_text,
            "raw": combined.as_dict(),
        }
    )


@api_bp.get("/roast/<roast_id>")
def get_roast(roast_id):
    roast = Roast.query.filter_by(id=roast_id).first()
    if not roast:
        return jsonify({"error": "Roast Not Found"}), 404

    user_id = session.get("user_id")
    if user_id:
        track_recent_roast(user_id, roast_id)
        db.session.commit()

    return jsonify(roast.to_dict())


def track_recent_roast(user_id, roast_id):
    recent = RecentRoast.query.filter_by(user_id=user_id, roast_id=roast_id).first()

    if recent:
        recent.viewed_at = datetime.utcnow()

    else:
        recent = RecentRoast(user_id=user_id, roast_id=roast_id)
        db.session.add(recent)

    old_recents = (
        RecentRoast.query.filter_by(user_id=user_id)
        .order_by(RecentRoast.viewed_at.desc())
        .offset(20)
        .all()
    )
    for old in old_recents:
        db.session.delete(old)


# Roasts Are Auto-Saved On Generating
@api_bp.post("/roast/save")
def save_roast():
    return jsonify({"success": True})


@api_bp.get("/roast/history")
def get_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"roasts": []})

    recent_entries = (
        RecentRoast.query.filter_by(user_id=user_id)
        .order_by(RecentRoast.viewed_at.desc())
        .limit(10)
        .all()
    )

    roasts = [entry.roast.to_dict() for entry in recent_entries if entry.roast]
    return jsonify({"roasts": roasts})


@api_bp.get("/roast/public")
def get_public_roasts():
    page = request.args.get("page", 1, type=int)
    per_page = 20

    roasts = (
        Roast.query.filter_by(is_public=True)
        .order_by(Roast.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify(
        {
            "roasts": [r.to_dict() for r in roasts.items],
            "total": roasts.total,
            "page": page,
            "pages": roasts.pages,
        }
    )
