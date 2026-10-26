# Changelog

## v15
- Saved the compact website as v15, including horizontal galleries, expandable sections, grouped desktop layouts, and the full services and examples catalogue.
- Updated version metadata and link-preview paths for SYMZ_v15.
- Preserved the v14 folder. Local handoff; no remote publication performed.

## v14
- Compact browsing update: shorter section spacing, related desktop sections grouped together, mobile horizontal galleries with arrows and “Expand all” controls.
- Full service copy, kit inventory, interactive merch lineup, process, maker story, FAQ, and optional form fields are available in expandable panels. All earlier content, examples, order shortcuts, and 3D experiences are retained.
- Shared-row navigation highlights the visible sections; direct links open relevant panels.
- Visibility update: all six drawing/words examples now appear together, with individual request links.
- Added all ten visual service examples and four occasion examples from the custom-services flyer.
- All 32 existing merch items now appear in a page grid instead of nested scrolling columns or a phone carousel; filters and item/order viewers remain.
- Preserved all 22 shelf pieces, four paint-kit occasion examples, six kit contents, and the earlier photo-to-figure, gaming, cosplay, event, and 3D experiences.
- Added a Drawings → 3D section with six visible illustrated examples from the supplied flyer, each with a request link that carries the chosen idea into the form.
- Expanded services with custom apparel, tumblers/mugs, hats/bags, keychains, engraving, custom plates, signs and decor.
- Added call/text links for 848-336-0069 and kept Instagram @symzcustomz84.
- Updated request categories, FAQ, assistant replies, tour, navigation, metadata, and version references.
- Clarified that the form prepares a copyable message and that reference files must be attached when sending; required fields are validated.
- Preserved v13’s hero, 3D loader, exploded models, photo-to-figure animation, gallery, merch browser, and Sip & Paint section.
- Local v14 package; no remote publication performed.

## v13
- New section, **Sip & Paint packages** ("Custom paint kits"), between Photo → Figure and The Shelf, built from the paint-kit flyer:
  - the kit photo with numbered pins. Hovering a pin highlights that line of "What's in the kit", and the other way round: custom figure (printed in white, ready to paint), 8 paint colors, 4 brushes, a shot to sip (swapped for prosecco, rosé or water to suit the occasion), SYMZ thank-you card, gift-ready bag;
  - occasions: weddings, birthdays, sweet 16s, baby showers, anniversaries, bridal showers, sip & paint events, just because. Also custom figures, paint kits, party favors and bulk orders;
  - four polaroid cards (Weddings, Birthdays & Sweet 16s, Baby showers, Sip & paint events), cut from the flyer.
- "Order paint kits" and each polaroid fill in the order form: the new **Sip & paint** lane, the occasion, and a line asking how many kits, which figure and which drink. A DM button goes to @symzcustomz84.
- The nav has a **Sip & Paint** link (it lights up in the section). The order form has new occasions (bridal shower, baby shower, sweet 16, anniversary, sip & paint event). The FAQ answers "What comes in a sip & paint kit?".
- Symz: a tip for the new section ("Paint it, sip it, keep it"), a "Sip & paint kits" quick reply in the chat, and he answers questions about kits, party favors, showers, sweet 16s and bulk orders. The tour now goes Photo → Figure → Sip & Paint → The Shelf.
- Link previews point at `https://jotsmedia.github.io/SYMZ_v13/`.

## v12
- Symz's turn in the hero now changes speed with the angle. He turns slowly while facing you, picks up speed through the sides, swings quickly past his back, then eases back into the front. His back is in view for only about 20% of each 10-second turn. The base still stays put.
- Link previews point at `https://jotsmedia.github.io/SYMZ_v12/`.

