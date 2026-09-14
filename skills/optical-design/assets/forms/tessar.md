# Tessar

4.0 mm EFL, f/4.5, four elements in three groups (N-SK15 positive / F2 negative,
airspace, K10-N-SK15 cemented pair), 20.5 degrees half field, 486.1 / 587.6 / 656.3
nm. `optiland.samples.objectives.TessarLens` unmodified — a miniature-scale Tessar,
not a classic 50 mm one; everything scales linearly for a bigger version. On-axis RMS
spot 0.5 um, inside the 3.1 um Airy radius — genuinely diffraction-limited on-axis,
the best-corrected sample in this library at this field angle.

Good for the same territory as the Cooke triplet — 15-25 degrees half field, f/3.5-f/6
— with one more free glass boundary (the cemented rear pair) correcting coma and
astigmatism together, historically at much lower cost than a fully separated
4-element lens. Think "triplet with its rear element split into a cemented pair."
Runs out of room past about f/3.2 or 28-30 degrees half field, same failure mode as
the triplet.

Release the front element and the pre-stop airspace first, then the cemented pair's
outer curvatures; touch the cemented interface itself last — it mainly trims color.

Kingslake, *A History of the Photographic Lens* (Rudolph, 1902); Smith, *Modern Lens
Design*, ch. 9.
