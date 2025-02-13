from plone.protect.testing import PROTECT_FUNCTIONAL_TESTING
from plone.protect.utils import addTokenToUrl
from plone.protect.utils import protect
from unittest import defaultTestLoader
from unittest import TestCase
from unittest import TestSuite

import unittest


def funcWithoutRequest():
    pass


def funcWithRequest(one, two, REQUEST=None):
    return (one, two)


class DummyChecker:
    def __call__(self, request):
        self.request = request


class DecoratorTests(TestCase):
    def testFunctionMustHaveRequest(self):
        protector = protect()
        self.assertRaises(ValueError, protector, funcWithoutRequest)

    def testArgumentsPassed(self):
        wrapped = protect()(funcWithRequest)
        self.assertEqual(wrapped("one", "two"), ("one", "two"))

    def testKeywordArguments(self):
        wrapped = protect()(funcWithRequest)
        self.assertEqual(wrapped(one="one", two="two"), ("one", "two"))

    def testMixedArguments(self):
        wrapped = protect()(funcWithRequest)
        self.assertEqual(wrapped("one", two="two"), ("one", "two"))

    def testRequestPassedToChecker(self):
        checker = DummyChecker()
        wrapped = protect(checker)(funcWithRequest)
        request = []
        wrapped("one", "two", request)
        self.assertTrue(checker.request is request)


class UrlTests(unittest.TestCase):
    layer = PROTECT_FUNCTIONAL_TESTING

    def testWithUrlFromSameDomain(self):
        url = addTokenToUrl("http://nohost/foobar", self.layer["request"])
        self.assertTrue("_authenticator=" in url)

    def testWithUrlFromOtherDomain(self):
        url = addTokenToUrl("http://other/foobar", self.layer["request"])
        self.assertTrue("_authenticator=" not in url)

    def testAddingWithQueryParams(self):
        url = addTokenToUrl("http://nohost/foobar?foo=bar", self.layer["request"])
        self.assertTrue("_authenticator=" in url)

    def testWithoutRequest(self):
        url = addTokenToUrl("http://nohost/foobar")
        self.assertTrue("_authenticator=" in url)

    def testWithNone(self):
        url = addTokenToUrl(None, self.layer["request"])
        self.assertTrue(not url)


def test_suite():
    return TestSuite(
        (
            defaultTestLoader.loadTestsFromTestCase(DecoratorTests),
            defaultTestLoader.loadTestsFromTestCase(UrlTests),
        )
    )
