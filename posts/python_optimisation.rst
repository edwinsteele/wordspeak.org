.. title: Python performance drill-down: map vs list comprehensions
.. slug: python-performance-drill-down-map-vs-list-comprehensions
.. date: 2013/09/26 17:30:01
.. tags: Python, draft
.. link:
.. description:

Recently I saw a quick python benchmark comparing
the map function with list comprehensions. It was high level and reminded me how
interesting I found Doug Hellmann's `dictionary performance analysis <http://doughellmann.com/2012/11/the-performance-impact-of-using-dict-instead-of-in-cpython-2-7-2.html>`_
and how it was an easy introduction to python bytecode and to the interpreter source.
It's a great read if you've got a bit of time.


Anyway, take a quick look at the `original article <http://threebean.org/blog/quickstrip/>`_
You'll see that there's about 3% difference

There's no mention (it's a short article after all) about the interpreter version. I see
a big difference between versions, and even between different builds of the same
version. As I don't have access to a bare-metal machine with CPU isolation and
the various versions of the interpreter, I adjusted the timeit parameters so that
it performs a smaller number of iterations per timing run (10000 instead of 1000000
as in the original), but a performs this smaller test 100 times and uses the minimum reading in accordance
with the `timeit documentation <http://localhost/~esteele/python-2.7.3-docs-html/library/timeit.html?highlight=timeit#timeit>`_. With as
little running on my machine as possible, I hope this gives a reasonable indication
of elapsed time.

.. csv-table:: python version and build comparison
    :widths: 20 50 20 20 20
    :header: "Version", "Source", "map time", "list comp time", Difference %"

    "2.6.8", "Python.org Mac x64", "1.524", "1.665", "8%"
    "2.7.2", "OS X 10.8 default", "2.085s", "2.087s", "0%"
    "2.7.2", "Python.org Mac x64", "1.508s", "1.642s", "9%"
    "3.3.0", "Python.org Mac x64", "1.510s", "1.615s", "7%"

Based on these results, I can't work out which version the original is using,
so I'll run the test with 2.7.2 (I haven't quite made the jump into 3.3 yet)
I'm also shocked at how poorly the default python interpreter performed

For ease of reference, I'll *enfunctionate* the routines. All the source is
`available <https://github.com/edwinsteele/python-scripts/blob/master/map_vs_listcomp_comparison.py>`_:

.. code-block:: python

 def run_map():
     return set(map(str.strip, ['wat '] * 200))

 def run_listcomp():
     return set([s.strip() for s in ['wat '] * 200])


run_map(): 78.1 usec/loop
run_listcomp(): 81.3 usec/pass

So run_listcomp() is 3 micros slower per iteration. Where is it coming from?
Let's look at the bytecode for each function (bytecode is different between versions)

.. csv-table:: disassemble comparison
    :widths: 50 60 30
    :header: "run_map()", "run_listcomp()", "Notes"
    :keepspace:

	``0  LOAD_GLOBAL           0 (set)``   ,       ``0 LOAD_GLOBAL 0 (set)``,Load 'set' from the global namespace
	                                       ,       ``3 BUILD_LIST  0``,Create an empty list
	``3  LOAD_GLOBAL           1 (map)``   ,,
	``6  LOAD_GLOBAL           2 (str)``   ,,
	``9  LOAD_ATTR             3 (strip)`` ,,
	``12 LOAD_CONST            1 ('wat ')``,       ``6 LOAD_CONST               1 ('wat ')``,Next 4 lines create a list of 200 'wat ' strings
	``15 BUILD_LIST            1``         ,       ``9 BUILD_LIST               1``,
	``18 LOAD_CONST            2 (200)``   ,      ``12 LOAD_CONST               2 (200)``,
	``21 BINARY_MULTIPLY``                 ,      ``15 BINARY_MULTIPLY``
	                                       ,      ``16 GET_ITER``,
	                                       ,``>> 17 FOR_ITER                18 (to 38)``,
	                                       ,      ``20 STORE_FAST               0 (s)``,
	                                       ,      ``23 LOAD_FAST                0 (s)``,
	                                       ,      ``26 LOAD_ATTR                1 (strip)``,
	                                       ,      ``29 CALL_FUNCTION            0``,
	                                       ,      ``32 LIST_APPEND              2``,
	                                       ,      ``35 JUMP_ABSOLUTE           17``,
	``22 CALL_FUNCTION         2``         ,,Call the 'map' function
	``25 CALL_FUNCTION         1``         ,``>> 38 CALL_FUNCTION            1``,Call the 'set' function
	``28 RETURN_VALUE``                    ,      ``41 RETURN_VALUE``,Return the list
	  

