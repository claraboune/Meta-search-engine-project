import unittest

from MetAPI.engine.abstractEngine import AbstractEngine

class AbstractEngineTest(unittest.TestCase):

    #@unittest.mock.patch.object(AbstractEngine, __abstractmethods__=set())
    def test(self):
        self.engine_instance = AbstractEngine()
