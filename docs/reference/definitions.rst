.. py:module:: skald.definitions
.. py:currentmodule:: skald.definitions

:py:mod:`defintions` Module
===========================

A minimal example is show below, which fetches http://www.python.org and
puts a tooltip at the search input field.

.. code-block:: python

    from selenium import webdriver
    from skald.definitions import Screenshot, Document, save

    # Create a Firefox webdriver
    driver = webdriver.Firefox()
    # Load python.org
    driver.get("http://www.python.org")
    # Get the #id-search-field element
    search_field = driver.find_element_by_id("id-search-field")

    # Create a screenshot
    screenshot = Screenshot(name="python", path="skald")
    # Create a document for the screenshot
    document = Document(name="search")
    # Add the search field element with a tooltip
    document.add_element(search_field, tooltip="Enter your search terms here")
    # Add the document to the screenshot
    screenshot.add_document(document)
    # Save the screenshot, this is when the actual screenshot is taken
    save(screenshot, driver)

    driver.close()

Classes
-------

.. autoclass:: Screenshot
   :members:
   :special-members: __init__

.. autoclass:: Document
   :members:
   :special-members: __init__

.. autoclass:: Element
   :members:
   :special-members: __init__

.. autoclass:: Tooltip
   :members:
   :special-members: __init__

.. autoclass:: Position
   :members:

.. autoclass:: Alignment
   :members:

Functions
---------

.. autofunction:: get_positions
.. autofunction:: get_alignments
