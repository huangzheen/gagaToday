# Review Tasks — Hofbräuhaus München Draft

**Draft ID:** restaurant_munich_hofbraeuhaus
**Generated:** 2026-06-21 by restaurant-import-agent
**Status:** `draft` → awaits human review before promotion to `approved`

This file lists everything a human reviewer MUST verify, fix, or decide on before this draft can be promoted out of `frontend/src/content/drafts/restaurants/` into `frontend/src/content/munich/`.

---

## P0 — Blockers for publish

### T1. Verify every price_eur against an actual menu

- **Why:** All `price_eur` values are `price_type: "estimated"` because Hofbräuhaus does not publish a PDF menu online.
- **How:** Either (a) someone with a printed/photographed menu at home, (b) a field visit (call +49 89 290 136 100 first), or (c) written confirmation from Hofbräuhaus press office.
- **Files affected:** `restaurant_munich_hofbraeuhaus.profile.draft.json`, `restaurant_munich_hofbraeuhaus.menu_items.draft.json`, `restaurant_munich_hofbraeuhaus.price_notes.draft.json`.
- **Specific items to verify:**
  - Schweinshaxe (estimate 19-23 EUR)
  - Schweinsbraten (estimate 14.50-18 EUR)
  - Brezn (estimate 3.50-5 EUR)
  - Weißwurst mit Brezn (estimate 9-12 EUR, confirm morning-only vs all-day)
  - Leberknödelsuppe (estimate 7-9.50 EUR)
  - Hendl (estimate 13.50-16.50 EUR)
  - Käsespätzle (estimate 10.50-13.50 EUR)
  - Brotzeitteller (estimate 12.50-16.50 EUR)
  - Kaiserschmarrn (estimate 9-12 EUR)
  - Apfelstrudel (estimate 5.50-7.50 EUR)
  - Bayerische Creme (estimate 5-7 EUR)
  - Sauerkraut / Kartoffelsalat side (estimate 4-5.50 EUR)
  - Apfelschorle / Spezi / Mineralwasser (estimate 3.20-4.80 EUR)
  - All Maß beer prices (estimate 11-13 EUR)
- **On verify:** Set `price_type: "official_or_confirmed"`, populate `valid_from`, set `confidence >= 0.85`.

### T2. Source 1-3 image_candidates — ✅ DONE (2026-06-21 12:40 PT)

- **Why:** Game cannot render without images.
- **Resolution status:** 4 candidates now populated:
  - 2 Wikimedia Commons (1 PD + 1 CC-BY-SA-4.0) — approved_for_draft, ready to use
  - 1 AI-generated Brezn — approved_for_draft, ready to use
  - 1 official Hofbräuhaus Schwemme image — needs_review (awaiting written permission for redistribution)
- **Remaining action:** Email Hofbräuhaus press office (medienanfragen@hofbraeuhaus.de) for written permission on the Schwemme image. If denied, generate AI placeholder for Schwemme.
- **Files affected:** `restaurant_munich_hofbraeuhaus.profile.draft.json` (image_candidates array — already updated), local cache in `docs/agent_runs/restaurants/assets/`.
- **Verified URLs (HTTP 200):**
  - `https://upload.wikimedia.org/wikipedia/commons/d/d4/Hofbr%C3%A4uhaus_M%C3%BCnchen_2023.jpg`
  - `https://upload.wikimedia.org/wikipedia/commons/6/60/Hofbrauhaus.JPG`
  - `https://www.hofbraeuhaus.de/wp-content/uploads/2023/08/hofbraeuhaus-schwemme-692x1024.png`
  - AI Brezn: `docs/agent_runs/restaurants/assets/brezn_ai_generated.png`

### T3. Verify OSM coordinates

- **Why:** I used well-known Altstadt placement. Exact OSM way/node id was not fetched.
- **How:** Query https://www.openstreetmap.org/search?query=Platzl+9+M%C3%BCnchen and capture the node/way id. Verify lat/lng to 6 decimal places.
- **Files affected:** `restaurant_munich_hofbraeuhaus.profile.draft.json` (coordinates block).

