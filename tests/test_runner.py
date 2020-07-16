import unittest

import tests

baseTestSuite = unittest.TestSuite()
baseTestSuite.addTest(unittest.makeSuite(tests.UtilsTest))
baseTestSuite.addTests(unittest.makeSuite(tests.ZohoSimpleAPITests))

runner = unittest.TextTestRunner(verbosity=2)
runner.run(baseTestSuite)
