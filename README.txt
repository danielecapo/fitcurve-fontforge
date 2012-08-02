A script for manipulating control points of a bezier curve to increase, or decrease, its 'squareness'.

[I've seen a similar feature in Glyphs (http://www.glyphsapp.com).]

To use it, select at least two consecutive points, then run the fit curve script under the Tools menu, enter a number (with 0 the curve becomes a line, with 100 the two handles are extended until they touch, if you enter a number greater than 100, handles cross and the curve becomes concave).
If the handles of the selected bezier segment are parallel, or the segment is a line, nothing happens.

Place this script in ~/.FontForge/python/ as usual.
