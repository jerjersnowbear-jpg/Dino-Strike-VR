# DINO STRIKE VR 1.0

A standalone browser-based, controller-free arcade game for smartphone Cardboard-style viewers. An automatic rail cart moves forward through three procedural landscapes. The player aims by turning their head. The first uninterrupted five-second lock on a single moving target triggers a non-graphic energy burst. Looking away or switching targets resets the timer. Raptor, T-Rex, Triceratops and flying Pteranodon opponents move toward the cart. Pteranodon is a prehistoric flying reptile, not technically a dinosaur.

## Start
1. Upload all files in this folder to the root of a separate GitHub repository (for example `Dino-Strike-VR`). Enable GitHub Pages, main branch, root folder, HTTPS.
2. Open the URL in Chrome directly. First choose Play on screen. Drag to look around and center the reticle on a target. Arrow keys work on desktop.
3. For Cardboard, enable auto-rotate, turn your phone sideways, and choose Start Cardboard VR. Confirm the adult safety check. Test split screen without the viewer first; it is a static scene for checking stereo only, not a moving ride.
4. Exit the test and select Enable motion & start ride. Center the phone while holding it comfortably. Motion must be available before the ride starts.
5. Remove the viewer before tapping Pause / exit. If tracking stops, the ride pauses and requires recentering.

Gentle is the default. Comfort and Arcade increase the forward movement speed. Each ride lasts up to 150 seconds or ends when five shields are lost. A ground target is 100 points and a flying target is 150. Local personal best is stored in the browser. No accounts, remote assets, subscriptions, or API keys are used.

## Safety
Use seated, with adult supervision and only if the viewer's age and fit guidance permits. Start on screen and with the slowest speed. Remove the viewer and stop at any discomfort. No physical movement is required. The game uses a moving virtual viewpoint and can cause motion sickness. It does not implement forced fullscreen, official Cardboard SDK or viewer-specific lens distortion correction.

## Verification
`python tests/smoke.py` uses Playwright with mock WebGL to validate the application logic, 5-second dwell, switching/interruptions, motion of the ride, enemy collision, flying target scoring, two-eye overlay and safety gate. The current environment blocked normal Chromium file navigation, so actual 3D rendering and physical smartphone/headset motion have not been verified. GitHub Actions can rerun the same logic tests. The scene uses stylized procedural graphics; this initial edition is a moving straight-rail expedition, not a full roller coaster with loops or steep drops. Offline caching is included but not physically verified.