### T4. Confirm minor-visible flag rendering

- **Why:** Age-gating is implemented as data flag; the actual render-layer filter is in the game engine, not this draft.
- **How:** Coordinate with the agent-pipeline-agent or game developer. Confirm the game engine's restaurant UI reads `minor_visible_in_player_menu` and `age_gate` fields and filters accordingly.
- **Files affected:** Render layer (out of scope for this agent, but flagged here).

---

## P1 — Should be done before publish, but not strict blockers

### T5. Weißwurst serving window confirmation

- **Why:** Cultural convention says Weißwurst is served before noon, but restaurant policies vary. Some restaurants serve all day.
- **How:** Confirm with Hofbräuhaus directly or with a recent visitor's photo of the menu.
- **Decision options:**
  - (a) Mark as morning-only (`served_before_noon_tradition: true`, surface in game only before 12:00)
  - (b) Mark as all-day (simpler)
- **Files affected:** `restaurant_munich_hofbraeuhaus.menu_items.draft.json` (menu_item_hb_weisswurst).

### T6. Cover charge / Brot und Gedeck verification

- **Why:** Some German restaurants add a small cover charge (1-3 EUR per person) not listed online.
- **How:** Confirm via phone or visit.
- **Files affected:** `restaurant_munich_hofbraeuhaus.price_notes.draft.json` (tips_and_extras section).

### T7. Festsaal vs Schwemme price differential

- **Why:** Some restaurants have different prices for the upstairs event hall. Hofbräuhaus may or may not.
- **How:** Confirm during menu verification.
- **Files affected:** `restaurant_munich_hofbraeuhaus.price_notes.draft.json` (surcharge_notes section).

### T8. OpenStreetMap nearby POIs

- **Why:** `near_location_ids` are textual guesses. Should be cross-checked against OSM or the project's `munich/` directory for canonical IDs.
- **How:** Read `frontend/src/content/munich/locations.draft.json` (or equivalent) if it exists; align IDs.
- **Files affected:** `restaurant_munich_hofbraeuhaus.profile.draft.json` (near_location_ids).

---

## P2 — Nice-to-have improvements

### T9. Add Weißwurst cultural hint to game dialogue

- **Cultural lesson opportunity:** "Weißwurst should be eaten before noon — what time is it now?"
- **Owner:** game-script author, not restaurant-import-agent. Just flagging.

### T10. Beer-garden status

- **Current draft:** notes "Calmer when weather permits. Closed in winter."
- **Improve:** Confirm exact seasonal opening of the Hofbräuhaus Biergarten (inner courtyard with chestnut trees). It's typically open April-October but may vary year to year.

### T11. Add language task "Trinkgeld / 'Stimmt so'"

- **Cultural lesson:** A1/A2 students should learn the German tipping convention. The draft mentions this in `game_role.language_tasks_supported` but a dedicated menu task could be added.
- **Owner:** game-script author.

### T12. Cross-reference with related Bavarian-restaurant drafts

- **Why:** Hofbräuhaus is one of ~5 major Munich beer halls. Augustiner-Keller, Schneider Bräuhaus, Hofbräuhaus am Platzl, Augustiner am Platzl, Ratskeller, etc. share many menu items.
- **How:** Once this draft is approved, the `food_items.draft.json` entries (which are already restaurant-agnostic) can be reused across the other Bavarian-restaurant drafts. Saves work.
- **Owner:** restaurant-import-agent (future task).

---

## P3 — Acceptance sign-off

When all P0 items are resolved and P1 items are at least answered (with "yes/no, here's why"), the draft is ready for promotion:

```bash
# Reviewer runs this after resolving P0/P1:
mv frontend/src/content/drafts/restaurants/restaurant_munich_hofbraeuhaus.profile.draft.json \
   frontend/src/content/munich/restaurant_munich_hofbraeuhaus.json

# Then update review_status from "draft" to "approved" in the moved file.
# Then update the canonical restaurants index (if one exists in munich/).
```

Coordinate with agent-pipeline-agent for the index update.

---

*End of review tasks. Generated by restaurant-import-agent, 2026-06-21.*
