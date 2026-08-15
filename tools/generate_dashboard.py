#!/usr/bin/env python3
"""Generate an importable Lovelace dashboard without accessing Home Assistant."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--player-entity", required=True, help="Primary media_player entity")
    p.add_argument("--spotify-entity", help="Optional Spotify media_player entity")
    p.add_argument("--music-assistant-entity", help="Optional Music Assistant media_player entity")
    p.add_argument("--presence-entity", help="Optional binary_sensor; off dims the dashboard")
    p.add_argument("--tick-entity", help="Optional sensor that changes every second")
    p.add_argument("--no-iframe", action="store_true", help="Do not include the keep-Silk iframe")
    p.add_argument("--output", type=Path, default=Path("dashboard.yaml"))
    a = p.parse_args()

    player = a.player_entity
    spotify = a.spotify_entity or ""
    ma = a.music_assistant_entity or ""
    tick = a.tick_entity or ""
    # Empty optional entities are represented by a harmless unavailable entity.
    fallback = "sensor.echo_dashboard_optional_not_configured"
    spotify_ref = spotify or fallback
    ma_ref = ma or fallback
    spotify_state = f"states('{spotify_ref}')" if spotify else "'unavailable'"
    ma_state = f"states('{ma_ref}')" if ma else "'unavailable'"
    source_entity = player
    active = f"states('{source_entity}') in ['playing', 'paused']"
    selection = (
        f"'{source_entity}' if {active} else "
        f"'{spotify_ref}' if {spotify_state} in ['playing', 'paused'] else "
        f"'{ma_ref}' if {ma_state} in ['playing', 'paused'] else '{source_entity}'"
    )
    image = (
        "{% set entity = " + selection + " %}"
        "{% set image = state_attr(entity, 'entity_picture') %}"
        "{% if image %}<img src=\"{{ image }}\" width=\"414\" height=\"414\" "
        "style=\"object-fit:contain;border-radius:16px;\">{% endif %}"
    )
    title = (
        "{% set entity = " + selection + " %}"
        "# {{ state_attr(entity, 'media_title') or 'Nothing playing' }}\n"
        "## {{ state_attr(entity, 'media_artist') or '' }}"
    )
    progress_style = (
        "{% set entity = " + selection + " %}"
        "{% set position = state_attr(entity, 'media_position') | float(0) %}"
        "{% set duration = state_attr(entity, 'media_duration') | float(0) %}"
        "{% set percent = (position / duration * 100) if duration > 0 else 0 %}"
        "ha-card { position:relative; min-height:28px; } ha-card::before { content:''; "
        "position:absolute; left:0; right:0; bottom:4px; height:5px; border-radius:4px; "
        "background:linear-gradient(to right, #16a9df {{ [percent, 100] | min }}%, "
        "rgba(128,128,128,.28) {{ [percent, 100] | min }}%); }"
    )

    controls = [
        {"type": "button", "icon": "mdi:skip-previous", "show_name": False,
         "icon_height": "37px", "tap_action": {"action": "call-service", "service": "media_player.media_previous_track", "target": {"entity_id": player}}},
        {"type": "button", "icon": "mdi:play-pause", "show_name": False,
         "icon_height": "37px", "tap_action": {"action": "call-service", "service": "media_player.media_play_pause", "target": {"entity_id": player}}},
        {"type": "button", "icon": "mdi:skip-next", "show_name": False,
         "icon_height": "37px", "tap_action": {"action": "call-service", "service": "media_player.media_next_track", "target": {"entity_id": player}}},
    ]
    right_cards = [
        {"type": "horizontal-stack", "cards": controls, "card_mod": {"style": "ha-card { padding: 0; }"}},
        {"type": "tile", "entity": player, "name": "Volume", "icon": "mdi:volume-high", "hide_state": True,
         "features": [{"type": "media-player-volume-slider"}], "features_position": "bottom",
         "card_mod": {"style": {"ha-card": {"--feature-height": "21px", "padding": "4px 12px"}}}},
        {"type": "markdown", "content": title},
        {"type": "markdown", "content": " " if not tick else "{% set tick = states('" + tick + "') %}", "card_mod": {"style": progress_style}},
    ]
    if not a.no_iframe:
        right_cards.append({"type": "iframe", "url": "/local/keep-silk-black.html", "aspect_ratio": "1%", "allow": "autoplay", "dark_mode": True})

    cards = [{"type": "grid", "columns": 2, "square": False, "cards": [
        {"type": "markdown", "content": image},
        {"type": "vertical-stack", "cards": right_cards},
    ]}]
    if a.presence_entity:
        cards.append({"type": "conditional", "conditions": [{"entity": a.presence_entity, "state": "off"}], "card": {"type": "markdown", "content": " ", "card_mod": {"style": "ha-card { position:fixed; inset:0; z-index:9999; background:#000; opacity:.8; pointer-events:none; border-radius:0; }"}}})

    config = {"title": "Now Playing", "kiosk_mode": {"hide_sidebar": True, "hide_header": True}, "views": [{"title": "Now Playing", "path": "now-playing", "type": "panel", "cards": [{"type": "vertical-stack", "cards": cards}]}]}
    a.output.write_text(json.dumps(config, indent=2) + "\n")
    print(f"Wrote {a.output}")


if __name__ == "__main__":
    main()
