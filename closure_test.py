"""
what is closure
function that can access non-global variables that are defined outside of its body.

terms 
    free variable : that non-global and accesible variable
"""

""" about variable scope in python >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
python closure needs understanding variable scopes
below snippet's local b has error
in python check's variable names between inside and outside scope
"""
def scope_doctest():
    """
    >>> b = 6
    >>> def f2(a):
    ...     print(a)
    ...     print(b)
    ...     b = 9  # this is now allowed
    ... 
    >>> f2(3)
    3
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 3, in f2
    UnboundLocalError: local variable 'b' referenced before assignment
    """
    pass


""" test closure w/ averager examples >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
"""
# simple averager impl w/ class
class Averager():
    def __init__(self):
        self.series = []

    def __call__(self, new_value):
        self.series.append(new_value)
        total = sum(self.series)
        return total/len(self.series)

# now using function only
def make_averager():
    series = []

    def averager(new_val):
        # series is non-global out of scope variable
        series.append(new_val)
        total = sum(series)
        return total/len(series)

    return averager

'''
test closure
>>> avg1 = make_averager()
>>> avg1(10)
10.0
>>> avg1(11)
10.5
>>> avg1(12)
11.0

can see variable state
>>> avg1.__code__.co_varnames
('new_val', 'total')
>>> avg1.__code__.co_freevars
('series',)

can see closere state
>>> avg1.__closure__
(<cell at 0x7fd0ed326d98: list object at 0x7fd0eb598a88>,)
>>> avg1.__closure__[0].cell_contents
[10, 11, 12]
'''

""" this shows why nonlocal is needed in python closure
when closure modifies free variables, python's scope don't allow it.
only nonlocal scope error nont happen
"""
def make_averager():
    count = 0
    total = 0

    def averager(new_val):
        # if this line is ommited, 
        # UnboundLocalError: local variable 'count' referenced before assignment
        nonlocal count, total
        count += 1
        total += new_val
        return total / count

    return averager