Much of the bytecode is shared, so we will compare execution time for
run_map():3,6,9,22 vs run_listcomp():16-35.

Setup Costs
===========

Let's examine the setup costs of map vs list comprehensions by iterating
over an empty list:

.. code:: python
 
 def run_map_empty_list():
     return set(map(str.strip, []))
 
 def run_listcomp_empty_list():
     return set([s.strip() for s in []])


run_map_empty_list: 1.215 usec/loop.
run_listcomp_empty_list: 0.688 usec/loop.

So there isn't any difference of consequence, in setup costs.

Runtime Costs
=============

There are two other significant differences between run_map() and
run_listcomp(). The list comprehension
uses more bytecode, and the two functions are different: the str.strip()
method descriptor vs the builtin function strip()

By running a comparison with a non-empty list, executing the same, cheap-to-run
function, we can see whether the runtime cost of list comprehension itself is more expensive than
map.

.. code-block:: python

 def noop(s):
     return s

 def run_map_noop():
     return set(map(noop, ['wat '] * 200))

 def run_listcomp_noop():
     return set([noop(s) for s in ['wat '] * 200])


run_map_noop: 53.326 usec/loop.
run_listcomp_noop: 56.856 usec/loop.

And it looks like list comprehension is slower than map with 200 elements.

Remember, though, that list comprehension was faster with an empty list. What
sort of performance do we get as we run with lists of different sizes?

<comparison at different lengths. at what point do map and list comprehension
performance become equal? Possibly make reference to the way the default OS X
python interpreter is actually quite a bit faster for list comp for large
size>

The difference between run_map_noop vs run_listcomp_noop is the same as
run_map vs run_listcomp, in percentage
terms, so it's puzzling why method descriptor is slower than the builtin
function, even once we've cached the strip lookup from bytecode line 9

"wat ".strip(): Min: 0.278 usec/loop. All: 0.280, 0.279, 0.278, 0.282, 0.283
str.strip("wat "): Min: 0.449 usec/loop. All: 0.456, 0.449, 0.449, 0.449, 0.472
str_strip("wat "): Min: 0.335 usec/loop. All: 0.341, 0.335, 0.335, 0.335, 0.338



a: Min: 77.806 usec/loop. All: 77.878, 81.836, 77.845, 77.806, 78.205
b: Min: 82.062 usec/loop. All: 82.423, 82.062, 85.186, 85.316, 85.758
a_empty_list_with_construction: Min: 3.151 usec/loop. All: 3.271, 3.407, 3.153, 3.151, 3.151
b_empty_list_with_construction: Min: 2.590 usec/loop. All: 2.595, 2.605, 2.592, 2.590, 2.598
a_noop: Min: 53.326 usec/loop. All: 53.326, 53.727, 53.465, 56.433, 53.749
b_noop: Min: 56.856 usec/loop. All: 56.930, 56.869, 56.929, 56.856, 56.857
b_noop_with_lookup: Min: 75.208 usec/loop. All: 75.684, 75.264, 75.476, 75.289, 75.208
set(["wat"] * 200): Min: 8.089 usec/loop. All: 8.123, 8.089, 8.095, 8.097, 8.096
set(wats_list): Min: 6.282 usec/loop. All: 6.417, 6.438, 6.398, 6.282, 6.438
"wat ".strip(): Min: 0.278 usec/loop. All: 0.280, 0.279, 0.278, 0.282, 0.283
str.strip("wat "): Min: 0.449 usec/loop. All: 0.456, 0.449, 0.449, 0.449, 0.472
str_strip("wat "): Min: 0.335 usec/loop. All: 0.341, 0.335, 0.335, 0.335, 0.338
