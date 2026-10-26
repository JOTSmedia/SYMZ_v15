# SYMZ CUSTOMZ: website v15

The umbrella site for **Symz Customz**: drawings and written ideas to full-color 3D figures, custom apparel, drinkware, hats and bags, keychains, engraving, plates, signs and decor, plus custom 3D printing (custom and pre-built), event merch (gender reveals, graduations, birthdays, baby announcements), SYMZ merch, gaming accessories and cosplay.

Built by JOTS.MEDIA. See `CHANGELOG.md` for what changed in each version.

## What's on the page

- **Loading screen:** a photoreal enclosed 3D printer, rendered in Blender (Cycles), prints Symz himself (the Meshy 3D model) hovering halfway between the bed and the top of the frame. He is built up layer by layer from his sneakers, in step with the real load progress, while the toolhead sweeps each layer, and a percentage counts up. Every refresh starts here, then the hero.
- **Hero + Symz:** headline on the left. On the right, Symz as a full 3D figure (the Meshy model, `models/symz.glb`) turning on a SYMZ hex base that stays still (slow while he faces you, quick past his back: the back shows for about 20% of each turn), with a see-through thought cloud. On phones Symz stands on the right and the cloud sits on the left under the headline. If the model can't load, the page falls back to the two-sided avatar art.
  - Closing the thought (✕), tapping anywhere else, or scrolling sends him to the bottom-right corner. There he acts as the site assistant: a short thought at each section, and tapping him opens the chat.
  - He flies back up to his hero spot any time you scroll back up into the hero.
  - Phones: headline, then Symz (thought to his right), then the intro and buttons.
- **Thought clouds:** small and see-through. In the corner, each thought is placed in whichever spot around Symz covers the least page content. Clicks go through the cloud (only its buttons take them), and corner thoughts fade once they have been read.
- **Autoscroll tour:** after about 4 seconds without input, the page drifts down at 33% speed and stops at each new section for Symz's thought. Any wheel, touch, click or key stops it.
- **Exploded View:** photoreal Blender renders of a sword, a name plaque and a controller dock, in one console sized to fit the screen: model picker on top, the render in the middle, and the Explode button, slider and readout along the bottom. Each model prints layer by layer on a textured PEI plate under a moving toolhead, then pulls apart into its labelled printed parts. You can also drag across the picture.
- **What Symz makes:** ten service previews and four occasion illustrations in compact scrollable galleries. The complete descriptions of all six service divisions are available in an expandable panel.
- **Drawings → 3D:** all six illustrated examples are featured in a swipeable gallery with individual request links and an “Expand all” grid. On desktop it shares a frame with Photo → Figure. Original flyer art is preserved unchanged; crops are applied only by the page layout.
- **Photo → Figure:** an animation using the real job. The customer's photo loses its background and gets 3D scanned into a wireframe. The wireframe then adjusts into the print version (pose and proportions) and becomes a solid print-ready model. A photoreal toolhead then prints it layer by layer on the SYMZ plate, and the render gives way to the photo of the real finished figure.
- **Sip & Paint packages:** custom paint kits. The kit photo has numbered pins (the figure printed in white, 8 paints, 4 brushes, a shot to sip that can be swapped for the occasion, a thank-you card and the bag) next to the same list. Below that are the occasions and four polaroid examples. "Order paint kits" and the polaroids fill in the order form. Images are in `img/sip/`, cut from the paint-kit flyer.
- **The Shelf:** all 22 pieces in a filterable scrollable gallery, with an “Expand all” grid and the full-screen viewer.
- **Merch:** all 32 named pieces in a compact scrollable gallery with optional filters and “Expand all”. Each item opens its viewer and order shortcut. The complete interactive lineup is in an expandable panel. Desktop places Merch beside The Shelf.
- **Process**, **maker story**, and **FAQ** are compact expandable panels. The order form leads with required fields; service choices and optional occasion, timing, and reference inputs expand inline. Every original field and answer is retained.
- Type is all caps / small caps throughout. The nav stays on top. Phones get a ☰ menu.

## Files

```
index.html          the whole site (HTML, CSS, JS in one file)
img/                gallery photos (full size, for the viewer), logo, avatar art, share image
img/t/              light WebP versions of the gallery photos used in the grids
img/merch/          merch lineup photo, item close-ups, t/ = grid thumbnails
img/p2f/            Photo → Figure animation layers (cut-out, scan mesh, grey model, printed figure)
assets/loader/      loading-screen printer frames p00..p48 (Blender renders)
models/symz.glb     Symz, the Meshy 3D model (web version) used in the hero and the corner assistant
assets/symz-textures.js  Symz figure art, inlined so the figure works offline (avatar-*.webp = same art as files)
assets/lab/         Exploded View frames per model + bare build plate (Blender renders)
audio/              drop Symz voice recordings here (see audio/README.md)
tools/              the scripts that make all of the above (see "Re-rendering")
.nojekyll           tells GitHub Pages to serve files as-is
```

No build step. The loader and Exploded View are pre-rendered in Blender; Symz is drawn live with three.js r128 and its GLTFLoader (from CDNs, like Google Fonts). To go back to the flat two-sided art, delete the `window.SYMZ_MODEL=` line in `index.html`.

## Preview locally

Serve the folder (double-clicking `index.html` also works in most browsers):

```
python3 -m http.server 8000
# open http://localhost:8000
```

## Put it on GitHub Pages

1. Create a new repository (for example `symz-customz`) on GitHub.
2. Upload the **contents** of this folder to the repository root (drag-and-drop in the GitHub web UI works; include `.nojekyll`), or:
   ```
   git init && git add . && git commit -m "SYMZ v15"
   git branch -M main
   git remote add origin https://github.com/<you>/symz-customz.git
   git push -u origin main
   ```
