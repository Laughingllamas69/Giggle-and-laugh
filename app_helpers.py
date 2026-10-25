"""Small, side-effect-free helpers shared by the app and its tests."""

import hashlib
from collections.abc import Sequence
from datetime import date, datetime, timedelta
import os


def hash_pseudonym(raw_id: str) -> str:
    """Turn a nickname into the stable public identifier used by the app."""
    normalized_id = raw_id.strip().lower()
    return "FUN-" + hashlib.sha256(normalized_id.encode("utf-8")).hexdigest()[:8].upper()


def get_rps_result(player: str, computer: str) -> str:
    """Return the result for a valid Rock, Paper, Scissors round."""
    valid_moves = {"Rock", "Paper", "Scissors"}
    if player not in valid_moves or computer not in valid_moves:
        raise ValueError("Moves must be Rock, Paper, or Scissors.")
    if player == computer:
        return "draw"
    winning_moves = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}
    return "win" if winning_moves[player] == computer else "loss"


def summarize_mood_scores(scores: Sequence[int]) -> dict[str, float | int | None]:
    """Summarize mood scores ordered from oldest to newest."""
    if not scores:
        return {"count": 0, "average": None, "change": None}
    if any(score not in (1, 2, 3, 4) for score in scores):
        raise ValueError("Mood scores must be between 1 and 4.")
    return {
        "count": len(scores),
        "average": sum(scores) / len(scores),
        "change": scores[-1] - scores[0] if len(scores) > 1 else 0,
    }


def count_recent_distress_checkins(
    records: Sequence[dict[str, object]], today: date | None = None
) -> int:
    """Count Sad/Hopeless check-ins in the trailing seven calendar days."""
    current_day = today or date.today()
    first_day = current_day - timedelta(days=6)
    count = 0
    for record in records:
        mood_label = record.get("mood_label")
        timestamp = record.get("timestamp")
        if not isinstance(mood_label, str) or mood_label.casefold() not in {"sad", "hopeless"}:
            continue
        if not isinstance(timestamp, str):
            continue
        try:
            logged_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date()
        except ValueError:
            continue
        if first_day <= logged_at <= current_day:
            count += 1
    return count


def build_mood_garden(
    records: Sequence[dict[str, object]],
) -> list[dict[str, str | int]]:
    """Create one mood-matched plant per logged day; gaps never reduce growth."""
    plants = {
        "sad": ("🌵", "Cactus"),
        "hopeless": ("🌵", "Cactus"),
        "low energy": ("🌱", "Seedling"),
        "neutral": ("🌼", "Daisy"),
        "good": ("🌷", "Tulip"),
        "great": ("🌻", "Sunflower"),
        "happy": ("🌻", "Sunflower"),
        "playfully confident": ("🌻", "Sunflower"),
        "caffeine-fueled": ("🌷", "Tulip"),
        "overwhelmed but coping": ("🌵", "Cactus"),
        "decision overload": ("🌵", "Cactus"),
        "choosing rest": ("🌱", "Seedling"),
        "pulled in two directions": ("🌼", "Daisy"),
    }
    daily_records: dict[date, tuple[datetime, dict[str, object]]] = {}
    for record in records:
        timestamp = record.get("timestamp")
        if not isinstance(timestamp, str):
            continue
        try:
            logged_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            continue
        day = logged_at.date()
        if day not in daily_records or logged_at > daily_records[day][0]:
            daily_records[day] = (logged_at, record)

    days = sorted(daily_records)
    growth_labels = {1: "Just planted", 2: "Growing", 3: "Blooming"}
    garden = []
    for index, day in enumerate(days):
        record = daily_records[day][1]
        mood_label = record.get("mood_label")
        if not isinstance(mood_label, str):
            mood_label = ""
        if mood_label.casefold() in {"", "unspecified"}:
            legacy_labels = {1: "Low Energy", 2: "Neutral", 3: "Good", 4: "Great"}
            try:
                mood_label = legacy_labels.get(int(record.get("mood_score", 0)), "")
            except (TypeError, ValueError):
                mood_label = ""
        flower, plant_name = plants.get(mood_label.casefold(), ("🌼", "Daisy"))
        growth = min(len(days) - index, 3)
        garden.append(
            {
                "date": day.isoformat(),
                "mood_label": mood_label or "Mood check-in",
                "flower": flower,
                "plant_name": plant_name,
                "growth": growth,
                "growth_label": growth_labels[growth],
            }
        )
    return garden


