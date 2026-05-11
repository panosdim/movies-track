"""Email service for sending movie notifications via SMTP."""

import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

from app.utils.tmdb import TMDB_IMAGE_BASE_URL

logger = logging.getLogger(__name__)

MAIL_HOST = os.getenv("MAIL_HOST", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)


def _create_single_movie_html(movie: dict) -> str:
    """Create HTML content for a single movie notification."""
    poster_url = ""
    if movie.get("poster"):
        poster_url = f"{TMDB_IMAGE_BASE_URL}{movie['poster']}"

    providers_html = ""
    if movie.get("providers"):
        providers_html = '<div style="margin-top: 15px;">'
        for provider in movie["providers"]:
            logo_url = ""
            if provider.get("logo_path"):
                logo_url = f"{TMDB_IMAGE_BASE_URL}{provider['logo_path']}"
            provider_name = provider.get("provider_name", "Unknown")
            if logo_url:
                providers_html += f'<img src="{logo_url}" alt="{provider_name}" style="height: 30px; margin: 5px;" />'
            else:
                providers_html += f'<span style="margin: 5px; padding: 5px 10px; background: #333; color: white; border-radius: 3px; font-size: 12px;">{provider_name}</span>'
        providers_html += "</div>"

    return f"""
    <div style="margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
        <h3 style="margin: 0 0 10px 0;">{movie.get('title', 'Unknown Movie')}</h3>
        {f'<img src="{poster_url}" alt="{movie.get("title", "")}" style="max-width: 200px; border-radius: 5px;" />' if poster_url else ''}
        {providers_html}
    </div>
    """


def send_notification(user_email: str, movie: dict) -> bool:
    """Send a single-movie HTML email notification."""
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        logger.warning("SMTP not configured, skipping email notification")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New Release Available: {movie.get('title', 'Movie')}"
        msg["From"] = MAIL_FROM
        msg["To"] = user_email

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                <h2 style="color: #333;">New Movie Available!</h2>
                {_create_single_movie_html(movie)}
                <p style="color: #666; font-size: 12px;">You're receiving this email because you have this movie in your watchlist.</p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)

        logger.info("Sent notification email to %s for movie %s", user_email, movie.get("title"))
        return True

    except (smtplib.SMTPException, ConnectionError, OSError) as e:
        logger.error("Failed to send notification email to %s: %s", user_email, e)
        return False


def send_summary_notification(user_email: str, movies: List[dict]) -> bool:
    """Send a batch email grouping all updated movies for a user."""
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        logger.warning("SMTP not configured, skipping summary email notification")
        return False

    if not movies:
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Watchlist Update: {len(movies)} Movie(s) Available"
        msg["From"] = MAIL_FROM
        msg["To"] = user_email

        movies_html = "".join([_create_single_movie_html(m) for m in movies])

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px;">
                <h2 style="color: #333;">Watchlist Update</h2>
                <p>The following movies have new streaming providers available:</p>
                {movies_html}
                <p style="color: #666; font-size: 12px;">You're receiving this email because you have these movies in your watchlist.</p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)

        logger.info("Sent summary email to %s with %d movies", user_email, len(movies))
        return True

    except (smtplib.SMTPException, ConnectionError, OSError) as e:
        logger.error("Failed to send summary email to %s: %s", user_email, e)
        return False
