# Thai Tiny Homes

Landing page for the tiny homes in Ban Nai Rai, Krabi. Own the house, lease the land.

Static site, no build step. Netlify publishes the repo root.

- `index.html`, `styles.css`, `main.js`: the page.
- `assets/img`: WebP at 800 and 1600 px. `assets/video`: short muted H.264 loops with poster frames. `assets/fonts`: self-hosted Bricolage Grotesque and Fraunces, trimmed to the axes and glyphs the page uses.
- `build-artifact.py`: flattens everything into one HTML file with data URIs, for previewing on a phone without a server.

Preview locally: `python3 -m http.server 8080` then open http://localhost:8080

Copy and open questions are tracked in the project brief and claims register (Dropbox: `007.TH-Capsules-Landing/Docs`).
