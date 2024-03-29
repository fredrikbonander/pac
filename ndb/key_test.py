"""Tests for key.py."""

import base64
import pickle
import unittest

from google.appengine.api import datastore_errors
from google.appengine.datastore import entity_pb

from . import eventloop, key, model, tasklets, test_utils

class KeyTests(test_utils.DatastoreTest):

  def testShort(self):
    k0 = key.Key('Kind', None)
    self.assertEqual(k0.flat(), ('Kind', None))
    k1 = key.Key('Kind', 1)
    self.assertEqual(k1.flat(), ('Kind', 1))
    k2 = key.Key('Parent', 42, 'Kind', 1)
    self.assertEqual(k2.flat(), ('Parent', 42, 'Kind', 1))

  def testFlat(self):
    flat = ('Kind', 1)
    pairs = tuple((flat[i], flat[i+1]) for i in xrange(0, len(flat), 2))
    k = key.Key(flat=flat)
    self.assertEqual(k.pairs(), pairs)
    self.assertEqual(k.flat(), flat)
    self.assertEqual(k.kind(), 'Kind')

  def testFlatLong(self):
    flat = ('Kind', 1, 'Subkind', 'foobar')
    pairs = tuple((flat[i], flat[i+1]) for i in xrange(0, len(flat), 2))
    k = key.Key(flat=flat)
    self.assertEqual(k.pairs(), pairs)
    self.assertEqual(k.flat(), flat)
    self.assertEqual(k.kind(), 'Subkind')

  def testSerialized(self):
    flat = ['Kind', 1, 'Subkind', 'foobar']
    r = entity_pb.Reference()
    r.set_app('_')
    e = r.mutable_path().add_element()
    e.set_type(flat[0])
    e.set_id(flat[1])
    e = r.mutable_path().add_element()
    e.set_type(flat[2])
    e.set_name(flat[3])
    serialized = r.Encode()
    urlsafe = base64.urlsafe_b64encode(r.Encode()).rstrip('=')

    k = key.Key(flat=flat)
    self.assertEqual(k.serialized(), serialized)
    self.assertEqual(k.urlsafe(), urlsafe)
    self.assertEqual(k.reference(), r)

    k = key.Key(urlsafe=urlsafe)
    self.assertEqual(k.serialized(), serialized)
    self.assertEqual(k.urlsafe(), urlsafe)
    self.assertEqual(k.reference(), r)

    k = key.Key(serialized=serialized)
    self.assertEqual(k.serialized(), serialized)
    self.assertEqual(k.urlsafe(), urlsafe)
    self.assertEqual(k.reference(), r)

    k = key.Key(reference=r)
    self.assertTrue(k.reference() is not r)
    self.assertEqual(k.serialized(), serialized)
    self.assertEqual(k.urlsafe(), urlsafe)
    self.assertEqual(k.reference(), r)

    k = key.Key(reference=r, app=r.app(), namespace='')
    self.assertTrue(k.reference() is not r)
    self.assertEqual(k.serialized(), serialized)
    self.assertEqual(k.urlsafe(), urlsafe)
    self.assertEqual(k.reference(), r)

    k1 = key.Key('A', 1)
    self.assertEqual(k1.urlsafe(), 'agFfcgcLEgFBGAEM')
    k2 = key.Key(urlsafe=k1.urlsafe())
    self.assertEqual(k1, k2)

  def testId(self):
    k1 = key.Key('Kind', 'foo', app='app1', namespace='ns1')
    self.assertEqual(k1.id(), 'foo')

    k2 = key.Key('Subkind', 42, parent=k1)
    self.assertEqual(k2.id(), 42)

    k3 = key.Key('Subkind', 'bar', parent=k2)
    self.assertEqual(k3.id(), 'bar')

    # incomplete key
    k4 = key.Key('Subkind', None, parent=k3)
    self.assertEqual(k4.id(), None)

  def testStringId(self):
    k1 = key.Key('Kind', 'foo', app='app1', namespace='ns1')
    self.assertEqual(k1.string_id(), 'foo')

    k2 = key.Key('Subkind', 'bar', parent=k1)
    self.assertEqual(k2.string_id(), 'bar')

    k3 = key.Key('Subkind', 42, parent=k2)
    self.assertEqual(k3.string_id(), None)

    # incomplete key
    k4 = key.Key('Subkind', None, parent=k3)
    self.assertEqual(k4.string_id(), None)

  def testIntegerId(self):
    k1 = key.Key('Kind', 42, app='app1', namespace='ns1')
    self.assertEqual(k1.integer_id(), 42)

    k2 = key.Key('Subkind', 43, parent=k1)
    self.assertEqual(k2.integer_id(), 43)

    k3 = key.Key('Subkind', 'foobar', parent=k2)
    self.assertEqual(k3.integer_id(), None)

    # incomplete key
    k4 = key.Key('Subkind', None, parent=k3)
    self.assertEqual(k4.integer_id(), None)

  def testParent(self):
    p = key.Key('Kind', 1, app='app1', namespace='ns1')
    self.assertEqual(p.parent(), None)

    k = key.Key('Subkind', 'foobar', parent=p)
    self.assertEqual(k.flat(), ('Kind', 1, 'Subkind', 'foobar'))
    self.assertEqual(k.parent(), p)

    k = key.Key('Subkind', 'foobar', parent=p,
                app=p.app(), namespace=p.namespace())
    self.assertEqual(k.flat(), ('Kind', 1, 'Subkind', 'foobar'))
    self.assertEqual(k.parent(), p)

  def testRoot(self):
    p = key.Key('Kind', 1, app='app1', namespace='ns1')
    self.assertEqual(p.root(), p)

    k = key.Key('Subkind', 'foobar', parent=p)
    self.assertEqual(k.flat(), ('Kind', 1, 'Subkind', 'foobar'))
    self.assertEqual(k.root(), p)

    k2 = key.Key('Subsubkind', 42, parent=k,
                app=p.app(), namespace=p.namespace())
    self.assertEqual(k2.flat(), ('Kind', 1,
                                 'Subkind', 'foobar',
                                 'Subsubkind', 42))
    self.assertEqual(k2.root(), p)

  def testRepr_Inferior(self):
    k = key.Key('Kind', 1L, 'Subkind', 'foobar')
    self.assertEqual(repr(k),
                     "Key('Kind', 1, 'Subkind', 'foobar')")
    self.assertEqual(repr(k), str(k))

  def testRepr_Toplevel(self):
    k = key.Key('Kind', 1)
    self.assertEqual(repr(k), "Key('Kind', 1)")

  def testRepr_Incomplete(self):
    k = key.Key('Kind', None)
    self.assertEqual(repr(k), "Key('Kind', None)")

  def testRepr_UnicodeKind(self):
    k = key.Key(u'\u1234', 1)
    self.assertEqual(repr(k), "Key('\\xe1\\x88\\xb4', 1)")

  def testRepr_UnicodeId(self):
    k = key.Key('Kind', u'\u1234')
    self.assertEqual(repr(k), "Key('Kind', '\\xe1\\x88\\xb4')")

  def testRepr_App(self):
    k = key.Key('Kind', 1, app='foo')
    self.assertEqual(repr(k), "Key('Kind', 1, app='foo')")

  def testRepr_Namespace(self):
    k = key.Key('Kind', 1, namespace='foo')
    self.assertEqual(repr(k), "Key('Kind', 1, namespace='foo')")

  def testUnicode(self):
    flat_input = (u'Kind\u1234', 1, 'Subkind', u'foobar\u4321')
    flat = (flat_input[0].encode('utf8'), flat_input[1],
            flat_input[2], flat_input[3].encode('utf8'))
    pairs = tuple((flat[i], flat[i+1]) for i in xrange(0, len(flat), 2))
    k = key.Key(flat=flat_input)
    self.assertEqual(k.pairs(), pairs)
    self.assertEqual(k.flat(), flat)
    # TODO: test these more thoroughly
    r = k.reference()
    serialized = k.serialized()
    urlsafe = k.urlsafe()
    key.Key(urlsafe=urlsafe.decode('utf8'))
    key.Key(serialized=serialized.decode('utf8'))
    key.Key(reference=r)
    # TODO: this may not make sense -- the protobuf utf8-encodes values
    r = entity_pb.Reference()
    r.set_app('_')
    e = r.mutable_path().add_element()
    e.set_type(flat_input[0])
    e.set_name(flat_input[3])
    k = key.Key(reference=r)
    self.assertEqual(k.reference(), r)

  def testHash(self):
    flat = ['Kind', 1, 'Subkind', 'foobar']
    pairs = [(flat[i], flat[i+1]) for i in xrange(0, len(flat), 2)]
    k = key.Key(flat=flat)
    self.assertEqual(hash(k), hash(tuple(pairs)))

  def testPickling(self):
    flat = ['Kind', 1, 'Subkind', 'foobar']
    pairs = [(flat[i], flat[i+1]) for i in xrange(0, len(flat), 2)]
    k = key.Key(flat=flat)
    for proto in range(pickle.HIGHEST_PROTOCOL + 1):
      s = pickle.dumps(k, protocol=proto)
      kk = pickle.loads(s)
      self.assertEqual(k, kk)

  def testIncomplete(self):
    k = key.Key(flat=['Kind', None])
    self.assertRaises(datastore_errors.BadArgumentError,
                      key.Key, flat=['Kind', None, 'Subkind', 1])
    self.assertRaises(AssertionError, key.Key, flat=['Kind', ()])

  def testKindFromModel(self):
    from . import model
    class M(model.Model):
      pass
    class N(model.Model):
      @classmethod
      def _get_kind(cls):
        return 'NN'
    k = key.Key(M, 1)
    self.assertEqual(k, key.Key('M', 1))
    k = key.Key('X', 1, N, 2, 'Y', 3)
    self.assertEqual(k, key.Key('X', 1, 'NN', 2, 'Y', 3))

  def testKindFromBadValue(self):
    # TODO: BadArgumentError
    self.assertRaises(Exception, key.Key, 42, 42)

  def testDeleteHooksCalled(self):
    test = self # Closure for inside hook
    self.pre_counter = 0
    self.post_counter = 0

    class HatStand(model.Model):
      @classmethod
      def _pre_delete_hook(cls, ctx, key):
        test.pre_counter += 1
      @classmethod
      def _post_delete_hook(cls, ctx, key):
        test.post_counter += 1

    furniture = HatStand()
    key = furniture.put()
    self.assertEqual(self.pre_counter, 0, 'Pre delete hook called early')
    key.delete()
    self.assertEqual(self.pre_counter, 1, 'Pre delete hook not called')
    self.assertEqual(self.post_counter, 0, 'Post delete hook called early')
    eventloop.get_event_loop().run()
    self.assertEqual(self.post_counter, 1, 'Post delete hook not called')

    # All counters now read 1, calling delete_multi for 10 keys makes this 11
    new_furniture = [HatStand() for _ in range(10)]
    keys = model.put_multi(new_furniture)
    model.delete_multi(keys)
    self.assertEqual(self.pre_counter, 11,
                     'Pre delete hooks not called on model.delete_multi')
    self.assertEqual(self.post_counter, 1,
                     'Post delete hooks called early on model.delete_multi')
    eventloop.get_event_loop().run()
    self.assertEqual(self.post_counter, 11,
                     'Post delete hooks not called on model.delete_multi')

  def test_issue_58_delete(self):
    ctx = tasklets.get_context()
    ctx.set_cache_policy(False)
    class EmptyModel(model.Model):
      pass
    entity = EmptyModel()
    entity.put()
    entity.key.delete()
    ev = eventloop.get_event_loop()
    ev.run0() # Trigger check_success
    ev_len = len(ev.queue)
    self.assertEqual(ev_len, 0,
                     'Delete hook queued default no-op: %r' % ev.queue)

  def testGetHooksCalled(self):
    test = self # Closure for inside hook
    self.pre_counter = 0
    self.post_counter = 0

    class HatStand(model.Model):
      @classmethod
      def _pre_get_hook(cls, ctx, key):
        test.pre_counter += 1
      @classmethod
      def _post_get_hook(cls, ctx, key):
        test.post_counter += 1

    furniture = HatStand()
    key = furniture.put()
    self.assertEqual(self.pre_counter, 0, 'Pre get hook called early')
    key.get()
    self.assertEqual(self.pre_counter, 1, 'Pre get hook not called')
    self.assertEqual(self.post_counter, 0, 'Post get hook called early')
    eventloop.get_event_loop().run()
    self.assertEqual(self.post_counter, 1, 'Post get hook not called')

    # All counters now read 1, calling get for 10 keys should make this 11
    new_furniture = [HatStand() for _ in range(10)]
    keys = model.put_multi(new_furniture)
    model.get_multi(keys)
    self.assertEqual(self.pre_counter, 11,
                     'Pre get hooks not called on model.get_multi')
    self.assertEqual(self.post_counter, 1,
                     'Post get hooks called early on model.get_multi')
    eventloop.get_event_loop().run()
    self.assertEqual(self.post_counter, 11,
                     'Post get hooks not called on model.get_multi')

  def testMonkeyPatchHooks(self):
    hook_attr_names = ('_pre_get_hook', '_post_get_hook',
                       '_pre_delete_hook', '_post_delete_hook')
    original_hooks = {}

    # Backup the original hooks
    for name in hook_attr_names:
      original_hooks[name] = getattr(model.Model, name)

    self.pre_get_flag = False
    self.post_get_flag = False
    self.pre_delete_flag = False
    self.post_delete_flag = False

    class HatStand(model.Model):
      @classmethod
      def _pre_get_hook(cls, ctx, key):
        self.pre_get_flag = True
      @classmethod
      def _post_get_hook(cls, ctx, key):
        self.post_get_flag = True
      @classmethod
      def _pre_delete_hook(cls, ctx, key):
        self.pre_delete_flag = True
      @classmethod
      def _post_delete_hook(cls, ctx, key):
        self.post_delete_flag = True

    # Monkey patch the hooks
    for name in hook_attr_names:
      hook = getattr(HatStand, name)
      setattr(model.Model, name, hook)

    try:
      key = HatStand().put()
      key.get()
      self.assertTrue(self.pre_get_flag,
                      'Pre get hook not called when model is monkey patched')
      eventloop.get_event_loop().run()
      self.assertTrue(self.post_get_flag,
                      'Post get hook not called when model is monkey patched')
      key.delete()
      self.assertTrue(self.pre_delete_flag,
                     'Pre delete hook not called when model is monkey patched')
      eventloop.get_event_loop().run()
      self.assertTrue(self.post_delete_flag,
                    'Post delete hook not called when model is monkey patched')
    finally:
      # Restore the original hooks
      for name in hook_attr_names:
        setattr(model.Model, name, original_hooks[name])

  def testPreHooksCannotCancelRPC(self):
    class Foo(model.Model):
      @classmethod
      def _pre_get_hook(*args):
        raise tasklets.Return()
      @classmethod
      def _pre_delete_hook(*args):
        raise tasklets.Return()
    entity = Foo()
    entity.put()
    self.assertRaises(tasklets.Return, entity.key.get)
    self.assertRaises(tasklets.Return, entity.key.delete)

  def test_issue_58_get(self):
    ctx = tasklets.get_context()
    ctx.set_cache_policy(False)
    class EmptyModel(model.Model):
      pass
    entity = EmptyModel()
    entity.put()
    entity.key.get()
    ev = eventloop.get_event_loop()
    ev.run0() # Trigger check_success
    ev_len = len(ev.queue)
    self.assertEqual(ev_len, 0,
                     'Get hook queued default no-op: %r' % ev.queue)


def main():
  unittest.main()

if __name__ == '__main__':
  main()