## v11
- Symz is now the full 3D model from Meshy (`models/symz.glb`) in all three places: the hero, the assistant in the bottom-right corner, and the loading screen. The original was 55 MB; the site copy is 2.6 MB (about 70,000 triangles, smaller textures).
- Only Symz turns. The SYMZ hex base stays still in the hero and in the corner.
- Every 3D printing animation is now photoreal, rendered in Blender (Cycles) with one shared print kit (`tools/blender/printkit.py`):
  - a real CoreXY toolhead: rounded housing, front fan behind a grille, side blower, ring duct, red silicone sock and a brass nozzle;
  - an aluminium X beam with a steel linear rail and GT2 belts, and a PTFE tube that follows the toolhead;
  - textured PEI spring-steel plates on a magnetic heated bed;
  - plastic that goes down one layer at a time, with visible layer lines, the infill pattern showing on the open top layer, and the wet shine of the newest layer (the old glow effects are gone).
- Loading screen: a full enclosed printer (smoked-glass sides and lid, light bar, touchscreen, flying gantry) prints Symz from the Meshy model, still hovering halfway up. 49 frames are cross-faded smoothly, and the toolhead sweeps across each layer in real time.
- Exploded View: the plate is now a textured PEI sheet with the SYMZ graphic, and every model has a new print-in. The model is printed layer by layer while the toolhead sweeps across it, then the head lifts away before the model explodes.
- Photo → Figure: the print step is a real render. The figure is printed in colour on the SYMZ plate, with the toolhead and beam moving up layer by layer, then it cross-fades to the photo of the finished figure.
- Phones: in the hero, Symz stands on the right and his thought cloud sits on the left, under the headline.
- The site title is all caps (SYMZ CUSTOMZ) in the browser tab and link previews, and the big name in "The face on the hoodie" section reads SYMZ.
- Link previews point at `https://jotsmedia.github.io/SYMZ_v11/`.

## v10
- Merch on desktop: the side columns are now 16 and 16. Odd-numbered items (1, 3, 5…) are on the left and even-numbered (2, 4, 6…) on the right, in the merch list's order. Hovering still links the map and the pictures both ways. Phones are unchanged.
- The red scrolling band under the hero is now straight instead of tilted.
- Loading screen: the printer now prints Symz (a 3D version of the avatar) instead of the logo, from his sneakers up, still hovering halfway up the frame.
- Link previews point at `https://jotsmedia.github.io/SYMZ_v10/`.

## v9
- Merch on desktop: the map is centered with the filters above it, and the item pictures run in one scrolling column on each side. The left column holds the pieces from the left half of the map and the right column the right half, in the same top-to-bottom order as the map. Both columns match the map's height. Hovering a piece on the map scrolls its column to it; hovering a picture outlines it on the map. Phones are unchanged.
- Link previews point at `https://jotsmedia.github.io/SYMZ_v9/`.

## v8
- Link previews point at where the site actually lives, `https://jotsmedia.github.io/SYMZ_v8/`, so iMessage and other apps can fetch the SYMZ 3D CUSTOMZ badge. In v7 they pointed at symzcustomz84.com, which still runs the old site. Change the address in the four preview tags when the site moves.
- Review pass on the v7 behaviour, all confirmed working:
  - the nav highlights each section as you reach it, including the order button on the form;
  - Photo → Figure holds on the photo until it is fully in view and the page is still;
  - the autoscroll tour stops on Photo → Figure and stays for the whole animation.
- Safety limits added: the tour never waits more than about 24 seconds on that section, and never waits at all for visitors with reduced motion turned on.

