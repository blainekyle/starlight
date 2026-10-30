# Starlight Cinema Classics 🎬✨

[![GitHub Pages](https://img.shields.io/badge/Hosted%20on-GitHub%20Pages-blue?logo=github)](https://blainekyle.github.io/AO-Movies/)
[![License: Public Domain](https://img.shields.io/badge/License-Public%20Domain-yellow.svg)](https://creativecommons.org/publicdomain/mark/1.0/)
[![Sync Architecture](https://img.shields.io/badge/Live%20Sync-Zero--Server%20Procedural%20PRNG-brightgreen)](#the-magic-serverless-globally-synchronized-live-broadcast)

> **A curated, retro-futuristic Art Deco movie palace in your browser.** Continuous golden-age American sound cinema, vintage concession bumper prerolls, immersive 3D velvet drapes, and a **stateless, zero-server communal LIVE broadcast** running entirely on static GitHub Pages.

---

## 🌟 The Magic: Serverless, Globally-Synchronized LIVE Broadcast

The technical centerpiece of Starlight Cinema is its **parallel LIVE Broadcast Mode**. 

Typically, synchronized communal playback ("watch parties") demands expensive, stateful server backends running WebSocket relays, headless browser playback instances, or Redis Pub/Sub workers to maintain real-time client state. 

**Starlight Cinema accomplishes universal sync with zero server infrastructure.** It runs 100% on static GitHub Pages while ensuring that any viewer across the globe—opening the page on a desktop in New York, a tablet in Tokyo, or a TV in London—watches the **exact same frame of the exact same film at the exact same millisecond**.

```
                           [ Public Epoch Anchor ]
                            2026-01-01T00:00:00Z
                                     │
                      ┌──────────────┴──────────────┐
                      ▼                             ▼
        Client A (New York, US)        Client B (Tokyo, JP)
        Boot: Query timeapi.io         Boot: Query timeapi.io
        Offset: -120ms local drift     Offset: +85ms local drift
                      │                             │
                      ▼                             ▼
        ┌────────────────────────────────────────────────────────┐
        │        Deterministic Mulberry32 PRNG Schedule Engine    │
        │    Procedural Cadence: [Preroll] ➔ [Feature] ➔ ...    │
        └────────────────────────────────────────────────────────┘
                      │                             │
                      ▼                             ▼
          Seek to Target Film            Seek to Target Film
          Offset: 01:14:22.418           Offset: 01:14:22.418
                      └──────────────┬──────────────┘
                                     │
                      [ Perfect Global Unison Frame ]
```

### How It Works Under the Hood

1. **Epoch Anchor & Deterministic Mulberry32 PRNG:**
   Playback timelines are procedurally generated from a fixed historical epoch (`2026-01-01T00:00:00Z`) using an explicit 32-bit PRNG seed (`19401225`). Because PRNG state sequences are mathematically deterministic, every client computes an identical broadcast schedule indefinitely into the future.
2. **True Network Time Sync (Eliminating Local Drift):**
   Client system clocks frequently drift by seconds or minutes. On boot, the client queries a lightweight public time API (`timeapi.io`) to calculate a high-precision `networkTimeOffsetMs`, compensating for local clock discrepancy without persistent polling.
3. **Mathematical Program Offset Resolution:**
   The client calculates elapsed time since the epoch ($\Delta t = t_{\text{true\_utc}} - t_{\text{epoch}}$), steps through the deterministic sequence of alternating features and vintage policy bumpers, locates the current active item, and seeks directly to the target timestamp ($t_{\text{current}} = \Delta t - t_{\text{program\_start}}$).
4. **Seamless Solo/Live State Transitions:**
   Switching between **SOLO** and **LIVE** modes preserves solo session positions. Pausing and track-skipping are locked out during LIVE mode, replacing controls with a subdued, authentic low-glow theater red LED indicator (`● LIVE`).
5. **Static Schedule Overrides & Interventions (`live-sched.json`):**
   To broadcast special events or manual premieres, the system fetches [`live-sched.json`](./live-sched.json) directly from the repository. Broadcasters can inject hard interrupts or graceful transitions (allowing the active film to conclude before cutting to the special presentation).

---

## 🏛️ Architectural Highlights & Features

- **Art Deco Movie Palace Atmosphere:**
  - Viewport-locked (`100vw`/`100vh`), scroll-free cinema presentation.
  - Multi-tier velvet stage drapes with procedural wavy hemlines (60% amplitude) and dynamic matting curtains that expand to fit Academy Ratio (4:3) black bars.
  - Real-time HTML5 floor reflection canvas mirroring video projection with perspective skew and Gaussian blur.
  - Perspective floor marquee displaying hyperlinked Archive.org source attribution opening in `_blank` tabs.
- **Strict Content Curation:**
  - Classic American sound cinema (strictly $\le 1991$).
  - Purged silent cinema, Soviet montage, German Expressionism, and modern trailer spam.
  - Curated vintage concession bumpers, countdown clocks, and theater policy reels (15s–150s).
- **TV & Gamepad-First Navigation:**
  - Full Gamepad API integration (D-Pad navigation, Face buttons for Play/Pause, Info drawer, and Mute).
  - Keyboard hotkeys (`Space`, `F` / `LEAN IN`, `I`, `M`, Arrow keys).
  - Sync-safe "LEAN IN" mode that harmonizes with native browser F11 fullscreen without stacking bugs.
- **In-Drawer Info & Timeline:**
  - Real-time countdown timer, runtime display, and archive synopsis drawer.
- **3-Slot In-Memory / LocalStorage Save Engine:**
  - Dedicated retro Pause Menu drawer with 3 isolated save slots.
  - Import/Export session states as discrete `.json` payloads with overwrite confirmation guards.

---

## 🎛️ Python Desktop Companion App (`companion.py`)

A zero-dependency Python 3 / Tkinter companion application is included for local schedule administration, broadcast inspection, and schedule curation:

```powershell
python companion.py
```

### Capabilities:
- **12-Hour Broadcast Timeline Preview:** Computes and displays the exact upcoming airtimes, durations, and film titles as synchronized across the world.
- **PRNG Seed Generator:** Test and save new mathematical seeds directly into `live-sched.json`.
- **Live Sync Pull:** Fetch published schedules directly from the remote GitHub Pages endpoint.
- **Custom Schedule Inserts:** Schedule manual video interventions (Archive.org, BitChute/bstr.video, self-hosted MP4s) with `hard` or `graceful` cut modes.
- **Test Save Exporter:** Generate valid 3-slot save states for rapid testing against the web player's pause menu.

---

## 🚀 Getting Started

### Play in the Browser
Visit the live player hosted on GitHub Pages:
👉 **[https://blainekyle.github.io/AO-Movies/](https://blainekyle.github.io/AO-Movies/)**

### Run Locally
No Node.js, npm, or build tools are required! Simply serve the directory with any static HTTP server:

```powershell
# Using Python
python -m http.server 8000
```
Open `http://localhost:8000` in any modern web browser.

---

## 🎮 Controls & Shortcuts

| Action | Keyboard | Gamepad | Description |
| :--- | :--- | :--- | :--- |
| **Play / Pause** | `Space` | `A` (Button 0) | Toggle playback (Disabled in LIVE mode) |
| **LEAN IN / Fullscreen** | `F` | `Back / Select` | Distraction-free immersive view |
| **Info Panel** | `I` | `X` (Button 2) | Toggle synopsis, runtime, and progress timeline |
| **Mute / Unmute** | `M` | `Y` (Button 3) | Toggle audio mute |
| **Previous Feature** | `Left Arrow` | `LB` (Button 4) | Skip to previous film in queue (SOLO only) |
| **Next Feature** | `Right Arrow` | `RB` (Button 5) | Skip to next film in queue (SOLO only) |
| **Navigate Menus** | `Up / Down Arrows` | `D-Pad` | Navigate pause menu slots and options |

---

## 📜 Credits & License

- **Films & Media:** Public domain materials hosted by the [Internet Archive](https://archive.org/).
- **Typography:** *Federo* by Olexa Volochay; *Century Gothic*.
- **Branding:** Starlight Cinemas custom art deco vector motif.
- **Code License:** Released under the [Public Domain Mark 1.0](https://creativecommons.org/publicdomain/mark/1.0/) / MIT compatible.
