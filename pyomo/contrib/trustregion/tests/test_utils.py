#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright 2017 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

import pyomo.common.unittest as unittest
from pyomo.contrib.trustregion.utils import (
    copyVector, minIgnoreNone, maxIgnoreNone,
    IterationLogger, numpy_available)
from pyomo.common.log import LoggingIntercept
from io import StringIO

class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipUnless(numpy_available, "numpy is not available")
    def test_copyVector(self):
        x = [1, 2, 3]
        y = [2, 7, 9]
        z = [1.0, 4.0, 10.0]
        c_x, c_y, c_z = copyVector(x, y, z)
        self.assertTrue(x[i] == c_x[i] for i in range(len(x)))
        self.assertTrue(y[j] == c_y[j] for j in range(len(y)))
        self.assertTrue(z[k] == c_z[k] for k in range(len(z)))
        self.assertFalse(id(x) == id(c_x))
        self.assertFalse(id(y) == id(c_y))
        self.assertFalse(id(z) == id(c_z))

    def test_minIgnoreNone(self):
        a = 1
        b = 2
        self.assertEqual(minIgnoreNone(a, b), a)
        a = None
        self.assertEqual(minIgnoreNone(a, b), b)
        a = 1
        b = None
        self.assertEqual(minIgnoreNone(a, b), a)
        a = None
        self.assertEqual(minIgnoreNone(a, b), None)

    def test_maxIgnoreNone(self):
        a = 1
        b = 2
        self.assertEqual(maxIgnoreNone(a, b), b)
        a = None
        self.assertEqual(maxIgnoreNone(a, b), b)
        a = 1
        b = None
        self.assertEqual(maxIgnoreNone(a, b), a)
        a = None
        self.assertEqual(maxIgnoreNone(a, b), None)

class TestLogger(unittest.TestCase):
    def setUp(self):
        self.iterLogger = IterationLogger()
        self.iteration = 0
        self.inputs = ['x1', 'x2']
        self.outputs = ['x3']
        self.other = []
        self.thetak = 10.0
        self.objk = 5.0
        self.params = [3, 5]
        self.verbosity = 1

    def tearDown(self):
        pass

    def test_newIteration(self):
        self.iterLogger.newIteration(self.iteration, self.inputs,
                                 self.outputs, self.other,
                                 self.thetak, self.objk,
                                 self.verbosity, 0, self.params)
        self.assertEqual(len(self.iterLogger.iterations), 1)

    # def test_printIteration(self):
    #     self.iterLogger.newIteration(self.iteration, self.inputs,
    #                              self.outputs, self.other,
    #                              self.thetak, self.objk,
    #                              self.verbosity, 0, self.params)
    #     OUTPUT = StringIO()
    #     with LoggingIntercept(OUTPUT, 'pyomo.contrib.trustregion'):
    #         self.iterLogger.printIteration(self.iteration, self.verbosity)
    #     self.assertIn('Iteration 0:', OUTPUT.getvalue())
