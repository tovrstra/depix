#!/usr/bin/env python
# Depix is a program to convert plots back into datasets.
# Copyright (C) 2016 Toon Verstraelen <Toon.Verstraelen@UGent.be>, Center
# for Molecular Modeling (CMM), Ghent University, Ghent, Belgium; all rights
# reserved unless otherwise stated.
#
# This file is part of Depix.
#
# Depix is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Depix is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --


import numpy as np
import sys


def load_pix_data_svg(fn):
    x_axis = None
    y_axis = None
    px_data = None

    def parse_svg_coordinates(name, s):
        print(f"Parsing coordinates id='{name}' path='{s}'")
        words = s.split()
        result = []
        if words[0] != "m" and words[0] != "M":
            raise ValueError("Path data should either start with M or m.")
        mode = "m"
        for word in words[1:]:
            if word == "V":
                mode = "v"
                continue
            if word == "H":
                mode = "h"
                continue
            values = word.split(",")
            if mode == "m":
                if len(values) != 2:
                    raise ValueError(f"Expecting two values after m, got {word}")
                x = float(values[0])
                y = float(values[1])
            elif mode == "v":
                if len(values) != 1:
                    raise ValueError(f"Expecting one value after v, got {word}")
                y = float(values[0])
            elif mode == "h":
                if len(values) != 1:
                    raise ValueError(f"Expecting one value after h, got {word}")
                x = float(values[0])
            row = np.array([x, y])
            if len(result) > 0 and words[0] == "m":
                row += result[-1]
            result.append(row)
        return result

    def parse_axis(name, path):
        result = parse_svg_coordinates(name, path.getAttribute("d"))
        if len(result) != 2:
            raise ValueError(f"Expected two points, got {len(result)} ({name})")
        words = name.split(":")
        result.append(float(words[1]))
        result.append(float(words[2]))
        result.append(str(words[3]))
        return result

    def parse_data(path):
        result = parse_svg_coordinates(name, path.getAttribute("d"))
        return np.array(result)

    from xml.dom.minidom import parse

    dom = parse(fn)
    paths = dom.getElementsByTagName("path")
    for path in paths:
        name = path.getAttribute("id")
        if name.startswith("xaxis"):
            if x_axis is not None:
                raise ValueError("X-axis defined twice.")
            x_axis = parse_axis(name, path)
        elif name.startswith("yaxis"):
            if y_axis is not None:
                raise ValueError("X-axis defined twice.")
            y_axis = parse_axis(name, path)
        elif name.startswith("data"):
            if px_data is not None:
                raise ValueError("Data defined twice.")
            px_data = parse_data(path)
    print()

    if x_axis is None:
        raise ValueError("No x-axis found.")
    if y_axis is None:
        raise ValueError("No y-axis found.")
    if px_data is None:
        raise ValueError("No data points found.")
    return x_axis, y_axis, px_data


def transform_px_data(x_axis, y_axis, px_data):
    # Print the pixel data on screen, useful for debugging.
    print("X axis specs")
    print(x_axis)
    print()
    print("Y axis specs")
    print(y_axis)
    print()
    print("Pixel data points")
    print(px_data)
    print()

    # construct x- and y-unit vectors in pixel coordinates
    px_xunit = x_axis[1] - x_axis[0]
    px_yunit = y_axis[1] - y_axis[0]

    # the affine transformation to pixel coordinates
    mat_to_pix = np.array([px_xunit, px_yunit]).T

    # the inverse affine transformation
    mat_from_pix = np.linalg.inv(mat_to_pix)

    # reference point for the x and y values
    x_low = np.dot(mat_from_pix, x_axis[0])
    y_low = np.dot(mat_from_pix, y_axis[0])

    # transform the datapoints to data coordinates
    data = np.dot(mat_from_pix, px_data.T).T
    data[:, 0] -= x_low[0]
    data[:, 1] -= y_low[1]

    def convert_unit(values, low, high, kind):
        if kind == "lin":
            values[:] = values * (high - low) + low
        elif kind == "log":
            llow = np.log(low)
            lhigh = np.log(high)
            values[:] = np.exp(values * (lhigh - llow) + llow)
        else:
            raise NotImplementedError

    # convert to plot units
    convert_unit(data[:, 0], x_axis[2], x_axis[3], x_axis[4])
    convert_unit(data[:, 1], y_axis[2], y_axis[3], y_axis[4])

    return data


def process_file(fn):
    if fn.endswith(".svg"):
        x_axis, y_axis, px_data = load_pix_data_svg(fn)
    else:
        raise ValueError("Unsopported extension for file %s" % fn)
    return transform_px_data(x_axis, y_axis, px_data)


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        raise ValueError("Expecting two arguments: input.svg output.dat")
    print("Processing data from %s" % args[0])
    print()
    data = process_file(args[0])

    np.savetxt(args[1], data)
    print("Written data in plot units to %s" % args[1])


if __name__ == "__main__":
    main()
