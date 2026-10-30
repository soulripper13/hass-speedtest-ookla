# v3.1.6

This release introduces a hard timeout and process cleanup to terminate hung Ookla speedtest CLI processes (#44, #45).

When network errors occurred (such as `Error: [101] Network unreachable`), the Ookla CLI could enter a tight userspace spin loop burning CPU indefinitely without exiting. Because previous versions executed the CLI synchronously in an executor thread without a timeout, the executor thread was blocked indefinitely, preventing the coordinator from completing updates and silently stopping future speed tests until Home Assistant was restarted.

## Highlights

- **120-Second Hard Timeout**: Speedtest CLI executions are now limited to 120 seconds, preventing runaway processes from hanging indefinitely.
- **Process Group Termination & Zombie Cleanup**: Runs the CLI in its own session (`start_new_session=True`) and immediately sends `SIGKILL` to the entire process group on timeout expiry, followed by child reaping to prevent leaked or zombie processes.
- **Graceful Coordinator Failure Recovery**: Timeout events raise `UpdateFailed`, notifying the coordinator of the failure and allowing Home Assistant to retry on the next scheduled polling interval without blocking the event loop or executor threads.
- **Full Backward Compatibility**: Normal tests and server fallback behaviors on non-zero CLI exit codes (`CalledProcessError`) remain unchanged.

# v3.1.5

This release fixes an SSL handshake error (`UNEXPECTED_EOF_WHILE_READING`) when downloading the speedtest binary on modern Python environments (such as Python 3.14).

## Highlights

- **Native Async HTTP Client**: Migrated binary download from legacy `urllib.request.urlretrieve` to Home Assistant's managed `aiohttp` client session with modern TLS and browser-compatible headers.
- **Robust Retry & Multi-Tier Fallbacks**: Added automatic retries with exponential backoff on transient network drops/SSL EOF resets, with fallbacks to system `curl` and `urllib`.
- **Graceful Startup Recovery**: Setup failures during binary download now raise `ConfigEntryNotReady`, allowing Home Assistant to automatically retry initialization in the background rather than hard-failing the integration.
- **Flexible Binary Path Resolution**: Improved binary path resolution to support custom HA installations and development environments alongside standard HA OS `/config`.

# v3.1.4

This release adds a configuration and options flow setting to control the automatic copying of card files to `/config/www` and the auto-registration of Lovelace resources (#43).

## Highlights

- **Configurable Card Installation**: Added an `auto_register_cards` setting ("Install & Register Lovelace Cards") to both initial setup and options flows.
- **Clean Opt-Out & Resource Cleanup**: Disabling the option automatically cleans up copied card files from `/config/www/ookla_speedtest` and unregisters associated Lovelace dashboard resources.
- **Manual Service Management**: Added the `ookla_speedtest.remove_card_resources` service alongside `ookla_speedtest.register_card_resources` for on-demand management.
- **Smooth Upgrade Transition**: Existing installations retain cards by default unless explicitly disabled, avoiding disruption for current setups.

# v3.1.3

This release preserves the most recent speed test results across Home Assistant restarts instead of resetting sensor states to `unknown` (#42).

Lovelace gauges, custom cards, and charts retain previous test data upon restart until the next scheduled or manual test completes, avoiding `NaN` or empty displays.

## Highlights

- **State Restoration Across Restarts**: Sensors now inherit from `RestoreSensor` and persist previous test metrics across Home Assistant reboots.
- **Seamless Upgrade Migration**: Backward-compatible fallback restores last-known state from entity registry for existing installations upon updating.
- **Preserved State During Manual Runs**: Running `run_speedtest` no longer blanks out sensor states to `unknown` while the test runs.
- **Card Defensive Hardening**: Bundled custom cards (`minimal`, `compact`, `dashboard`, `card`, `card-simple`) gracefully handle unknown/unavailable states without rendering `NaN`.

# v3.1.2

This release adds timing diagnostics to help compare results across hosts and
containers. The bundled Ookla CLI uses its built-in connection strategy.

Configuration flow titles and descriptions are now available in German,
Spanish, French, Italian, and Dutch (with Home Assistant falling back to
English for any untranslated field).

Please answer the [v3.1.2 follow-up poll](https://github.com/soulripper13/hass-speedtest-ookla/discussions/37)
after upgrading so we can verify whether the change improves download and upload results.

## Highlights

- Logs test duration and command details at debug level.
- Existing installations receive a one-time notification linking to the follow-up poll.
- Bufferbloat grading now includes `A+` (0-5 ms), `E` (301-600 ms), and `F` (>600 ms).
- Corrected an incompatible CLI option that prevented tests from running.

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
