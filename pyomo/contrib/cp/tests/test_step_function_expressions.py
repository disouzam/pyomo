#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2008-2022
#  National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

import pyomo.common.unittest as unittest
from pyomo.contrib.cp import IntervalVar
from pyomo.contrib.cp.scheduling_expr import Step, Pulse
from pyomo.contrib.cp.scheduling_expr.step_function_expressions import (
    CumulativeFunction, NegatedStepFunction)

from pyomo.environ import ConcreteModel

from pytest import set_trace

class CommonTests(unittest.TestCase):
    def get_model(self):
        m = ConcreteModel()
        m.a = IntervalVar()
        m.b = IntervalVar()

        return m

class TestSumStepFunctions(CommonTests):
    def test_sum_step_and_pulse(self):
        m = self.get_model()
        expr = Step(m.a.start_time, height=4) + Pulse(m.b, height=-1)

        self.assertIsInstance(expr, CumulativeFunction)
        self.assertEqual(len(expr.args), 2)
        self.assertEqual(expr.nargs(), 2)
        self.assertIsInstance(expr.args[0], Step)
        self.assertIsInstance(expr.args[1], Pulse)

        self.assertEqual(str(expr), "Step(a.start_time, height=4) + "
                         "Pulse(b, height=-1)")

    def test_args_clone_correctly(self):
        m = self.get_model()
        expr = Step(m.a.start_time, height=4) + Pulse(m.b, height=-1)
        expr2 = expr + Step(m.b.end_time, height=4)

        self.assertIsInstance(expr2, CumulativeFunction)
        self.assertEqual(len(expr2.args), 3)
        self.assertEqual(expr2.nargs(), 3)
        self.assertIsInstance(expr2.args[0], Step)
        self.assertIsInstance(expr2.args[1], Pulse)
        self.assertIsInstance(expr2.args[2], Step)

        # This will force expr to clone its arguments because it did the
        # appending trick to make expr2.
        expr3 = expr + Pulse(m.b, height=-5)

        self.assertIsInstance(expr3, CumulativeFunction)
        self.assertEqual(len(expr3.args), 3)
        self.assertEqual(expr3.nargs(), 3)
        self.assertIsInstance(expr3.args[0], Step)
        self.assertIsInstance(expr3.args[1], Pulse)
        self.assertIsInstance(expr3.args[2], Pulse)

    def test_sum_two_pulses(self):
        pass

    def test_sum_in_place(self):
        m = self.get_model()
        expr = Step(m.a.start_time, height=4) + Pulse(m.b, height=-1)
        expr += Step(0, 1)

        self.assertEqual(len(expr.args), 3)
        self.assertEqual(expr.nargs(), 3)
        self.assertIsInstance(expr.args[0], Step)
        self.assertIsInstance(expr.args[1], Pulse)
        self.assertIsInstance(expr.args[2], Step)

        self.assertEqual(str(expr), "Step(a.start_time, height=4) + "
                         "Pulse(b, height=-1) + Step(0, height=1)")

    def test_sum_pulses_in_place(self):
        m = self.get_model()
        p1 = Pulse(m.a, height=2)
        expr = p1

        self.assertEqual(len(expr.args), 1)
        self.assertEqual(expr.nargs(), 1)

        p2 = Pulse(m.b, height=3)
        expr += p2

        self.assertIsInstance(expr, CumulativeFunction)
        self.assertEqual(len(expr.args), 2)
        self.assertEqual(expr.nargs(), 2)
        self.assertIs(expr.args[0], p1)
        self.assertIs(expr.args[1], p2)

    def test_sum_steps_in_place(self):
        m = self.get_model()
        s1 = Step(m.a.end_time, height=2)
        expr = s1

        self.assertIsInstance(expr, Step)
        self.assertEqual(len(expr.args), 1)
        self.assertEqual(expr.nargs(), 1)

        s2 = Pulse(m.b.end_time, height=3)
        expr += s2

        self.assertIsInstance(expr, CumulativeFunction)
        self.assertEqual(len(expr.args), 2)
        self.assertEqual(expr.nargs(), 2)
        self.assertIs(expr.args[0], s1)
        self.assertIs(expr.args[1], s2)

    def test_sum_pulses_in_place(self):
        m = self.get_model()
        p1 = Pulse(m.a, height=2)
        expr = p1

        self.assertIsInstance(expr, Pulse)
        self.assertEqual(len(expr.args), 1)
        self.assertEqual(expr.nargs(), 1)

        p2 = Pulse(m.b, height=3)
        expr += p2

        self.assertIsInstance(expr, CumulativeFunction)
        self.assertEqual(len(expr.args), 2)
        self.assertEqual(expr.nargs(), 2)
        self.assertIs(expr.args[0], p1)
        self.assertIs(expr.args[1], p2)

    def test_cannot_add_constant(self):
        m = self.get_model()
        with self.assertRaisesRegexp(
                TypeError,
                "Cannot add object of class <class 'int'> to object of class "
                "<class 'pyomo.contrib.cp.scheduling_expr."
                "step_function_expressions.Step'>"):
            expr = Step(m.a.start_time, height=6) + 3

    def test_cannot_add_to_constant(self):
        m = self.get_model()
        with self.assertRaisesRegexp(
                TypeError,
                "Cannot add object of class <class 'pyomo.contrib.cp."
                "scheduling_expr.step_function_expressions.Step'> to object "
                "of class <class 'int'>"):
            expr = 4 + Step(m.a.start_time, height=6)

