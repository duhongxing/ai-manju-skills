# Continuity v2 (draft)

The 21 existing genre skills remain intact except separately reviewed edits. Schemas and script are additive.

Run: `python -m unittest discover -s tests -v`

Run sample: `python scripts/validate_continuity.py examples/mie-men-zhi-ye/shots.json`

This validates metadata only. It does not prove character identity, hand anatomy, prop positions or video continuity in generated pixels. Generated images and videos require manual review.

Character front/side/back views must be three separate files, never a collage. The example shot files are references, not generated images.
