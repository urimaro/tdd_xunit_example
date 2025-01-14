class TestResult:
    def __init__(self):
        self.runCount = 0
        self.errorCount = 0

    def testStarted(self):
        self.runCount = self.runCount + 1

    def testFailed(self):
        self.errorCount = self.errorCount + 1

    def summary(self):
        return "%d run, %d failed" % (self.runCount, self.errorCount)

class TestCase:
    def __init__(self, name):
        self.name = name

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def run(self, result):
        result.testStarted()
        try:
            self.setUp()
            method = getattr(self, self.name)
            method()
        except:
            result.testFailed()
        self.tearDown()

class TestSuite:
    def __init__(self, clazz = None):
        self.tests = []

        if clazz:
            for name in self.testMethodNames(clazz):
                self.tests.append(clazz(name))

    def testMethodNames(self, clazz):
        subclass_method_names = dir(clazz)
        testcase_method_names = dir(TestCase)
        return set(subclass_method_names) - set(testcase_method_names)

    def add(self, test):
        self.tests.append(test)

    def run(self, result):
        for test in self.tests:
            test.run(result)

class WasRun(TestCase):
    def setUp(self):
        self.log = "setUp "

    def testMethod(self):
        self.log = self.log + "testMethod "

    def testBrokenMethod(self):
        raise Exception

    def tearDown(self):
        self.log = self.log + "tearDown "

class SetupFailed(TestCase):
    def setUp(self):
        raise Exception

    def testMethod(self):
        pass

class TestCaseTest(TestCase):
    def setUp(self):
        self.result = TestResult()

    def testTemplateMethod(self):
        test = WasRun("testMethod")
        test.run(self.result)
        assert("setUp testMethod tearDown " == test.log)

    def testResult(self):
        test = WasRun("testMethod")
        test.run(self.result)
        assert("1 run, 0 failed" == self.result.summary())

    def testFailedResult(self):
        test = WasRun("testBrokenMethod")
        test.run(self.result)
        assert("1 run, 1 failed" == self.result.summary())

    def testFailedResultFormatting(self):
        self.result.testStarted()
        self.result.testFailed()
        assert("1 run, 1 failed" == self.result.summary())

    def testSuite(self):
        suite = TestSuite()
        suite.add(WasRun("testMethod"))
        suite.add(WasRun("testBrokenMethod"))
        suite.run(self.result)
        assert("2 run, 1 failed" == self.result.summary())

    def testFailedSetupResult(self):
        test = SetupFailed("testMethod")
        test.run(self.result)
        assert("1 run, 1 failed" == self.result.summary())

    def testFailedLog(self):
        test = WasRun("testBrokenMethod")
        test.run(self.result)
        assert("tearDown " in test.log)

    def testSuiteFromTestCase(self):
        suite = TestSuite(WasRun)
        suite.run(self.result)
        assert("2 run, 1 failed" == self.result.summary())

    def testChildMethods(self):
        test = WasRun("testMethod")
        subclass_method_names = dir(type(test))
        testcase_method_names = dir(TestCase)
        diff = set(subclass_method_names) - set(testcase_method_names)
        assert({'testBrokenMethod', 'testMethod'} == diff)

    def testPassClassToConstructor(self):
        test = TestSuite(WasRun)
        assert(2 == len(test.tests))

suite = TestSuite(TestCaseTest)
result = TestResult()
suite.run(result)
print(result.summary())