3. In the repo: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / root**.
4. The site goes live at `https://<you>.github.io/symz-customz/`. To use `symzcustomz84.com`, add it under Settings → Pages → Custom domain and point the domain's DNS at GitHub Pages.

Updating from an earlier version: replace everything in the repo with the contents of this folder. Files from older versions that aren't in this folder (`img/symz3d/`, `img/avatar.png`, `assets/avatar-back.webp`, `assets/logo-*.png`, `tools/build_textures.py`) are no longer used and can be deleted.

## Link previews

Sharing the link (iMessage, Facebook, X, WhatsApp, Slack) shows `img/og-symz.jpg`: the SYMZ 3D CUSTOMZ badge with Symz (1200×1200, under 300 KB so every app accepts it).

The preview tags must hold the site's real public address. They are set to **`https://jotsmedia.github.io/SYMZ_v15/`**. When the site moves (a new repo name, or `symzcustomz84.com`), find and replace that address everywhere in `index.html` (4 places: `og:url`, `og:image`, `og:image:secure_url`, `twitter:image`).

Apps cache previews, so a link that was already shared may keep its old look for a while. To test a fresh preview, add something to the end of the link, for example `https://jotsmedia.github.io/SYMZ_v15/?v=2`.

## Editing

| What | Where in `index.html` |
|---|---|
| Gallery photos, titles, categories | `const WORK=[` (add the image to `img/`) |
| Merch items (names, blurbs, categories, hotspot positions) | `const MERCH=[`; outlines in `const MSHAPE=` |
| Symz's thoughts and buttons | `const LINES={` |
| Assistant quick answers | `const A={` and `const QUICK=` |
| Thought-cloud placement | `function placeDocked` and `function placeUI` |
| Autoscroll speed and wait | `AUTO_SPEED` (0.33 = 33%) and `AUTO_IDLE` (ms) |
| Brand colors and fonts | `:root{` at the top of the `<style>` |
| Photo → Figure timing and captions | `const PH=[` in the PHOTO → FIGURE script |

## Re-rendering (Blender)

All renders come from scripts in `tools/`. They use Blender as a Python module (`pip install bpy`, Blender 4.2+/5.x) and Cycles on the CPU.

| Output | Script | Notes |
|---|---|---|
| `assets/loader/p00..p48`, `head-*` | `tools/blender/loader_printer.py` | `W=800 H=500 SAMPLES=24 FRAMES=49` (reads `models/symz.glb`); frames → `pNN.webp`, toolhead sprites → `head-K.webp`; the nozzle path in `loader.json` goes into `const LD=` |
| `models/symz.glb` | `tools/web_glb.py` | from Meshy's full GLB: `python3 web_glb.py SYMZavatar.glb models/symz.glb 0.1` (keeps 10% of the triangles, textures to 2048/1024) |
| `assets/lab/<model>-NN`, `-pNN`, `-headK`, `-beamK` | `tools/blender/lab_models.py` | `MODEL=blade|plaque|dock`, 9 explode steps + 20 print-in steps + toolhead/beam sprites; the JSON (tags, nozzle path) goes into `const LAB=` |
| `img/p2f/print-NN`, `head-K`, `beam-K` | `tools/blender/p2f_print.py` | the figure as a relief (`tools/depth_symz.py` on `fig.webp`), 24 print steps; `print.json` goes into `const PRT=` |
| shared print parts | `tools/blender/printkit.py` | toolhead, beam, PEI plate, layer lines and the layer-by-layer clip used by all three |
| `img/p2f/*` | `tools/build_p2f.py` | from background-removed cut-outs of the two photos (rembg) |
| adjust-for-print wireframe (`D.m` in the page) | `tools/build_p2f_morph.py` | start points in the scanned person, end points on the figure |
| merch outlines | `tools/merch_segment.py` | SAM (vit-b) masks per item, then traced into `MSHAPE` |

Render PNGs are converted to WebP (quality ~80) before going into the site.

## Before launch

- **Order form:** it currently builds the request text for the visitor to copy into an Instagram DM. To receive submissions directly, connect a form service (Formspree, Netlify Forms, Basin) and post the form there.
- **Merch:** no prices are shown; every merch order goes through the order form. Add prices to the item viewer if the client wants them.
- **Copy:** a few lines are drafts to confirm with the client (shop story, FAQ answers, turnaround wording).
- **Instagram:** links point to `@symzcustomz84`.

## v14 service requests

Call **848-336-0069**, text the same number, or DM **@symzcustomz84**. The form prepares a copyable request; it does not send messages or upload files. Selected reference files must be attached in the visitor’s messaging app. Service choices include drawings/words to 3D, photo-to-figure, custom apparel, drinkware, hats/bags, keychains, engraving, and plates/signs/decor. Pricing is by custom quote.

This folder and `SYMZ_v15.zip` are the v14 handoff; deployment is a separate step. Existing 3D experiences and Sip & Paint remain from v13. The supplied flyers are illustrative service artwork, and the new example selector labels them as illustrated examples.

## Compact browsing update

The default page is approximately three quarters shorter than the previous full-grid layout. Related offerings share desktop sections; mobile galleries swipe horizontally. All 6 drawing examples, 10 service examples, 4 occasion examples, 32 merch pieces, 22 work-gallery pieces, 4 paint-kit examples, 6 kit components, 6 service descriptions, and 10 FAQ answers are retained. Gallery controls provide previous/next, keyboard navigation, counts, and “Expand all” / “Collapse”. Native expandable panels hold the longer copy, complete kit contents, interactive merch map, process, maker story, FAQ, and optional form inputs. Navigation opens relevant panels before scrolling to them.
