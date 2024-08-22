# Depix

Depix is a program to convert plots back into datasets.

Despite the simplicity of Depix, it provides a very convenient work flow for transforming
(scanned) plots back into (x,y) datasets.

Depix was created on a standard Linux Desktop environment with Python, Numpy, Gimp,
pdfimages, and Inkscape installed. I have only used it on such an environment. If you get
it working on another OS, feel free to make a pull request.

If you encounter troubles when using Depix, check the FAQ at the bottom of this
file. If that does not solve your problem, feel free to get in touch:
Toon.Verstraelen@UGent.be.


## Release history

* This program was written by Toon Verstraelen in Sep 2012 for the preparation of a paper
  with the title, "ACKS2: Atom-Condensed Kohn-Sham approximated to second order", in order
  to convert some plots of an old JCP paper into datasets for comparison with a newly
  proposed model.

* Support for logarithmic scales was added May 2016.

* Cleanup and conversion to Python 3 (Aug 2024).


## Work flow

1. If the plot is part of a pdf, use ``pdfimages`` to extract the figures from the PDF as
   ``.pbm`` files. One can also use Evince to extract bitmaps from a PDF: right click on
   the image and "Save Image As ...".

2. Open the image containing the plot with Gimp, crop it if needed and save the file as a
   ``.png`` file.

3. Open the ``.png`` file with Inkscape. Use the "link" option to avoid large ``.svg``
   files in one of the following steps.

4. Draw the x- and y-axis as two separate straight line segments, i.e. lines with only a
   beginning and end node. The accuracy of the extracted data will improve when these line
   segments are made as long as possible. However, make sure the beginning and the end
   node lie at sensible points on the x- and y-axis. Depix can handle cases where the x-
   and y-axis are not orthogonal or rotated, e.g. due to a poor scan.

5. Draw a polyline, consisting of straight line segments (not Bezier curves), over the
   curve of interest. Make sure your drawing falls nicely over the curve in the scanned
   image, as this will also determine the accuracy of the final data. It may be helpful to
   use a bright colored and semi-transparent line style.

4. Open the XML window in Inkscape. Select the x-axis and change the id of the path to
   ``xaxis:x0:x1:kind``, where ``x0`` and ``x1`` are replaced by the numerical x-values of
   the beginning and end points of the line segment for the x-axis. The last part,
   ``kind``, must be replaced by ``lin`` or ``log`` for linear or logarithmic scales,
   respectively. Do the same for the y-axis, using the id ``yaxis:y0:y1:kind``, following
   the same conventions. The path with the datapoints should be given the id "data".

5. Use the "File" -> "Save as" menu item to save the file in ``.svg`` format.

6. Run Depix as follows:

        ./depix.py yourfile.svg yourdata.txt

   Some screen output is given, which may be useful for debugging, if things don't work as
   expected. The text file ``yourdata.txt`` contains two columns with x and y data.

This work flow has the advantage that all intermediate steps are saved in files, such that
you can make incremental improvements. Furthermore, thanks to the neat graphical interface
of Inkscape, one can make fairly accurate overlays of the data points on top of the
scanned figure.

If you need to extract more than one curve from a single plot, just copy the ``.svg`` file
with the first curve to a new file and trace the second curve in this copy.


## Examples distributed with the source code


The example ``hf_135.svg``comes from the paper http://dx.doi.org/10.1063/1.466016. The
figure is converted to a dataset as follows:

    ./depix.py hf_135.svg hf_135.txt

The example ``diffusion.svg`` comes from the paper http://dx.doi.org/10.1016/j.molliq.2014.11.010.
figure is converted to a dataset as follows:

    ./depix.py diffusion.svg diffusion.txt


FAQ
===

**Q.** I get errors when running Depix, e.g. like the following:

    Traceback (most recent call last):
      File "./depix.py", line 177, in <module>
        main()
      File "./depix.py", line 170, in main
        data = process_file(args[0])
      File "./depix.py", line 159, in process_file
        x_axis, y_axis, px_data = load_pix_data_svg(fn)
      File "./depix.py", line 76, in load_pix_data_svg
        px_data = parse_data(path)
      File "./depix.py", line 56, in parse_data
        x, y = word.split(',')
    ValueError: need more than 1 value to unpack

**A.** Make sure the x- and y-axis are straight lines and the data polyline consists of
straight line segments. This may happen when Bezier curves were used instead.


**Q.** The data points are mirrored horizontally or vertically. How can I fix this?

**A.** One must make sure that the order of the two points in the line segments for the x-
and y-axis are compatible with the order of ``x0`` and ``x1`` in the path id
``xaxis:x0:x1:kind``. One may add an end marker in Inkscape to see clearly what the end
point of the line segment is. With the menu item "Path" -> "Reverse path", one can swap
begin and end.
