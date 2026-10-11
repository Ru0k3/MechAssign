# Frontend (Brief)

**Code:** `frontend/index.html`, `frontend/script.js`, `frontend/style.css`

The frontend is a plain HTML/CSS/vanilla-JS single page — no framework, no build step, no AI logic of its own. Its only job is to **visualize and narrate** what the backend's classical-AI pipeline decides. It is included here for completeness, not because it's part of the "Fundamentals of AI" material.

## What it does

1. **Draws the maze as SVG.** On load, it fetches `/api/city`, `/api/entities`, `/api/questions` and draws every road (`city.edges`) and junction (`city.nodes`) as SVG paths/circles, plus a marker for every shop/store (`drawMap()`, `frontend/script.js:46`).
2. **Lets the user click a road** to place the breakdown marker at the nearest point on that road (`openPopup()`, projects the click onto the line segment between the road's two endpoints using vector projection, `script.js:91-100`), then collects a damage type + follow-up answer + "already have the part" checkbox.
3. **Calls `POST /dispatch`** with that input, then plays back the returned `logs` array one line at a time with a short delay (`script.js:128`) so the algorithm trace reads like a live narration rather than appearing all at once — purely cosmetic pacing, no computation happens client-side.
4. **Animates the chosen routes** (`renderRoutes()`, `script.js:102`) by drawing the A* path for the technician and (if needed) the parts store as dashed, animated SVG strokes, and auto-removes them 5 seconds after the repair is "complete."
5. **"Simulate delay" button** calls `POST /simulate-delay` with a hardcoded 10-minute delay and a fixed set of completed steps, then re-renders the updated plan/coordination panel (`simulateDelay()`, `script.js:136`) — this is the UI trigger for the backend's replanning demo (`07-planning.md`).

## What it is not

- It does not implement or re-implement any search, CSP, inference, or planning logic — every `fetch()` call hands the real decision-making to the Flask backend and only renders the JSON result.
- There's no client-side state persistence beyond a few JS variables (`lastPlan`, `lastCoordination`, etc.) held in memory for the current page session, used only to resend context (like the current ETAs) to `/simulate-delay`.
