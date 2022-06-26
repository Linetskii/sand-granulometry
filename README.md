#sand-granulometry
Fast and simple application for routine analysis of sand samples
##Reqirements
* Python 3.10 or above
##Setup
To setup, create and activate a new python venv and run `pip install -r- reqirements.txt`
Then run main.py using `py main.py`
##How to use

###Add sample tab
You can use Tab button to switch to the next input field
The date should be in yyyy.mm.dd format

###Compare samples tab
* Left click on header - sort by chosen column, in ascending or descending order.
* Right click on header - open filter window.
    * Values list - select any number of values and press "Filter" button. Press "Clear all" to clear all filters
    * Index information.
    * From-to - write minimal and maximal values and press "Filter".
* Left click on row - select one row.
* Ctrl + Left click on row - select multiple rows.
* "Plot" button - draw Cumulative curves.

###Settings
* General settings - rounding and default fractions
* Converter - convert sand diameter
* Add fractions scheme - save mesh size diameter (in φ units) of your sieves in descending order.