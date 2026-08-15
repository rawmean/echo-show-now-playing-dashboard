# Echo Show Now Playing Dashboard

A small, artwork-first Home Assistant dashboard for an Amazon Echo Show running in Silk. It displays the track currently playing on a media player, with artwork, title, artist, progress, transport controls, and volume. An optional invisible iframe keeps Silk awake.

The project is intentionally provider-agnostic: it works with WiiM/LinkPlay, Music Assistant, Spotify Connect, Qobuz, and other Home Assistant `media_player` entities that expose standard media attributes.

## What it includes

- Artwork-first two-column layout sized for the Echo Show 5.
- Native Home Assistant media-player controls (previous, play/pause, next, volume).
- Progress bar driven by standard `media_position`/`media_duration` attributes.
- Optional one-second tick sensor for live progress refresh.
- Optional presence-based dimming.
- Optional hidden keep-Silk iframe.
- No credentials, cloud account, or custom backend.

## Requirements

- Home Assistant 2024.6 or newer.
- An entity with the standard Home Assistant `media_player` integration.
- A Lovelace dashboard in YAML mode, or a way to paste generated YAML into the dashboard editor.
- The `card-mod` frontend resource is recommended for the progress bar and presence overlay. The dashboard still renders without it, but those styles will be absent.

## Quick start

1. Download this repository.
2. Run the generator with your Home Assistant entity IDs:

   ```sh
   python3 tools/generate_dashboard.py \
     --player-entity media_player.wiim_office \
     --output dashboard.yaml
   ```

   Add `--spotify-entity`, `--music-assistant-entity`, `--presence-entity`, or `--tick-entity` when those entities exist.

3. Add the generated contents of `dashboard.yaml` as a Lovelace dashboard.
4. If you want the anti-timeout iframe, copy `keep-silk-black.html` to Home Assistant's `/config/www/` directory and leave the iframe card enabled in the generated YAML.
5. Open the dashboard in Silk. For a clean Echo display, use kiosk mode or add the `kiosk-mode` frontend resource.

The generator never reads Home Assistant credentials or contacts Home Assistant.

## Configuration examples

WiiM/LinkPlay:

```sh
python3 tools/generate_dashboard.py \
  --player-entity media_player.office_upstairs \
  --presence-entity binary_sensor.office_presence \
  --tick-entity sensor.playback_tick \
  --output dashboard.yaml
```

Music Assistant:

```sh
python3 tools/generate_dashboard.py \
  --player-entity media_player.wiim_office \
  --music-assistant-entity media_player.wiim_office \
  --output dashboard.yaml
```

If you do not have a presence sensor, omit `--presence-entity`; the dimming overlay will not be included. If you omit `--tick-entity`, the progress bar updates when Home Assistant reports media-player changes rather than every second.

## Keep-Silk iframe

The optional iframe points to the community keep-Silk page and is only 1×1 pixels with a black background. Remove the iframe card if you do not want to use this workaround. Echo behavior can vary by firmware and Amazon account, so test it on your device.

## Privacy and security

This repository contains only dashboard YAML, a static helper page, and a local generator. It does not contain Home Assistant tokens, Spotify credentials, Qobuz credentials, LAN addresses, or telemetry code. Keep your generated YAML private if it includes private entity names or URLs.

## License

MIT. See [LICENSE](LICENSE).
