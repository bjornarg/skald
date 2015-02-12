.. py:module:: skald.geometry
.. py:currentmodule:: skald.geometry

:py:mod:`geometry` Module
==============================

The geometry module contains various geometrical functionality, generally as a
sub-class of :py:obj:`~tuple` to support interoperability with frameworks while
making manipulation easier.

This is done through heavy use of :py:func:`~collections.namedtuple`.

Classes
-------

.. autoclass:: Point
   :members:
   :special-members: __add__, __sub__

.. autoclass:: Rectangle
   :members:
   :special-members: __contains__, __add__, __sub__

.. autoclass:: Size

.. autoclass:: Box
