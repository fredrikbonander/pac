"""Unittests by Fredrik Bonander.

See:
https://groups.google.com/forum/?pli=1#!topic/appengine-ndb-discuss/SVXvyy3cnPU
"""

import unittest

from ndb import model, test_utils


class FredTests(test_utils.DatastoreTest):

  def test_1(self):
    class Ent1(model.Model):
      name = model.StringProperty()
    class Ent2(model.Model):
      age = model.StringProperty()

    ent = Ent1(name='fredrik')
    key = ent.put()

    ent2 = Ent2(parent=key, age='12')
    ent2.put()

    test_ent = Ent2.query(ancestor=key).get()
    self.assertEqual(test_ent.age, '12')


def main():
  unittest.main()

if __name__ == '__main__':
  main()

  