class TestSubtractStepFunctions(CommonTests):
    def test_subtract_two_steps(self):
        m = self.get_model()

        s = Step(m.a, height=2) - Step(m.b, height=5)

        self.assertIsInstance(s, CumulativeFunction)
        self.assertEqual(len(s.args), 2)
        self.assertEqual(s.nargs(), 2)
        self.assertIsInstance(s.args[0], Step)
        self.assertIsInstance(s.args[1], NegatedStepFunction)
        self.assertEqual(len(s.args[1].args), 1)
        self.assertEqual(s.args[1].nargs(), 1)
        self.assertIsInstance(s.args[1].args[0], Step)

    def test_subtract_step_and_pulse(self):
        m = self.get_model()
        s1 = Step(m.a.end_time, height=2)
        s2 = Step(m.b.start_time, height=5)
        p = Pulse(m.a.end_time, height=3)

        expr = s1 - s2 - p

        self.assertIsInstance(expr, CumulativeFunction)
        self.assertEqual(len(expr.args), 3)
        self.assertEqual(expr.nargs(), 3)
        self.assertIs(expr.args[0], s1)
        self.assertIsInstance(expr.args[1], NegatedStepFunction)
        self.assertIs(expr.args[1].args[0], s2)
        self.assertIsInstance(expr.args[2], NegatedStepFunction)
        self.assertIs(expr.args[2].args[0], p)

    def test_subtract_pulse_from_two_steps(self):
        m = self.get_model()
        s1 = Step(m.a.end_time, height=2)
        s2 = Step(m.b.start_time, height=5)
        p = Pulse(m.a, height=3)

        expr = s1 + s2 - p
        self.assertIsInstance(expr, CumulativeFunction)
        self.assertEqual(len(expr.args), 3)
        self.assertEqual(expr.nargs(), 3)
        self.assertIs(expr.args[0], s1)
        self.assertIs(expr.args[1], s2)
        self.assertIsInstance(expr.args[2], NegatedStepFunction)
        self.assertIs(expr.args[2].args[0], p)

    def test_subtract_pulses_in_place(self):
        m = self.get_model()
        p1 = Pulse(m.a, height = 1)
        p2 = Pulse(m.b, height = 3)

        expr = p1
        expr -= p2

        self.assertIsInstance(expr, CumulativeFunction)
        self.assertEqual(len(expr.args), 2)
        self.assertEqual(expr.nargs(), 2)
        self.assertIs(expr.args[0], p1)
        self.assertIsInstance(expr.args[1], NegatedStepFunction)
        self.assertIs(expr.args[1].args[0], p2)

    def test_subtract_steps_in_place(self):
        m = self.get_model()
        s1 = Pulse(m.a.start_time, height = 1)
        s2 = Pulse(m.b.end_time, height = 3)

        expr = s1
        expr -= s2

        self.assertIsInstance(expr, CumulativeFunction)
        self.assertEqual(len(expr.args), 2)
        self.assertEqual(expr.nargs(), 2)
        self.assertIs(expr.args[0], s1)
        self.assertIsInstance(expr.args[1], NegatedStepFunction)
        self.assertIs(expr.args[1].args[0], s2)

    def test_cannot_subtract_constant(self):
        m = self.get_model()
        with self.assertRaisesRegexp(
                TypeError,
                "Cannot subtract object of class <class 'int'> from object of "
                "class <class 'pyomo.contrib.cp."
                "scheduling_expr.step_function_expressions.Step'>"):
            expr = Step(m.a.start_time, height=6) - 3

    def test_cannot_subtract_from_constant(self):
        m = self.get_model()
        with self.assertRaisesRegexp(
                TypeError,
                "Cannot subtract object of class <class 'pyomo.contrib.cp."
                "scheduling_expr.step_function_expressions.Step'> from object "
                "of class <class 'int'>"):
            expr = 3 - Step(m.a.start_time, height=6)
