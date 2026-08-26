# v3.1.2

This release makes multi-connection mode explicit for the Ookla CLI and adds
timing diagnostics to help compare results across hosts and containers.

Configuration flow titles and descriptions are now available in German,
Spanish, French, Italian, and Dutch (with Home Assistant falling back to
English for any untranslated field).

Please answer the [v3.1.2 follow-up poll](https://github.com/soulripper13/hass-speedtest-ookla/discussions/37)
after upgrading so we can verify whether the change improves download and upload results.

## Highlights

- Explicitly passes `--multi` to the bundled Ookla CLI.
- Logs test duration and command details at debug level.
- Existing installations receive a one-time notification linking to the follow-up poll.
- Bufferbloat grading now includes `A+` (0-5 ms), `E` (301-600 ms), and `F` (>600 ms).

# v3.1.1

This release adds an optional, one-time feedback notification for existing installations to help investigate lower-than-expected download results on high-speed connections.

## Highlights

- Added a dismissible persistent notification linking to the [Ookla Speedtest performance survey](https://github.com/soulripper13/hass-speedtest-ookla/discussions/33).
- The notification is shown once per existing installation and is not shown for fresh installations.
- No survey information is collected or submitted automatically by the integration.
- Added the `persistent_notification` Home Assistant dependency.

# v3.0.5

This release focuses on Lovelace card customization, visual consistency, and theme compatibility. The speedtest integration, entities, and service behavior are unchanged.

## Highlights

- Added comprehensive chart customization to the Dashboard card.
- Added shared appearance controls to all five bundled cards.
- Fixed oversized chart lines on wide cards.
- Fixed card styles leaking into unrelated Home Assistant cards.
- Improved cache busting and synchronized all card versions with the integration version.

## Dashboard Chart Customization

The Dashboard card now supports visual-editor and YAML controls for:

- History range, maximum data points, and chart height.
- Line width, solid/dashed/dotted styles, and line-cap shape.
- Independent download, upload, and ping line colors.
- Independent area-fill colors, visibility, and opacity.
- Optional data-point markers and configurable marker radius.
- Automatic scaling or a vertical scale that starts at zero.

Chart strokes now use a non-scaling width, keeping the configured line width consistent across mobile, desktop, and wide dashboard layouts.

## Card Appearance

All bundled cards now share an `appearance` configuration block and matching visual-editor controls for:

- Theme, none, subtle, medium, strong, or custom shadows.
- Background, border, text, and accent colors.
- Border width and corner radius.
- Backdrop blur and inner padding.
- Custom font family.

Every color option includes a native color picker in the visual editor. Appearance colors also retain a text field for alpha colors, HSL values, and Home Assistant CSS variables.

Unset appearance values continue to inherit from the active Home Assistant theme. Primary buttons, links, and actions now follow the configured accent color.

## Theme and Style Fixes

- Isolated every card's runtime styles with Shadow DOM, preventing generic card selectors from affecting other dashboard cards.
- Replaced forced outer shadows and corner radii with Home Assistant theme variables.
- Added live appearance updates in the card editor, including clean resets back to theme defaults.
- Applied the same appearance behavior to the Main, Dashboard, Minimal, Compact, and Simple cards.

## Cache Handling

- Updated the integration and card version to `3.0.5`.
- Lovelace resource URLs now use the `?v=3.0.5` cache key.
- Card resources read their cache version from the integration manifest, preventing future version mismatches.
- Added a versioned shared card utility asset for appearance rendering and editor controls.

## Upgrade Notes

Restart Home Assistant after updating so the new shared card utility is copied to `/config/www/ookla_speedtest/` and the Lovelace resource URLs are updated. The new versioned URLs should invalidate the old browser cache automatically.

---

# v3.0.4

## Bug Fixes

- Fixed speedtest results being discarded when the bundled Ookla CLI omits optional latency fields from its JSON output.
- Missing `ping.low`, `ping.high`, `download.latency.*`, and `upload.latency.*` values now default to `0` instead of raising `Unexpected data format` errors.

Core speed, ping, jitter, ISP, server, and result URL fields are unchanged.
