# Tessar

4.0 mm EFL, f/4.5, four elements in three groups (N-SK15 positive / F2 negative,
airspace, K10-N-SK15 cemented pair), 20.5 degrees half field, 486.1 / 587.6 / 656.3
nm. `optiland.samples.objectives.TessarLens` unmodified — note the small absolute
scale (a miniature/cellphone-class Tessar, not a 50 mm classic); everything below
scales linearly if you need a bigger one. On-axis RMS spot 0.5 um, inside the 3.1 um
Airy radius at this aperture — genuinely diffraction-limited on-axis, and the best
corrected of the samples in this library at this field angle.

Good for: the same territory as the Cooke triplet — 15-25 degrees half field, f/3.5-f/6
— with one more free glass boundary (the cemented rear pair) buying better correction
of coma and astigmatism simultaneously, historically at a fraction of the manufacturing
cost of a fully separated 4-element lens. It is a triplet with its rear element split
into a cemented pair; think of it as "Cooke triplet plus one more Seidel-balancing
surface." Runs out of room past about f/3.2 or 28-30 degrees half field, same failure
mode as the triplet: astigmatism and field curvature.

Release the front element and the airspace before the stop first, then the cemented
pair's outer curvatures, and touch the cemented interface itself last — it mainly
trims color and is sensitive to small changes.

Kingslake, *A History of the Photographic Lens* (Tessar, Rudolph 1902); Smith, *Modern
Lens Design*, ch. 9.