## v7
- Nav shows where you are: the link for the section on screen lights up with a red underline (in the phone menu, it turns red), and "Start an order" gets a ring on the order form. This works for normal scrolling and during the autoscroll tour.
- Photo → Figure only starts once the visitor is actually there, meaning the animation is in view and the page has stopped moving, so the whole sequence is seen from the photo onward. It restarts each time you come back. The autoscroll tour now stays on this section until one full run has played (Symz's thought fades once read), then moves on.
- Link previews (iMessage and everywhere else) now use the SYMZ 3D CUSTOMZ badge with Symz: `img/og-symz.jpg`, 1200×1200.

## v6
- Exploded View: everything is in one console that fits the screen, so no scrolling is needed. The Sword / Name plaque / Controller dock picker is on top, the render is in the middle, and the Explode button, Built-to-Apart slider and readout are along the bottom. On phones: the headline, then the console sized to the rest of the screen, then the intro; the controls leave room for Symz in the corner.
- Photo → Figure: a new "Adjust for print" step between the scan and the print. The scan wireframe reshapes from the customer's pose into the figure's (the horn swings up), then fills in as a solid print-ready model inside a print-volume box. That wireframe stays faintly visible above the print line while it prints.

## v5
- Merch: the item pictures moved to a 2-column scrolling list beside the map on desktop, and one swipeable row under the map on phones. The map and the list follow each other: hover (or tap) a piece on the map and the list scrolls to it; hover a picture, or swipe it to the middle of the row on phones, and it's outlined on the map. On phones, the first tap on the map picks a piece and the second opens it.
- Speed: first load is about a third lighter (about 3.1 MB down to 2.0 MB), and a full scroll is about 40% lighter (about 7 MB down to 4.4 MB).
  - Light WebP versions of the gallery photos are used in the grids; the full photos still open in the viewer.
  - Symz's art loads as WebP (101 KB instead of a 650 KB PNG), with a tiny face image for the chat header.
  - The unused Pacifico font is gone.
  - The loader's first frame is preloaded, and the CDN connection is opened early.
  - Leftover code is removed, including an old optional-model check that caused a 404.
- Autoscroll waits until the hero is actually on screen before its 4-second idle countdown, so the welcome thought always shows first. It used to start counting during the loading screen.
- Phones: bigger tap areas for the ORDER button, the thought-cloud buttons and ✕, and the footer links. The corner thought cloud is a little smaller and fades sooner once read.
- Checked at desktop (1440×900) and phone (390×844) sizes, section by section: no sideways scrolling, no broken images, no script errors.

## v4
- Photorealism pass: the loading screen and the Exploded View are now rendered in Blender (Cycles) and shipped as image sequences.
  - Loading screen: photoreal printer (V-slot frame, PEI bed, brass nozzle, red shroud, PTFE tube). The SYMZ CUSTOMZ logo is bigger, hovers halfway between the bed and the top of the frame (no stand), and prints in step with load progress.
  - Symz stays the 3D figure with the full-definition avatar art on both sides (a Blender-built version was tried and dropped in favour of this one).
  - Exploded View: the sword, name plaque and controller dock rebuilt part by part in Blender and rendered at 9 explode steps, plus a print-in from the build plate. Drag across the picture to pull it apart.
- Merch section (new, in the nav): the merch lineup photo (the map) with all 32 items clickable. Hovering an item outlines its shape in white, and hotspot dots show names. Under the map are the individual item pictures with category filters, plus an item viewer with "Order this" (adds a Merch line to the order form) and "Find in lineup".
- Photo → Figure: animated. Photo, background removed, laser 3D scan into a mesh, grey 3D model, layer-by-layer print, then the finished painted figure.
- Thought clouds: smaller. Corner thoughts are placed where they cover the least page content. The cloud lets clicks through (except its own buttons), and corner thoughts fade once read. The hero cloud stays inside Symz's column.
- Mobile ☰ menu, so every section, including Merch, is reachable from the nav on phones.
- Images reserve their space while loading, so jumping to a section lands in the right place.

## v3
- Autoscroll tour stops only when a new section's top reaches the top of the screen; Symz's thought shows at each stop for long enough to read.
- Phone hero: Symz centred between the headline and the intro, thought cloud to his right.
- Link previews: share image (logo + Symz) with Open Graph and Twitter card tags, plus a home-screen icon.

## v2
- Loading screen with a 3D printer printing the logo in step with load progress; every refresh starts at the loader.
- Photoreal two-sided Symz; thought cloud with ✕; corner assistant; autoscroll at 33% speed; Exploded View section; shorter nav that stays on top.

## v1
- First build: hero, divisions, photo → figure, gallery, process, FAQ, order form, Symz guide and assistant, all-caps / small-caps type.
