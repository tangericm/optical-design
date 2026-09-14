# Cooke triplet

50 mm EFL, f/5, three separated elements (SK16 positive / F2 negative / SK16
positive), stop at the negative element, 20 degrees half field (40 full), 480 / 550 /
650 nm. `optiland.samples.objectives.CookeTriplet` unmodified. On-axis RMS spot 4.3 um
against a 3.4 um Airy radius — well corrected on-axis; the interesting behavior is off
axis, where it grows to about 17 um at 0.7 field and 13 um at full field (the classic
triplet zonal dip, not monotonic).

Good for: the cheapest lens form that genuinely covers a wide field at a moderate
speed. Three elements, three separated airspaces, six curvatures and two glasses give
just enough variables (roughly one per Seidel term you need to zero: spherical, coma,
astigmatism, Petzval, distortion, axial color, lateral color minus the constraints
already used by power and achromatism) to balance the primary aberrations
simultaneously — which is why it has stayed in continuous use since 1893. Push past
about f/4 or about 25 degrees half field and it runs out of degrees of freedom;
astigmatism and field curvature are what give first.

Release the two air gaps first (they set stop position and Petzval balance), then the
four curvatures on the outer elements, then the negative element's curvatures last —
it carries most of the astigmatism correction and is sensitive.

Kingslake credits the Cooke triplet to Taylor, 1893; Kidger, *Fundamental Optical
Design*, ch. 6; Sasián, *Introduction to Lens Design*, ch. 12.
