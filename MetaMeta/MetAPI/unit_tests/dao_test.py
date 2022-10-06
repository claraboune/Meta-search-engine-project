import unittest

from MetAPI.DAO.cache import Cache

class DAOTest(unittest.TestCase):

    def test_put(self):
        c = Cache()
        c.put("Aristote","La poétique")
        r = c.get("Aristote","127.0.0.1")
        self.assertEqual(r[0]["results"], 'La poétique')

    def test_get(self):
        c=Cache()
        c.put("Sagan","Bonjour tristesse")
        r=c.get("Sagan","127.0.0.1")
        self.assertEqual(r[0]["results"], 'Bonjour tristesse')

    def test_purge(self):
        """ not a good idea to test purge
        you don't want to purge cache on
        testing purpose """
        pass