def summarize_mood_pulse(
    records: Sequence[dict[str, object]], min_participants: int = 5
) -> dict[str, object] | None:
    """Summarize broad mood groups only when enough distinct pseudonyms exist."""
    participants_by_vibe = {"upbeat": set(), "steady": set(), "taking it slow": set()}
    checkins_by_vibe = {"upbeat": 0, "steady": 0, "taking it slow": 0}
    checkins = 0
    for record in records:
        user_id = record.get("user_id")
        if not isinstance(user_id, str):
            continue
        checkins += 1
        label = str(record.get("mood_label") or "").casefold()
        try:
            score = int(record.get("mood_score", 0))
        except (TypeError, ValueError):
            score = 0
        if score >= 3 or label in {
            "great", "good", "happy", "playfully confident", "caffeine-fueled"
        }:
            vibe = "upbeat"
        elif score == 2 or label in {"neutral", "pulled in two directions"}:
            vibe = "steady"
        else:
            vibe = "taking it slow"
        participants_by_vibe[vibe].add(user_id)
        checkins_by_vibe[vibe] += 1

    participants = set().union(*participants_by_vibe.values())
    if len(participants) < min_participants:
        return None
    shared_mix = {
        vibe: count
        for vibe, count in checkins_by_vibe.items()
        if len(participants_by_vibe[vibe]) >= 3
    }
    suppressed_checkins = sum(
        count
        for vibe, count in checkins_by_vibe.items()
        if len(participants_by_vibe[vibe]) < 3
    )
    if suppressed_checkins:
        shared_mix["other (combined for privacy)"] = suppressed_checkins
    return {
        "participants": len(participants),
        "checkins": checkins,
        "mix": shared_mix,
    }


def validate_chat_attachment(filename: str, content_type: str, data: bytes) -> str:
    """Validate an allowed chat attachment by extension, declared type, and file signature."""
    if not data:
        raise ValueError("The selected file is empty.")
    if len(data) > 1024 * 1024:
        raise ValueError("Files must be 1 MB or smaller.")
    extension = os.path.splitext(filename.replace("\\", "/"))[1].casefold()
    allowed_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
        ".txt": "text/plain",
    }
    expected_type = allowed_types.get(extension)
    if expected_type is None or content_type != expected_type:
        raise ValueError("Upload a PNG, JPG, WebP, PDF, or plain text file.")
    if extension == ".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("The file contents do not match a PNG image.")
    if extension in {".jpg", ".jpeg"} and not data.startswith(b"\xff\xd8\xff"):
        raise ValueError("The file contents do not match a JPEG image.")
    if extension == ".webp" and not (
        data.startswith(b"RIFF") and data[8:12] == b"WEBP"
    ):
        raise ValueError("The file contents do not match a WebP image.")
    if extension == ".pdf" and not data.startswith(b"%PDF-"):
        raise ValueError("The file contents do not match a PDF document.")
    if extension == ".txt":
        if b"\x00" in data:
            raise ValueError("Plain text files cannot contain binary data.")
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("Text files must use UTF-8 encoding.") from error
    return expected_type


def build_rps_leaderboard(rounds: Sequence[dict[str, object]]) -> list[dict[str, str | int]]:
    """Aggregate stored RPS round outcomes by player."""
    players: dict[str, dict[str, int]] = {}
    for round_result in rounds:
        user_id = round_result.get("user_id")
        score = round_result.get("score")
        if not isinstance(user_id, str) or not isinstance(score, int) or score not in (0, 1):
            raise ValueError("Each round must contain a player ID and a 0/1 score.")
        player = players.setdefault(user_id, {"wins": 0, "rounds": 0})
        player["wins"] += score
        player["rounds"] += 1
    return [
        {"user_id": user_id, **totals}
        for user_id, totals in sorted(
            players.items(),
            key=lambda item: (-item[1]["wins"], -item[1]["rounds"], item[0]),
        )[:10]
    ]


def calculate_activity_streak(activity_dates: Sequence[str], today: date | None = None) -> int:
    """Count consecutive active days ending today or yesterday."""
    active_days = {date.fromisoformat(day) for day in activity_dates}
    current_day = today or date.today()
    if current_day not in active_days:
        current_day -= timedelta(days=1)
    streak = 0
    while current_day in active_days:
        streak += 1
        current_day -= timedelta(days=1)
    return streak


def get_profile_badges(points: int, streak: int, games_played: int) -> list[str]:
    """Return earned achievement labels based on profile activity."""
    badges = []
    if points >= 10:
        badges.append("First steps")
    if streak >= 3:
        badges.append("3-day streak")
    if streak >= 7:
        badges.append("Week of good vibes")
    if games_played >= 10:
        badges.append("Game regular")
    if points >= 100:
        badges.append("Community regular")
    return badges
