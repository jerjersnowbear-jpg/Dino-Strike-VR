# DINO STRIKE VR 1.3.2: Photo Realism Edition

A standalone browser-based, controller-free arcade game for smartphone Cardboard-style viewers. An automatic rail cart moves forward through three procedural landscapes. The player aims by turning their head. The first uninterrupted two-second lock on a single moving target triggers a non-graphic energy burst. Looking away or switching targets resets the timer. Raptor, T-Rex, Triceratops and flying Pteranodon opponents move toward the cart. Pteranodon is a prehistoric flying reptile, not technically a dinosaur.

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
`python tests/smoke.py` uses Playwright with mock WebGL to validate the application logic, 2-second dwell, switching/interruptions, motion of the ride, enemy collision, flying target scoring, two-eye overlay and safety gate. The current environment blocked normal Chromium file navigation, so actual 3D rendering and physical smartphone/headset motion have not been verified. GitHub Actions can rerun the same logic tests. The scene uses enhanced procedural 3D graphics; it remains a moving straight-rail expedition, not a full roller coaster with loops or steep drops. Offline caching is included but not physically verified.


## 1.1 visual upgrade
- Organic reusable meshes, tapered limbs and tails, claw and tooth geometry, modeled wing membranes, improved heads and running poses.
- Procedural skin, stone, leaf, bark and metal shading; sky gradients, clouds, directional light and distance fog with a palette for each zone.
- Two alternating scenery tiles per zone, detailed rails, cart-mounted laser housings, energy effects and approximate contact shadows.
- No external asset downloads. The stereo startup and two-second gaze-lock rules are unchanged. Geometry and model matrices were verified with mock WebGL. A separate real WebGL browser smoke test was added to CI; its results and physical phone performance must be confirmed. These are stylized procedural models, not photorealistic artist-authored assets. There is no native Cardboard SDK integration or viewer-specific lens correction.

## 1.2 Cinematic mode
Select Cinematic models and wait for the status counter to reach four. The separate Three.js renderer uses animated glTF/GLB imports, physical materials, photographic textures, a forest panorama and HDR lighting. The original targeting and ride rules are unchanged. Missing models use procedural substitutes. If the renderer fails or frame intervals remain above 100 ms for three seconds, moving rides pause and Classic graphics are selected. The first cinematic download requires internet, unless all dependencies are installed locally. Browser CORS, memory and device speed may affect loading. The new CI workflow prepares an optional same-origin asset pack and uploads it as an Actions artifact. Extract that pack into the repository's assets folder if direct downloads fail. Classic mode remains self-contained. Cinematic output and physical phone performance are not yet verified.

## 1.3
Adds real-time directional shadows, normal/roughness maps for terrain, photographic bark, and optional scanned fern and mossy rock models. The automatic Photo Realism build downloads and validates models, copies Three.js and assets into one self-contained site, then runs a local-only WebGL stereo test. The branch-hosted site still uses external fallback sources for assets not present locally. To publish the packaged site, choose Settings > Pages > Source > GitHub Actions, then Actions > Build and publish photorealistic edition > Run workflow with publish checked. This is an explicit deployment; the regular push build only produces a downloadable artifact. The current build and visual output require verification. Classic mode remains available.
## 1.3.1
Continuous laser lock reduced to 2 seconds in both graphics modes. Looking away or switching targets still resets it. Countdown and charge ring derive from the same constant.

## 1.3.2
Live gaze-lock charge uses real elapsed time independently of the capped physics timestep. First acquisition starts at zero, gaps longer than 750 ms reset charge, and pauses or target changes still reset. Use play-1.3.2.html for a release-specific URL. Both entry pages share the same code.
