MultiPanel Context Manager
--------------------------

.. currentmodule:: stonerplots.context

Another common requirement when writing papers and theses is to create a figure with several distinct panels shwing
different (related) datasets. In this case, the :py:class:`MultiPanel` context manager works in a very analogous way to the
:py:class:`StackVertical` context manager.::

    with MultiPanel((2,2)) as axes:
    for ax,x,y in zip (axes,[x1,x2,x3,x4],[y1,y2,y3,y4]):
        ax.plot(x,y)

The only required parameter is the number of panels to show. This can be either a tuple of (n_rows,n_cols) or an
integer specifying a number of columns (number of rows is assumed to be one in this case.)

Optional Parameters
~~~~~~~~~~~~~~~~~~~

The *figure*, *sharex*, *sharey* and *label_panels* work exactly as for the :py:class:`StackVertical` Context manager
described above, except that the default is not to share any axes - see `Stacked Plots<stackvertical>` for more
details.

The *adjust_figsize* parameter lets you specify a tuple to give different expansion factors for width and height. The
default value is to expand the width by exactly the number of columns and the height by the height of one row + 80% of
additional rows. Since full-page width figures are more than double a single column, it may be useful to do something
like::

    with SavedFigure("example.png",stle=["stoner","aip","aip2"]):
        with MultiPanel((2,2),adjust_figsize=(0,0.12)) as axes:
            for ax,x,y in zip (axes,[x1,x2,x3,x4],[y1,y2,y3,y4]):
                ax.plot(x,y)

To make a genuinely full width x 2 single plots high figure.

For the figure below (from the style gallery), the *adjust_figsize* was set to (0,-0.25), meaning that width was
preserved, and height was reduced by a factor of -25%. Whilst a postivie expansion factor is applied to the additional
rows, the negative value is applied to the original figure size. (The logic here is that the times you are needing to
shrink the original figure size is when the final aspect ratio will be higher than the original figure.)

.. image:: ../../examples/figures/fig02h_1.png
  :alt: A single row of 2 sub-plats created from MultiPanel
  :align: center
