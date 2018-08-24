#!/usr/bin/env python

# Copyright (c) 2018, DIANA-HEP
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import math
import numbers
import operator

import awkward.util

class Common(object):
    def mag2(self):
        return self.dot(self)

    def mag(self):
        return awkward.util.numpy.sqrt(self.mag2())

    def rho2(self):
        out = self.x * self.x
        out += self.y * self.y
        return out

    def delta_phi(self, other):
        return (self.phi() - other.phi() + math.pi) % (2*math.pi) - math.pi

    def isparallel(self, other, tolerance=1e-10):
        return 1 - self.cosdelta(other) < tolerance

    def isantiparallel(self, other, tolerance=1e-10):
        return self.cosdelta(other) - (-1) < tolerance

    def iscollinear(self, other, tolerance=1e-10):
        return 1 - awkward.util.numpy.absolute(self.cosdelta(other)) < tolerance

    def __lt__(self, other):
        raise TypeError("spatial vectors have no natural ordering")

    def __gt__(self, other):
        raise TypeError("spatial vectors have no natural ordering")

    def __le__(self, other):
        raise TypeError("spatial vectors have no natural ordering")

    def __ge__(self, other):
        raise TypeError("spatial vectors have no natural ordering")

class ArrayMethods(Common):
    def unit(self, inplace=False):
        if inplace:
            self /= self.mag()
        else:
            return self / self.mag()

    def rho(self):
        out = self.rho2()
        return awkward.util.numpy.sqrt(out, out=out)

    def phi(self):
        return awkward.util.numpy.arctan2(self.y, self.x)

    def cosdelta(self, other):
        denom = self.mag2()
        denom *= other.mag2()
        mask = (denom > 0)
        denom = denom[mask]
        denom[:] = awkward.util.numpy.sqrt(denom)

        out = self.dot(other)
        out[mask] /= denom

        awkward.util.numpy.logical_not(mask, out=mask)
        out[mask] = 1

        return awkward.util.numpy.clip(out, -1, 1, out=out)

    def angle(self, other, normal=None, degrees=False):
        out = awkward.util.numpy.arccos(self.cosdelta(other))
        if normal is not None:
            a = self.unit()
            b = other.unit()
            out *= awkward.util.numpy.sign(normal.dot(a.cross(b)))
        if degrees:
            awkward.util.numpy.multiply(out, 180.0/awkward.util.numpy.pi, out=out)
        return out

    def isopposite(self, other, tolerance=1e-10):
        tmp = self + other
        awkward.util.numpy.absolute(tmp.x, out=tmp.x)
        awkward.util.numpy.absolute(tmp.y, out=tmp.y)
        awkward.util.numpy.absolute(tmp.z, out=tmp.z)

        out = (tmp.x < tolerance)
        awkward.util.numpy.bitwise_and(out, tmp.y < tolerance, out=out)
        awkward.util.numpy.bitwise_and(out, tmp.z < tolerance, out=out)
        return out

    def isperpendicular(self, other, tolerance=1e-10):
        tmp = self.dot(other)
        awkward.util.numpy.absolute(tmp.x, out=tmp.x)
        awkward.util.numpy.absolute(tmp.y, out=tmp.y)
        awkward.util.numpy.absolute(tmp.z, out=tmp.z)

        out = (tmp.x < tolerance)
        awkward.util.numpy.bitwise_and(out, tmp.y < tolerance, out=out)
        awkward.util.numpy.bitwise_and(out, tmp.z < tolerance, out=out)
        return out

class Methods(Common):
    def unit(self):
        return self / self.mag()

    def rho(self):
        return math.sqrt(self.rho2())

    def phi(self):
        return math.atan2(self.y, self.x)

    def cosdelta(self, other):
        m1 = self.mag2()
        m2 = other.mag2()
        if m1 == 0 or m2 == 0:
            return 1.0
        r = self.dot(other) / math.sqrt(m1 * m2)
        return max(-1.0, min(1.0, r))

    def angle(self, other, degrees=False):
        out = math.acos(self.cosdelta(other))
        if degrees:
            out *= 180.0/math.pi
        return out

    def isopposite(self, other, tolerance=1e-10):
        tmp = self + other
        return abs(tmp.x) < tolerance and abs(tmp.y) < tolerance and abs(tmp.z) < tolerance

    def isperpendicular(self, other, tolerance=1e-10):
        tmp = self.dot(other)
        return abs(tmp.x) < tolerance and abs(tmp.y) < tolerance and abs(tmp.z) < tolerance

    def __add__(self, other):
        return self._vector(operator.add, other)