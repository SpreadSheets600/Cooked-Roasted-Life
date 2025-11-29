from . import api_bp
from ..models import CombinedUserData
from ..models.database import db, Roast, RecentRoast
from ..services import (
    ValorantService,
    SpotifyService,
    GeminiRoaster,
    AnimeService,
    SteamService,
)

import uuid
from datetime import datetime, timedelta
from flask import jsonify, request, session

rate_limit_store = {}


@api_bp.get("/ping")
def ping():
    return jsonify({"ok": True})


@api_bp.get("/auth/status")
def auth_status():
    return jsonify(
        {
            "spotify_authenticated": bool(session.get("spotify_authenticated")),
            "user": {
                "name": session.get("user_name"),
            }
        }
    )


@api_bp.post("/roast")
def generate_roast():
    client_ip = request.remote_addr
    now = datetime.utcnow()

    last_request = rate_limit_store.get(client_ip)

    if last_request:
        elapsed = now - last_request
        if elapsed < timedelta(minutes=5):
            wait_time = 300 - int(elapsed.total_seconds())
            return jsonify(
                {"error": f"Rate limit exceeded. Please wait {wait_time} seconds."}
            ), 429

    rate_limit_store[client_ip] = now

    body = request.get_json(force=True) if request.is_json else request.form
    valorant_name = body.get("valorant_name")
    valorant_tag = body.get("valorant_tag")
    valorant_region = body.get("valorant_region") or "na"
    anilist_user = body.get("anilist_user")

    steam_id = body.get("steam_id")
    steam_vanity = body.get("steam_vanity")

    user_inputs = {
        "valorant_name": valorant_name,
        "valorant_tag": valorant_tag,
        "valorant_region": valorant_region,
        "anilist_user": anilist_user,
        "steam_id": steam_id,
        "steam_vanity": steam_vanity,
    }

    spotify_display_name = None
    spotify_service = SpotifyService()
    if spotify_service.is_ready():
        spotify_data = spotify_service.get_roast_profile_data()
        spotify_display_name = session.get("user_name")
    else:
        spotify_data = {}
        if session.get("spotify_token_info"):
            session.pop("spotify_token_info", None)

    valorant_data = {}
    if valorant_name and valorant_tag:
        valorant_data = ValorantService().get_roast_data(
            valorant_name, valorant_tag, region=valorant_region
        ) or {}
        if not valorant_data:
            valorant_data = {
                "type": "valorant",
                "ign": f"{valorant_name}#{valorant_tag}",
                "notes": "Valorant API unavailable; rely on handle only.",
            }

    anime_data = {}
    if anilist_user:
        anime_data = AnimeService().get_roast_data(anilist_user) or {}
        if not anime_data:
            anime_data = {
                "type": "anime",
                "username": anilist_user,
                "notes": "AniList data unavailable at generation time.",
            }

    steam_data = {}
    if steam_id or steam_vanity:
        steam_data = SteamService().get_roast_data(
            steam_id=steam_id, vanity=steam_vanity
        ) or {}
        if not steam_data:
            steam_data = {
                "type": "steam",
                "steam_id": steam_id or steam_vanity,
                "notes": "Steam stats unavailable; id provided only.",
            }

    combined = CombinedUserData(
        spotify=spotify_data,
        valorant=valorant_data,
        anime=anime_data,
        steam=steam_data,
        inputs={**user_inputs, "spotify_name": spotify_display_name},
    )
    combined_payload = combined.as_dict()
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
        sources=combined_payload["sources"],
        raw_data=combined_payload,
        inputs={**user_inputs, "spotify_name": spotify_display_name},
        is_public=True,
    )
    db.session.add(roast)

    if user_id:
        track_recent_roast(user_id, roast_id)

    db.session.commit()

    try:
        my_roast_ids = session.get("my_roast_ids", [])

        if roast_id in my_roast_ids:
            my_roast_ids.remove(roast_id)

        my_roast_ids.insert(0, roast_id)
        session["my_roast_ids"] = my_roast_ids[:20]
    except Exception:
        pass

    session.pop("spotify_token_info", None)

    return jsonify(
        {
            "id": roast_id,
            "sources": combined_payload["sources"],
            "roast": roast_text,
            "raw": combined_payload,
            "inputs": roast.inputs,
            "timestamp": roast.created_at.isoformat() + "Z",
        }
    )


@api_bp.get("/roast/<roast_id>")
def get_roast(roast_id):
    roast = Roast.query.filter_by(id=roast_id).first()
    if not roast:
        return jsonify({"error": "Roast not found!"}), 404

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
            "has_next": roasts.has_next,
            "has_prev": roasts.has_prev,
            "per_page": per_page,
        }
    )


@api_bp.get("/roast/mine")
def get_my_roasts():
    ids = session.get("my_roast_ids", [])

    if not ids:
        return jsonify({"roasts": []})

    items = Roast.query.filter(Roast.id.in_(ids)).all()
    by_id = {r.id: r for r in items}

    ordered = [by_id[i].to_dict() for i in ids if i in by_id]

    return jsonify({"roasts": ordered})
