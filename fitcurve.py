import fontforge
from math import sqrt

# FontForge Fit Curve v0.1

# Copyright (c) 2012, Daniele Capo (capo.daniele@gmail.com)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# A script for manipulating control points of a bezier curve to make it
# more 'square' or more 'round'.
# I've seen a similar feature in Glyphs (glyphsapp.com).
# To use it, select at least two consecutive points,
# then run the fit curve script under Tools menu,
# enter a number (0 retract the handles, the curve becomes a line,
# with 100 the two handles are extended until they touch,
# if you enter a number greater than 100, handles cross,
# the curve becomes concave).
# If the handles of the selected bezier segment are parallel,
# or the segment is a line, nothing happens

# Place this script in ~/.FontForge/python/ as usual

# Transform a FF point in a vector (a couple)

def point_to_vec (p):
    return (p.x, p.y)

# Common operations on vectors

def vec_sub (v1, v2):
    return (v1[0]-v2[0], v1[1]-v2[1])

def vec_add (v1, v2):
    return (v1[0]+v2[0], v1[1]+v2[1])

def vec_mul (v, n):
    return (v[0]*n, v[1]*n)


def dot_product (v1, v2):
    return (v1[0] * v2[0]) + (v1[1] * v2[1])

def len_vector (v):
    return sqrt(v[0]**2 + v[1]**2)

def normalize (v):
    l = len_vector (v)
    return (v[0]/l, v[1]/l)

# Given a contour we can get from it a list of segments
# every segment is a list made by a tag, a start point, 
# an end point and, for curve segments, two control points.

def accumulate_segments (points, segments = ()):
    if len (points)>1:
        current_point = points[0]
        next_point    = points[1]
        if next_point.on_curve: # is a line segment
            return accumulate_segments (points[1:], segments + \
                                            (('line', current_point, next_point),))
        else:
            cp1 = next_point
            cp2 = points[2]
            end_point = points[3]
            return accumulate_segments (points[3:], segments + \
                                            (('curve', current_point, end_point, cp1, cp2), ))
    else: return segments

def segments (contour):
    points = map (lambda p: p, contour)
    if contour.closed:
        points.append (points[0])
    return accumulate_segments (points)

# accessors for segment
def start_point (segment):
    return segment[1]

def end_point (segment):
    return segment[2]

def cp_1 (segment):
    return segment[3]

def cp_2 (segment):
    return segment[4]

# predicates for segment

def is_line_seg (segment):
    return segment[0] == 'line'

def is_curve_seg (segment):
    return segment[0] == 'curve'

# if the start and end point are selected, then the segment is selected
def is_selected (segment):
    return start_point (segment).selected and end_point (segment).selected 

# so we can get the list of selected segments in a contour
def selected_segments (contour):
    return filter (is_selected, segments(contour))

def fit_curve ():
# functions used to check if the lines that join points and their
# control points intersect somewhere. 

    def almost_eq (v1, v2):
        return abs (len_vector (vec-sub (v1, v2))) < 0.0001

    def parallel (v1, v2):
        v1 = normalize (v1)
        v2 = normalize (v2)
        return abs (v1[0]*v2[1] - v1[1]*v2[0]) < 0.0001

    def handles_vec (segment):
        v1 = vec_sub (point_to_vec (cp_1 (segment)), \
                          point_to_vec (start_point (segment)))
        v2 = vec_sub (point_to_vec (cp_2 (segment)), \
                          point_to_vec (end_point (segment)))
        return (v1, v2)

    def converge (segment):
        if is_line_seg (segment): return False
        v1, v2 = handles_vec (segment)
        if parallel (v1, v2): return False
        return True
    
    def intersection (x1, y1, x2, y2, v1, v2):
        if v1[0] == 0.0:
            if v2[1] == 0.0: return (x1, y2)
            else:
                m = v2[0]/v2[1]
                return (x1, y2 + (x1 - x2) / m)
        if v1[1] == 0.0:
            if v2[0] == 0.0: return (x2, y1)
            else:
                m = v2[0]/v2[1]
                return (x2 + (y1 - y2) *m , y1)
        if v2[0] == 0.0 or v2[1] == 0.0:
            return intersection (x2, y2, x1, y1, v2, v1)
        else:
            m1 = v1[0]/v1[1]
            m2 = v2[0]/v2[1]
            y = (x2 - x1 + y1*m1 - y2*m2) / (m1 - m2)
            x = (y - y1) * m1 + x1
            return (x, y)
        
    
    def convergence (segment):
        x1, y1 = point_to_vec (start_point (segment))
        x2, y2 = point_to_vec (end_point (segment))
        v1, v2 = handles_vec (segment)
        return intersection (x1, y1, x2, y2, v1, v2)
          
    # I don't know if the term fit is the correct one. I think that in 'glyphs' 
    # (www.glyphsapp.com) a similar feature is called 'fit curve'

    def fit_segment (segment, v):
        if converge (segment):
            x1, y1 = point_to_vec (start_point (segment))
            x2, y2 = point_to_vec (end_point (segment))
            cp1 = cp_1 (segment)
            cp2 = cp_2 (segment)
            if v == 0.0:
                cp1.x = x1
                cp1.y = y1
                cp2.x = x2
                cp2.y = y2
            else:
                cx, cy = convergence (segment)
                cp1.x = x1 + (cx - x1) * v
                cp1.y = y1 + (cy - y1) * v
                cp2.x = x2 + (cx - x2) * v
                cp2.y = y2 + (cy - y2) * v
    
        

    def ask_user_fit ():
        value = fontforge.askString("Fit Curve", """Enter a number 
(0 = curve becomes a line, 100 = control points converge)""")
        if value == None: return False
        else:
            return int(value)/100.0

    def fit_selected_segments (registerobject, glyph):
        l = glyph.layers[glyph.activeLayer]
        selection = map (selected_segments, l) 
        try:
            v = ask_user_fit ()
        except:
            fontforge.postError("Bad Value", "Input was not a number")
        if v == False: return
        for contour in selection:
            for s in filter (is_curve_seg, contour):
                fit_segment (s, v)
        glyph.layers[glyph.activeLayer] = l
        print 'done'
    
    
    return fit_selected_segments

if fontforge.hasUserInterface():
    keyShortcut = None
    menuText = "Fit curve"
    fontforge.registerMenuItem(fit_curve(), None, None, \
                                   "Glyph", keyShortcut, menuText)


