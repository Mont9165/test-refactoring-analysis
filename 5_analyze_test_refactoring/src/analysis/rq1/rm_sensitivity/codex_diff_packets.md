## Row 1
commit_url: https://github.com/virtualsatellite/VirtualSatellite4-Core/commit/730abe93f6b064e8a9998a9324f3ccdfda869c01
rm_type: Change Return Type
rm_description: Change Return Type TestStructuralElement to IBeanStructuralElementInstance in method public createSei(name String) : IBeanStructuralElementInstance from class de.dlr.sc.virsat.performance.PerformanceTest.StudyGenerator
file_path: de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java
left_side: [{"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 105, "endLine": 105, "startColumn": 9, "endColumn": 30, "codeElementType": "TYPE", "description": "original return type", "codeElement": "TestStructuralElement"}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 99, "endLine": 110, "startColumn": 2, "endColumn": 3, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public createSE(name String) : TestStructuralElement"}]
right_side: [{"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 337, "endLine": 337, "startColumn": 10, "endColumn": 40, "codeElementType": "TYPE", "description": "changed return type", "codeElement": "IBeanStructuralElementInstance"}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 337, "endLine": 341, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "method declaration with changed return type", "codeElement": "public createSei(name String) : IBeanStructuralElementInstance"}]

### Patch: de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java
```diff
@@ -26,7 +26,6 @@
 import org.eclipse.core.runtime.CoreException;
 import org.eclipse.emf.common.util.EList;
 import org.junit.AfterClass;
-import org.junit.Before;
 import org.junit.BeforeClass;
 import org.junit.Test;
 import org.junit.runner.RunWith;
@@ -36,6 +35,7 @@
 
 import de.dlr.sc.virsat.apps.api.external.ModelAPI;
 import de.dlr.sc.virsat.concept.unittest.util.test.AConceptProjectTestCase;
+import de.dlr.sc.virsat.model.concept.types.structural.IBeanStructuralElementInstance;
 import de.dlr.sc.virsat.model.dvlm.categories.CategoryAssignment;
 import de.dlr.sc.virsat.model.dvlm.concepts.Concept;
 import de.dlr.sc.virsat.model.dvlm.structural.StructuralElementInstance;
@@ -51,7 +51,21 @@ public class PerformanceTest extends AConceptProjectTestCase {
     public static final int MIN_STUDY_SIZE = 200;
     public static final int MAX_STUDY_SIZE = 10000;
     public static final int STUDY_SIZE_INCREASE_STEP = 200;
-    
+
+	protected ModelAPI modelAPI;
+	protected Concept testConcept;
+
+    /**
+	 * (Study size -> (Measure -> Elapsed Time))
+     */
+    protected static Map<Integer, Map<String, Long>> performanceMeasures;
+
+	/**
+	 * For injecting parameters of a parameterized test
+	 */
+	@Parameter
+	public int testNumberOfElements;
+
     /**
      * Collection of study sizes for parameterized test. These values will be injected into field testNumberOfElements
      * @return collection of arrays of size one containing study sizes
@@ -65,20 +79,7 @@ public static Collection<Object[]> data() {
         return studySizes;
     }
 
-	/*
-	 * (Study size -> (Measure -> Elapsed Time))
-	 */
-	private static Map<Integer, Map<String, Long>> performanceMeasures;
-	
-	private ModelAPI modelAPI;
-	private Concept testConcept;
-
 	@Override
-	public void initializeTimeOutRule() {
-		// No timeout
-	}
-	
-	@Before
 	public void setUp() throws CoreException {
 		super.setUp();
 		addEditingDomainAndRepository();
@@ -96,45 +97,29 @@ public String getCurrentProjectAbsolutePath() {
 		};
 	}
 
-	/**
-	 * method to create new structural element
-	 * @param name name of the structural element
-	 * @return structural element
-	 * @throws IOException 
-	 */
-	public TestStructuralElement createSE(String name) throws IOException {
-		TestStructuralElement se = new TestStructuralElement(testConcept);
-		se.setName(name);
-		modelAPI.createSeiStorage(se);
-		return se;
+	@Override
+	public void initializeTimeOutRule() {
+		// No timeout
 	}
 
-	@Parameter
-	//CHECKSTYLE:OFF
-	// For injecting parameters of a parameterized test
-	public int testNumberOfElements;
-	//CHECKSTYLE:ON
-	
 	/**
-	 * Before the tests are executed prepare a storage for timing of all tests
+	 * Prepare storage for timing results of all tests
 	 */
 	@BeforeClass
 	public static void init() {
 		performanceMeasures = new LinkedHashMap<>();
 	}
 	
 	/**
-	 * Logs a performance measurement result
+	 * After the tests are executed write the test timings into a file
+	 * @throws IOException 
 	 */
-	private void logTime(String measure, long value) {
-		if (!performanceMeasures.containsKey(testNumberOfElements)) {
-			performanceMeasures.put(testNumberOfElements, new LinkedHashMap<>());
-		}
-		assertFalse("No duplicate measures", performanceMeasures.get(testNumberOfElements).containsKey(measure));
-		performanceMeasures.get(testNumberOfElements).put(measure, value);
+	@AfterClass
+	public static void end() throws IOException {
+		Files.write(Paths.get("performanceTestReport.csv"), getPerformanceReportCsv());
 	}
 
-	private static List<String> getPerformanceReportCsv() {
+	protected static List<String> getPerformanceReportCsv() {
 		List<String> result = new ArrayList<>();
 		List<String> measures = new ArrayList<>(performanceMeasures.get(MIN_STUDY_SIZE).keySet());
 		String header = "Number of elements," + String.join(",", measures);
@@ -151,20 +136,27 @@ private static List<String> getPerformanceReportCsv() {
 		return result;
 	}
 
-	/**
-	 * After the tests are executed write the test timings into a file
-	 * @throws IOException 
-	 */
-	@AfterClass
-	public static void end() throws IOException {
-		Files.write(Paths.get("performanceTestReport.csv"), getPerformanceReportCsv());
-	}
-	
+
 	@Test
 	public final void testSaveAndLoad() throws CoreException, IOException {
 		long start = System.currentTimeMillis();
-		
-		generateRandomTreeWithReferences(testNumberOfElements);
+
+		// Add a category with random values to all SEIs
+		new StudyGenerator() {
+			
+			@Override
+			public IBeanStructuralElementInstance createSei(String name) {
+				IBeanStructuralElementInstance sei = super.createSei(name);
+
+				TestCategoryBase cat = new TestCategoryBase(testConcept);
+				cat.setTestBaseProperty(ThreadLocalRandom.current().nextInt());
+				cat.setTestReference(getRandomPreviousSei().getFirst(TestCategoryBase.class));
+
+				sei.add(cat);
+				return sei;
+			}
+		}
+		.generate();
 		
 		long timestampCreated = System.currentTimeMillis();
 		modelAPI.performInheritance();
@@ -186,7 +178,29 @@ public final void testSaveAndLoad() throws CoreException, IOException {
 
 	@Test
 	public final void testInheritance() throws CoreException, IOException {
-		generateRandomTreeWithInheritance(testNumberOfElements);
+
+		// Add random inheritance to the generated SEIs, and a CA only to the root SEI
+		new StudyGenerator() {
+			
+			public IBeanStructuralElementInstance createRootSei(String name) {
+				IBeanStructuralElementInstance sei = super.createSei(name);
+
+				TestCategoryBase cat = new TestCategoryBase(testConcept);
+				cat.setTestBaseProperty(ThreadLocalRandom.current().nextInt());
+				cat.setTestReference((TestCategoryBase) getRandomPreviousSei());
+				sei.add(cat);
+
+				return sei;
+			};
+			
+			public IBeanStructuralElementInstance createSei(String name) {
+				IBeanStructuralElementInstance sei = super.createSei(name);
+				IBeanStructuralElementInstance superSei = getRandomPreviousSei();
+				sei.addSuperSei(superSei);
+				return sei;
+			}
+		}
+		.generate();
 		
 		long timestampCreated = System.currentTimeMillis();
 		modelAPI.performInheritance();
@@ -212,44 +226,57 @@ public final void testInheritance() throws CoreException, IOException {
 		logTime("Reload With Inheritance", timestampAllLoaded - timestampAllSaved);
 	}
 	
+		
 	/**
-	 * Make sure that after changing random inheritance parameters some values are different
-	 * from root super SEI value
+	 * Logs a performance measurement result
 	 */
-	private void assertNotAllSeisHaveSameInheritedValue() {
+	private void logTime(String measure, long value) {
+		if (!performanceMeasures.containsKey(testNumberOfElements)) {
+			performanceMeasures.put(testNumberOfElements, new LinkedHashMap<>());
+		}
+		assertFalse("No duplicate measures", performanceMeasures.get(testNumberOfElements).containsKey(measure));
+		performanceMeasures.get(testNumberOfElements).put(measure, value);
+	}
+	
+
+	/**
+	 * Make sure that all SEIs have inherited the same value from root super SEI
+	 */
+	private void assertAllSeisHaveSameInheritedValue() {
 		TestStructuralElement rootSei = modelAPI.getRootSeis(TestStructuralElement.class).get(0);
 		TestCategoryBase rootCat = rootSei.getAll(TestCategoryBase.class).get(0);
 		long rootValue = rootCat.getTestBaseProperty();
 		EList<StructuralElementInstance> allInherited = rootSei.getStructuralElementInstance().getDeepChildren();
 		assertEquals(testNumberOfElements - 1, allInherited.size());
-		boolean differentValue = false;
 		for (StructuralElementInstance sei : allInherited) {
 			assertEquals(1, sei.getCategoryAssignments().size());
 			CategoryAssignment ca = sei.getCategoryAssignments().get(0);
 			TestCategoryBase caBean = new TestCategoryBase(ca);
-			if (rootValue != caBean.getTestBaseProperty()) {
-				differentValue = true;
-				break;
-			}
+			assertEquals(rootValue, caBean.getTestBaseProperty());
 		}
-		assertTrue(differentValue);
 	}
 
 	/**
-	 * Make sure that all SEIs have inherited the same value from root super SEI
+	 * Make sure that after changing random inheritance parameters some values are different
+	 * from root super SEI value
 	 */
-	private void assertAllSeisHaveSameInheritedValue() {
+	private void assertNotAllSeisHaveSameInheritedValue() {
 		TestStructuralElement rootSei = modelAPI.getRootSeis(TestStructuralElement.class).get(0);
 		TestCategoryBase rootCat = rootSei.getAll(TestCategoryBase.class).get(0);
 		long rootValue = rootCat.getTestBaseProperty();
 		EList<StructuralElementInstance> allInherited = rootSei.getStructuralElementInstance().getDeepChildren();
 		assertEquals(testNumberOfElements - 1, allInherited.size());
+		boolean differentValue = false;
 		for (StructuralElementInstance sei : allInherited) {
 			assertEquals(1, sei.getCategoryAssignments().size());
 			CategoryAssignment ca = sei.getCategoryAssignments().get(0);
 			TestCategoryBase caBean = new TestCategoryBase(ca);
-			assertEquals(rootValue, caBean.getTestBaseProperty());
+			if (rootValue != caBean.getTestBaseProperty()) {
+				differentValue = true;
+				break;
+			}
 		}
+		assertTrue(differentValue);
 	}
 
 	private void changeRandomInheritanceParameters() {
@@ -292,60 +319,55 @@ public void assertProjectHasElements() {
 		}
 		assertEquals(testNumberOfElements, elementCount);
 	}
-	
-	
+
+
 	/**
-	 * method to create random tree with structural element
-	 * @param n size of the tree
-	 * @throws IOException 
+	 * Generator of a study for the test cases
 	 */
-	private void generateRandomTreeWithReferences(int n) throws IOException {
-		TestStructuralElement root = createSE("root");
-		TestCategoryBase cat = new TestCategoryBase(testConcept);
-		cat.setTestBaseProperty(ThreadLocalRandom.current().nextInt());
-		root.add(cat);
-		modelAPI.addRootSei(root);
-		List<TestStructuralElement> allElements = new ArrayList<>();
-		allElements.add(root);
-		for (int i = 0; i < n - 1; i++) {
-			TestStructuralElement newElement = createSE("element_" + (i + 1));
-			TestStructuralElement parent = allElements.get(ThreadLocalRandom.current().nextInt(allElements.size()));
-			parent.add(newElement);
-
-			TestStructuralElement referenceTo = allElements.get(ThreadLocalRandom.current().nextInt(allElements.size()));
-			TestCategoryBase referencedCa = referenceTo.getAll(TestCategoryBase.class).get(0);
-			cat = new TestCategoryBase(testConcept);
-			cat.setTestBaseProperty(ThreadLocalRandom.current().nextInt());
-			cat.setTestReference(referencedCa);
-			newElement.add(cat);
-			
-			allElements.add(newElement);
+	class StudyGenerator {
+		protected List<IBeanStructuralElementInstance> addedElements;
+
+
+		public IBeanStructuralElementInstance createRootSei(String name) {
+			TestStructuralElement sei = new TestStructuralElement(testConcept);
+			sei.setName(name);
+			return sei;
 		}
-	}
 
-	/**
-	 * method to create random tree with inheritance
-	 * @param n size of the tree
-	 * @throws IOException 
-	 */
-	private void generateRandomTreeWithInheritance(int n) throws IOException {
-		TestStructuralElement root = createSE("root");
-		TestCategoryBase cat = new TestCategoryBase(testConcept);
-		cat.setTestBaseProperty(ThreadLocalRandom.current().nextInt());
-		root.add(cat);
-		modelAPI.addRootSei(root);
-		List<TestStructuralElement> allElements = new ArrayList<>();
-		allElements.add(root);
-		for (int i = 0; i < n - 1; i++) {
-			TestStructuralElement newElement = createSE("element_" + (i + 1));
-			TestStructuralElement parent = allElements.get(ThreadLocalRandom.current().nextInt(allElements.size()));
-			parent.add(newElement);
-
-			TestStructuralElement inheritsFrom = allElements.get(ThreadLocalRandom.current().nextInt(allElements.size()));
-			newElement.addSuperSei(inheritsFrom);
+		public IBeanStructuralElementInstance createSei(String name) {
+			TestStructuralElement se = new TestStructuralElement(testConcept);
+			se.setName(name);
+			return se;
+		}
+		
+		public void generate() throws IOException {
+			addedElements = new ArrayList<>();
+
+			IBeanStructuralElementInstance root = createRootSei("root");
+			modelAPI.createSeiStorage(root);
+			modelAPI.addRootSei(root);
+			addedElements.add(root);
+
+			for (int i = 0; i < testNumberOfElements - 1; i++) {
+				IBeanStructuralElementInstance newElement = createSei("element_" + (i + 1));
+				modelAPI.createSeiStorage(newElement);
+
+				IBeanStructuralElementInstance parent = getRandomPreviousSei();
+				parent.add(newElement);
+
+				addedElements.add(newElement);
+			}
 			
-			allElements.add(newElement);
+		}
+		
+		/**
+		 * @return one of previously generated SEIs or null if nothing has been generated yet
+		 */
+		public IBeanStructuralElementInstance getRandomPreviousSei() {
+			if (addedElements.isEmpty()) {
+				return null;
+			}
+			return addedElements.get(ThreadLocalRandom.current().nextInt(addedElements.size()));
 		}
 	}
-
 }
```

## Row 2
commit_url: https://github.com/flightstats/hub/commit/20351c7f6fc61a453fd9d956205df0eb712af15b
rm_type: Inline Variable
rm_description: Inline Variable attempt : DeliveryAttempt in method public testShouldGiveUpIf() : void from class com.flightstats.hub.webhook.WebhookRetryerTest
file_path: src/test/java/com/flightstats/hub/webhook/WebhookRetryerTest.java
left_side: [{"filePath": "src/test/java/com/flightstats/hub/webhook/WebhookRetryerTest.java", "startLine": 23, "endLine": 23, "startColumn": 25, "endColumn": 68, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "inlined variable declaration", "codeElement": "attempt : DeliveryAttempt"}, {"filePath": "src/test/java/com/flightstats/hub/webhook/WebhookRetryerTest.java", "startLine": 25, "endLine": 25, "startColumn": 9, "endColumn": 51, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement with the name of the inlined variable", "codeElement": null}]
right_side: [{"filePath": "src/test/java/com/flightstats/hub/webhook/WebhookRetryerTest.java", "startLine": 25, "endLine": 25, "startColumn": 9, "endColumn": 77, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement with the initializer of the inlined variable", "codeElement": null}]

### Patch: src/test/java/com/flightstats/hub/webhook/WebhookRetryerTest.java
```diff
@@ -12,76 +12,50 @@
 
 public class WebhookRetryerTest {
 
+    private List<Predicate<DeliveryAttempt>> giveUpIfs = new ArrayList<>();
+    private List<Predicate<DeliveryAttempt>> tryLaterIfs = new ArrayList<>();
+    private int connectTimeoutSeconds = 10;
+    private int readTimeoutSeconds = 10;
+    private WebhookError webhookError = mock(WebhookError.class);
+
     @Test
     public void testShouldGiveUpIf() {
-        List<Predicate<DeliveryAttempt>> giveUpIfs = new ArrayList<>();
         giveUpIfs.add(attempt -> true);
-        List<Predicate<DeliveryAttempt>> tryLaterIfs = new ArrayList<>();
-        int timeoutSeconds = 10;
-        WebhookError webhookError = mock(WebhookError.class);
-        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, timeoutSeconds, webhookError);
-        DeliveryAttempt attempt = DeliveryAttempt.builder().build();
-
-        assertTrue(retryer.shouldGiveUp(attempt));
+        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, connectTimeoutSeconds, readTimeoutSeconds, webhookError);
+        assertTrue(retryer.shouldGiveUp(DeliveryAttempt.builder().build()));
     }
 
     @Test
     public void testShouldTryLaterIf() {
-        List<Predicate<DeliveryAttempt>> giveUpIfs = new ArrayList<>();
-        List<Predicate<DeliveryAttempt>> tryLaterIfs = new ArrayList<>();
         tryLaterIfs.add(attempt -> true);
-        int timeoutSeconds = 10;
-        WebhookError webhookError = mock(WebhookError.class);
-        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, timeoutSeconds, webhookError);
-        DeliveryAttempt attempt = DeliveryAttempt.builder().build();
-
-        assertTrue(retryer.shouldTryLater(attempt));
+        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, connectTimeoutSeconds, readTimeoutSeconds, webhookError);
+        assertTrue(retryer.shouldTryLater(DeliveryAttempt.builder().build()));
     }
 
     @Test
     public void testDetermineResultFromStatusCode() {
-        List<Predicate<DeliveryAttempt>> giveUpIfs = new ArrayList<>();
-        List<Predicate<DeliveryAttempt>> tryLaterIfs = new ArrayList<>();
-        int timeoutSeconds = 10;
-        WebhookError webhookError = mock(WebhookError.class);
-        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, timeoutSeconds, webhookError);
-
+        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, connectTimeoutSeconds, readTimeoutSeconds, webhookError);
         assertEquals("200 OK", retryer.determineResult(DeliveryAttempt.builder().statusCode(200).build()));
         assertEquals("400 Bad Request", retryer.determineResult(DeliveryAttempt.builder().statusCode(400).build()));
     }
 
     @Test
     public void testDetermineResultFromException() {
-        List<Predicate<DeliveryAttempt>> giveUpIfs = new ArrayList<>();
-        List<Predicate<DeliveryAttempt>> tryLaterIfs = new ArrayList<>();
-        int timeoutSeconds = 10;
-        WebhookError webhookError = mock(WebhookError.class);
-        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, timeoutSeconds, webhookError);
-
+        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, connectTimeoutSeconds, readTimeoutSeconds, webhookError);
         assertEquals("java.lang.NullPointerException: something", retryer.determineResult(DeliveryAttempt.builder().exception(new NullPointerException("something")).build()));
     }
 
     @Test
     public void testIsSuccessful() {
-        List<Predicate<DeliveryAttempt>> giveUpIfs = new ArrayList<>();
-        List<Predicate<DeliveryAttempt>> tryLaterIfs = new ArrayList<>();
-        int timeoutSeconds = 10;
-        WebhookError webhookError = mock(WebhookError.class);
-        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, timeoutSeconds, webhookError);
-
+        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, connectTimeoutSeconds, readTimeoutSeconds, webhookError);
         assertTrue(retryer.isSuccessful(DeliveryAttempt.builder().statusCode(200).build()));
         assertTrue(retryer.isSuccessful(DeliveryAttempt.builder().statusCode(201).build()));
         assertTrue(retryer.isSuccessful(DeliveryAttempt.builder().statusCode(303).build()));
     }
 
     @Test
     public void calculateSleepTimeMS() {
-        List<Predicate<DeliveryAttempt>> giveUpIfs = new ArrayList<>();
-        List<Predicate<DeliveryAttempt>> tryLaterIfs = new ArrayList<>();
-        int timeoutSeconds = 10;
-        WebhookError webhookError = mock(WebhookError.class);
-        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, timeoutSeconds, webhookError);
-
+        WebhookRetryer retryer = new WebhookRetryer(giveUpIfs, tryLaterIfs, connectTimeoutSeconds, readTimeoutSeconds, webhookError);
         assertEquals(2000, retryer.calculateSleepTimeMS(DeliveryAttempt.builder().number(1).build(), 1000, 10000));
         assertEquals(4000, retryer.calculateSleepTimeMS(DeliveryAttempt.builder().number(2).build(), 1000, 10000));
         assertEquals(8000, retryer.calculateSleepTimeMS(DeliveryAttempt.builder().number(3).build(), 1000, 10000));
```

## Row 3
commit_url: https://github.com/ibi-group/datatools-server/commit/629ffd2764e667074c751072951a041d05d75f47
rm_type: Replace Attribute With Variable
rm_description: Replace Attribute With Variable mockFeedSource2 : FeedSource to mockFeedSource : FeedSource in method private createFeedSource(name String) : FeedSource from class com.conveyal.datatools.manager.jobs.AutoDeployFeedJobTest
file_path: src/test/java/com/conveyal/datatools/manager/jobs/AutoDeployFeedJobTest.java
left_side: [{"filePath": "src/test/java/com/conveyal/datatools/manager/jobs/AutoDeployFeedJobTest.java", "startLine": 42, "endLine": 42, "startColumn": 31, "endColumn": 46, "codeElementType": "FIELD_DECLARATION", "description": "original variable declaration", "codeElement": "mockFeedSource2 : FeedSource"}, {"filePath": "src/test/java/com/conveyal/datatools/manager/jobs/AutoDeployFeedJobTest.java", "startLine": 75, "endLine": 75, "startColumn": 9, "endColumn": 115, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "src/test/java/com/conveyal/datatools/manager/jobs/AutoDeployFeedJobTest.java", "startLine": 76, "endLine": 76, "startColumn": 9, "endColumn": 57, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}]
right_side: [{"filePath": "src/test/java/com/conveyal/datatools/manager/jobs/AutoDeployFeedJobTest.java", "startLine": 225, "endLine": 225, "startColumn": 20, "endColumn": 108, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "renamed variable declaration", "codeElement": "mockFeedSource : FeedSource"}, {"filePath": "src/test/java/com/conveyal/datatools/manager/jobs/AutoDeployFeedJobTest.java", "startLine": 225, "endLine": 225, "startColumn": 9, "endColumn": 109, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}, {"filePath": "src/test/java/com/conveyal/datatools/manager/jobs/AutoDeployFeedJobTest.java", "startLine": 226, "endLine": 226, "startColumn": 9, "endColumn": 56, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}]

### Patch: src/test/java/com/conveyal/datatools/manager/jobs/AutoDeployFeedJobTest.java
```diff
@@ -40,6 +40,11 @@ public class AutoDeployFeedJobTest extends DatatoolsTest {
     private static Project project;
     private static FeedSource mockFeedSource1;
     private static FeedSource mockFeedSource2;
+    private static FeedSource mockFeedSource3;
+    private static FeedSource mockFeedSource4;
+    private static FeedSource mockFeedSource5;
+    private static FeedSource mockFeedSource6;
+    private static FeedSource mockFeedSourceForFakeJob;
     private static FeedVersion feedVersion;
     private final String FEED_VERSION_ZIP_FOLDER_NAME = "fake-agency-expire-in-2099";
 
@@ -70,10 +75,13 @@ public static void setUp() throws IOException {
         deployment.projectId = project.id;
         Persistence.deployments.create(deployment);
 
-        mockFeedSource1 = new FeedSource("Mock Feed Source 1", project.id, FeedRetrievalMethod.MANUALLY_UPLOADED);
-        Persistence.feedSources.create(mockFeedSource1);
-        mockFeedSource2 = new FeedSource("Mock Feed Source 2", project.id, FeedRetrievalMethod.MANUALLY_UPLOADED);
-        Persistence.feedSources.create(mockFeedSource2);
+        mockFeedSource1 = createFeedSource("Mock Feed Source 1");
+        mockFeedSource2 = createFeedSource("Mock Feed Source 2");
+        mockFeedSource3 = createFeedSource("Mock Feed Source 3");
+        mockFeedSource4 = createFeedSource("Mock Feed Source 4");
+        mockFeedSource5 = createFeedSource("Mock Feed Source 5");
+        mockFeedSource6 = createFeedSource("Mock Feed Source 6");
+        mockFeedSourceForFakeJob = createFeedSource("Mock Feed Source For Fake Job");
     }
 
     @AfterClass
@@ -82,16 +90,22 @@ public static void tearDown() {
         server.delete();
         deployment.delete();
         mockFeedSource1.delete();
+        mockFeedSource2.delete();
+        mockFeedSource3.delete();
+        mockFeedSource4.delete();
+        mockFeedSource5.delete();
+        mockFeedSource6.delete();
         Persistence.projects.removeById(project.id);
-        Persistence.feedSources.removeById(mockFeedSource2.id);
+        // Part of a job that is not started so the feed source has to be deleted straight from DB.
+        Persistence.feedSources.removeById(mockFeedSourceForFakeJob.id);
         if (feedVersion != null) {
             Persistence.feedVersions.removeById(feedVersion.id);
         }
     }
 
     @Test
     public void skipJobIfFeedSourceNotDeployable() throws IOException {
-        setFeedSourceDeployable(false);
+        setFeedSourceDeployable(mockFeedSource1, false);
         setProjectAutoDeploy(true);
         setProjectPinnedDeploymentId(deployment.id);
         ProcessSingleFeedJob processSingleFeedJob = triggerProcessSingleFeedJob(mockFeedSource1, FEED_VERSION_ZIP_FOLDER_NAME);
@@ -102,47 +116,47 @@ public void skipJobIfFeedSourceNotDeployable() throws IOException {
 
     @Test
     public void failIfDeploymentNotPinned() throws IOException {
-        setFeedSourceDeployable(true);
+        setFeedSourceDeployable(mockFeedSource2, true);
         setProjectAutoDeploy(true);
         setProjectPinnedDeploymentId(null);
-        ProcessSingleFeedJob processSingleFeedJob = triggerProcessSingleFeedJob(mockFeedSource1, FEED_VERSION_ZIP_FOLDER_NAME);
+        ProcessSingleFeedJob processSingleFeedJob = triggerProcessSingleFeedJob(mockFeedSource2, FEED_VERSION_ZIP_FOLDER_NAME);
         MonitorableJob lastJob = getLastJob(processSingleFeedJob);
         assertTrue(lastJob instanceof AutoDeployFeedJob);
         assertThat(lastJob.status.message, equalTo("Pinned deployment does not exist. Cancelling auto-deploy."));
     }
 
     @Test
     public void skipJobIfProjectNotAutoDeploy() throws IOException {
-        setFeedSourceDeployable(true);
+        setFeedSourceDeployable(mockFeedSource3, true);
         setProjectAutoDeploy(false);
         setProjectPinnedDeploymentId(deployment.id);
-        ProcessSingleFeedJob processSingleFeedJob = triggerProcessSingleFeedJob(mockFeedSource1, FEED_VERSION_ZIP_FOLDER_NAME);
+        ProcessSingleFeedJob processSingleFeedJob = triggerProcessSingleFeedJob(mockFeedSource3, FEED_VERSION_ZIP_FOLDER_NAME);
         MonitorableJob lastJob = getLastJob(processSingleFeedJob);
         // Verify that the auto deploy job was not added as a subjob.
         assertFalse(lastJob instanceof AutoDeployFeedJob);
     }
 
     @Test
     public void canAutoDeployFeedVersion() throws IOException {
-        setFeedSourceDeployable(true);
+        setFeedSourceDeployable(mockFeedSource4, true);
         setProjectAutoDeploy(true);
         setProjectPinnedDeploymentId(deployment.id);
-        ProcessSingleFeedJob processSingleFeedJob = triggerProcessSingleFeedJob(mockFeedSource1, FEED_VERSION_ZIP_FOLDER_NAME);
+        ProcessSingleFeedJob processSingleFeedJob = triggerProcessSingleFeedJob(mockFeedSource4, FEED_VERSION_ZIP_FOLDER_NAME);
         MonitorableJob lastJob = getLastJob(processSingleFeedJob);
         assertTrue(lastJob instanceof AutoDeployFeedJob);
         assertThat(lastJob.status.message, equalTo(String.format("New deploy job initiated for %s", server.name)));
     }
 
     @Test
     public void failAutoDeployIfFetchStillInProgress() throws IOException {
-        setFeedSourceDeployable(true);
+        setFeedSourceDeployable(mockFeedSource5, true);
         setProjectAutoDeploy(true);
         setProjectPinnedDeploymentId(deployment.id);
 
-        // Create fake processing job for mock feed 1 (don't actually start it, to keep it in the userJobsMap
+        // Create fake processing job for mock feed (don't actually start it, to keep it in the userJobsMap
         // indefinitely).
         File zipFile = zipFolderFiles(FEED_VERSION_ZIP_FOLDER_NAME);
-        feedVersion = getFeedVersionFromGTFSFile(mockFeedSource2, zipFile);
+        feedVersion = getFeedVersionFromGTFSFile(mockFeedSourceForFakeJob, zipFile);
         Auth0UserProfile user = Auth0UserProfile.createTestAdminUser();
         Set<MonitorableJob> userJobs = Sets.newConcurrentHashSet();
         userJobs.add(new ProcessSingleFeedJob(feedVersion, user, true));
@@ -158,28 +172,28 @@ public void failAutoDeployIfFetchStillInProgress() throws IOException {
 
         // Process single feed job.
         ProcessSingleFeedJob processSingleFeedJob =
-            triggerProcessSingleFeedJob(mockFeedSource1, FEED_VERSION_ZIP_FOLDER_NAME);
+            triggerProcessSingleFeedJob(mockFeedSource5, FEED_VERSION_ZIP_FOLDER_NAME);
         MonitorableJob lastJob = getLastJob(processSingleFeedJob);
         assertTrue(lastJob instanceof AutoDeployFeedJob);
         assertThat(lastJob.status.message, equalTo("Auto-deploy skipped because of feed fetches in progress."));
     }
 
     @Test
     public void failIfFeedVersionHasHighSeverityErrorTypes() throws IOException {
-        setFeedSourceDeployable(true);
+        setFeedSourceDeployable(mockFeedSource6,true);
         setProjectAutoDeploy(true);
         setProjectPinnedDeploymentId(deployment.id);
         ProcessSingleFeedJob processSingleFeedJob =
-            triggerProcessSingleFeedJob(mockFeedSource1,
+            triggerProcessSingleFeedJob(mockFeedSource6,
                 "fake-agency-with-only-calendar-expire-in-2099-with-unused-route");
         MonitorableJob lastJob = getLastJob(processSingleFeedJob);
         assertTrue(lastJob instanceof AutoDeployFeedJob);
         assertThat(lastJob.status.message, equalTo("Feed version has critical errors or is out of date. Cancelling auto-deploy."));
     }
 
-    private void setFeedSourceDeployable(boolean deployable) {
-        mockFeedSource1.deployable = deployable;
-        Persistence.feedSources.replace(mockFeedSource1.id, mockFeedSource1);
+    private void setFeedSourceDeployable(FeedSource feedSource, boolean deployable) {
+        feedSource.deployable = deployable;
+        Persistence.feedSources.replace(feedSource.id, feedSource);
     }
 
     private void setProjectAutoDeploy(boolean autoDeploy) {
@@ -206,4 +220,10 @@ private MonitorableJob getLastJob(ProcessSingleFeedJob processSingleFeedJob) {
         List<MonitorableJob> subJobs = processSingleFeedJob.getSubJobs();
         return subJobs.get(subJobs.size() - 1);
     }
+
+    private static FeedSource createFeedSource(String name) {
+        FeedSource mockFeedSource = new FeedSource(name, project.id, FeedRetrievalMethod.MANUALLY_UPLOADED);
+        Persistence.feedSources.create(mockFeedSource);
+        return mockFeedSource;
+    }
 }
```

## Row 4
commit_url: https://github.com/stargate/stargate/commit/d343267977609b977cd3fa33dde60aab4dcf7a47
rm_type: Move And Rename Method
rm_description: Move And Rename Method public createIndex(session CqlSession) : void from class io.stargate.it.http.RestApiv2Test to public indexCreateBasic(session CqlSession) : void from class io.stargate.it.http.RestApiv2SchemaTest
file_path: testing/src/main/java/io/stargate/it/http/RestApiv2SchemaTest.java; testing/src/main/java/io/stargate/it/http/RestApiv2Test.java
left_side: [{"filePath": "testing/src/main/java/io/stargate/it/http/RestApiv2Test.java", "startLine": 150, "endLine": 219, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public createIndex(session CqlSession) : void"}]
right_side: [{"filePath": "testing/src/main/java/io/stargate/it/http/RestApiv2SchemaTest.java", "startLine": 950, "endLine": 1022, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "moved method declaration", "codeElement": "public indexCreateBasic(session CqlSession) : void"}]

### Patch: testing/src/main/java/io/stargate/it/http/RestApiv2SchemaTest.java
```diff
@@ -1,7 +1,12 @@
 package io.stargate.it.http;
 
 import static org.assertj.core.api.Assertions.assertThat;
+import static org.assertj.core.api.Assumptions.assumeThat;
 
+import com.datastax.oss.driver.api.core.CqlSession;
+import com.datastax.oss.driver.api.core.cql.Row;
+import com.datastax.oss.driver.api.core.cql.SimpleStatement;
+import com.fasterxml.jackson.core.type.TypeReference;
 import com.fasterxml.jackson.databind.JavaType;
 import com.fasterxml.jackson.databind.ObjectMapper;
 import io.stargate.auth.model.AuthTokenResponse;
@@ -10,19 +15,21 @@
 import io.stargate.it.driver.CqlSessionSpec;
 import io.stargate.it.http.models.Credentials;
 import io.stargate.it.storage.StargateConnectionInfo;
+import io.stargate.web.models.ApiError;
 import io.stargate.web.models.Keyspace;
-import io.stargate.web.restapi.models.ColumnDefinition;
-import io.stargate.web.restapi.models.PrimaryKey;
-import io.stargate.web.restapi.models.RESTResponseWrapper;
-import io.stargate.web.restapi.models.TableAdd;
-import io.stargate.web.restapi.models.TableOptions;
-import io.stargate.web.restapi.models.TableResponse;
+import io.stargate.web.restapi.models.*;
 import java.io.IOException;
 import java.lang.reflect.Method;
 import java.util.ArrayList;
+import java.util.Arrays;
+import java.util.Collection;
 import java.util.Collections;
+import java.util.HashMap;
 import java.util.List;
+import java.util.Map;
 import java.util.Optional;
+import java.util.UUID;
+import java.util.stream.Collectors;
 import net.jcip.annotations.NotThreadSafe;
 import org.apache.http.HttpStatus;
 import org.junit.jupiter.api.BeforeEach;
@@ -44,10 +51,16 @@ public class RestApiv2SchemaTest extends BaseIntegrationTest {
   private String host;
   private String restUrlBase;
 
+  static class ListOfMapsGetResponseWrapper extends GetResponseWrapper<List<Map<String, Object>>> {
+    public ListOfMapsGetResponseWrapper() {
+      super(-1, null, null);
+    }
+  }
+
   private static final ObjectMapper objectMapper = new ObjectMapper();
 
   @BeforeEach
-  public void setup(TestInfo testInfo, StargateConnectionInfo cluster) throws IOException {
+  void setup(TestInfo testInfo, StargateConnectionInfo cluster) throws IOException {
     host = "http://" + cluster.seedAddress();
     restUrlBase = host + ":8082";
 
@@ -203,7 +216,7 @@ public void keyspaceDelete() throws IOException {
    */
 
   @Test
-  public void tableCreateSimple() throws IOException {
+  public void tableCreateBasic() throws IOException {
     createTestKeyspace(keyspaceName);
     createSimpleTestTable(keyspaceName, tableName);
 
@@ -221,6 +234,82 @@ public void tableCreateSimple() throws IOException {
     assertThat(table.getColumnDefinitions()).isNotNull();
   }
 
+  @Test
+  public void tableCreateWithNullOptions() throws IOException {
+    createTestKeyspace(keyspaceName);
+
+    TableAdd tableAdd = new TableAdd();
+    tableAdd.setName("t1");
+
+    List<ColumnDefinition> columnDefinitions = new ArrayList<>();
+
+    columnDefinitions.add(new ColumnDefinition("id", "uuid"));
+    columnDefinitions.add(new ColumnDefinition("lastName", "text"));
+    columnDefinitions.add(new ColumnDefinition("firstName", "text"));
+
+    tableAdd.setColumnDefinitions(columnDefinitions);
+
+    PrimaryKey primaryKey = new PrimaryKey();
+    primaryKey.setPartitionKey(Collections.singletonList("id"));
+    tableAdd.setPrimaryKey(primaryKey);
+    tableAdd.setTableOptions(null);
+
+    String body =
+        RestUtils.post(
+            authToken,
+            String.format("%s/v2/schemas/keyspaces/%s/tables", restUrlBase, keyspaceName),
+            objectMapper.writeValueAsString(tableAdd),
+            HttpStatus.SC_CREATED);
+
+    RestApiv2Test.NameResponse response =
+        objectMapper.readValue(body, RestApiv2Test.NameResponse.class);
+    assertThat(response.name).isEqualTo(tableAdd.getName());
+  }
+
+  @Test
+  public void tableCreateWithNoClustering() throws IOException {
+    createTestKeyspace(keyspaceName);
+    TableAdd tableAdd = new TableAdd();
+    tableAdd.setName(tableName);
+
+    List<ColumnDefinition> columnDefinitions = new ArrayList<>();
+
+    columnDefinitions.add(new ColumnDefinition("pk1", "int"));
+    columnDefinitions.add(new ColumnDefinition("ck1", "int"));
+
+    tableAdd.setColumnDefinitions(columnDefinitions);
+
+    PrimaryKey primaryKey = new PrimaryKey();
+    primaryKey.setPartitionKey(Collections.singletonList("pk1"));
+    primaryKey.setClusteringKey(Collections.singletonList("ck1"));
+    tableAdd.setPrimaryKey(primaryKey);
+
+    tableAdd.setTableOptions(new TableOptions(0, null));
+
+    String body =
+        RestUtils.post(
+            authToken,
+            String.format("%s/v2/schemas/keyspaces/%s/tables", restUrlBase, keyspaceName),
+            objectMapper.writeValueAsString(tableAdd),
+            HttpStatus.SC_CREATED);
+
+    RestApiv2Test.NameResponse response =
+        objectMapper.readValue(body, RestApiv2Test.NameResponse.class);
+    assertThat(response.name).isEqualTo(tableAdd.getName());
+
+    body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s?raw=true",
+                restUrlBase, keyspaceName, tableName),
+            HttpStatus.SC_OK);
+
+    TableResponse table = objectMapper.readValue(body, TableResponse.class);
+    assertThat(table.getTableOptions().getClusteringExpression().get(0).getOrder())
+        .isEqualTo("ASC");
+  }
+
   @Test
   public void tableUpdateSimple() throws IOException {
     createTestKeyspace(keyspaceName);
@@ -352,6 +441,803 @@ public void tableDelete() throws IOException {
         HttpStatus.SC_NO_CONTENT);
   }
 
+  @Test
+  public void tableWithMixedCaseNames() throws IOException {
+    createTestKeyspace(keyspaceName);
+
+    String tableName = "MixedCaseTable";
+    TableAdd tableAdd = new TableAdd();
+    tableAdd.setName(tableName);
+
+    List<ColumnDefinition> columnDefinitions = new ArrayList<>();
+
+    columnDefinitions.add(new ColumnDefinition("ID", "uuid"));
+    columnDefinitions.add(new ColumnDefinition("Lastname", "text"));
+    columnDefinitions.add(new ColumnDefinition("Firstname", "text"));
+    tableAdd.setColumnDefinitions(columnDefinitions);
+
+    PrimaryKey primaryKey = new PrimaryKey();
+    primaryKey.setPartitionKey(Collections.singletonList("ID"));
+    tableAdd.setPrimaryKey(primaryKey);
+
+    // ensure table name is preserved
+    String body =
+        RestUtils.post(
+            authToken,
+            String.format("%s/v2/schemas/keyspaces/%s/tables", restUrlBase, keyspaceName),
+            objectMapper.writeValueAsString(tableAdd),
+            HttpStatus.SC_CREATED);
+
+    TableResponse tableResponse = objectMapper.readValue(body, TableResponse.class);
+    assertThat(tableResponse.getName()).isEqualTo(tableName);
+
+    // insert a row
+    String rowIdentifier = UUID.randomUUID().toString();
+    Map<String, String> row = new HashMap<>();
+    row.put("ID", rowIdentifier);
+    row.put("Firstname", "John");
+    row.put("Lastname", "Doe");
+
+    RestUtils.post(
+        authToken,
+        String.format("%s/v2/keyspaces/%s/%s", restUrlBase, keyspaceName, tableName),
+        objectMapper.writeValueAsString(row),
+        HttpStatus.SC_CREATED);
+
+    // retrieve the row by ID and ensure column names are as expected
+    String whereClause = String.format("{\"ID\":{\"$eq\":\"%s\"}}", rowIdentifier);
+    body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/keyspaces/%s/%s?where=%s",
+                restUrlBase, keyspaceName, tableName, whereClause),
+            HttpStatus.SC_OK);
+    ListOfMapsGetResponseWrapper getResponseWrapper =
+        objectMapper.readValue(body, ListOfMapsGetResponseWrapper.class);
+    List<Map<String, Object>> data = getResponseWrapper.getData();
+    assertThat(data.get(0).get("ID")).isEqualTo(rowIdentifier);
+    assertThat(data.get(0).get("Firstname")).isEqualTo("John");
+    assertThat(data.get(0).get("Lastname")).isEqualTo("Doe");
+  }
+
+  /*
+  /************************************************************************
+  /* Test methods for Column CRUD operations
+  /************************************************************************
+   */
+
+  @Test
+  public void columnAddBasic() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    ColumnDefinition columnDefinition = new ColumnDefinition("name", "text");
+
+    String body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns",
+                restUrlBase, keyspaceName, tableName),
+            objectMapper.writeValueAsString(columnDefinition),
+            HttpStatus.SC_CREATED);
+    @SuppressWarnings("unchecked")
+    Map<String, String> response = objectMapper.readValue(body, Map.class);
+
+    assertThat(response.get("name")).isEqualTo("name");
+
+    body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s?raw=true",
+                restUrlBase, keyspaceName, tableName, "name"),
+            HttpStatus.SC_OK);
+    ColumnDefinition column = objectMapper.readValue(body, ColumnDefinition.class);
+    assertThat(column).usingRecursiveComparison().isEqualTo(columnDefinition);
+  }
+
+  @Test
+  public void columnAddStatic() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createTestTableWithClustering(keyspaceName, tableName);
+
+    ColumnDefinition columnDefinition = new ColumnDefinition("balance", "float", true);
+
+    String body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns",
+                restUrlBase, keyspaceName, tableName),
+            objectMapper.writeValueAsString(columnDefinition),
+            HttpStatus.SC_CREATED);
+    @SuppressWarnings("unchecked")
+    Map<String, String> response = objectMapper.readValue(body, Map.class);
+
+    assertThat(response.get("name")).isEqualTo("balance");
+
+    body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s?raw=true",
+                restUrlBase, keyspaceName, tableName, "balance"),
+            HttpStatus.SC_OK);
+    ColumnDefinition column = objectMapper.readValue(body, ColumnDefinition.class);
+    assertThat(column).usingRecursiveComparison().isEqualTo(columnDefinition);
+  }
+
+  @Test
+  public void columnAddBadType() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    ColumnDefinition columnDefinition = new ColumnDefinition("name", "badType");
+
+    String body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns",
+                restUrlBase, keyspaceName, tableName),
+            objectMapper.writeValueAsString(columnDefinition),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnUpdate() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    final ColumnDefinition columnDefinition = new ColumnDefinition("identifier", "uuid");
+    String body =
+        RestUtils.put(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, keyspaceName, tableName, "id"),
+            objectMapper.writeValueAsString(columnDefinition),
+            HttpStatus.SC_OK);
+    @SuppressWarnings("unchecked")
+    Map<String, String> response = objectMapper.readValue(body, Map.class);
+    assertThat(response.get("name")).isEqualTo("identifier");
+    body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s?raw=true",
+                restUrlBase, keyspaceName, tableName, "identifier"),
+            HttpStatus.SC_OK);
+    ColumnDefinition column = objectMapper.readValue(body, ColumnDefinition.class);
+    assertThat(column).usingRecursiveComparison().isEqualTo(columnDefinition);
+  }
+
+  @Test
+  public void columnUpdateNotFound() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    String body =
+        RestUtils.put(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, keyspaceName, tableName, "notFound"),
+            objectMapper.writeValueAsString(new ColumnDefinition("name", "text")),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnUpdateBadTable() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    String body =
+        RestUtils.put(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, keyspaceName, "foo", "age"),
+            objectMapper.writeValueAsString(new ColumnDefinition("name", "text")),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnUpdateBadKeyspace() throws IOException {
+    String body =
+        RestUtils.put(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, "foo", tableName, "age"),
+            objectMapper.writeValueAsString(new ColumnDefinition("name", "text")),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnGetWrapped() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, keyspaceName, tableName, "age"),
+            HttpStatus.SC_OK);
+    ColumnDefinition column = readWrappedRESTResponse(body, ColumnDefinition.class);
+    assertThat(column)
+        .usingRecursiveComparison()
+        .isEqualTo(new ColumnDefinition("age", "int", false));
+  }
+
+  @Test
+  public void columnGetRaw() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s?raw=true",
+                restUrlBase, keyspaceName, tableName, "age"),
+            HttpStatus.SC_OK);
+    ColumnDefinition column = objectMapper.readValue(body, ColumnDefinition.class);
+    assertThat(column)
+        .usingRecursiveComparison()
+        .isEqualTo(new ColumnDefinition("age", "int", false));
+  }
+
+  @Test
+  public void columnGetComplex() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createComplexTestTable(keyspaceName, tableName);
+
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, keyspaceName, tableName, "col1"),
+            HttpStatus.SC_OK);
+    ColumnDefinition column = readWrappedRESTResponse(body, ColumnDefinition.class);
+    assertThat(column)
+        .usingRecursiveComparison()
+        .isEqualTo(new ColumnDefinition("col1", "frozen<map<date, text>>", false));
+  }
+
+  @Test
+  public void columnGetBadKeyspace() throws IOException {
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, "foo", tableName, "age"),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnGetBadTable() throws IOException {
+    createTestKeyspace(keyspaceName);
+
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, keyspaceName, "foo", "age"),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnGetNotFound() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, keyspaceName, tableName, "foo"),
+            HttpStatus.SC_NOT_FOUND);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_NOT_FOUND);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnsGetWrapped() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns",
+                restUrlBase, keyspaceName, tableName),
+            HttpStatus.SC_OK);
+    ColumnDefinition[] columns = readWrappedRESTResponse(body, ColumnDefinition[].class);
+    assertThat(columns)
+        .anySatisfy(
+            value ->
+                assertThat(value)
+                    .usingRecursiveComparison()
+                    .isEqualTo(new ColumnDefinition("id", "uuid", false)));
+  }
+
+  @Test
+  public void columnsGetRaw() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns?raw=true",
+                restUrlBase, keyspaceName, tableName),
+            HttpStatus.SC_OK);
+    ColumnDefinition[] columns = objectMapper.readValue(body, ColumnDefinition[].class);
+    assertThat(columns)
+        .anySatisfy(
+            value ->
+                assertThat(value)
+                    .usingRecursiveComparison()
+                    .isEqualTo(new ColumnDefinition("id", "uuid", false)));
+  }
+
+  @Test
+  public void columnsGetComplex() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createComplexTestTable(keyspaceName, tableName);
+
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns",
+                restUrlBase, keyspaceName, tableName),
+            HttpStatus.SC_OK);
+    ColumnDefinition[] columns = readWrappedRESTResponse(body, ColumnDefinition[].class);
+    assertThat(columns)
+        .anySatisfy(
+            value ->
+                assertThat(value)
+                    .usingRecursiveComparison()
+                    .isEqualTo(new ColumnDefinition("col2", "frozen<set<boolean>>", false)));
+  }
+
+  @Test
+  public void columnsGetBadTable() throws IOException {
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns", restUrlBase, keyspaceName, "foo"),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnsGetBadKeyspace() throws IOException {
+    createTestKeyspace(keyspaceName);
+
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns", restUrlBase, "foo", tableName),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnDelete() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    RestUtils.delete(
+        authToken,
+        String.format(
+            "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+            restUrlBase, keyspaceName, tableName, "age"),
+        HttpStatus.SC_NO_CONTENT);
+  }
+
+  @Test
+  public void columnDeleteNotFound() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    RestUtils.delete(
+        authToken,
+        String.format(
+            "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+            restUrlBase, keyspaceName, tableName, "foo"),
+        HttpStatus.SC_BAD_REQUEST);
+  }
+
+  @Test
+  public void columnDeleteBadTable() throws IOException {
+    createTestKeyspace(keyspaceName);
+
+    String body =
+        RestUtils.delete(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, keyspaceName, "foo", "age"),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnDeleteBadKeyspace() throws IOException {
+    String body =
+        RestUtils.delete(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, "foo", tableName, "age"),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  @Test
+  public void columnDeletePartitionKey() throws IOException {
+    createTestKeyspace(keyspaceName);
+    createSimpleTestTable(keyspaceName, tableName);
+
+    String body =
+        RestUtils.delete(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
+                restUrlBase, keyspaceName, tableName, "id"),
+            HttpStatus.SC_BAD_REQUEST);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription()).isNotEmpty();
+  }
+
+  /*
+  /************************************************************************
+  /* Test methods for Index CRUD operations
+  /************************************************************************
+   */
+
+  @Test
+  public void indexCreateBasic(CqlSession session) throws IOException {
+    createTestKeyspace(keyspaceName);
+    tableName = "tbl_createtable_" + System.currentTimeMillis();
+    createTestTable(
+        tableName,
+        Arrays.asList("id text", "firstName text", "lastName text", "email list<text>"),
+        Collections.singletonList("id"),
+        null);
+
+    IndexAdd indexAdd = new IndexAdd();
+    indexAdd.setColumn("firstName");
+    indexAdd.setName("test_idx");
+    indexAdd.setIfNotExists(false);
+
+    String body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/indexes",
+                restUrlBase, keyspaceName, tableName),
+            objectMapper.writeValueAsString(indexAdd),
+            HttpStatus.SC_CREATED);
+    SuccessResponse successResponse = objectMapper.readValue(body, SuccessResponse.class);
+    assertThat(successResponse.getSuccess()).isTrue();
+
+    List<Row> rows = session.execute("SELECT * FROM system_schema.indexes;").all();
+    assertThat(rows.stream().anyMatch(i -> "test_idx".equals(i.getString("index_name")))).isTrue();
+
+    // don't create an index if it already exists and don't throw error
+    indexAdd.setIfNotExists(true);
+    body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/indexes",
+                restUrlBase, keyspaceName, tableName),
+            objectMapper.writeValueAsString(indexAdd),
+            HttpStatus.SC_CREATED);
+    successResponse = objectMapper.readValue(body, SuccessResponse.class);
+    assertThat(successResponse.getSuccess()).isTrue();
+
+    // throw error if index already exists
+    indexAdd.setIfNotExists(false);
+    body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/indexes",
+                restUrlBase, keyspaceName, tableName),
+            objectMapper.writeValueAsString(indexAdd),
+            HttpStatus.SC_BAD_REQUEST);
+
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription())
+        .isEqualTo("Bad request: An index named test_idx already exists");
+
+    // successfully index a collection
+    indexAdd.setColumn("email");
+    indexAdd.setName(null);
+    indexAdd.setKind(IndexKind.VALUES);
+    body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/indexes",
+                restUrlBase, keyspaceName, tableName),
+            objectMapper.writeValueAsString(indexAdd),
+            HttpStatus.SC_CREATED);
+    successResponse = objectMapper.readValue(body, SuccessResponse.class);
+    assertThat(successResponse.getSuccess()).isTrue();
+  }
+
+  @Test
+  public void indexCreateCustom(CqlSession session) throws IOException {
+    // TODO remove this when we figure out how to enable SAI indexes in Cassandra 4
+    assumeThat(isCassandra4())
+        .as(
+            "Disabled because it is currently not possible to enable SAI indexes "
+                + "on a Cassandra 4 backend")
+        .isFalse();
+
+    createTestKeyspace(keyspaceName);
+    tableName = "tbl_createtable_" + System.currentTimeMillis();
+    createTestTable(
+        tableName,
+        Arrays.asList("id text", "firstName text", "lastName text", "email list<text>"),
+        Collections.singletonList("id"),
+        null);
+
+    IndexAdd indexAdd = new IndexAdd();
+    String indexType = "org.apache.cassandra.index.sasi.SASIIndex";
+    indexAdd.setColumn("lastName");
+    indexAdd.setName("test_custom_idx");
+    indexAdd.setType(indexType);
+    indexAdd.setIfNotExists(false);
+    indexAdd.setKind(null);
+
+    Map<String, String> options = new HashMap<>();
+    options.put("mode", "CONTAINS");
+    indexAdd.setOptions(options);
+
+    String body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/indexes",
+                restUrlBase, keyspaceName, tableName),
+            objectMapper.writeValueAsString(indexAdd),
+            HttpStatus.SC_CREATED);
+    SuccessResponse successResponse = objectMapper.readValue(body, SuccessResponse.class);
+    assertThat(successResponse.getSuccess()).isTrue();
+
+    Collection<Row> rows = session.execute("SELECT * FROM system_schema.indexes;").all();
+    Optional<Row> row =
+        rows.stream().filter(i -> "test_custom_idx".equals(i.getString("index_name"))).findFirst();
+    Map<String, String> optionsReturned = row.get().getMap("options", String.class, String.class);
+
+    assertThat(optionsReturned.get("class_name")).isEqualTo(indexType);
+    assertThat(optionsReturned.get("target")).isEqualTo("\"lastName\"");
+    assertThat(optionsReturned.get("mode")).isEqualTo("CONTAINS");
+  }
+
+  @Test
+  public void indexCreateInvalid() throws IOException {
+    createTestKeyspace(keyspaceName);
+    String tableName = "tbl_createtable_" + System.currentTimeMillis();
+    createTestTable(
+        tableName,
+        Arrays.asList("id text", "firstName text", "email list<text>"),
+        Collections.singletonList("id"),
+        null);
+
+    // invalid table
+    IndexAdd indexAdd = new IndexAdd();
+    indexAdd.setColumn("firstName");
+    String body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/invalid_table/indexes",
+                restUrlBase, keyspaceName),
+            objectMapper.writeValueAsString(indexAdd),
+            HttpStatus.SC_NOT_FOUND);
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_NOT_FOUND);
+    assertThat(response.getDescription()).isEqualTo("Table 'invalid_table' not found in keyspace.");
+
+    // invalid column
+    indexAdd.setColumn("invalid_column");
+    body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/indexes",
+                restUrlBase, keyspaceName, tableName),
+            objectMapper.writeValueAsString(indexAdd),
+            HttpStatus.SC_NOT_FOUND);
+
+    response = objectMapper.readValue(body, ApiError.class);
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_NOT_FOUND);
+    assertThat(response.getDescription()).isEqualTo("Column 'invalid_column' not found in table.");
+
+    // invalid index kind
+    indexAdd.setColumn("firstName");
+    indexAdd.setKind(IndexKind.ENTRIES);
+    body =
+        RestUtils.post(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/indexes",
+                restUrlBase, keyspaceName, tableName),
+            objectMapper.writeValueAsString(indexAdd),
+            HttpStatus.SC_BAD_REQUEST);
+
+    response = objectMapper.readValue(body, ApiError.class);
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
+    assertThat(response.getDescription())
+        .isEqualTo("Bad request: Indexing entries can only be used with a map");
+  }
+
+  @Test
+  public void indexListAll() throws IOException {
+    createTestKeyspace(keyspaceName);
+    tableName = "tbl_createtable_" + System.currentTimeMillis();
+    createTestTable(
+        tableName,
+        Arrays.asList("id text", "firstName text", "email list<text>"),
+        Collections.singletonList("id"),
+        null);
+
+    String body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/indexes",
+                restUrlBase, keyspaceName, tableName),
+            HttpStatus.SC_OK);
+    assertThat(body).isEqualTo("[]");
+
+    IndexAdd indexAdd = new IndexAdd();
+    indexAdd.setColumn("firstName");
+    indexAdd.setName("test_idx");
+    indexAdd.setIfNotExists(false);
+
+    RestUtils.post(
+        authToken,
+        String.format(
+            "%s/v2/schemas/keyspaces/%s/tables/%s/indexes", restUrlBase, keyspaceName, tableName),
+        objectMapper.writeValueAsString(indexAdd),
+        HttpStatus.SC_CREATED);
+
+    body =
+        RestUtils.get(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/indexes",
+                restUrlBase, keyspaceName, tableName),
+            HttpStatus.SC_OK);
+
+    List<Map<String, Object>> data =
+        objectMapper.readValue(body, new TypeReference<List<Map<String, Object>>>() {});
+
+    assertThat(data.stream().anyMatch(m -> "test_idx".equals(m.get("index_name")))).isTrue();
+  }
+
+  @Test
+  public void indexDrop(CqlSession session) throws IOException {
+    createTestKeyspace(keyspaceName);
+    tableName = "tbl_createtable_" + System.currentTimeMillis();
+    createTestTable(
+        tableName,
+        Arrays.asList("id text", "firstName text", "email list<text>"),
+        Collections.singletonList("id"),
+        null);
+
+    IndexAdd indexAdd = new IndexAdd();
+    indexAdd.setColumn("firstName");
+    indexAdd.setName("test_idx");
+    indexAdd.setIfNotExists(false);
+
+    RestUtils.post(
+        authToken,
+        String.format(
+            "%s/v2/schemas/keyspaces/%s/tables/%s/indexes", restUrlBase, keyspaceName, tableName),
+        objectMapper.writeValueAsString(indexAdd),
+        HttpStatus.SC_CREATED);
+
+    SimpleStatement selectIndexes =
+        SimpleStatement.newInstance(
+            "SELECT * FROM system_schema.indexes WHERE keyspace_name = ? AND table_name = ?",
+            keyspaceName,
+            tableName);
+    List<Row> rows = session.execute(selectIndexes).all();
+    assertThat(rows.size()).isEqualTo(1);
+
+    String indexName = "test_idx";
+    RestUtils.delete(
+        authToken,
+        String.format(
+            "%s/v2/schemas/keyspaces/%s/tables/%s/indexes/%s",
+            restUrlBase, keyspaceName, tableName, indexName),
+        HttpStatus.SC_NO_CONTENT);
+
+    rows = session.execute(selectIndexes).all();
+    assertThat(rows.size()).isEqualTo(0);
+
+    indexName = "invalid_idx";
+    String body =
+        RestUtils.delete(
+            authToken,
+            String.format(
+                "%s/v2/schemas/keyspaces/%s/tables/%s/indexes/%s",
+                restUrlBase, keyspaceName, tableName, indexName),
+            HttpStatus.SC_NOT_FOUND);
+
+    ApiError response = objectMapper.readValue(body, ApiError.class);
+    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_NOT_FOUND);
+    assertThat(response.getDescription()).isEqualTo("Index 'invalid_idx' not found.");
+
+    // ifExists=true
+    indexName = "invalid_idx";
+    RestUtils.delete(
+        authToken,
+        String.format(
+            "%s/v2/schemas/keyspaces/%s/tables/%s/indexes/%s?ifExists=true",
+            restUrlBase, keyspaceName, tableName, indexName),
+        HttpStatus.SC_NO_CONTENT);
+  }
+
   /*
   /************************************************************************
   /* Helper methods for setting up tests
@@ -401,6 +1287,37 @@ private void createSimpleTestTable(String keyspaceName, String tableName) {
     }
   }
 
+  private void createTestTable(
+      String tableName, List<String> columns, List<String> partitionKey, List<String> clusteringKey)
+      throws IOException {
+    TableAdd tableAdd = new TableAdd();
+    tableAdd.setName(tableName);
+
+    List<ColumnDefinition> columnDefinitions =
+        columns.stream()
+            .map(x -> x.split(" "))
+            .map(y -> new ColumnDefinition(y[0], y[1]))
+            .collect(Collectors.toList());
+    tableAdd.setColumnDefinitions(columnDefinitions);
+
+    PrimaryKey primaryKey = new PrimaryKey();
+    primaryKey.setPartitionKey(partitionKey);
+    if (clusteringKey != null) {
+      primaryKey.setClusteringKey(clusteringKey);
+    }
+    tableAdd.setPrimaryKey(primaryKey);
+
+    String body =
+        RestUtils.post(
+            authToken,
+            String.format("%s/v2/schemas/keyspaces/%s/tables", restUrlBase, keyspaceName),
+            objectMapper.writeValueAsString(tableAdd),
+            HttpStatus.SC_CREATED);
+
+    TableResponse tableResponse = objectMapper.readValue(body, TableResponse.class);
+    assertThat(tableResponse.getName()).isEqualTo(tableName);
+  }
+
   private void createComplexTestTable(String keyspaceName, String tableName) {
     TableAdd tableAdd = new TableAdd();
     tableAdd.setName(tableName);
@@ -429,6 +1346,33 @@ private void createComplexTestTable(String keyspaceName, String tableName) {
     }
   }
 
+  private void createTestTableWithClustering(String keyspaceName, String tableName)
+      throws IOException {
+    TableAdd tableAdd = new TableAdd();
+    tableAdd.setName(tableName);
+
+    List<ColumnDefinition> columnDefinitions = new ArrayList<>();
+
+    columnDefinitions.add(new ColumnDefinition("id", "int"));
+    columnDefinitions.add(new ColumnDefinition("lastName", "text"));
+    columnDefinitions.add(new ColumnDefinition("firstName", "text"));
+    columnDefinitions.add(new ColumnDefinition("age", "int", true));
+    columnDefinitions.add(new ColumnDefinition("expense_id", "int"));
+
+    tableAdd.setColumnDefinitions(columnDefinitions);
+
+    PrimaryKey primaryKey = new PrimaryKey();
+    primaryKey.setPartitionKey(Collections.singletonList("id"));
+    primaryKey.setClusteringKey(Collections.singletonList("expense_id"));
+    tableAdd.setPrimaryKey(primaryKey);
+
+    RestUtils.post(
+        authToken,
+        String.format("%s/v2/schemas/keyspaces/%s/tables", restUrlBase, keyspaceName),
+        objectMapper.writeValueAsString(tableAdd),
+        HttpStatus.SC_CREATED);
+  }
+
   private <T> T readWrappedRESTResponse(String body, Class<T> wrappedType) {
     JavaType wrapperType =
         objectMapper
```
### Patch: testing/src/main/java/io/stargate/it/http/RestApiv2Test.java
```diff
@@ -21,8 +21,6 @@
 
 import com.datastax.oss.driver.api.core.CqlSession;
 import com.datastax.oss.driver.api.core.cql.ResultSet;
-import com.datastax.oss.driver.api.core.cql.Row;
-import com.datastax.oss.driver.api.core.cql.SimpleStatement;
 import com.datastax.oss.driver.shaded.guava.common.collect.ImmutableMap;
 import com.fasterxml.jackson.core.type.TypeReference;
 import com.fasterxml.jackson.databind.JavaType;
@@ -44,13 +42,11 @@
 import io.stargate.web.restapi.models.RESTResponseWrapper;
 import io.stargate.web.restapi.models.SuccessResponse;
 import io.stargate.web.restapi.models.TableAdd;
-import io.stargate.web.restapi.models.TableOptions;
 import io.stargate.web.restapi.models.TableResponse;
 import java.io.IOException;
 import java.lang.reflect.Method;
 import java.util.ArrayList;
 import java.util.Arrays;
-import java.util.Collection;
 import java.util.Collections;
 import java.util.HashMap;
 import java.util.HashSet;
@@ -147,363 +143,6 @@ public void setup(TestInfo testInfo, StargateConnectionInfo cluster) throws IOEx
   /************************************************************************
    */
 
-  @Test
-  public void createIndex(CqlSession session) throws IOException {
-    createKeyspace(keyspaceName);
-    tableName = "tbl_createtable_" + System.currentTimeMillis();
-    createTestTable(
-        tableName,
-        Arrays.asList("id text", "firstName text", "lastName text", "email list<text>"),
-        Collections.singletonList("id"),
-        null);
-
-    IndexAdd indexAdd = new IndexAdd();
-    indexAdd.setColumn("firstName");
-    indexAdd.setName("test_idx");
-    indexAdd.setIfNotExists(false);
-
-    String body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-            objectMapper.writeValueAsString(indexAdd),
-            HttpStatus.SC_CREATED);
-    SuccessResponse successResponse =
-        objectMapper.readValue(body, new TypeReference<SuccessResponse>() {});
-    assertThat(successResponse.getSuccess()).isTrue();
-
-    List<Row> rows = session.execute("SELECT * FROM system_schema.indexes;").all();
-    assertThat(rows.stream().anyMatch(i -> "test_idx".equals(i.getString("index_name")))).isTrue();
-
-    // don't create and index if it already exists and don't throw error
-    indexAdd.setIfNotExists(true);
-    body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-            objectMapper.writeValueAsString(indexAdd),
-            HttpStatus.SC_CREATED);
-    successResponse = objectMapper.readValue(body, new TypeReference<SuccessResponse>() {});
-    assertThat(successResponse.getSuccess()).isTrue();
-
-    // throw error if index already exists
-    indexAdd.setIfNotExists(false);
-    body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-            objectMapper.writeValueAsString(indexAdd),
-            HttpStatus.SC_BAD_REQUEST);
-
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription())
-        .isEqualTo("Bad request: An index named test_idx already exists");
-
-    // successufully index a collection
-    indexAdd.setColumn("email");
-    indexAdd.setName(null);
-    indexAdd.setKind(IndexKind.VALUES);
-    body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-            objectMapper.writeValueAsString(indexAdd),
-            HttpStatus.SC_CREATED);
-    successResponse = objectMapper.readValue(body, new TypeReference<SuccessResponse>() {});
-    assertThat(successResponse.getSuccess()).isTrue();
-  }
-
-  @Test
-  public void createCustomIndex(CqlSession session) throws IOException {
-    // TODO remove this when we figure out how to enable SAI indexes in Cassandra 4
-    assumeThat(isCassandra4())
-        .as(
-            "Disabled because it is currently not possible to enable SAI indexes "
-                + "on a Cassandra 4 backend")
-        .isFalse();
-
-    createKeyspace(keyspaceName);
-    tableName = "tbl_createtable_" + System.currentTimeMillis();
-    createTestTable(
-        tableName,
-        Arrays.asList("id text", "firstName text", "lastName text", "email list<text>"),
-        Collections.singletonList("id"),
-        null);
-
-    IndexAdd indexAdd = new IndexAdd();
-    String indexType = "org.apache.cassandra.index.sasi.SASIIndex";
-    indexAdd.setColumn("lastName");
-    indexAdd.setName("test_custom_idx");
-    indexAdd.setType(indexType);
-    indexAdd.setIfNotExists(false);
-    indexAdd.setKind(null);
-
-    Map<String, String> options = new HashMap<>();
-    options.put("mode", "CONTAINS");
-    indexAdd.setOptions(options);
-
-    String body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-            objectMapper.writeValueAsString(indexAdd),
-            HttpStatus.SC_CREATED);
-    SuccessResponse successResponse =
-        objectMapper.readValue(body, new TypeReference<SuccessResponse>() {});
-    assertThat(successResponse.getSuccess()).isTrue();
-
-    Collection<Row> rows = session.execute("SELECT * FROM system_schema.indexes;").all();
-    Optional<Row> row =
-        rows.stream().filter(i -> "test_custom_idx".equals(i.getString("index_name"))).findFirst();
-    Map<String, String> optionsReturned = row.get().getMap("options", String.class, String.class);
-
-    assertThat(optionsReturned.get("class_name")).isEqualTo(indexType);
-    assertThat(optionsReturned.get("target")).isEqualTo("\"lastName\"");
-    assertThat(optionsReturned.get("mode")).isEqualTo("CONTAINS");
-  }
-
-  @Test
-  public void createInvalidIndex() throws IOException {
-    createKeyspace(keyspaceName);
-    String tableName = "tbl_createtable_" + System.currentTimeMillis();
-    createTestTable(
-        tableName,
-        Arrays.asList("id text", "firstName text", "email list<text>"),
-        Collections.singletonList("id"),
-        null);
-
-    // invalid table
-    IndexAdd indexAdd = new IndexAdd();
-    indexAdd.setColumn("firstName");
-    String body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/invalid_table/indexes", host, keyspaceName),
-            objectMapper.writeValueAsString(indexAdd),
-            HttpStatus.SC_NOT_FOUND);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_NOT_FOUND);
-    assertThat(response.getDescription()).isEqualTo("Table 'invalid_table' not found in keyspace.");
-
-    // invalid column
-    indexAdd.setColumn("invalid_column");
-    body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-            objectMapper.writeValueAsString(indexAdd),
-            HttpStatus.SC_NOT_FOUND);
-
-    response = objectMapper.readValue(body, ApiError.class);
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_NOT_FOUND);
-    assertThat(response.getDescription()).isEqualTo("Column 'invalid_column' not found in table.");
-
-    // invalid index kind
-    indexAdd.setColumn("firstName");
-    indexAdd.setKind(IndexKind.ENTRIES);
-    body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-            objectMapper.writeValueAsString(indexAdd),
-            HttpStatus.SC_BAD_REQUEST);
-
-    response = objectMapper.readValue(body, ApiError.class);
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription())
-        .isEqualTo("Bad request: Indexing entries can only be used with a map");
-  }
-
-  @Test
-  public void listAllIndexes(CqlSession session) throws IOException {
-    createKeyspace(keyspaceName);
-    tableName = "tbl_createtable_" + System.currentTimeMillis();
-    createTestTable(
-        tableName,
-        Arrays.asList("id text", "firstName text", "email list<text>"),
-        Collections.singletonList("id"),
-        null);
-
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-            HttpStatus.SC_OK);
-    assertThat(body).isEqualTo("[]");
-
-    IndexAdd indexAdd = new IndexAdd();
-    indexAdd.setColumn("firstName");
-    indexAdd.setName("test_idx");
-    indexAdd.setIfNotExists(false);
-
-    RestUtils.post(
-        authToken,
-        String.format(
-            "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-        objectMapper.writeValueAsString(indexAdd),
-        HttpStatus.SC_CREATED);
-
-    body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-            HttpStatus.SC_OK);
-
-    List<Map<String, Object>> data =
-        objectMapper.readValue(body, new TypeReference<List<Map<String, Object>>>() {});
-
-    assertThat(data.stream().anyMatch(m -> "test_idx".equals(m.get("index_name")))).isTrue();
-  }
-
-  @Test
-  public void dropIndex(CqlSession session) throws IOException {
-    createKeyspace(keyspaceName);
-    tableName = "tbl_createtable_" + System.currentTimeMillis();
-    createTestTable(
-        tableName,
-        Arrays.asList("id text", "firstName text", "email list<text>"),
-        Collections.singletonList("id"),
-        null);
-
-    IndexAdd indexAdd = new IndexAdd();
-    indexAdd.setColumn("firstName");
-    indexAdd.setName("test_idx");
-    indexAdd.setIfNotExists(false);
-
-    RestUtils.post(
-        authToken,
-        String.format(
-            "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes", host, keyspaceName, tableName),
-        objectMapper.writeValueAsString(indexAdd),
-        HttpStatus.SC_CREATED);
-
-    SimpleStatement selectIndexes =
-        SimpleStatement.newInstance(
-            "SELECT * FROM system_schema.indexes WHERE keyspace_name = ? AND table_name = ?",
-            keyspaceName,
-            tableName);
-    List<Row> rows = session.execute(selectIndexes).all();
-    assertThat(rows.size()).isEqualTo(1);
-
-    String indexName = "test_idx";
-    RestUtils.delete(
-        authToken,
-        String.format(
-            "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes/%s",
-            host, keyspaceName, tableName, indexName),
-        HttpStatus.SC_NO_CONTENT);
-
-    rows = session.execute(selectIndexes).all();
-    assertThat(rows.size()).isEqualTo(0);
-
-    indexName = "invalid_idx";
-    String body =
-        RestUtils.delete(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes/%s",
-                host, keyspaceName, tableName, indexName),
-            HttpStatus.SC_NOT_FOUND);
-
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_NOT_FOUND);
-    assertThat(response.getDescription()).isEqualTo("Index 'invalid_idx' not found.");
-
-    // ifExists=true
-    indexName = "invalid_idx";
-    RestUtils.delete(
-        authToken,
-        String.format(
-            "%s:8082/v2/schemas/keyspaces/%s/tables/%s/indexes/%s?ifExists=true",
-            host, keyspaceName, tableName, indexName),
-        HttpStatus.SC_NO_CONTENT);
-  }
-
-  @Test
-  public void createTableWithNullOptions() throws IOException {
-    createKeyspace(keyspaceName);
-
-    TableAdd tableAdd = new TableAdd();
-    tableAdd.setName("t1");
-
-    List<ColumnDefinition> columnDefinitions = new ArrayList<>();
-
-    columnDefinitions.add(new ColumnDefinition("id", "uuid"));
-    columnDefinitions.add(new ColumnDefinition("lastName", "text"));
-    columnDefinitions.add(new ColumnDefinition("firstName", "text"));
-
-    tableAdd.setColumnDefinitions(columnDefinitions);
-
-    PrimaryKey primaryKey = new PrimaryKey();
-    primaryKey.setPartitionKey(Collections.singletonList("id"));
-    tableAdd.setPrimaryKey(primaryKey);
-    tableAdd.setTableOptions(null);
-
-    String body =
-        RestUtils.post(
-            authToken,
-            String.format("%s:8082/v2/schemas/keyspaces/%s/tables", host, keyspaceName),
-            objectMapper.writeValueAsString(tableAdd),
-            HttpStatus.SC_CREATED);
-
-    NameResponse response = objectMapper.readValue(body, NameResponse.class);
-    assertThat(response.name).isEqualTo(tableAdd.getName());
-  }
-
-  @Test
-  public void createTableMissingClustering() throws IOException {
-    createKeyspace(keyspaceName);
-    TableAdd tableAdd = new TableAdd();
-    tableAdd.setName(tableName);
-
-    List<ColumnDefinition> columnDefinitions = new ArrayList<>();
-
-    columnDefinitions.add(new ColumnDefinition("pk1", "int"));
-    columnDefinitions.add(new ColumnDefinition("ck1", "int"));
-
-    tableAdd.setColumnDefinitions(columnDefinitions);
-
-    PrimaryKey primaryKey = new PrimaryKey();
-    primaryKey.setPartitionKey(Collections.singletonList("pk1"));
-    primaryKey.setClusteringKey(Collections.singletonList("ck1"));
-    tableAdd.setPrimaryKey(primaryKey);
-
-    tableAdd.setTableOptions(new TableOptions(0, null));
-
-    String body =
-        RestUtils.post(
-            authToken,
-            String.format("%s:8082/v2/schemas/keyspaces/%s/tables", host, keyspaceName),
-            objectMapper.writeValueAsString(tableAdd),
-            HttpStatus.SC_CREATED);
-
-    NameResponse response = objectMapper.readValue(body, NameResponse.class);
-    assertThat(response.name).isEqualTo(tableAdd.getName());
-
-    body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s?raw=true",
-                host, keyspaceName, tableName),
-            HttpStatus.SC_OK);
-
-    TableResponse table = objectMapper.readValue(body, TableResponse.class);
-    assertThat(table.getTableOptions().getClusteringExpression().get(0).getOrder())
-        .isEqualTo("ASC");
-  }
-
   /*
   /************************************************************************
   /* Test methods for Row Access CRUD operations
@@ -2111,476 +1750,31 @@ public void deleteRowsMixedClusteringAndCK() throws IOException {
   /************************************************************************
    */
 
+  /*
+  /************************************************************************
+  /* Test methods for User-Defined Type (UDT) CRUD operations
+  /************************************************************************
+   */
+
   @Test
-  public void getColumns() throws IOException {
+  public void createUdt() throws IOException {
     createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
 
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns", host, keyspaceName, tableName),
-            HttpStatus.SC_OK);
-    List<ColumnDefinition> columns =
-        readWrappedRESTResponse(body, new TypeReference<List<ColumnDefinition>>() {});
-    assertThat(columns)
-        .anySatisfy(
-            value ->
-                assertThat(value)
-                    .usingRecursiveComparison()
-                    .isEqualTo(new ColumnDefinition("id", "uuid", false)));
-  }
+    // create UDT
+    String udtString =
+        "{\"name\": \"udt1\", \"fields\":"
+            + "[{\"name\":\"firstname\",\"typeDefinition\":\"text\"},"
+            + "{\"name\":\"birthdate\",\"typeDefinition\":\"date\"}]}";
 
-  @Test
-  public void getColumnsRaw() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
+    RestUtils.post(
+        authToken,
+        String.format("%s:8082/v2/schemas/keyspaces/%s/types", host, keyspaceName),
+        udtString,
+        HttpStatus.SC_CREATED);
 
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns?raw=true",
-                host, keyspaceName, tableName),
-            HttpStatus.SC_OK);
-    List<ColumnDefinition> columns =
-        objectMapper.readValue(body, new TypeReference<List<ColumnDefinition>>() {});
-    assertThat(columns)
-        .anySatisfy(
-            value ->
-                assertThat(value)
-                    .usingRecursiveComparison()
-                    .isEqualTo(new ColumnDefinition("id", "uuid", false)));
-  }
-
-  @Test
-  public void getColumnsComplex() throws IOException {
-    createKeyspace(keyspaceName);
-    createComplexTable(keyspaceName, tableName);
-
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns", host, keyspaceName, tableName),
-            HttpStatus.SC_OK);
-    List<ColumnDefinition> columns =
-        readWrappedRESTResponse(body, new TypeReference<List<ColumnDefinition>>() {});
-    assertThat(columns)
-        .anySatisfy(
-            value ->
-                assertThat(value)
-                    .usingRecursiveComparison()
-                    .isEqualTo(new ColumnDefinition("col2", "frozen<set<boolean>>", false)));
-  }
-
-  @Test
-  public void getColumnsBadTable() throws IOException {
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns", host, keyspaceName, "foo"),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void getColumnsBadKeyspace() throws IOException {
-    createKeyspace(keyspaceName);
-
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns", host, "foo", tableName),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void getColumn() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, keyspaceName, tableName, "age"),
-            HttpStatus.SC_OK);
-    ColumnDefinition column = readWrappedRESTResponse(body, ColumnDefinition.class);
-    assertThat(column)
-        .usingRecursiveComparison()
-        .isEqualTo(new ColumnDefinition("age", "int", false));
-  }
-
-  @Test
-  public void getColumnNotFound() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, keyspaceName, tableName, "foo"),
-            HttpStatus.SC_NOT_FOUND);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_NOT_FOUND);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void getColumnRaw() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s?raw=true",
-                host, keyspaceName, tableName, "age"),
-            HttpStatus.SC_OK);
-    ColumnDefinition column = objectMapper.readValue(body, ColumnDefinition.class);
-    assertThat(column)
-        .usingRecursiveComparison()
-        .isEqualTo(new ColumnDefinition("age", "int", false));
-  }
-
-  @Test
-  public void getColumnComplex() throws IOException {
-    createKeyspace(keyspaceName);
-    createComplexTable(keyspaceName, tableName);
-
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, keyspaceName, tableName, "col1"),
-            HttpStatus.SC_OK);
-    ColumnDefinition column = readWrappedRESTResponse(body, ColumnDefinition.class);
-    assertThat(column)
-        .usingRecursiveComparison()
-        .isEqualTo(new ColumnDefinition("col1", "frozen<map<date, text>>", false));
-  }
-
-  @Test
-  public void getColumnBadTable() throws IOException {
-    createKeyspace(keyspaceName);
-
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, keyspaceName, "foo", "age"),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void getColumnBadKeyspace() throws IOException {
-    String body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, "foo", tableName, "age"),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void addColumn() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    ColumnDefinition columnDefinition = new ColumnDefinition("name", "text");
-
-    String body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns", host, keyspaceName, tableName),
-            objectMapper.writeValueAsString(columnDefinition),
-            HttpStatus.SC_CREATED);
-    @SuppressWarnings("unchecked")
-    Map<String, String> response = objectMapper.readValue(body, Map.class);
-
-    assertThat(response.get("name")).isEqualTo("name");
-
-    body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s?raw=true",
-                host, keyspaceName, tableName, "name"),
-            HttpStatus.SC_OK);
-    ColumnDefinition column = objectMapper.readValue(body, ColumnDefinition.class);
-    assertThat(column).usingRecursiveComparison().isEqualTo(columnDefinition);
-  }
-
-  @Test
-  public void addColumnBadType() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    ColumnDefinition columnDefinition = new ColumnDefinition("name", "badType");
-
-    String body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns", host, keyspaceName, tableName),
-            objectMapper.writeValueAsString(columnDefinition),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void addColumnStatic() throws IOException {
-    createKeyspace(keyspaceName);
-    createTableWithClustering(keyspaceName, tableName);
-
-    ColumnDefinition columnDefinition = new ColumnDefinition("balance", "float", true);
-
-    String body =
-        RestUtils.post(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns", host, keyspaceName, tableName),
-            objectMapper.writeValueAsString(columnDefinition),
-            HttpStatus.SC_CREATED);
-    @SuppressWarnings("unchecked")
-    Map<String, String> response = objectMapper.readValue(body, Map.class);
-
-    assertThat(response.get("name")).isEqualTo("balance");
-
-    body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s?raw=true",
-                host, keyspaceName, tableName, "balance"),
-            HttpStatus.SC_OK);
-    ColumnDefinition column = objectMapper.readValue(body, ColumnDefinition.class);
-    assertThat(column).usingRecursiveComparison().isEqualTo(columnDefinition);
-  }
-
-  @Test
-  public void updateColumn() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    ColumnDefinition columnDefinition = new ColumnDefinition("identifier", "uuid");
-
-    String body =
-        RestUtils.put(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, keyspaceName, tableName, "id"),
-            objectMapper.writeValueAsString(columnDefinition),
-            HttpStatus.SC_OK);
-    @SuppressWarnings("unchecked")
-    Map<String, String> response = objectMapper.readValue(body, Map.class);
-
-    assertThat(response.get("name")).isEqualTo("identifier");
-
-    body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s?raw=true",
-                host, keyspaceName, tableName, "identifier"),
-            HttpStatus.SC_OK);
-    ColumnDefinition column = objectMapper.readValue(body, ColumnDefinition.class);
-    assertThat(column).usingRecursiveComparison().isEqualTo(columnDefinition);
-  }
-
-  @Test
-  public void updateColumnNotFound() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    ColumnDefinition columnDefinition = new ColumnDefinition("name", "text");
-
-    String body =
-        RestUtils.put(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, keyspaceName, tableName, "notFound"),
-            objectMapper.writeValueAsString(columnDefinition),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void updateColumnBadTable() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    ColumnDefinition columnDefinition = new ColumnDefinition("name", "text");
-
-    String body =
-        RestUtils.put(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, keyspaceName, "foo", "age"),
-            objectMapper.writeValueAsString(columnDefinition),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void updateColumnBadKeyspace() throws IOException {
-    ColumnDefinition columnDefinition = new ColumnDefinition("name", "text");
-
-    String body =
-        RestUtils.put(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, "foo", tableName, "age"),
-            objectMapper.writeValueAsString(columnDefinition),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void deleteColumn() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    RestUtils.delete(
-        authToken,
-        String.format(
-            "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-            host, keyspaceName, tableName, "age"),
-        HttpStatus.SC_NO_CONTENT);
-  }
-
-  @Test
-  public void deleteColumnNotFound() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    RestUtils.delete(
-        authToken,
-        String.format(
-            "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-            host, keyspaceName, tableName, "foo"),
-        HttpStatus.SC_BAD_REQUEST);
-  }
-
-  @Test
-  public void deleteColumnBadTable() throws IOException {
-    createKeyspace(keyspaceName);
-
-    String body =
-        RestUtils.delete(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, keyspaceName, "foo", "age"),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void deleteColumnBadKeyspace() throws IOException {
-    String body =
-        RestUtils.delete(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, "foo", tableName, "age"),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  @Test
-  public void deleteColumnPartitionKey() throws IOException {
-    createKeyspace(keyspaceName);
-    createTable(keyspaceName, tableName);
-
-    String body =
-        RestUtils.delete(
-            authToken,
-            String.format(
-                "%s:8082/v2/schemas/keyspaces/%s/tables/%s/columns/%s",
-                host, keyspaceName, tableName, "id"),
-            HttpStatus.SC_BAD_REQUEST);
-    ApiError response = objectMapper.readValue(body, ApiError.class);
-
-    assertThat(response.getCode()).isEqualTo(HttpStatus.SC_BAD_REQUEST);
-    assertThat(response.getDescription()).isNotEmpty();
-  }
-
-  /*
-  /************************************************************************
-  /* Test methods for User-Defined Type (UDT) CRUD operations
-  /************************************************************************
-   */
-
-  @Test
-  public void createUdt() throws IOException {
-    createKeyspace(keyspaceName);
-
-    // create UDT
-    String udtString =
-        "{\"name\": \"udt1\", \"fields\":"
-            + "[{\"name\":\"firstname\",\"typeDefinition\":\"text\"},"
-            + "{\"name\":\"birthdate\",\"typeDefinition\":\"date\"}]}";
-
-    RestUtils.post(
-        authToken,
-        String.format("%s:8082/v2/schemas/keyspaces/%s/types", host, keyspaceName),
-        udtString,
-        HttpStatus.SC_CREATED);
-
-    // throws error because same name, but ifNotExists = false
-    String response =
-        RestUtils.post(
+    // throws error because same name, but ifNotExists = false
+    String response =
+        RestUtils.post(
             authToken,
             String.format("%s:8082/v2/schemas/keyspaces/%s/types", host, keyspaceName),
             udtString,
@@ -2883,67 +2077,6 @@ public void listAllTypes() throws IOException {
     assertThat(fields.get(0).get("typeDefinition")).isEqualTo("text");
   }
 
-  @Test
-  public void testMixedCaseTable() throws IOException {
-    createKeyspace(keyspaceName);
-
-    String tableName = "MixedCaseTable";
-    TableAdd tableAdd = new TableAdd();
-    tableAdd.setName(tableName);
-
-    List<ColumnDefinition> columnDefinitions = new ArrayList<>();
-
-    columnDefinitions.add(new ColumnDefinition("ID", "uuid"));
-    columnDefinitions.add(new ColumnDefinition("Lastname", "text"));
-    columnDefinitions.add(new ColumnDefinition("Firstname", "text"));
-    tableAdd.setColumnDefinitions(columnDefinitions);
-
-    PrimaryKey primaryKey = new PrimaryKey();
-    primaryKey.setPartitionKey(Collections.singletonList("ID"));
-    tableAdd.setPrimaryKey(primaryKey);
-
-    // ensure table name is preserved
-    String body =
-        RestUtils.post(
-            authToken,
-            String.format("%s:8082/v2/schemas/keyspaces/%s/tables", host, keyspaceName),
-            objectMapper.writeValueAsString(tableAdd),
-            HttpStatus.SC_CREATED);
-
-    TableResponse tableResponse =
-        objectMapper.readValue(body, new TypeReference<TableResponse>() {});
-    assertThat(tableResponse.getName()).isEqualTo(tableName);
-
-    // insert a row
-    String rowIdentifier = UUID.randomUUID().toString();
-    Map<String, String> row = new HashMap<>();
-    row.put("ID", rowIdentifier);
-    row.put("Firstname", "John");
-    row.put("Lastname", "Doe");
-
-    RestUtils.post(
-        authToken,
-        String.format("%s:8082/v2/keyspaces/%s/%s", host, keyspaceName, tableName),
-        objectMapper.writeValueAsString(row),
-        HttpStatus.SC_CREATED);
-
-    // retrieve the row by ID and ensure column names are as expected
-    String whereClause = String.format("{\"ID\":{\"$eq\":\"%s\"}}", rowIdentifier);
-    body =
-        RestUtils.get(
-            authToken,
-            String.format(
-                "%s:8082/v2/keyspaces/%s/%s?where=%s", host, keyspaceName, tableName, whereClause),
-            HttpStatus.SC_OK);
-
-    ListOfMapsGetResponseWrapper getResponseWrapper =
-        LIST_OF_MAPS_GETRESPONSE_READER.readValue(body);
-    List<Map<String, Object>> data = getResponseWrapper.getData();
-    assertThat(data.get(0).get("ID")).isEqualTo(rowIdentifier);
-    assertThat(data.get(0).get("Firstname")).isEqualTo("John");
-    assertThat(data.get(0).get("Lastname")).isEqualTo("Doe");
-  }
-
   /*
   /************************************************************************
   /* Helper methods for setting up tests
@@ -2969,7 +2102,7 @@ private void createTable(String keyspaceName, String tableName) throws IOExcepti
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/schemas/keyspaces/%s/tables", host, keyspaceName),
+        String.format("%s/v2/schemas/keyspaces/%s/tables", restUrlBase, keyspaceName),
         objectMapper.writeValueAsString(tableAdd),
         HttpStatus.SC_CREATED);
   }
@@ -2997,40 +2130,16 @@ private void createTestTable(
     String body =
         RestUtils.post(
             authToken,
-            String.format("%s:8082/v2/schemas/keyspaces/%s/tables", host, keyspaceName),
+            String.format("%s/v2/schemas/keyspaces/%s/tables", restUrlBase, keyspaceName),
             objectMapper.writeValueAsString(tableAdd),
             HttpStatus.SC_CREATED);
 
-    TableResponse tableResponse =
-        objectMapper.readValue(body, new TypeReference<TableResponse>() {});
+    TableResponse tableResponse = objectMapper.readValue(body, TableResponse.class);
     assertThat(tableResponse.getName()).isEqualTo(tableName);
   }
 
-  private void createComplexTable(String keyspaceName, String tableName) throws IOException {
-    TableAdd tableAdd = new TableAdd();
-    tableAdd.setName(tableName);
-
-    List<ColumnDefinition> columnDefinitions = new ArrayList<>();
-
-    columnDefinitions.add(new ColumnDefinition("pk0", "uuid"));
-    columnDefinitions.add(new ColumnDefinition("col1", "frozen<map<date, text>>"));
-    columnDefinitions.add(new ColumnDefinition("col2", "frozen<set<boolean>>"));
-    columnDefinitions.add(new ColumnDefinition("col3", "frozen<tuple<duration, inet>>"));
-
-    tableAdd.setColumnDefinitions(columnDefinitions);
-
-    PrimaryKey primaryKey = new PrimaryKey();
-    primaryKey.setPartitionKey(Collections.singletonList("pk0"));
-    tableAdd.setPrimaryKey(primaryKey);
-
-    RestUtils.post(
-        authToken,
-        String.format("%s:8082/v2/schemas/keyspaces/%s/tables", host, keyspaceName),
-        objectMapper.writeValueAsString(tableAdd),
-        HttpStatus.SC_CREATED);
-  }
-
-  private void createTableWithClustering(String keyspaceName, String tableName) throws IOException {
+  private void createTestTableWithClustering(String keyspaceName, String tableName)
+      throws IOException {
     TableAdd tableAdd = new TableAdd();
     tableAdd.setName(tableName);
 
@@ -3051,12 +2160,12 @@ private void createTableWithClustering(String keyspaceName, String tableName) th
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/schemas/keyspaces/%s/tables", host, keyspaceName),
+        String.format("%s/v2/schemas/keyspaces/%s/tables", restUrlBase, keyspaceName),
         objectMapper.writeValueAsString(tableAdd),
         HttpStatus.SC_CREATED);
   }
 
-  private void createTableWithMixedClustering(String keyspaceName, String tableName)
+  private void createTestTableWithMixedClustering(String keyspaceName, String tableName)
       throws IOException {
     TableAdd tableAdd = new TableAdd();
     tableAdd.setName(tableName);
@@ -3079,7 +2188,7 @@ private void createTableWithMixedClustering(String keyspaceName, String tableNam
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/schemas/keyspaces/%s/tables", host, keyspaceName),
+        String.format("%s/v2/schemas/keyspaces/%s/tables", restUrlBase, keyspaceName),
         objectMapper.writeValueAsString(tableAdd),
         HttpStatus.SC_CREATED);
   }
@@ -3090,7 +2199,7 @@ private void createKeyspace(String keyspaceName) throws IOException {
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/schemas/keyspaces", host),
+        String.format("%s/v2/schemas/keyspaces", restUrlBase),
         createKeyspaceRequest,
         HttpStatus.SC_CREATED);
   }
@@ -3117,8 +2226,7 @@ private void createTestIndex(
                 restUrlBase, keyspaceName, tableName),
             objectMapper.writeValueAsString(indexAdd),
             HttpStatus.SC_CREATED);
-    SuccessResponse successResponse =
-        objectMapper.readValue(body, new TypeReference<SuccessResponse>() {});
+    SuccessResponse successResponse = objectMapper.readValue(body, SuccessResponse.class);
     assertThat(successResponse.getSuccess()).isTrue();
   }
 
@@ -3144,7 +2252,7 @@ private List<Map<String, String>> insertTestTableRows(List<List<String>> rows)
 
       RestUtils.post(
           authToken,
-          String.format("%s:8082/v2/keyspaces/%s/%s", host, keyspaceName, tableName),
+          String.format("%s/v2/keyspaces/%s/%s", restUrlBase, keyspaceName, tableName),
           objectMapper.writeValueAsString(rowMap),
           HttpStatus.SC_CREATED);
     }
@@ -3166,7 +2274,7 @@ private void insertTypedTestTableRows(List<Map<String, Object>> rows) throws IOE
 
   private String setupClusteringTestCase() throws IOException {
     createKeyspace(keyspaceName);
-    createTableWithClustering(keyspaceName, tableName);
+    createTestTableWithClustering(keyspaceName, tableName);
 
     String rowIdentifier = "1";
     Map<String, String> row = new HashMap<>();
@@ -3176,7 +2284,7 @@ private String setupClusteringTestCase() throws IOException {
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/keyspaces/%s/%s", host, keyspaceName, tableName),
+        String.format("%s/v2/keyspaces/%s/%s", restUrlBase, keyspaceName, tableName),
         objectMapper.writeValueAsString(row),
         HttpStatus.SC_CREATED);
 
@@ -3187,7 +2295,7 @@ private String setupClusteringTestCase() throws IOException {
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/keyspaces/%s/%s", host, keyspaceName, tableName),
+        String.format("%s/v2/keyspaces/%s/%s", restUrlBase, keyspaceName, tableName),
         objectMapper.writeValueAsString(row),
         HttpStatus.SC_CREATED);
 
@@ -3198,7 +2306,7 @@ private String setupClusteringTestCase() throws IOException {
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/keyspaces/%s/%s", host, keyspaceName, tableName),
+        String.format("%s/v2/keyspaces/%s/%s", restUrlBase, keyspaceName, tableName),
         objectMapper.writeValueAsString(row),
         HttpStatus.SC_CREATED);
 
@@ -3209,7 +2317,7 @@ private String setupClusteringTestCase() throws IOException {
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/keyspaces/%s/%s", host, keyspaceName, tableName),
+        String.format("%s/v2/keyspaces/%s/%s", restUrlBase, keyspaceName, tableName),
         objectMapper.writeValueAsString(row),
         HttpStatus.SC_CREATED);
 
@@ -3218,7 +2326,7 @@ private String setupClusteringTestCase() throws IOException {
 
   private void setupMixedClusteringTestCase() throws IOException {
     createKeyspace(keyspaceName);
-    createTableWithMixedClustering(keyspaceName, tableName);
+    createTestTableWithMixedClustering(keyspaceName, tableName);
 
     Map<String, String> row = new HashMap<>();
     row.put("pk0", "1");
@@ -3230,7 +2338,7 @@ private void setupMixedClusteringTestCase() throws IOException {
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/keyspaces/%s/%s", host, keyspaceName, tableName),
+        String.format("%s/v2/keyspaces/%s/%s", restUrlBase, keyspaceName, tableName),
         objectMapper.writeValueAsString(row),
         HttpStatus.SC_CREATED);
 
@@ -3244,7 +2352,7 @@ private void setupMixedClusteringTestCase() throws IOException {
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/keyspaces/%s/%s", host, keyspaceName, tableName),
+        String.format("%s/v2/keyspaces/%s/%s", restUrlBase, keyspaceName, tableName),
         objectMapper.writeValueAsString(row),
         HttpStatus.SC_CREATED);
 
@@ -3258,7 +2366,7 @@ private void setupMixedClusteringTestCase() throws IOException {
 
     RestUtils.post(
         authToken,
-        String.format("%s:8082/v2/keyspaces/%s/%s", host, keyspaceName, tableName),
+        String.format("%s/v2/keyspaces/%s/%s", restUrlBase, keyspaceName, tableName),
         objectMapper.writeValueAsString(row),
         HttpStatus.SC_CREATED);
   }
@@ -3272,16 +2380,6 @@ private <T> T readWrappedRESTResponse(String body, Class<T> wrappedType) throws
     return wrapped.getData();
   }
 
-  private <T> T readWrappedRESTResponse(String body, TypeReference wrappedType) throws IOException {
-    JavaType resolvedWrappedType = objectMapper.getTypeFactory().constructType(wrappedType);
-    JavaType wrapperType =
-        objectMapper
-            .getTypeFactory()
-            .constructParametricType(RESTResponseWrapper.class, resolvedWrappedType);
-    RESTResponseWrapper<T> wrapped = objectMapper.readValue(body, wrapperType);
-    return wrapped.getData();
-  }
-
   // Simple helper method for the case of single primary key, standard auth token;
   // will use "raw" Rows endpoint to access entries, return as Tree (JsonNode)
   private JsonNode readRawRowsBySingleKey(String keyspaceName, String tableName, Object rowId)
```

## Row 5
commit_url: https://github.com/errai/errai/commit/058e50b10da2d9fc3fcd7736f2d1215c591f9c42
rm_type: Remove Thrown Exception Type
rm_description: Remove Thrown Exception Type Exception in method public testNestedForeachLoops() : void from class org.jboss.errai.ioc.tests.rebind.LoopBuilderTest
file_path: errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/LoopBuilderTest.java
left_side: [{"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/LoopBuilderTest.java", "startLine": 132, "endLine": 132, "startColumn": 47, "endColumn": 56, "codeElementType": "TYPE", "description": "removed thrown exception type", "codeElement": "Exception"}, {"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/LoopBuilderTest.java", "startLine": 131, "endLine": 150, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testNestedForeachLoops() : void"}]
right_side: [{"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/LoopBuilderTest.java", "startLine": 135, "endLine": 154, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "method declaration with removed thrown exception type", "codeElement": "public testNestedForeachLoops() : void"}]

### Patch: errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/LoopBuilderTest.java
```diff
@@ -30,7 +30,6 @@
 import org.jboss.errai.ioc.rebind.ioc.codegen.Context;
 import org.jboss.errai.ioc.rebind.ioc.codegen.Statement;
 import org.jboss.errai.ioc.rebind.ioc.codegen.Variable;
-import org.jboss.errai.ioc.rebind.ioc.codegen.builder.LoopBuilder;
 import org.jboss.errai.ioc.rebind.ioc.codegen.builder.impl.ContextBuilder;
 import org.jboss.errai.ioc.rebind.ioc.codegen.builder.impl.StatementBuilder;
 import org.jboss.errai.ioc.rebind.ioc.codegen.exception.InvalidExpressionException;
@@ -49,13 +48,7 @@
 public class LoopBuilderTest extends AbstractStatementBuilderTest implements LoopBuilderTestResult {
 
   @Test
-  public void testForeachLoop() throws Exception {
-    Statement createObject = StatementBuilder.create()
-        .newObject(String.class);
-
-    Statement createAnotherObject = StatementBuilder.create()
-        .newObject(Object.class);
-
+  public void testForeachLoopWithStringInParameterizedList() {
     String foreachWithListOfStrings = StatementBuilder.create()
         .addVariable("list", new TypeLiteral<List<String>>() {})
         .loadVariable("list")
@@ -64,7 +57,12 @@ public void testForeachLoop() throws Exception {
 
     assertEquals("failed to generate foreach loop using a List<String>",
         FOREACH_RESULT_STRING_IN_LIST, foreachWithListOfStrings);
-    
+  }
+
+  @Test
+  public void testForeachLoopWithStringInArray() {
+    Statement createObject = StatementBuilder.create().newObject(String.class);
+
     String foreachWithStringArray = StatementBuilder.create()
         .addVariable("list", String[].class)
         .loadVariable("list")
@@ -75,7 +73,13 @@ public void testForeachLoop() throws Exception {
 
     assertEquals("failed to generate foreach loop using a String[]",
         FOREACH_RESULT_STRING_IN_ARRAY_ONE_STATEMENT, foreachWithStringArray);
-    
+  }
+
+  @Test
+  public void testForeachLoopWithStringInList() {
+    Statement createObject = StatementBuilder.create().newObject(String.class);
+    Statement createAnotherObject = StatementBuilder.create().newObject(Object.class);
+
     String foreachWithList = StatementBuilder.create()
         .addVariable("list", List.class)
         .loadVariable("list")
@@ -89,7 +93,7 @@ public void testForeachLoop() throws Exception {
   }
 
   @Test
-  public void testForeachLoopWithUndefinedCollection() throws Exception {
+  public void testForeachLoopWithUndefinedCollection() {
     try {
       StatementBuilder.create()
           .loadVariable("list")
@@ -104,7 +108,7 @@ public void testForeachLoopWithUndefinedCollection() throws Exception {
   }
 
   @Test
-  public void testForeachLoopWithProvidedLoopVarType() throws Exception {
+  public void testForeachLoopWithProvidedLoopVarType() {
     Builder builder = StatementBuilder.create()
         .addVariable("list", new TypeLiteral<List<String>>() {})
         .loadVariable("list")
@@ -129,7 +133,7 @@ public void testForeachLoopWithProvidedLoopVarType() throws Exception {
   }
 
   @Test
-  public void testNestedForeachLoops() throws Exception {
+  public void testNestedForeachLoops() {
     Statement createObject = StatementBuilder.create().newObject(String.class);
 
     Builder outerLoop = StatementBuilder.create()
@@ -150,7 +154,7 @@ public void testNestedForeachLoops() throws Exception {
   }
 
   @Test
-  public void testForeachLoopWithInvalidCollectionType() throws Exception {
+  public void testForeachLoopWithInvalidCollectionType() {
 
     try {
       StatementBuilder.create()
@@ -167,7 +171,7 @@ public void testForeachLoopWithInvalidCollectionType() throws Exception {
   }
 
   @Test
-  public void testForeachLoopWithInvoke() throws Exception {
+  public void testForeachLoopWithInvoke() {
     Builder loop = StatementBuilder.create()
         .addVariable("map", Map.class)
         .loadVariable("map")
@@ -179,29 +183,32 @@ public void testForeachLoopWithInvoke() throws Exception {
   }
 
   @Test
-  public void testForeachLoopWithLiterals() throws Exception {
-    LoopBuilder loopBuilder = StatementBuilder.create()
+  public void testForeachLoopWithLiterals() {
+    String s = StatementBuilder.create()
         .loadLiteral(new String[] { "s1", "s2" })
         .foreach("s")
         .append(StatementBuilder.create().loadVariable("s").invoke("getBytes"))
-        .finish();
+        .finish().toJavaString();
 
     assertEquals("failed to generate foreach loop using a literal String array",
-        FOREACH_RESULT_LITERAL_STRING_ARRAY, loopBuilder.toJavaString());
+        FOREACH_RESULT_LITERAL_STRING_ARRAY, s);
+  }
 
+  @Test
+  public void testForeachLoopWithProvidedContext() {
     Context c = ContextBuilder.create().addVariable(Variable.create("s", String.class)).getContext();
-    loopBuilder = StatementBuilder.create(c)
+    String s = StatementBuilder.create(c)
         .loadLiteral(new String[] { "s1", "s2" })
         .foreach("s")
         .append(StatementBuilder.create().loadVariable("s").invoke("getBytes"))
-        .finish();
+        .finish().toJavaString();
 
     assertEquals("failed to generate foreach loop using a literal String array",
-        FOREACH_RESULT_LITERAL_STRING_ARRAY, loopBuilder.toJavaString());
+        FOREACH_RESULT_LITERAL_STRING_ARRAY, s);
   }
 
   @Test
-  public void testWhileLoopWithInvalidExpressions() {
+  public void testWhileLoopWithInvalidExpression() {
     try {
       StatementBuilder.create()
           .addVariable("n", Integer.class)
@@ -229,72 +236,100 @@ public void testWhileLoopWithInvalidExpressions() {
   }
 
   @Test
-  public void testWhileLoop() {
+  public void testWhileLoopWithEmptyExpressionWithoutBody() {
     String s = StatementBuilder.create()
         .addVariable("b", Boolean.class)
         .loadVariable("b")
         .while_().finish().toJavaString();
 
     assertEquals("failed to generate empty while loop", WHILE_RESULT_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testWhileLoopWithEmptyExpressionWithBody() {
+    String s = StatementBuilder.create()
         .addVariable("b", Boolean.class)
         .loadVariable("b")
         .while_()
           .append(StatementBuilder.create().loadVariable("b").assignValue(false))
         .finish().toJavaString();
 
     assertEquals("failed to generate while loop with body", WHILE_RESULT_WITH_BODY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testWhileLoopWithNullCheck() {
+    String s = StatementBuilder.create()
         .addVariable("str", String.class)
         .loadVariable("str")
         .while_(BooleanOperator.NotEquals, null)
         .finish().toJavaString();
 
-    assertEquals("failed to generate while loop with rhs (null check) and body", 
+    assertEquals("failed to generate while loop with rhs (null check) and no body",
         WHILE_RESULT_RHS_NULL_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testWhileLoopWithExpression() {
+    String s = StatementBuilder.create()
         .addVariable("str", String.class)
         .loadVariable("str")
         .invoke("length")
         .while_(BooleanOperator.GreaterThanOrEqual, 2)
         .finish().toJavaString();
 
-    assertEquals("failed to generate while loop with rhs and body", WHILE_RESULT_RHS_EMPTY, s);
+    assertEquals("failed to generate while loop with rhs and no body", WHILE_RESULT_RHS_EMPTY, s);
+  }
+
+  @Test
+  public void testWhileLoopUnchainedWithExpression() {
+    Context ctx = Context.create().addVariable("str", String.class);
+    String s = StatementBuilder.create(ctx)
+        .while_(Bool.expr(Stmt.create().loadVariable("str").invoke("length"), BooleanOperator.GreaterThanOrEqual, 2))
+        .finish().toJavaString();
 
-    s = StatementBuilder.create()
+    assertEquals("failed to generate while loop with rhs and no body", WHILE_RESULT_RHS_EMPTY, s);
+  }
+
+  @Test
+  public void testWhileLoopWithNestedExpressions() {
+    String s = StatementBuilder.create()
         .addVariable("str", String.class)
         .while_(Bool.expr(
             Bool.expr(Variable.get("str"), BooleanOperator.NotEquals, null),
             BooleanOperator.And,
             Bool.expr(Stmt.create().loadVariable("str").invoke("length"), BooleanOperator.GreaterThan, 0)))
         .finish().toJavaString();
 
-    assertEquals("failed to generate while loop with nested expression", WHILE_RESULT_NESTED_EMPTY, s);
+    assertEquals("failed to generate while loop with nested expression and no body", WHILE_RESULT_NESTED_EMPTY, s);
   }
 
   @Test
-  public void testForLoop() {
+  public void testForLoopWithoutInitializer() {
     String s = StatementBuilder.create()
         .addVariable("i", Integer.class)
         .for_(Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100))
         .finish().toJavaString();
 
     assertEquals("failed to generate for loop without initializer",
         FOR_RESULT_NO_INITIALIZER_NO_COUNTING_EXP_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testForLoopWithInitializer() {
+    String s = StatementBuilder.create()
         .addVariable("i", Integer.class)
         .for_(StatementBuilder.create().loadVariable("i").assignValue(0),
             Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100))
         .finish().toJavaString();
 
     assertEquals("failed to generate for loop with initializer",
         FOR_RESULT_INITIALIZER_NO_COUNTING_EXP_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testForLoopWithInitializerAndCountingExpression() {
+    String s = StatementBuilder.create()
         .addVariable("i", Integer.class)
         .for_(StatementBuilder.create().loadVariable("i").assignValue(0),
             Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100),
@@ -303,17 +338,23 @@ public void testForLoop() {
 
     assertEquals("failed to generate for loop with initializer and counting expression",
         FOR_RESULT_INITIALIZER_COUNTING_EXP_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testForLoopWithInitializerAndChainedLhs() {
+    String s = StatementBuilder.create()
         .addVariable("i", Integer.class, 0)
         .loadVariable("i")
         .for_(Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100))
         .finish().toJavaString();
 
     assertEquals("failed to generate for loop with initializer and chained lhs",
         FOR_RESULT_CHAINED_INITIALIZER_NO_COUNTING_EXP_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testForLoopWithInitializerAndCountingExpressionAndChainedLhs() {
+    String s = StatementBuilder.create()
         .addVariable("i", Integer.class, 0)
         .loadVariable("i")
         .for_(Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100),
@@ -322,8 +363,11 @@ public void testForLoop() {
 
     assertEquals("failed to generate for loop with initializer, counting expression and chained lhs",
         FOR_RESULT_CHAINED_INITIALIZER_COUNTING_EXP_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testForLoopUnchainedWithDeclaringInitializerAndCountingExpression() {
+    String s = StatementBuilder.create()
         .for_(ContextBuilder.create().declareVariable("i", int.class).initializeWith(0),
             Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100),
             StatementBuilder.create().loadVariable("i").assignValue(AssignmentOperator.PreIncrementAssign, 1))
@@ -335,7 +379,7 @@ public void testForLoop() {
   }
 
   @Test
-  public void testDoWhileLoop() {
+  public void testDoWhileLoopWithoutOperatorAndRhs() {
     String s = StatementBuilder.create()
         .addVariable("b", Boolean.class)
         .do_()
@@ -344,9 +388,27 @@ public void testDoWhileLoop() {
         .while_(Bool.expr(Variable.get("b")))
         .toJavaString();
 
-    assertEquals("failed to generate for do whileloop with simple expression", DOWHILE_RESULT_SIMPLE_EXPRESSION, s);
+    assertEquals("failed to generate for do whileloop with simple expression (no operator and rhs)",
+        DOWHILE_RESULT_SIMPLE_EXPRESSION, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testDoWhileLoopUnchainedWithoutOperatorAndRhs() {
+    Context ctx = Context.create().addVariable("b", Boolean.class);
+    String s = StatementBuilder.create(ctx)
+        .do_()
+          .append(StatementBuilder.create().loadVariable("b").assignValue(false))
+        .finish()
+        .while_(Bool.expr(Variable.get("b")))
+        .toJavaString();
+
+    assertEquals("failed to generate for do whileloop with simple expression (no operator and rhs)",
+        DOWHILE_RESULT_SIMPLE_EXPRESSION, s);
+  }
+
+  @Test
+  public void testDoWhileLoopWithNestedExpressions() {
+    String s = StatementBuilder.create()
         .addVariable("str", String.class)
         .do_()
           .append(StatementBuilder.create().loadStatic(System.class, "out").invoke("println", Variable.get("str")))
```

## Row 6
commit_url: https://github.com/b3dgs/lionengine/commit/649a57eca8fc3e0ca0b86fd6b7c0f2941e8bd234
rm_type: Add Class Modifier
rm_description: Add Class Modifier final in class com.b3dgs.lionengine.ConstantTest
file_path: lionengine-core/src/test/java/com/b3dgs/lionengine/ConstantTest.java
left_side: [{"filePath": "lionengine-core/src/test/java/com/b3dgs/lionengine/ConstantTest.java", "startLine": 27, "endLine": 132, "startColumn": 0, "endColumn": 2, "codeElementType": "TYPE_DECLARATION", "description": "original class declaration", "codeElement": "com.b3dgs.lionengine.ConstantTest"}]
right_side: [{"filePath": "lionengine-core/src/test/java/com/b3dgs/lionengine/ConstantTest.java", "startLine": 27, "endLine": 131, "startColumn": 0, "endColumn": 2, "codeElementType": "TYPE_DECLARATION", "description": "class declaration with added modifier", "codeElement": "com.b3dgs.lionengine.ConstantTest"}]

### Patch: lionengine-core/src/test/java/com/b3dgs/lionengine/ConstantTest.java
```diff
@@ -25,9 +25,9 @@
 import com.b3dgs.lionengine.util.UtilTests;
 
 /**
- * Test the constants.
+ * Test {@link Constant}.
  */
-public class ConstantTest
+public final class ConstantTest
 {
     /**
      * Test the constructor.
@@ -93,7 +93,7 @@ public void testConstants()
     }
 
     /**
-     * Test the system property with default value.
+     * Test system property with default value.
      */
     @Test
     public void testSystemPropertyDefault()
@@ -102,7 +102,7 @@ public void testSystemPropertyDefault()
     }
 
     /**
-     * Test the system property with existing value.
+     * Test system property with existing value.
      */
     @Test
     public void testSystemPropertyExists()
@@ -111,7 +111,7 @@ public void testSystemPropertyExists()
     }
 
     /**
-     * Test the system property with security not allowing it.
+     * Test system property with security not allowing it.
      */
     @Test
     public void testSystemPropertySecurityException()
@@ -127,6 +127,5 @@ public void testSystemPropertySecurityException()
             System.setSecurityManager(null);
         }
         Verbose.info("****************************************************************************************");
-
     }
 }
```

## Row 7
commit_url: https://github.com/FasterXML/jackson-modules-java8/commit/8c3d032fb564148c39b5fdf1cdd6e314e6af1cb5
rm_type: Move And Inline Method
rm_description: Move And Inline Method private read(reader ObjectReader, json String) : LocalDateTime moved from class com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserTest to class com.fasterxml.jackson.datatype.jsr310.deser.LocalDateDeserTest & inlined to private expectSuccess(reader ObjectReader, exp Object, json String) : void
file_path: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java; datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java
left_side: [{"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java", "startLine": 483, "endLine": 485, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "inlined method declaration", "codeElement": "private read(reader ObjectReader, json String) : LocalDateTime"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java", "startLine": 484, "endLine": 484, "startColumn": 9, "endColumn": 53, "codeElementType": "RETURN_STATEMENT", "description": "inlined code from inlined method declaration", "codeElement": null}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 333, "endLine": 337, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration before inline", "codeElement": "private expectSuccess(reader ObjectReader, exp Object, json String) : void"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 334, "endLine": 334, "startColumn": 33, "endColumn": 51, "codeElementType": "METHOD_INVOCATION", "description": "inlined method invocation", "codeElement": "read(reader,json)"}]
right_side: [{"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 358, "endLine": 362, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration after inline", "codeElement": "private expectSuccess(reader ObjectReader, exp Object, json String) : void"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 359, "endLine": 359, "startColumn": 9, "endColumn": 70, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "inlined code in target method declaration", "codeElement": null}]

### Patch: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java
```diff
@@ -128,7 +128,20 @@ public void testBadDeserializationAsString02() throws Exception
             verifyException(e, "from String \"");
         }
     }
-    
+
+    @Test
+    public void testDeserializationWithTypeInfo01() throws Exception
+    {
+        ObjectMapper mapper = mapperBuilder()
+               .addMixIn(Temporal.class, MockObjectConfiguration.class)
+               .build();
+        LocalDate date = LocalDate.of(2005, Month.NOVEMBER, 5);
+        Temporal value = mapper.readValue(
+                "[\"" + LocalDate.class.getName() + "\",\"" + date.toString() + "\"]", Temporal.class
+                );
+        assertEquals("The value is not correct.", date, value);
+    }
+
     /*
     /**********************************************************
     /* Deserialization from alternate representation: int (number
@@ -170,7 +183,6 @@ public void testStricDeserializeFromInt() throws Exception
     /*
     /**********************************************************
     /* Tests for empty string handling
-     */
     /**********************************************************
      */
 
@@ -227,7 +239,7 @@ public void testStrictDeserializFromEmptyString() throws Exception {
     public void testDeserializationAsArrayDisabled() throws Throwable
     {
         try {
-            read(READER, "[\"2000-01-01\"]");
+            READER.readValue("[\"2000-01-01\"]");
             fail("expected MismatchedInputException");
         } catch (MismatchedInputException e) {
             verifyException(e, "Unexpected token (VALUE_STRING) within Array");
@@ -238,7 +250,41 @@ public void testDeserializationAsArrayDisabled() throws Throwable
     public void testDeserializationAsEmptyArrayDisabled() throws Throwable
     {
         // works even without the feature enabled
-        assertNull(read(READER, "[]"));
+        assertNull(READER.readValue("[]"));
+    }
+
+    @Test
+    public void testDeserializationAsArrayEnabled() throws Throwable
+    {
+        LocalDate actual = READER
+                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS)
+                .readValue("[\"2000-01-01\"]");
+        assertEquals("The value is not correct.", LocalDate.of(2000, 1, 1), actual);
+    }
+
+    @Test
+    public void testDeserializationAsEmptyArrayEnabled() throws Throwable
+    {
+        LocalDate value = READER
+                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS,
+                        DeserializationFeature.ACCEPT_EMPTY_ARRAY_AS_NULL_OBJECT)
+                .readValue("[]");
+        assertNull(value);
+    }
+
+    /*
+    /**********************************************************
+    /* Custom format
+    /**********************************************************
+     */
+
+    // for [datatype-jsr310#37]
+    @Test
+    public void testCustomFormat() throws Exception
+    {
+        Wrapper w = MAPPER.readValue("{\"value\":\"2015_07_28T13:53+0300\"}", Wrapper.class);
+        LocalDate date = w.value; 
+        assertEquals(28, date.getDayOfMonth());
     }
 
     /*
@@ -294,29 +340,10 @@ public void testDeserializationCaseInsensitiveDisabled_InvalidDate() throws Thro
         	expectFailure(reader, json);
         }
     }
-    
-    @Test
-    public void testDeserializationAsArrayEnabled() throws Throwable
-    {
-        LocalDate actual = READER
-                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS)
-                .readValue("[\"2000-01-01\"]");
-        assertEquals("The value is not correct.", LocalDate.of(2000, 1, 1), actual);
-    }
 
-    @Test
-    public void testDeserializationAsEmptyArrayEnabled() throws Throwable
-    {
-        LocalDate value = READER
-                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS,
-                        DeserializationFeature.ACCEPT_EMPTY_ARRAY_AS_NULL_OBJECT)
-                .readValue("[]");
-        assertNull(value);
-    }
-    
     private void expectFailure(ObjectReader reader, String json) throws Throwable {
         try {
-            read(reader, json);
+            reader.readValue(aposToQuotes(json));
             fail("expected DateTimeParseException");
         } catch (JsonProcessingException e) {
             if (e.getCause() == null) {
@@ -325,56 +352,14 @@ private void expectFailure(ObjectReader reader, String json) throws Throwable {
             if (!(e.getCause() instanceof DateTimeParseException)) {
                 throw e.getCause();
             }
-        } catch (IOException e) {
-            throw e;
         }
     }
 
     private void expectSuccess(ObjectReader reader, Object exp, String json) throws IOException {
-        final LocalDate value = read(reader, json);
-        notNull(value);
-        expect(exp, value);
-    }
-
-    private LocalDate read(ObjectReader reader, final String json) throws IOException {
-        return reader.readValue(aposToQuotes(json));
-    }
-
-    private static void notNull(Object value) {
+        final LocalDate value = reader.readValue(aposToQuotes(json));
         assertNotNull("The value should not be null.", value);
-    }
-
-    private static void expect(Object exp, Object value) {
         assertEquals("The value is not correct.", exp,  value);
     }
-
-    @Test
-    public void testDeserializationWithTypeInfo01() throws Exception
-    {
-        ObjectMapper mapper = mapperBuilder()
-               .addMixIn(Temporal.class, MockObjectConfiguration.class)
-               .build();
-        LocalDate date = LocalDate.of(2005, Month.NOVEMBER, 5);
-        Temporal value = mapper.readValue(
-                "[\"" + LocalDate.class.getName() + "\",\"" + date.toString() + "\"]", Temporal.class
-                );
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    /*
-    /**********************************************************
-    /* Custom format
-    /**********************************************************
-     */
-
-    // for [datatype-jsr310#37]
-    @Test
-    public void testCustomFormat() throws Exception
-    {
-        Wrapper w = MAPPER.readValue("{\"value\":\"2015_07_28T13:53+0300\"}", Wrapper.class);
-        LocalDate date = w.value; 
-        assertEquals(28, date.getDayOfMonth());
-    }
 }
```
### Patch: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java
```diff
@@ -459,14 +459,14 @@ public void testDeserializationCaseInsensitiveDisabled_InvalidDate() throws Thro
     }
 
     private void expectSuccess(ObjectReader reader, Object exp, String json) throws IOException {
-        final LocalDateTime value = read(reader, json);
-        notNull(value);
-        expect(exp, value);
+        final LocalDateTime value = reader.readValue(aposToQuotes(json));
+        assertNotNull("The value should not be null.", value);
+        assertEquals("The value is not correct.", exp,  value);
     }
 
     private void expectFailure(ObjectReader reader, String json) throws Throwable {
         try {
-            read(reader, json);
+            reader.readValue(aposToQuotes(json));
             fail("expected DateTimeParseException");
         } catch (JsonProcessingException e) {
             if (e.getCause() == null) {
@@ -475,20 +475,6 @@ private void expectFailure(ObjectReader reader, String json) throws Throwable {
             if (!(e.getCause() instanceof DateTimeParseException)) {
                 throw e.getCause();
             }
-        } catch (IOException e) {
-            throw e;
         }
     }
-
-    private LocalDateTime read(ObjectReader reader, final String json) throws IOException {
-        return reader.readValue(aposToQuotes(json));
-    }
-
-    private void notNull(Object value) {
-        assertNotNull("The value should not be null.", value);
-    }
-
-    private void expect(Object exp, Object value) {
-        assertEquals("The value is not correct.", exp,  value);
-    }
 }
```

## Row 8
commit_url: https://github.com/blackducksoftware/detect/commit/9ba649982b1172954289bfe6307ca135466728f2
rm_type: Replace Attribute With Variable
rm_description: Replace Attribute With Variable goModDependencyManager : GoModDependencyManager to dependencyManager : GoModDependencyManager in method package versionWithGitHash() : void from class com.synopsys.integration.detectable.detectables.go.gomod.process.GoModDependencyManagerTest
file_path: detectable/src/test/java/com/synopsys/integration/detectable/detectables/go/gomod/process/GoModDependencyManagerTest.java
left_side: [{"filePath": "detectable/src/test/java/com/synopsys/integration/detectable/detectables/go/gomod/process/GoModDependencyManagerTest.java", "startLine": 23, "endLine": 23, "startColumn": 35, "endColumn": 57, "codeElementType": "FIELD_DECLARATION", "description": "original variable declaration", "codeElement": "goModDependencyManager : GoModDependencyManager"}, {"filePath": "detectable/src/test/java/com/synopsys/integration/detectable/detectables/go/gomod/process/GoModDependencyManagerTest.java", "startLine": 67, "endLine": 67, "startColumn": 9, "endColumn": 98, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}]
right_side: [{"filePath": "detectable/src/test/java/com/synopsys/integration/detectable/detectables/go/gomod/process/GoModDependencyManagerTest.java", "startLine": 43, "endLine": 43, "startColumn": 32, "endColumn": 112, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "renamed variable declaration", "codeElement": "dependencyManager : GoModDependencyManager"}, {"filePath": "detectable/src/test/java/com/synopsys/integration/detectable/detectables/go/gomod/process/GoModDependencyManagerTest.java", "startLine": 44, "endLine": 44, "startColumn": 9, "endColumn": 86, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}]

### Patch: detectable/src/test/java/com/synopsys/integration/detectable/detectables/go/gomod/process/GoModDependencyManagerTest.java
```diff
@@ -1,14 +1,13 @@
 package com.synopsys.integration.detectable.detectables.go.gomod.process;
 
 import static org.junit.jupiter.api.Assertions.assertEquals;
-import static org.junit.jupiter.api.Assertions.assertFalse;
-import static org.junit.jupiter.api.Assertions.assertTrue;
+import static org.junit.jupiter.api.Assertions.assertNull;
 
 import java.util.Arrays;
-import java.util.List;
-import java.util.Optional;
+import java.util.Collections;
+
+import javax.annotation.Nullable;
 
-import org.junit.jupiter.api.BeforeAll;
 import org.junit.jupiter.api.Test;
 
 import com.synopsys.integration.bdio.model.dependency.Dependency;
@@ -17,94 +16,96 @@
 import com.synopsys.integration.detectable.detectables.go.gomod.model.ReplaceData;
 
 class GoModDependencyManagerTest {
-    static String MODULE_A_PATH = "example.io/module/a";
-    static String MODULE_B_PATH = "example.io/module/b";
-    static String MODULE_NO_VERSION_PATH = "example.io/module/no_version";
-    static GoModDependencyManager goModDependencyManager;
-    static ExternalIdFactory externalIdFactory;
-
-    @BeforeAll
-    static void init() {
-        GoListAllData moduleA = new GoListAllData();
-        moduleA.setPath(MODULE_A_PATH);
-        moduleA.setVersion("1.0.0");
-
-        GoListAllData moduleB = new GoListAllData();
-        moduleB.setPath(MODULE_B_PATH);
-        moduleB.setVersion("2.0.0");
-        ReplaceData replaceData = new ReplaceData();
-        replaceData.setPath(MODULE_A_PATH);
-        replaceData.setVersion("2.3.4");
-        moduleB.setReplace(replaceData);
-
-        GoListAllData noVersionModule = new GoListAllData();
-        noVersionModule.setPath(MODULE_NO_VERSION_PATH);
-        // Explicitly not setting a version here.
-
-        GoListAllData incompatibleModule = new GoListAllData();
-        incompatibleModule.setPath("example.io/incompatible");
-        incompatibleModule.setVersion("2.0.0+incompatible");
-
-        GoListAllData gitModule = new GoListAllData();
-        gitModule.setPath("example.io/hash");
-        gitModule.setVersion("version_with_hash-123abc-456xyz");
-
-        List<GoListAllData> goListAllData = Arrays.asList(moduleA, moduleB, incompatibleModule, gitModule, noVersionModule);
-        externalIdFactory = new ExternalIdFactory();
-        goModDependencyManager = new GoModDependencyManager(goListAllData, externalIdFactory);
+    @Test
+    void happyPathTest() {
+        String moduleName = "example.io/module/a";
+        String moduleVersion = "1.0.0";
+        GoModDependencyManager dependencyManager = createManagerWithModuleLoadedWith(moduleName, moduleVersion);
+        Dependency dependency = dependencyManager.getDependencyForModule(moduleName);
+        assertEquals(moduleName, dependency.getName());
+        assertEquals(moduleVersion, dependency.getVersion());
     }
 
     @Test
     void versionWithIncompatible() {
-        Dependency dependency = goModDependencyManager.getDependencyForModule("example.io/incompatible");
-        Optional<String> versionForModule = Optional.ofNullable(dependency.getVersion());
-        assertTrue(versionForModule.isPresent());
-        assertEquals("2.0.0", versionForModule.get());
+        String moduleName = "example.io/incompatible";
+        String moduleVersion = "2.0.0+incompatible";
+        GoModDependencyManager dependencyManager = createManagerWithModuleLoadedWith(moduleName, moduleVersion);
+        Dependency dependency = dependencyManager.getDependencyForModule(moduleName);
+        assertEquals(moduleName, dependency.getName());
+        assertEquals("2.0.0", dependency.getVersion(), "The '+incompatible' should have been stripped from the version.");
     }
 
     @Test
     void versionWithGitHash() {
-        Dependency dependency = goModDependencyManager.getDependencyForModule("example.io/hash");
-        Optional<String> versionForModule = Optional.ofNullable(dependency.getVersion());
-        assertTrue(versionForModule.isPresent());
-        assertEquals("456xyz", versionForModule.get());
+        String moduleName = "example.io/hash";
+        String moduleVersion = "version_with_sha1_hash-62ecb2f7638dbe3bcb6b4b92540333a8b61fcd1c";
+        GoModDependencyManager dependencyManager = createManagerWithModuleLoadedWith(moduleName, moduleVersion);
+        Dependency dependency = dependencyManager.getDependencyForModule(moduleName);
+        assertEquals(moduleName, dependency.getName());
+        assertEquals("62ecb2f7638dbe3bcb6b4b92540333a8b61fcd1c", dependency.getVersion(), "When a SHA1 is present, other version text should be stripped.");
     }
 
     @Test
-    void nonExistentModuleVersionTest() {
-        Dependency dependency = goModDependencyManager.getDependencyForModule("non-existent.io/module");
-        Optional<String> versionForModule = Optional.ofNullable(dependency.getVersion());
-        assertFalse(versionForModule.isPresent());
+    void versionWithDash() {
+        String moduleName = "example.io/dash";
+        String moduleVersion = "1.2.3-preview4";
+        GoModDependencyManager dependencyManager = createManagerWithModuleLoadedWith(moduleName, moduleVersion);
+        Dependency dependency = dependencyManager.getDependencyForModule(moduleName);
+        assertEquals(moduleName, dependency.getName());
+        assertEquals(moduleVersion, dependency.getVersion(), "The version does not contain a commit and should be unmodified.");
     }
 
     @Test
-    void happyPathTest() {
-        Dependency dependency = goModDependencyManager.getDependencyForModule(MODULE_A_PATH);
-        Optional<String> versionForModule = Optional.ofNullable(dependency.getVersion());
-        assertTrue(versionForModule.isPresent());
-        assertEquals("1.0.0", versionForModule.get());
+    void nonExistentModuleTest() {
+        String moduleName = "non-existent.io/module";
+        GoModDependencyManager dependencyManager = createManagerWithModuleLoadedWith("something-else", "1.2.3");
+        Dependency dependency = dependencyManager.getDependencyForModule(moduleName);
+        assertEquals(moduleName, dependency.getName(), "A dependency should have been created from the query.");
+        assertNull(dependency.getVersion(), "There should not be a version to match the given query.");
     }
 
     @Test
-    void replacementTest() {
-        Dependency dependencyForModule = goModDependencyManager.getDependencyForModule(MODULE_B_PATH);
-        assertEquals("2.3.4", dependencyForModule.getVersion(), "The version should be replaced.");
-        assertEquals(MODULE_A_PATH, dependencyForModule.getName(), "The path should be replaced.");
+    void nonExistentVersionTest() {
+        String moduleName = "non-existent.io/module";
+        GoModDependencyManager dependencyManager = createManagerWithModuleLoadedWith(moduleName, null);
+        Dependency dependency = dependencyManager.getDependencyForModule(moduleName);
+        assertEquals(moduleName, dependency.getName(), "A dependency should have been created from the query.");
+        assertNull(dependency.getVersion(), "There should not be a version to match the given query.");
     }
 
     @Test
-    void noVersionTest() {
-        Dependency dependency = goModDependencyManager.getDependencyForModule(MODULE_NO_VERSION_PATH);
-        Optional<String> versionForModule = Optional.ofNullable(dependency.getVersion());
-        assertFalse(versionForModule.isPresent(), "This module should have no version information.");
+    void moduleReplacementTest() {
+        String resolvedModulePath = "example.io/module/resolved";
+        String replacedModulePath = "example.io/module/replaced";
+
+        GoListAllData resolvedModule = new GoListAllData();
+        resolvedModule.setPath(resolvedModulePath);
+        resolvedModule.setVersion("1.0.0");
+
+        GoListAllData replacedModule = new GoListAllData();
+        replacedModule.setPath(replacedModulePath);
+        replacedModule.setVersion("2.0.0");
+        ReplaceData replaceData = new ReplaceData();
+        replaceData.setPath(resolvedModulePath);
+        replaceData.setVersion("2.3.4");
+        replacedModule.setReplace(replaceData);
+
+        GoModDependencyManager dependencyManager = new GoModDependencyManager(Arrays.asList(resolvedModule, replacedModule), new ExternalIdFactory());
+
+        Dependency resolvedDependency = dependencyManager.getDependencyForModule(resolvedModule.getPath());
+        assertEquals(resolvedModule.getPath(), resolvedDependency.getName());
+        assertEquals(resolvedModule.getVersion(), resolvedDependency.getVersion());
+
+        Dependency replacedDependency = dependencyManager.getDependencyForModule(replacedModulePath);
+        assertEquals(replaceData.getPath(), replacedDependency.getName(), "The dependency name (module path) should have been replaced.");
+        assertEquals(replaceData.getVersion(), replacedDependency.getVersion(), "The version should have been replaced.");
     }
 
-    @Test
-    void nonExistentModulePathTest() {
-        Dependency dependency = goModDependencyManager.getDependencyForModule("non-existent.io/module");
-        Optional<String> pathForModule = Optional.ofNullable(dependency.getName());
-        Optional<String> versionForModule = Optional.ofNullable(dependency.getVersion());
-        assertTrue(pathForModule.isPresent());
-        assertFalse(versionForModule.isPresent(), "If a module cannot be mapped to a dependency, a default dependency should be created with a null version.");
+    private GoModDependencyManager createManagerWithModuleLoadedWith(String modulePath, @Nullable String moduleVersion) {
+        GoListAllData module = new GoListAllData();
+        module.setPath(modulePath);
+        module.setVersion(moduleVersion);
+        return new GoModDependencyManager(Collections.singletonList(module), new ExternalIdFactory());
     }
 }
```

## Row 9
commit_url: https://github.com/apache/karaf/commit/100420f757c2bd6fe00a8d28c14a1388d665b8fe
rm_type: Assert Throws
rm_description: Assert Throws assertThrows(IllegalArgumentException.class,() -> { in method public testParseNoKeyValue() : void from class org.apache.karaf.event.command.EventSendCommandTest
file_path: event/src/test/java/org/apache/karaf/event/command/EventSendCommandTest.java
left_side: [{"filePath": "event/src/test/java/org/apache/karaf/event/command/EventSendCommandTest.java", "startLine": 82, "endLine": 82, "startColumn": 9, "endColumn": 64, "codeElementType": "EXPRESSION_STATEMENT", "description": "original code", "codeElement": "EventSendCommand.parse(Collections.singletonList(\"=\"));\n"}, {"filePath": "event/src/test/java/org/apache/karaf/event/command/EventSendCommandTest.java", "startLine": 80, "endLine": 83, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testParseNoKeyValue() : void"}]
right_side: [{"filePath": "event/src/test/java/org/apache/karaf/event/command/EventSendCommandTest.java", "startLine": 84, "endLine": 84, "startColumn": 13, "endColumn": 68, "codeElementType": "EXPRESSION_STATEMENT", "description": "assertThrows code", "codeElement": "EventSendCommand.parse(Collections.singletonList(\"=\"));\n"}, {"filePath": "event/src/test/java/org/apache/karaf/event/command/EventSendCommandTest.java", "startLine": 81, "endLine": 86, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "method declaration with introduced assertThrows", "codeElement": "public testParseNoKeyValue() : void"}]

### Patch: event/src/test/java/org/apache/karaf/event/command/EventSendCommandTest.java
```diff
@@ -25,6 +25,7 @@
 import static org.hamcrest.CoreMatchers.equalTo;
 import static org.junit.Assert.assertNotNull;
 import static org.junit.Assert.assertThat;
+import static org.junit.Assert.assertThrows;
 
 import java.util.Arrays;
 import java.util.Collections;
@@ -77,14 +78,19 @@ public void testParseNull() {
         assertThat(props.size(), equalTo(0));
     }
     
-    @Test(expected=IllegalArgumentException.class)
+    @Test
     public void testParseNoKeyValue() {
-        EventSendCommand.parse(Collections.singletonList("="));
+        assertThrows(IllegalArgumentException.class, () -> {
+            EventSendCommand.parse(Collections.singletonList("="));
+        });
     }
     
-    @Test(expected=IllegalArgumentException.class)
+    @Test
     public void testParseNoKey() {
-        EventSendCommand.parse(Collections.singletonList("=b"));
+        assertThrows(IllegalArgumentException.class, () -> {
+            EventSendCommand.parse(Collections.singletonList("=b"));
+        });
+
     }
     
     @Test
```

## Row 10
commit_url: https://github.com/MovingBlocks/Terasology/commit/c92f14ff5c5c73d849f7d6d0d2980846209ebead
rm_type: Extract Attribute
rm_description: Extract Attribute private SETTING_ID : SimpleUri in class org.terasology.config.flexible.SettingTest
file_path: engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java
left_side: [{"filePath": "engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java", "startLine": 72, "endLine": 73, "startColumn": 13, "endColumn": 76, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement with the initializer of the extracted attribute", "codeElement": null}]
right_side: [{"filePath": "engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java", "startLine": 33, "endLine": 33, "startColumn": 36, "endColumn": 90, "codeElementType": "FIELD_DECLARATION", "description": "extracted attribute declaration", "codeElement": "private SETTING_ID : SimpleUri"}, {"filePath": "engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java", "startLine": 74, "endLine": 75, "startColumn": 13, "endColumn": 76, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement with the name of the extracted attribute", "codeElement": null}]

### Patch: engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java
```diff
@@ -30,14 +30,16 @@
 
 @RunWith(Enclosed.class)
 public class SettingTest {
+    private static final SimpleUri SETTING_ID = new SimpleUri("engine-tests:TestSetting");
+
     public static class SetValue {
         private Setting<Integer> setting;
 
         private int eventResult;
 
         @Before
         public void setUp() {
-            setting = new SettingImpl<>(new SimpleUri("engine-tests:TestSetting"),
+            setting = new SettingImpl<>(SETTING_ID,
                     50, new RangedNumberValidator<>(0, 100, false, false));
 
             eventResult = -1;
@@ -69,7 +71,7 @@ public static class Subscribers {
 
         @Before
         public void setUp() {
-            setting = new SettingImpl<>(new SimpleUri("engine-tests:TestSetting"),
+            setting = new SettingImpl<>(SETTING_ID,
                     50, new RangedNumberValidator<>(0, 100, false, false));
 
             eventCallCount = 0;
@@ -94,51 +96,49 @@ public void testSetEventCall() {
 
             Random random = new FastRandom();
 
-            final int n = 50;
+            final int MAX_SET_VALUE_COUNT = 50;
             int expectedEventCallCount = 0;
 
-            for (int i = 0; i < n; i++) {
-                int r = random.nextInt(-50, 150);
-                expectedEventCallCount += setting.setValue(r) ? 1 : 0;
+            for (int i = 0; i < MAX_SET_VALUE_COUNT; i++) {
+                int randomInt = random.nextInt(-50, 150);
+                expectedEventCallCount += setting.setValue(randomInt) ? 1 : 0;
             }
 
             assertEquals(expectedEventCallCount, eventCallCount);
         }
 
         @Test
         public void testSubscribe() {
-            final int n = 10;
+            final int SUBSCRIBER_COUNT = 10;
 
-            for (int i = 0; i < n; i++) {
+            for (int i = 0; i < SUBSCRIBER_COUNT; i++) {
                 setting.subscribe(propertyChangeEvent -> eventCallCount++);
             }
 
             setting.setValue(30);
 
-            assertEquals(n, eventCallCount);
+            assertEquals(SUBSCRIBER_COUNT, eventCallCount);
         }
 
         @Test
         public void testUnsubscribe() {
-            int n = 10;
+            int subscriberCount = 10;
 
-            PropertyChangeListener[] listeners = new PropertyChangeListener[n];
+            PropertyChangeListener[] listeners = new PropertyChangeListener[subscriberCount];
 
-            for (int i = 0; i < n; i++) {
+            for (int i = 0; i < subscriberCount; i++) {
                 listeners[i] = propertyChangeEvent -> eventCallCount++;
                 setting.subscribe(listeners[i]);
             }
 
-            int halfN = n / 2;
-
-            for (int i = 0; i < new FastRandom().nextInt(halfN); i++) {
+            for (int i = 0; i < new FastRandom().nextInt(subscriberCount / 2); i++) {
                 setting.unsubscribe(listeners[i]);
-                n--;
+                subscriberCount--;
             }
 
             setting.setValue(30);
 
-            assertEquals(n, eventCallCount);
+            assertEquals(subscriberCount, eventCallCount);
         }
     }
 }
```

## Row 11
commit_url: https://github.com/AICP/frameworks_base/commit/669f02323f9c7298fdef79b44e1a512549d1411a
rm_type: Extract And Move Method
rm_description: Extract And Move Method public waitForIdleHandler(handlerThread HandlerThread, timeoutMs long) : void extracted from private waitForObserverToIdle() : void in class com.android.server.net.NetworkStatsObserversTest & moved to class com.android.internal.util.TestUtils
file_path: tests/net/java/com/android/server/net/NetworkStatsObserversTest.java
left_side: [{"filePath": "tests/net/java/com/android/server/net/NetworkStatsObserversTest.java", "startLine": 472, "endLine": 475, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "source method declaration before extraction", "codeElement": "private waitForObserverToIdle() : void"}, {"filePath": "tests/net/java/com/android/server/net/NetworkStatsObserversTest.java", "startLine": 473, "endLine": 473, "startColumn": 9, "endColumn": 80, "codeElementType": "EXPRESSION_STATEMENT", "description": "extracted code from source method declaration", "codeElement": null}]
right_side: [{"filePath": "tests/net/java/com/android/internal/util/TestUtils.java", "startLine": 29, "endLine": 35, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public waitForIdleHandler(handlerThread HandlerThread, timeoutMs long) : void"}, {"filePath": "tests/net/java/com/android/internal/util/TestUtils.java", "startLine": 34, "endLine": 34, "startColumn": 9, "endColumn": 65, "codeElementType": "EXPRESSION_STATEMENT", "description": "extracted code to extracted method declaration", "codeElement": null}, {"filePath": "tests/net/java/com/android/server/net/NetworkStatsObserversTest.java", "startLine": 473, "endLine": 476, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "source method declaration after extraction", "codeElement": "private waitForObserverToIdle() : void"}, {"filePath": "tests/net/java/com/android/server/net/NetworkStatsObserversTest.java", "startLine": 474, "endLine": 474, "startColumn": 9, "endColumn": 68, "codeElementType": "METHOD_INVOCATION", "description": "extracted method invocation", "codeElement": "waitForIdleHandler(mObserverHandlerThread,WAIT_TIMEOUT_MS)"}]

### Patch: tests/net/java/com/android/server/net/NetworkStatsObserversTest.java
```diff
@@ -27,6 +27,8 @@
 import static android.net.TrafficStats.MB_IN_BYTES;
 import static android.text.format.DateUtils.MINUTE_IN_MILLIS;
 
+import static com.android.internal.util.TestUtils.waitForIdleHandler;
+
 import static org.junit.Assert.assertEquals;
 import static org.junit.Assert.assertTrue;
 import static org.junit.Assert.fail;
@@ -56,7 +58,6 @@
 
 import com.android.internal.net.VpnInfo;
 import com.android.server.net.NetworkStatsService;
-import com.android.server.net.NetworkStatsServiceTest.IdleableHandlerThread;
 import com.android.server.net.NetworkStatsServiceTest.LatchedHandler;
 
 import java.util.ArrayList;
@@ -102,7 +103,7 @@ public class NetworkStatsObserversTest {
 
     private long mElapsedRealtime;
 
-    private IdleableHandlerThread mObserverHandlerThread;
+    private HandlerThread mObserverHandlerThread;
     private Handler mObserverNoopHandler;
 
     private LatchedHandler mHandler;
@@ -118,7 +119,7 @@ public class NetworkStatsObserversTest {
     public void setUp() throws Exception {
         MockitoAnnotations.initMocks(this);
 
-        mObserverHandlerThread = new IdleableHandlerThread("HandlerThread");
+        mObserverHandlerThread = new HandlerThread("HandlerThread");
         mObserverHandlerThread.start();
         final Looper observerLooper = mObserverHandlerThread.getLooper();
         mStatsObservers = new NetworkStatsObservers() {
@@ -319,7 +320,7 @@ public void testUpdateStats_deviceAccess_notifies() throws Exception {
                 xtSnapshot, uidSnapshot, mActiveIfaces, mActiveUidIfaces,
                 VPN_INFO, TEST_START);
         waitForObserverToIdle();
-        assertEquals(NetworkStatsManager.CALLBACK_LIMIT_REACHED, mHandler.mLastMessageType);
+        assertEquals(NetworkStatsManager.CALLBACK_LIMIT_REACHED, mHandler.lastMessageType);
     }
 
     @Test
@@ -356,7 +357,7 @@ public void testUpdateStats_defaultAccess_notifiesSameUid() throws Exception {
                 xtSnapshot, uidSnapshot, mActiveIfaces, mActiveUidIfaces,
                 VPN_INFO, TEST_START);
         waitForObserverToIdle();
-        assertEquals(NetworkStatsManager.CALLBACK_LIMIT_REACHED, mHandler.mLastMessageType);
+        assertEquals(NetworkStatsManager.CALLBACK_LIMIT_REACHED, mHandler.lastMessageType);
     }
 
     @Test
@@ -429,7 +430,7 @@ public void testUpdateStats_userAccess_usageSameUser_notifies() throws Exception
                 xtSnapshot, uidSnapshot, mActiveIfaces, mActiveUidIfaces,
                 VPN_INFO, TEST_START);
         waitForObserverToIdle();
-        assertEquals(NetworkStatsManager.CALLBACK_LIMIT_REACHED, mHandler.mLastMessageType);
+        assertEquals(NetworkStatsManager.CALLBACK_LIMIT_REACHED, mHandler.lastMessageType);
     }
 
     @Test
@@ -470,19 +471,7 @@ public void testUpdateStats_userAccess_usageAnotherUser_doesNotNotify() throws E
     }
 
     private void waitForObserverToIdle() {
-        waitForIdleLooper(mObserverHandlerThread.getLooper(), WAIT_TIMEOUT_MS);
-        waitForIdleLooper(mHandler.getLooper(), WAIT_TIMEOUT_MS);
-    }
-
-    // TODO: unify with ConnectivityService.waitForIdleHandler and
-    // NetworkServiceStatsTest.IdleableHandlerThread
-    private static void waitForIdleLooper(Looper looper, long timeoutMs) {
-        final ConditionVariable cv = new ConditionVariable();
-        final Handler handler = new Handler(looper);
-        handler.post(() -> cv.open());
-        if (!cv.block(timeoutMs)) {
-            fail("Looper did not become idle after " + timeoutMs + " ms");
-        }
+        waitForIdleHandler(mObserverHandlerThread, WAIT_TIMEOUT_MS);
+        waitForIdleHandler(mHandler, WAIT_TIMEOUT_MS);
     }
-
 }
```

## Row 12
commit_url: https://github.com/hyphanet/fred/commit/2e68720627ae6447ba12d712a9e6e4a123e66b95
rm_type: Merge Attribute
rm_description: Merge Attribute [totalTime : long, runsProcessed : int] to nativeTest : TestIntegers in class net.i2p.util.NativeBigIntegerTest
file_path: test/net/i2p/util/NativeBigIntegerTest.java
left_side: [{"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 32, "endLine": 32, "startColumn": 15, "endColumn": 28, "codeElementType": "FIELD_DECLARATION", "description": "merged attribute declaration", "codeElement": "totalTime : long"}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 27, "endLine": 27, "startColumn": 14, "endColumn": 27, "codeElementType": "FIELD_DECLARATION", "description": "merged attribute declaration", "codeElement": "runsProcessed : int"}]
right_side: [{"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 29, "endLine": 29, "startColumn": 15, "endColumn": 25, "codeElementType": "FIELD_DECLARATION", "description": "new attribute declaration", "codeElement": "nativeTest : TestIntegers"}]

### Patch: test/net/i2p/util/NativeBigIntegerTest.java
```diff
@@ -6,9 +6,10 @@
 import junit.framework.TestCase;
 
 public class NativeBigIntegerTest extends TestCase {
-	// Run with <code>ant -Dbenchmark=true</code> to do benchmark 
+	// Run with <code>ant -Dbenchmark=true</code> to do benchmark
 	private static final boolean BENCHMARK = Boolean.getBoolean("benchmark");
 	private static int numRuns = BENCHMARK ? 200 : 5;
+	private int runsProcessed;
 
 	/*
 	 * the sample numbers are elG generator/prime so we can test with reasonable
@@ -24,13 +25,10 @@ public class NativeBigIntegerTest extends TestCase {
 	        .toByteArray();
 
 	private SecureRandom rand;
-	private int runsProcessed;
-
-	private BigInteger jg;
-	private BigInteger jp;
 
-	private long totalTime = 0;
-	private long javaTime = 0;
+	TestIntegers nativeTest;
+	TestIntegers javaTest;
+	//TestIntegers java7Test;
 
 	protected void setUp() throws Exception {
 		if (!NativeBigInteger.isNative())
@@ -41,64 +39,65 @@ protected void setUp() throws Exception {
 		rand.nextBoolean();
 		printInfo("DEBUG: Random number generator warmed up");
 
-		jg = new BigInteger(_sampleGenerator);
-		jp = new BigInteger(_samplePrime);
+		byte[] randbytes = (new BigInteger(2048, rand)).toByteArray();
+
+		javaTest = new TestIntegers(
+			"java",
+			new BigInteger(_sampleGenerator),
+			new BigInteger(_samplePrime),
+			new BigInteger(randbytes)
+		);
+
+		nativeTest = new TestIntegers(
+			"native",
+			new NativeBigInteger(_sampleGenerator),
+			new NativeBigInteger(_samplePrime),
+			new NativeBigInteger(randbytes)
+		);
+
+		/*java7Test = new TestIntegers7(
+			"java7",
+			new java7.math.BigInteger(_sampleGenerator),
+			new java7.math.BigInteger(_samplePrime),
+			new java7.math.BigInteger(randbytes)
+		);*/
 
-		totalTime = javaTime = 0;
 	}
 
 	protected void tearDown() throws Exception {
-		printInfo("INFO: run time: " + totalTime + "ms (" + (totalTime / (runsProcessed + 1)) + "ms each)");
 		if (numRuns == runsProcessed)
 			printInfo("INFO: " + runsProcessed + " runs complete without any errors");
 		else
 			printError("ERROR: " + runsProcessed + " runs until we got an error");
 
-		printInfo("native run time: \t" + totalTime + "ms (" + (totalTime / (runsProcessed + 1)) + "ms each)");
-		printInfo("java run time:   \t" + javaTime + "ms (" + (javaTime / (runsProcessed + 1)) + "ms each)");
-		printInfo("native = " + ((totalTime * 100.0d) / (double) javaTime) + "% of pure java time");
+		printInfo(nativeTest.getReport());
+		printInfo(javaTest.getReport());
+		//printInfo(java7Test.getReport());
+		printInfo("native = " + (nativeTest.getTime() * 100.0 / javaTest.getTime()) + "% of pure java time");
+		//printInfo("java 7 = " + (java7Test.getTime() * 100.0 / javaTest.getTime()) + "% of pure java time");
 	}
 
 	public void testModPow() {
 		for (runsProcessed = 0; runsProcessed < numRuns; runsProcessed++) {
-			BigInteger bi = new BigInteger(2048, rand);
-			NativeBigInteger g = new NativeBigInteger(_sampleGenerator);
-			NativeBigInteger p = new NativeBigInteger(_samplePrime);
-			NativeBigInteger k = new NativeBigInteger(1, bi.toByteArray());
-
-			long beforeModPow = System.currentTimeMillis();
-			BigInteger myValue = g.modPow(k, p);
-			long afterModPow = System.currentTimeMillis();
-			BigInteger jval = jg.modPow(bi, jp);
-			long afterJavaModPow = System.currentTimeMillis();
-
-			totalTime += (afterModPow - beforeModPow);
-			javaTime += (afterJavaModPow - afterModPow);
+			BigInteger nativeVal = nativeTest.modPow();
+			BigInteger javaVal = javaTest.modPow();
+			//BigInteger java7Val = java7Test.modPow();
 
-			assertEquals(jval, myValue);
+			assertEquals(nativeVal, javaVal);
+			//assertEquals(javaVal, java7Val);
+			//assertEquals(java7Val, nativeVal);
 		}
 	}
 
 	public void testDoubleValue() {
-		BigInteger jg = new BigInteger(_sampleGenerator);
-
-		int MULTIPLICATOR = 50000; //Run the doubleValue() calls within a loop since they are pretty fast.. 
 		for (runsProcessed = 0; runsProcessed < numRuns; runsProcessed++) {
-			NativeBigInteger g = new NativeBigInteger(_sampleGenerator);
-			long beforeDoubleValue = System.currentTimeMillis();
-			double dNative = 0;
-			for (int mult = 0; mult < MULTIPLICATOR; mult++)
-				dNative = g.doubleValue();
-			long afterDoubleValue = System.currentTimeMillis();
-			double jval = 0;
-			for (int mult = 0; mult < MULTIPLICATOR; mult++)
-				jval = jg.doubleValue();
-			long afterJavaDoubleValue = System.currentTimeMillis();
-
-			totalTime += (afterDoubleValue - beforeDoubleValue);
-			javaTime += (afterJavaDoubleValue - afterDoubleValue);
-
-			assertEquals(jval, dNative, 0);
+			double nativeVal = nativeTest.doubleValue();
+			double javaVal = javaTest.doubleValue();
+			//double java7Val = java7Test.doubleValue();
+
+			assertEquals(nativeVal, javaVal);
+			//assertEquals(javaVal, java7Val);
+			//assertEquals(java7Val, nativeVal);
 		}
 	}
 
@@ -111,4 +110,87 @@ private static void printError(String info) {
 		if (BENCHMARK)
 			System.err.println(info);
 	}
+
+	static class TestIntegers {
+
+		final String name;
+		final BigInteger g;
+		final BigInteger p;
+		final BigInteger k;
+
+		protected long time;
+		protected int runs;
+
+		final static int DOUBLE_VAL_TEST_RUNS = 0x10000; // Run the doubleValue() calls within a loop since they are pretty fast..
+
+		public TestIntegers(String n, BigInteger g, BigInteger p, BigInteger k) {
+			name = n;
+			this.g = g;
+			this.p = p;
+			this.k = k;
+		}
+
+		public BigInteger modPow() {
+			long start = System.currentTimeMillis();
+			BigInteger r = g.modPow(p, k);
+			time += System.currentTimeMillis() - start;
+			++runs;
+			return r;
+		}
+
+		public double doubleValue() {
+			long start = System.currentTimeMillis();
+			double r = 0.0;
+			for (int i=0; i < DOUBLE_VAL_TEST_RUNS; ++i) {
+				r = g.doubleValue();
+			}
+			++runs;
+			time += System.currentTimeMillis() - start;
+			return r;
+		}
+
+		public long getTime() {
+			return time;
+		}
+
+		public String getReport() {
+			return name + " run time: \t" + time + "ms (" + (time/runs) + "ms each)";
+		}
+
+	}
+
+	/*static class TestIntegers7 extends TestIntegers {
+
+		final java7.math.BigInteger g;
+		final java7.math.BigInteger p;
+		final java7.math.BigInteger k;
+
+		public TestIntegers7(String name, java7.math.BigInteger g, java7.math.BigInteger p, java7.math.BigInteger k) {
+			super(name, null, null, null);
+			this.g = g;
+			this.p = p;
+			this.k = k;
+		}
+
+		public BigInteger modPow() {
+			long start = System.currentTimeMillis();
+			java7.math.BigInteger r = g.modPow(p, k);
+			time += System.currentTimeMillis() - start;
+			++runs;
+			return new BigInteger(r.toByteArray());
+		}
+
+		public double doubleValue() {
+			long start = System.currentTimeMillis();
+			double r = 0.0;
+			for (int i=0; i < DOUBLE_VAL_TEST_RUNS; ++i) {
+				r = g.doubleValue();
+			}
+			++runs;
+			time += System.currentTimeMillis() - start;
+			return r;
+		}
+
+	}*/
+
 }
```

## Row 13
commit_url: https://github.com/FasterXML/jackson-modules-java8/commit/8c3d032fb564148c39b5fdf1cdd6e314e6af1cb5
rm_type: Move And Inline Method
rm_description: Move And Inline Method private read(reader ObjectReader, json String) : LocalDateTime moved from class com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserTest to class com.fasterxml.jackson.datatype.jsr310.deser.LocalDateDeserTest & inlined to public testDeserializationAsArrayDisabled() : void
file_path: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java; datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java
left_side: [{"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java", "startLine": 483, "endLine": 485, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "inlined method declaration", "codeElement": "private read(reader ObjectReader, json String) : LocalDateTime"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java", "startLine": 484, "endLine": 484, "startColumn": 9, "endColumn": 53, "codeElementType": "RETURN_STATEMENT", "description": "inlined code from inlined method declaration", "codeElement": null}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 226, "endLine": 235, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration before inline", "codeElement": "public testDeserializationAsArrayDisabled() : void"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 230, "endLine": 230, "startColumn": 13, "endColumn": 45, "codeElementType": "METHOD_INVOCATION", "description": "inlined method invocation", "codeElement": "read(READER,\"[\\\"2000-01-01\\\"]\")"}]
right_side: [{"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 238, "endLine": 247, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration after inline", "codeElement": "public testDeserializationAsArrayDisabled() : void"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 242, "endLine": 242, "startColumn": 13, "endColumn": 50, "codeElementType": "EXPRESSION_STATEMENT", "description": "inlined code in target method declaration", "codeElement": null}]

### Patch: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java
```diff
@@ -128,7 +128,20 @@ public void testBadDeserializationAsString02() throws Exception
             verifyException(e, "from String \"");
         }
     }
-    
+
+    @Test
+    public void testDeserializationWithTypeInfo01() throws Exception
+    {
+        ObjectMapper mapper = mapperBuilder()
+               .addMixIn(Temporal.class, MockObjectConfiguration.class)
+               .build();
+        LocalDate date = LocalDate.of(2005, Month.NOVEMBER, 5);
+        Temporal value = mapper.readValue(
+                "[\"" + LocalDate.class.getName() + "\",\"" + date.toString() + "\"]", Temporal.class
+                );
+        assertEquals("The value is not correct.", date, value);
+    }
+
     /*
     /**********************************************************
     /* Deserialization from alternate representation: int (number
@@ -170,7 +183,6 @@ public void testStricDeserializeFromInt() throws Exception
     /*
     /**********************************************************
     /* Tests for empty string handling
-     */
     /**********************************************************
      */
 
@@ -227,7 +239,7 @@ public void testStrictDeserializFromEmptyString() throws Exception {
     public void testDeserializationAsArrayDisabled() throws Throwable
     {
         try {
-            read(READER, "[\"2000-01-01\"]");
+            READER.readValue("[\"2000-01-01\"]");
             fail("expected MismatchedInputException");
         } catch (MismatchedInputException e) {
             verifyException(e, "Unexpected token (VALUE_STRING) within Array");
@@ -238,7 +250,41 @@ public void testDeserializationAsArrayDisabled() throws Throwable
     public void testDeserializationAsEmptyArrayDisabled() throws Throwable
     {
         // works even without the feature enabled
-        assertNull(read(READER, "[]"));
+        assertNull(READER.readValue("[]"));
+    }
+
+    @Test
+    public void testDeserializationAsArrayEnabled() throws Throwable
+    {
+        LocalDate actual = READER
+                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS)
+                .readValue("[\"2000-01-01\"]");
+        assertEquals("The value is not correct.", LocalDate.of(2000, 1, 1), actual);
+    }
+
+    @Test
+    public void testDeserializationAsEmptyArrayEnabled() throws Throwable
+    {
+        LocalDate value = READER
+                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS,
+                        DeserializationFeature.ACCEPT_EMPTY_ARRAY_AS_NULL_OBJECT)
+                .readValue("[]");
+        assertNull(value);
+    }
+
+    /*
+    /**********************************************************
+    /* Custom format
+    /**********************************************************
+     */
+
+    // for [datatype-jsr310#37]
+    @Test
+    public void testCustomFormat() throws Exception
+    {
+        Wrapper w = MAPPER.readValue("{\"value\":\"2015_07_28T13:53+0300\"}", Wrapper.class);
+        LocalDate date = w.value; 
+        assertEquals(28, date.getDayOfMonth());
     }
 
     /*
@@ -294,29 +340,10 @@ public void testDeserializationCaseInsensitiveDisabled_InvalidDate() throws Thro
         	expectFailure(reader, json);
         }
     }
-    
-    @Test
-    public void testDeserializationAsArrayEnabled() throws Throwable
-    {
-        LocalDate actual = READER
-                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS)
-                .readValue("[\"2000-01-01\"]");
-        assertEquals("The value is not correct.", LocalDate.of(2000, 1, 1), actual);
-    }
 
-    @Test
-    public void testDeserializationAsEmptyArrayEnabled() throws Throwable
-    {
-        LocalDate value = READER
-                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS,
-                        DeserializationFeature.ACCEPT_EMPTY_ARRAY_AS_NULL_OBJECT)
-                .readValue("[]");
-        assertNull(value);
-    }
-    
     private void expectFailure(ObjectReader reader, String json) throws Throwable {
         try {
-            read(reader, json);
+            reader.readValue(aposToQuotes(json));
             fail("expected DateTimeParseException");
         } catch (JsonProcessingException e) {
             if (e.getCause() == null) {
@@ -325,56 +352,14 @@ private void expectFailure(ObjectReader reader, String json) throws Throwable {
             if (!(e.getCause() instanceof DateTimeParseException)) {
                 throw e.getCause();
             }
-        } catch (IOException e) {
-            throw e;
         }
     }
 
     private void expectSuccess(ObjectReader reader, Object exp, String json) throws IOException {
-        final LocalDate value = read(reader, json);
-        notNull(value);
-        expect(exp, value);
-    }
-
-    private LocalDate read(ObjectReader reader, final String json) throws IOException {
-        return reader.readValue(aposToQuotes(json));
-    }
-
-    private static void notNull(Object value) {
+        final LocalDate value = reader.readValue(aposToQuotes(json));
         assertNotNull("The value should not be null.", value);
-    }
-
-    private static void expect(Object exp, Object value) {
         assertEquals("The value is not correct.", exp,  value);
     }
-
-    @Test
-    public void testDeserializationWithTypeInfo01() throws Exception
-    {
-        ObjectMapper mapper = mapperBuilder()
-               .addMixIn(Temporal.class, MockObjectConfiguration.class)
-               .build();
-        LocalDate date = LocalDate.of(2005, Month.NOVEMBER, 5);
-        Temporal value = mapper.readValue(
-                "[\"" + LocalDate.class.getName() + "\",\"" + date.toString() + "\"]", Temporal.class
-                );
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    /*
-    /**********************************************************
-    /* Custom format
-    /**********************************************************
-     */
-
-    // for [datatype-jsr310#37]
-    @Test
-    public void testCustomFormat() throws Exception
-    {
-        Wrapper w = MAPPER.readValue("{\"value\":\"2015_07_28T13:53+0300\"}", Wrapper.class);
-        LocalDate date = w.value; 
-        assertEquals(28, date.getDayOfMonth());
-    }
 }
```
### Patch: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java
```diff
@@ -459,14 +459,14 @@ public void testDeserializationCaseInsensitiveDisabled_InvalidDate() throws Thro
     }
 
     private void expectSuccess(ObjectReader reader, Object exp, String json) throws IOException {
-        final LocalDateTime value = read(reader, json);
-        notNull(value);
-        expect(exp, value);
+        final LocalDateTime value = reader.readValue(aposToQuotes(json));
+        assertNotNull("The value should not be null.", value);
+        assertEquals("The value is not correct.", exp,  value);
     }
 
     private void expectFailure(ObjectReader reader, String json) throws Throwable {
         try {
-            read(reader, json);
+            reader.readValue(aposToQuotes(json));
             fail("expected DateTimeParseException");
         } catch (JsonProcessingException e) {
             if (e.getCause() == null) {
@@ -475,20 +475,6 @@ private void expectFailure(ObjectReader reader, String json) throws Throwable {
             if (!(e.getCause() instanceof DateTimeParseException)) {
                 throw e.getCause();
             }
-        } catch (IOException e) {
-            throw e;
         }
     }
-
-    private LocalDateTime read(ObjectReader reader, final String json) throws IOException {
-        return reader.readValue(aposToQuotes(json));
-    }
-
-    private void notNull(Object value) {
-        assertNotNull("The value should not be null.", value);
-    }
-
-    private void expect(Object exp, Object value) {
-        assertEquals("The value is not correct.", exp,  value);
-    }
 }
```

## Row 14
commit_url: https://github.com/AdoptOpenJDK/jitwatch/commit/7788103ee76fde8751ccbe5adc03855c89ef4bdc
rm_type: Add Method Modifier
rm_description: Add Method Modifier static in method public tearDown() : void from class org.adoptopenjdk.jitwatch.test.TestBytecodeLoaderWithInnerClasses
file_path: core/src/test/java/org/adoptopenjdk/jitwatch/test/TestBytecodeLoaderWithInnerClasses.java
left_side: [{"filePath": "core/src/test/java/org/adoptopenjdk/jitwatch/test/TestBytecodeLoaderWithInnerClasses.java", "startLine": 136, "endLine": 138, "startColumn": 2, "endColumn": 3, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public tearDown() : void"}]
right_side: [{"filePath": "core/src/test/java/org/adoptopenjdk/jitwatch/test/TestBytecodeLoaderWithInnerClasses.java", "startLine": 136, "endLine": 138, "startColumn": 2, "endColumn": 3, "codeElementType": "METHOD_DECLARATION", "description": "method declaration with added modifier", "codeElement": "public tearDown() : void"}]

### Patch: core/src/test/java/org/adoptopenjdk/jitwatch/test/TestBytecodeLoaderWithInnerClasses.java
```diff
@@ -25,8 +25,8 @@
 import org.adoptopenjdk.jitwatch.model.bytecode.MemberBytecode;
 import org.adoptopenjdk.jitwatch.model.bytecode.SourceMapper;
 import org.adoptopenjdk.jitwatch.process.compiler.CompilerJava;
-import org.junit.After;
-import org.junit.Before;
+import org.junit.AfterClass;
+import org.junit.BeforeClass;
 import org.junit.Test;
 
 /*
@@ -69,19 +69,19 @@
  */
 public class TestBytecodeLoaderWithInnerClasses
 {
-	private String classNameOuter = "TestInner";
-	private String classNameInner1 = "TestInner$Inner1";
-	private String classNameInner2 = "TestInner$Inner1$Inner2";
+	private static String classNameOuter = "TestInner";
+	private static String classNameInner1 = "TestInner$Inner1";
+	private static String classNameInner2 = "TestInner$Inner1$Inner2";
 
-	private Path pathToSourceDir;
-	private Path pathToTempClassDir;
-	private List<String> classpathLocations;
+	private static Path pathToSourceDir;
+	private static Path pathToTempClassDir;
+	private static List<String> classpathLocations;
 
-	private ClassBC classBytecodeForOuter;
-	private ClassBC classBytecodeForInner1;
-	private ClassBC classBytecodeForInner2;
+	private static ClassBC classBytecodeForOuter;
+	private static ClassBC classBytecodeForInner1;
+	private static ClassBC classBytecodeForInner2;
 
-	@Before public void setUp()
+	@BeforeClass public static void setUp()
 	{
 		try
 		{
@@ -133,7 +133,7 @@ public class TestBytecodeLoaderWithInnerClasses
 		classBytecodeForInner2 = classBytecodeListForOuter.get(2);
 	}
 
-	@After public void tearDown()
+	@AfterClass public static void tearDown()
 	{
 	}
```

## Row 15
commit_url: https://github.com/oVirt/ovirt-engine/commit/94f5da8379ea345f24fb7024dc31ba427315a47c
rm_type: Rename Parameter
rm_description: Rename Parameter expected : ValidationResult to matcher : Matcher<ValidationResult> in method private portMirroringTest(matcher Matcher<ValidationResult>, networkName String, portMirroring boolean) : void from class org.ovirt.engine.core.bll.validator.VmNicValidatorTest
file_path: backend/manager/modules/bll/src/test/java/org/ovirt/engine/core/bll/validator/VmNicValidatorTest.java
left_side: [{"filePath": "backend/manager/modules/bll/src/test/java/org/ovirt/engine/core/bll/validator/VmNicValidatorTest.java", "startLine": 123, "endLine": 123, "startColumn": 36, "endColumn": 61, "codeElementType": "SINGLE_VARIABLE_DECLARATION", "description": "original variable declaration", "codeElement": "expected : ValidationResult"}]
right_side: [{"filePath": "backend/manager/modules/bll/src/test/java/org/ovirt/engine/core/bll/validator/VmNicValidatorTest.java", "startLine": 131, "endLine": 131, "startColumn": 36, "endColumn": 69, "codeElementType": "SINGLE_VARIABLE_DECLARATION", "description": "renamed variable declaration", "codeElement": "matcher : Matcher<ValidationResult>"}]

### Patch: backend/manager/modules/bll/src/test/java/org/ovirt/engine/core/bll/validator/VmNicValidatorTest.java
```diff
@@ -1,8 +1,14 @@
 package org.ovirt.engine.core.bll.validator;
 
-import static org.junit.Assert.assertEquals;
+import static org.junit.Assert.assertThat;
+import static org.junit.matchers.JUnitMatchers.both;
+import static org.junit.matchers.JUnitMatchers.hasItem;
 import static org.mockito.Mockito.when;
+import static org.ovirt.engine.core.bll.validator.ValidationResultMatchers.failsWith;
+import static org.ovirt.engine.core.bll.validator.ValidationResultMatchers.isValid;
+import static org.ovirt.engine.core.bll.validator.ValidationResultMatchers.replacements;
 
+import org.hamcrest.Matcher;
 import org.junit.Before;
 import org.junit.Rule;
 import org.junit.Test;
@@ -44,86 +50,88 @@ public void setup() {
 
     @Test
     public void unlinkedWhenUnlinkingNotSupported() throws Exception {
-        unlinkingTest(new ValidationResult(VdcBllMessages.UNLINKING_IS_NOT_SUPPORTED, CLUSTER_VERSION_REPLACEMENT),
+        unlinkingTest(both(failsWith(VdcBllMessages.UNLINKING_IS_NOT_SUPPORTED))
+                .and(replacements(hasItem(CLUSTER_VERSION_REPLACEMENT))),
                 false,
                 false);
     }
 
     @Test
     public void linkedWhenUnlinkingNotSupported() throws Exception {
-        unlinkingTest(ValidationResult.VALID, false, true);
+        unlinkingTest(isValid(), false, true);
     }
 
     @Test
     public void unlinkedWhenUnlinkingSupported() throws Exception {
-        unlinkingTest(ValidationResult.VALID, true, false);
+        unlinkingTest(isValid(), true, false);
     }
 
     @Test
     public void linkedWhenUnlinkingSupported() throws Exception {
-        unlinkingTest(ValidationResult.VALID, true, true);
+        unlinkingTest(isValid(), true, true);
     }
 
     @Test
     public void nullNetworkNameWhenUnlinkingNotSupported() throws Exception {
-        networkNameTest(new ValidationResult(VdcBllMessages.NULL_NETWORK_IS_NOT_SUPPORTED, CLUSTER_VERSION_REPLACEMENT),
+        networkNameTest(both(failsWith(VdcBllMessages.NULL_NETWORK_IS_NOT_SUPPORTED))
+                .and(replacements(hasItem(CLUSTER_VERSION_REPLACEMENT))),
                 false,
                 null);
     }
 
     @Test
     public void validNetworkNameWhenUnlinkingNotSupported() throws Exception {
-        networkNameTest(ValidationResult.VALID, false, "net");
+        networkNameTest(isValid(), false, "net");
     }
 
     @Test
     public void nullNetworkNameWhenUnlinkingSupported() throws Exception {
-        networkNameTest(ValidationResult.VALID, true, null);
+        networkNameTest(isValid(), true, null);
     }
 
     @Test
     public void validNetworkNameWhenUnlinkingSupported() throws Exception {
-        networkNameTest(ValidationResult.VALID, true, "net");
+        networkNameTest(isValid(), true, "net");
     }
 
     @Test
     public void validNetworkWhenPortMirroring() throws Exception {
-        portMirroringTest(ValidationResult.VALID, "net", true);
+        portMirroringTest(isValid(), "net", true);
     }
 
     @Test
     public void nullNetworkWhenPortMirroring() throws Exception {
-        portMirroringTest(new ValidationResult(VdcBllMessages.PORT_MIRRORING_REQUIRES_NETWORK), null, true);
+        portMirroringTest(failsWith(VdcBllMessages.PORT_MIRRORING_REQUIRES_NETWORK), null, true);
     }
 
     @Test
     public void validNetworkWhenNoPortMirroring() throws Exception {
-        portMirroringTest(ValidationResult.VALID, "net", false);
+        portMirroringTest(isValid(), "net", false);
     }
 
     @Test
     public void nullNetworkWhenNoPortMirroring() throws Exception {
-        portMirroringTest(ValidationResult.VALID, null, false);
+        portMirroringTest(isValid(), null, false);
     }
 
-    private void unlinkingTest(ValidationResult expected, boolean networkLinkingSupported, boolean nicLinked) {
+    private void unlinkingTest(Matcher<ValidationResult> matcher, boolean networkLinkingSupported, boolean nicLinked) {
         mockConfigRule.mockConfigValue(ConfigValues.NetworkLinkingSupported, version, networkLinkingSupported);
         when(nic.isLinked()).thenReturn(nicLinked);
 
-        assertEquals(expected, validator.linkedCorrectly());
+        assertThat(validator.linkedCorrectly(), matcher);
     }
 
-    private void networkNameTest(ValidationResult expected, boolean networkLinkingSupported, String networkName) {
+    private void networkNameTest(Matcher<ValidationResult> matcher, boolean networkLinkingSupported, String networkName) {
         mockConfigRule.mockConfigValue(ConfigValues.NetworkLinkingSupported, version, networkLinkingSupported);
         when(nic.getNetworkName()).thenReturn(networkName);
 
-        assertEquals(expected, validator.networkNameValid());
+        assertThat(validator.networkNameValid(), matcher);
     }
 
-    private void portMirroringTest(ValidationResult expected, String networkName, boolean portMirroring) {
+    private void portMirroringTest(Matcher<ValidationResult> matcher, String networkName, boolean portMirroring) {
         when(nic.getNetworkName()).thenReturn(networkName);
         when(nic.isPortMirroring()).thenReturn(portMirroring);
 
-        assertEquals(expected, validator.networkProvidedForPortMirroring());
+        assertThat(validator.networkProvidedForPortMirroring(), matcher);
     }
 }
```

## Row 16
commit_url: https://github.com/errai/errai/commit/058e50b10da2d9fc3fcd7736f2d1215c591f9c42
rm_type: Rename Variable
rm_description: Rename Variable str : VariableReference to n : VariableReference in method public testAddVariableWithIntegerTypeInference() : void from class org.jboss.errai.ioc.tests.rebind.StatementBuilderTest
file_path: errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java
left_side: [{"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java", "startLine": 94, "endLine": 94, "startColumn": 23, "endColumn": 51, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "original variable declaration", "codeElement": "str : VariableReference"}, {"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java", "startLine": 94, "endLine": 94, "startColumn": 5, "endColumn": 52, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java", "startLine": 95, "endLine": 95, "startColumn": 5, "endColumn": 63, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java", "startLine": 96, "endLine": 96, "startColumn": 5, "endColumn": 99, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java", "startLine": 103, "endLine": 103, "startColumn": 5, "endColumn": 99, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}]
right_side: [{"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java", "startLine": 66, "endLine": 66, "startColumn": 23, "endColumn": 47, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "renamed variable declaration", "codeElement": "n : VariableReference"}, {"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java", "startLine": 66, "endLine": 66, "startColumn": 5, "endColumn": 48, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}, {"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java", "startLine": 67, "endLine": 67, "startColumn": 5, "endColumn": 59, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}, {"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java", "startLine": 68, "endLine": 68, "startColumn": 5, "endColumn": 98, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}, {"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java", "startLine": 69, "endLine": 69, "startColumn": 5, "endColumn": 94, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}]

### Patch: errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/StatementBuilderTest.java
```diff
@@ -16,7 +16,22 @@
 
 package org.jboss.errai.ioc.tests.rebind;
 
-import org.jboss.errai.ioc.rebind.ioc.codegen.*;
+import static org.junit.Assert.assertTrue;
+import static org.junit.Assert.fail;
+
+import java.lang.annotation.Annotation;
+import java.util.List;
+
+import javax.annotation.PostConstruct;
+import javax.enterprise.util.TypeLiteral;
+import javax.inject.Inject;
+
+import org.jboss.errai.ioc.rebind.ioc.codegen.AssignmentOperator;
+import org.jboss.errai.ioc.rebind.ioc.codegen.Context;
+import org.jboss.errai.ioc.rebind.ioc.codegen.MetaClassFactory;
+import org.jboss.errai.ioc.rebind.ioc.codegen.Statement;
+import org.jboss.errai.ioc.rebind.ioc.codegen.Variable;
+import org.jboss.errai.ioc.rebind.ioc.codegen.VariableReference;
 import org.jboss.errai.ioc.rebind.ioc.codegen.builder.impl.ObjectBuilder;
 import org.jboss.errai.ioc.rebind.ioc.codegen.builder.impl.StatementBuilder;
 import org.jboss.errai.ioc.rebind.ioc.codegen.builder.values.LiteralFactory;
@@ -25,15 +40,6 @@
 import org.junit.Assert;
 import org.junit.Test;
 
-import javax.annotation.PostConstruct;
-import javax.enterprise.util.TypeLiteral;
-import javax.inject.Inject;
-import java.lang.annotation.Annotation;
-import java.util.List;
-
-import static org.junit.Assert.assertTrue;
-import static org.junit.Assert.fail;
-
 /**
  * Tests the {@link StatementBuilder} API.
  * 
@@ -42,35 +48,44 @@
 public class StatementBuilderTest extends AbstractStatementBuilderTest {
 
   @Test
-  public void testAddVariableWithLiteralInitialization() {
+  public void testAddVariableWithExactTypeProvided() {
     Context ctx = Context.create();
     StatementBuilder.create().addVariable("n", Integer.class, 10).generate(ctx);
 
     VariableReference n = ctx.getVariable("n");
     assertEquals("Wrong variable name", "n", n.getName());
     Assert.assertEquals("Wrong variable type", MetaClassFactory.get(Integer.class), n.getType());
     Assert.assertEquals("Wrong variable value", LiteralFactory.getLiteral(10), n.getValue());
+  }
 
-    ctx = Context.create();
+  @Test
+  public void testAddVariableWithIntegerTypeInference() {
+    Context ctx = Context.create();
     StatementBuilder.create().addVariable("n", 10).generate(ctx);
 
-    n = ctx.getVariable("n");
+    VariableReference n = ctx.getVariable("n");
     assertEquals("Wrong variable name", "n", n.getName());
     Assert.assertEquals("Wrong variable type", MetaClassFactory.get(Integer.class), n.getType());
     Assert.assertEquals("Wrong variable value", LiteralFactory.getLiteral(10), n.getValue());
+  }
 
-    ctx = Context.create();
+  @Test
+  public void testAddVariableWithStringTypeInference() {
+    Context ctx = Context.create();
     StatementBuilder.create().addVariable("n", "10").generate(ctx);
 
-    n = ctx.getVariable("n");
+    VariableReference n = ctx.getVariable("n");
     assertEquals("Wrong variable name", "n", n.getName());
     Assert.assertEquals("Wrong variable type", MetaClassFactory.get(String.class), n.getType());
     Assert.assertEquals("Wrong variable value", LiteralFactory.getLiteral("10"), n.getValue());
+  }
 
-    ctx = Context.create();
+  @Test
+  public void testAddVariableWithImplicitTypeConversion() {
+    Context ctx = Context.create();
     StatementBuilder.create().addVariable("n", Integer.class, "10").generate(ctx);
 
-    n = ctx.getVariable("n");
+    VariableReference n = ctx.getVariable("n");
     assertEquals("Wrong variable name", "n", n.getName());
     Assert.assertEquals("Wrong variable type", MetaClassFactory.get(Integer.class), n.getType());
     Assert.assertEquals("Wrong variable value", LiteralFactory.getLiteral(10), n.getValue());
@@ -86,25 +101,28 @@ public void testAddVariableWithLiteralInitialization() {
   }
 
   @Test
-  public void testAddVariableWithObjectInitialization() {
+  public void testAddVariableWithObjectInitializationWithExactTypeProvided() {
     Context ctx = Context.create();
     StatementBuilder.create().addVariable("str", String.class,
         ObjectBuilder.newInstanceOf(String.class)).generate(ctx);
 
     VariableReference str = ctx.getVariable("str");
     assertEquals("Wrong variable name", "str", str.getName());
     Assert.assertEquals("Wrong variable type", MetaClassFactory.get(String.class), str.getType());
+  }
 
-    ctx = Context.create();
+  @Test
+  public void testAddVariableWithObjectInitializationWithStringTypeInference() {
+    Context ctx = Context.create();
     StatementBuilder.create().addVariable("str", ObjectBuilder.newInstanceOf(String.class)).generate(ctx);
 
-    str = ctx.getVariable("str");
+    VariableReference str = ctx.getVariable("str");
     assertEquals("Wrong variable name", "str", str.getName());
     Assert.assertEquals("Wrong variable type", MetaClassFactory.get(String.class), str.getType());
   }
 
   @Test
-  public void testUndefinedVariable() {
+  public void testLoadUndefinedVariable() {
     try {
       StatementBuilder.create().loadVariable("n").toJavaString();
       fail("Expected OutOfScopeException");
@@ -116,6 +134,12 @@ public void testUndefinedVariable() {
 
   @Test
   public void testCreateAndInitializeArray() {
+    String s = StatementBuilder.create().newArray(String.class).initialize("1", "2").toJavaString();
+    assertEquals("new String[] {\"1\",\"2\"}", s);
+  }
+
+  @Test
+  public void testCreateAndInitializeArrayWithInvalidInitialization() {
     try {
       StatementBuilder.create().newArray(Annotation.class)
           .initialize("1", "2")
@@ -125,7 +149,10 @@ public void testCreateAndInitializeArray() {
     catch (InvalidTypeException oose) {
       // expected
     }
+  }
 
+  @Test
+  public void testCreateAndInitializeArrayWithMissingInitializationAndDimensions() {
     try {
       StatementBuilder.create().newArray(String.class).toJavaString();
       fail("Expected RuntimeException");
@@ -134,10 +161,10 @@ public void testCreateAndInitializeArray() {
       // expected
       assertEquals("Must provide either dimension expressions or an array initializer", e.getMessage());
     }
+  }
 
-    String s = StatementBuilder.create().newArray(String.class).initialize("1", "2").toJavaString();
-    assertEquals("new String[] {\"1\",\"2\"}", s);
-
+  @Test
+  public void testCreateAndInitializeAnnotationArray() {
     Statement annotation1 = ObjectBuilder.newInstanceOf(Annotation.class)
         .extend()
         .publicOverridesMethod("annotationType")
@@ -152,7 +179,7 @@ public void testCreateAndInitializeArray() {
         .finish()
         .finish();
 
-    s = StatementBuilder.create().newArray(Annotation.class)
+    String s = StatementBuilder.create().newArray(Annotation.class)
         .initialize(annotation1, annotation2)
         .toJavaString();
 
@@ -172,27 +199,38 @@ public void testCreateAndInitializeArray() {
 
   @Test
   @SuppressWarnings(value = { "all" })
-  public void testCreateAndInitializeMultiDimensionalArray() {
-
+  public void testCreateAndInitializeTwoDimensionalArray() {
     String s = StatementBuilder.create().newArray(Integer.class)
         .initialize(new Integer[][] { { 1, 2 }, { 3, 4 } })
         .toJavaString();
 
     assertEquals("Failed to generate two dimensional array", "new Integer[][] {{1,2},{3,4}}", s);
+  }
 
-    s = StatementBuilder.create().newArray(Integer.class)
+  @Test
+  @SuppressWarnings(value = { "all" })
+  public void testCreateAndInitializeTwoDimensionalArrayWithSingleValue() {
+    String s = StatementBuilder.create().newArray(Integer.class)
         .initialize(new Object[][] { { 1, 2 } })
         .toJavaString();
 
     assertEquals("Failed to generate two dimensional array", "new Integer[][] {{1,2}}", s);
+  }
 
-    s = StatementBuilder.create().newArray(Object.class)
+  @Test
+  @SuppressWarnings(value = { "all" })
+  public void testCreateAndInitializeTwoDimensionalObjectArrayWithIntegers() {
+    String s = StatementBuilder.create().newArray(Object.class)
         .initialize(new Object[][] { { 1, 2 } })
         .toJavaString();
 
     assertEquals("Failed to generate two dimensional array", "new Object[][] {{1,2}}", s);
+  }
 
-    s = StatementBuilder.create().newArray(String.class)
+  @Test
+  @SuppressWarnings(value = { "all" })
+  public void testCreateAndInitializeTwoDimensionalArrayWithStatements() {
+    String s = StatementBuilder.create().newArray(String.class)
         .initialize(new Statement[][] {
             { StatementBuilder.create().invokeStatic(Integer.class, "toString", 1),
                 StatementBuilder.create().invokeStatic(Integer.class, "toString", 2) },
@@ -203,8 +241,12 @@ public void testCreateAndInitializeMultiDimensionalArray() {
     assertEquals("Failed to generate two dimensional array using statements",
         "new String[][] {{Integer.toString(1),Integer.toString(2)}," +
             "{Integer.toString(3),Integer.toString(4)}}", s);
+  }
 
-    s = StatementBuilder.create().newArray(String.class)
+  @Test
+  @SuppressWarnings(value = { "all" })
+  public void testCreateAndInitializeTwoDimensionalArrayWithStatementsAndLiterals() {
+    String s = StatementBuilder.create().newArray(String.class)
         .initialize(new Object[][] {
             { StatementBuilder.create().invokeStatic(Integer.class, "toString", 1), "2" },
             { StatementBuilder.create().invokeStatic(Integer.class, "toString", 3), "4" } })
@@ -213,8 +255,12 @@ public void testCreateAndInitializeMultiDimensionalArray() {
     assertEquals("Failed to generate two dimensional array using statements and objects",
         "new String[][] {{Integer.toString(1),\"2\"}," +
             "{Integer.toString(3),\"4\"}}", s);
+  }
 
-    s = StatementBuilder.create().newArray(String.class)
+  @Test
+  @SuppressWarnings(value = { "all" })
+  public void testCreateAndInitializeThreeDimensionalArray() {
+    String s = StatementBuilder.create().newArray(String.class)
         .initialize(new String[][][] { { { "1", "2" }, { "a", "b" } }, { { "3", "4" }, { "b", "c" } } })
         .toJavaString();
 
@@ -223,24 +269,30 @@ public void testCreateAndInitializeMultiDimensionalArray() {
   }
 
   @Test
-  public void testAssignArrayVariable() {
+  public void testAssignArrayValue() {
     String s = StatementBuilder.create()
         .addVariable("twoDimArray", String[][].class)
         .loadVariable("twoDimArray", 1, 2)
         .assignValue("test")
         .toJavaString();
 
     assertEquals("Failed to generate array assignment", "twoDimArray[1][2] = \"test\"", s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testAssignArrayValueWithPreIncrementAssignment() {
+    String s = StatementBuilder.create()
         .addVariable("twoDimArray", String[][].class)
         .loadVariable("twoDimArray", 1, 2)
         .assignValue(AssignmentOperator.PreIncrementAssign, "test")
         .toJavaString();
 
     assertEquals("Failed to generate array assignment", "twoDimArray[1][2] += \"test\"", s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testAssignArrayValueWithVariableIndexes() {
+    String s = StatementBuilder.create()
         .addVariable("twoDimArray", String[][].class)
         .addVariable("i", int.class)
         .addVariable("j", int.class)
@@ -249,7 +301,10 @@ public void testAssignArrayVariable() {
         .toJavaString();
 
     assertEquals("Failed to generate array assignment", "twoDimArray[i][j] = \"test\"", s);
+  }
 
+  @Test
+  public void testAssignArrayValueWithInvalidArray() {
     try {
       StatementBuilder.create()
           .addVariable("twoDimArray", String.class)
@@ -261,7 +316,10 @@ public void testAssignArrayVariable() {
     catch (InvalidTypeException ite) {
       // Expected, variable is not an array.
     }
+  }
 
+  @Test
+  public void testAssignArrayValueWithInvalidIndexType() {
     try {
       StatementBuilder.create()
           .addVariable("twoDimArray", String[][].class)
@@ -276,7 +334,7 @@ public void testAssignArrayVariable() {
       // Expected, indexes are no integers
     }
   }
-  
+
   @Test
   public void testObjectCreationWithParameterizedType() {
     String s = StatementBuilder.create().newObject(new TypeLiteral<List<String>>() {}).toJavaString();
```

## Row 17
commit_url: https://github.com/FasterXML/jackson-modules-java8/commit/8c3d032fb564148c39b5fdf1cdd6e314e6af1cb5
rm_type: Inline Method
rm_description: Inline Method private notNull(value Object) : void inlined to private expectSuccess(reader ObjectReader, exp Object, json String) : void in class com.fasterxml.jackson.datatype.jsr310.deser.LocalDateDeserTest
file_path: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java
left_side: [{"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 343, "endLine": 345, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "inlined method declaration", "codeElement": "private notNull(value Object) : void"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 344, "endLine": 344, "startColumn": 9, "endColumn": 63, "codeElementType": "EXPRESSION_STATEMENT", "description": "inlined code from inlined method declaration", "codeElement": null}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 333, "endLine": 337, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration before inline", "codeElement": "private expectSuccess(reader ObjectReader, exp Object, json String) : void"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 335, "endLine": 335, "startColumn": 9, "endColumn": 23, "codeElementType": "METHOD_INVOCATION", "description": "inlined method invocation", "codeElement": "notNull(value)"}]
right_side: [{"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 358, "endLine": 362, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration after inline", "codeElement": "private expectSuccess(reader ObjectReader, exp Object, json String) : void"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 360, "endLine": 360, "startColumn": 9, "endColumn": 63, "codeElementType": "EXPRESSION_STATEMENT", "description": "inlined code in target method declaration", "codeElement": null}]

### Patch: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java
```diff
@@ -128,7 +128,20 @@ public void testBadDeserializationAsString02() throws Exception
             verifyException(e, "from String \"");
         }
     }
-    
+
+    @Test
+    public void testDeserializationWithTypeInfo01() throws Exception
+    {
+        ObjectMapper mapper = mapperBuilder()
+               .addMixIn(Temporal.class, MockObjectConfiguration.class)
+               .build();
+        LocalDate date = LocalDate.of(2005, Month.NOVEMBER, 5);
+        Temporal value = mapper.readValue(
+                "[\"" + LocalDate.class.getName() + "\",\"" + date.toString() + "\"]", Temporal.class
+                );
+        assertEquals("The value is not correct.", date, value);
+    }
+
     /*
     /**********************************************************
     /* Deserialization from alternate representation: int (number
@@ -170,7 +183,6 @@ public void testStricDeserializeFromInt() throws Exception
     /*
     /**********************************************************
     /* Tests for empty string handling
-     */
     /**********************************************************
      */
 
@@ -227,7 +239,7 @@ public void testStrictDeserializFromEmptyString() throws Exception {
     public void testDeserializationAsArrayDisabled() throws Throwable
     {
         try {
-            read(READER, "[\"2000-01-01\"]");
+            READER.readValue("[\"2000-01-01\"]");
             fail("expected MismatchedInputException");
         } catch (MismatchedInputException e) {
             verifyException(e, "Unexpected token (VALUE_STRING) within Array");
@@ -238,7 +250,41 @@ public void testDeserializationAsArrayDisabled() throws Throwable
     public void testDeserializationAsEmptyArrayDisabled() throws Throwable
     {
         // works even without the feature enabled
-        assertNull(read(READER, "[]"));
+        assertNull(READER.readValue("[]"));
+    }
+
+    @Test
+    public void testDeserializationAsArrayEnabled() throws Throwable
+    {
+        LocalDate actual = READER
+                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS)
+                .readValue("[\"2000-01-01\"]");
+        assertEquals("The value is not correct.", LocalDate.of(2000, 1, 1), actual);
+    }
+
+    @Test
+    public void testDeserializationAsEmptyArrayEnabled() throws Throwable
+    {
+        LocalDate value = READER
+                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS,
+                        DeserializationFeature.ACCEPT_EMPTY_ARRAY_AS_NULL_OBJECT)
+                .readValue("[]");
+        assertNull(value);
+    }
+
+    /*
+    /**********************************************************
+    /* Custom format
+    /**********************************************************
+     */
+
+    // for [datatype-jsr310#37]
+    @Test
+    public void testCustomFormat() throws Exception
+    {
+        Wrapper w = MAPPER.readValue("{\"value\":\"2015_07_28T13:53+0300\"}", Wrapper.class);
+        LocalDate date = w.value; 
+        assertEquals(28, date.getDayOfMonth());
     }
 
     /*
@@ -294,29 +340,10 @@ public void testDeserializationCaseInsensitiveDisabled_InvalidDate() throws Thro
         	expectFailure(reader, json);
         }
     }
-    
-    @Test
-    public void testDeserializationAsArrayEnabled() throws Throwable
-    {
-        LocalDate actual = READER
-                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS)
-                .readValue("[\"2000-01-01\"]");
-        assertEquals("The value is not correct.", LocalDate.of(2000, 1, 1), actual);
-    }
 
-    @Test
-    public void testDeserializationAsEmptyArrayEnabled() throws Throwable
-    {
-        LocalDate value = READER
-                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS,
-                        DeserializationFeature.ACCEPT_EMPTY_ARRAY_AS_NULL_OBJECT)
-                .readValue("[]");
-        assertNull(value);
-    }
-    
     private void expectFailure(ObjectReader reader, String json) throws Throwable {
         try {
-            read(reader, json);
+            reader.readValue(aposToQuotes(json));
             fail("expected DateTimeParseException");
         } catch (JsonProcessingException e) {
             if (e.getCause() == null) {
@@ -325,56 +352,14 @@ private void expectFailure(ObjectReader reader, String json) throws Throwable {
             if (!(e.getCause() instanceof DateTimeParseException)) {
                 throw e.getCause();
             }
-        } catch (IOException e) {
-            throw e;
         }
     }
 
     private void expectSuccess(ObjectReader reader, Object exp, String json) throws IOException {
-        final LocalDate value = read(reader, json);
-        notNull(value);
-        expect(exp, value);
-    }
-
-    private LocalDate read(ObjectReader reader, final String json) throws IOException {
-        return reader.readValue(aposToQuotes(json));
-    }
-
-    private static void notNull(Object value) {
+        final LocalDate value = reader.readValue(aposToQuotes(json));
         assertNotNull("The value should not be null.", value);
-    }
-
-    private static void expect(Object exp, Object value) {
         assertEquals("The value is not correct.", exp,  value);
     }
-
-    @Test
-    public void testDeserializationWithTypeInfo01() throws Exception
-    {
-        ObjectMapper mapper = mapperBuilder()
-               .addMixIn(Temporal.class, MockObjectConfiguration.class)
-               .build();
-        LocalDate date = LocalDate.of(2005, Month.NOVEMBER, 5);
-        Temporal value = mapper.readValue(
-                "[\"" + LocalDate.class.getName() + "\",\"" + date.toString() + "\"]", Temporal.class
-                );
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    /*
-    /**********************************************************
-    /* Custom format
-    /**********************************************************
-     */
-
-    // for [datatype-jsr310#37]
-    @Test
-    public void testCustomFormat() throws Exception
-    {
-        Wrapper w = MAPPER.readValue("{\"value\":\"2015_07_28T13:53+0300\"}", Wrapper.class);
-        LocalDate date = w.value; 
-        assertEquals(28, date.getDayOfMonth());
-    }
 }
```

## Row 18
commit_url: https://github.com/oVirt/ovirt-engine/commit/94f5da8379ea345f24fb7024dc31ba427315a47c
rm_type: Rename Parameter
rm_description: Rename Parameter expected : ValidationResult to matcher : Matcher<ValidationResult> in method private networkNameAvailableTest(matcher Matcher<ValidationResult>, networks List<Network>) : void from class org.ovirt.engine.core.bll.validator.NetworkValidatorTest
file_path: backend/manager/modules/bll/src/test/java/org/ovirt/engine/core/bll/validator/NetworkValidatorTest.java
left_side: [{"filePath": "backend/manager/modules/bll/src/test/java/org/ovirt/engine/core/bll/validator/NetworkValidatorTest.java", "startLine": 253, "endLine": 253, "startColumn": 43, "endColumn": 68, "codeElementType": "SINGLE_VARIABLE_DECLARATION", "description": "original variable declaration", "codeElement": "expected : ValidationResult"}]
right_side: [{"filePath": "backend/manager/modules/bll/src/test/java/org/ovirt/engine/core/bll/validator/NetworkValidatorTest.java", "startLine": 255, "endLine": 255, "startColumn": 43, "endColumn": 76, "codeElementType": "SINGLE_VARIABLE_DECLARATION", "description": "renamed variable declaration", "codeElement": "matcher : Matcher<ValidationResult>"}]

### Patch: backend/manager/modules/bll/src/test/java/org/ovirt/engine/core/bll/validator/NetworkValidatorTest.java
```diff
@@ -1,16 +1,19 @@
 package org.ovirt.engine.core.bll.validator;
 
-import static org.junit.Assert.assertEquals;
+import static org.junit.Assert.assertThat;
 import static org.mockito.Matchers.any;
+import static org.mockito.Mockito.doReturn;
 import static org.mockito.Mockito.mock;
 import static org.mockito.Mockito.spy;
 import static org.mockito.Mockito.when;
-import static org.mockito.Mockito.doReturn;
+import static org.ovirt.engine.core.bll.validator.ValidationResultMatchers.failsWith;
+import static org.ovirt.engine.core.bll.validator.ValidationResultMatchers.isValid;
 
 import java.util.ArrayList;
 import java.util.Collections;
 import java.util.List;
 
+import org.hamcrest.Matcher;
 import org.junit.Before;
 import org.junit.Rule;
 import org.junit.Test;
@@ -90,136 +93,135 @@ public void setup() {
 
     @Test
     public void networkSet() throws Exception {
-        assertEquals(ValidationResult.VALID, validator.networkIsSet());
+        assertThat(validator.networkIsSet(), isValid());
     }
 
     @Test
     public void networkNull() throws Exception {
         validator = new NetworkValidator(null);
-        assertEquals(new ValidationResult(VdcBllMessages.NETWORK_NOT_EXISTS), validator.networkIsSet());
+        assertThat(validator.networkIsSet(), failsWith(VdcBllMessages.NETWORK_NOT_EXISTS));
     }
 
     @Test
     public void dataCenterDoesntExist() throws Exception {
         when(dataCenterDao.get(any(Guid.class))).thenReturn(null);
-        assertEquals(new ValidationResult(VdcBllMessages.ACTION_TYPE_FAILED_STORAGE_POOL_NOT_EXIST),
-                validator.dataCenterExists());
+        assertThat(validator.dataCenterExists(), failsWith(VdcBllMessages.ACTION_TYPE_FAILED_STORAGE_POOL_NOT_EXIST));
     }
 
     @Test
     public void dataCenterExists() throws Exception {
-        assertEquals(ValidationResult.VALID, validator.dataCenterExists());
+        assertThat(validator.dataCenterExists(), isValid());
     }
 
-    private void vmNetworkSetupTest(ValidationResult expected, boolean vmNetwork, boolean featureSupported) {
+    private void vmNetworkSetupTest(Matcher<ValidationResult> matcher, boolean vmNetwork, boolean featureSupported) {
         mockConfigRule.mockConfigValue(ConfigValues.NonVmNetworkSupported,
                 dataCenter.getcompatibility_version(),
                 featureSupported);
         when(network.isVmNetwork()).thenReturn(vmNetwork);
 
-        assertEquals(expected, validator.vmNetworkSetCorrectly());
+        assertThat(validator.vmNetworkSetCorrectly(), matcher);
     }
 
     @Test
     public void vmNetworkWhenSupported() throws Exception {
-        vmNetworkSetupTest(ValidationResult.VALID, true, true);
+        vmNetworkSetupTest(isValid(), true, true);
     }
 
     @Test
     public void vmNetworkWhenNotSupported() throws Exception {
-        vmNetworkSetupTest(ValidationResult.VALID, true, false);
+        vmNetworkSetupTest(isValid(), true, false);
     }
 
     @Test
     public void nonVmNetworkWhenSupported() throws Exception {
-        vmNetworkSetupTest(ValidationResult.VALID, false, true);
+        vmNetworkSetupTest(isValid(), false, true);
     }
 
     @Test
     public void nonVmNetworkWhenNotSupported() throws Exception {
-        vmNetworkSetupTest(new ValidationResult(VdcBllMessages.NON_VM_NETWORK_NOT_SUPPORTED_FOR_POOL_LEVEL),
+        vmNetworkSetupTest(failsWith(VdcBllMessages.NON_VM_NETWORK_NOT_SUPPORTED_FOR_POOL_LEVEL),
                 false,
                 false);
     }
 
-    private void stpTest(ValidationResult expected, boolean vmNetwork, boolean stp) {
+    private void stpTest(Matcher<ValidationResult> matcher, boolean vmNetwork, boolean stp) {
         when(network.isVmNetwork()).thenReturn(vmNetwork);
         when(network.getStp()).thenReturn(stp);
 
-        assertEquals(expected, validator.stpForVmNetworkOnly());
+        assertThat(validator.stpForVmNetworkOnly(), matcher);
     }
 
     @Test
     public void stpWhenVmNetwork() throws Exception {
-        stpTest(ValidationResult.VALID, true, true);
+        stpTest(isValid(), true, true);
     }
 
     @Test
     public void noStpWhenVmNetwork() throws Exception {
-        stpTest(ValidationResult.VALID, true, false);
+        stpTest(isValid(), true, false);
     }
 
     @Test
     public void stpWhenNonVmNetwork() throws Exception {
-        stpTest(new ValidationResult(VdcBllMessages.NON_VM_NETWORK_CANNOT_SUPPORT_STP), false, true);
+        stpTest(failsWith(VdcBllMessages.NON_VM_NETWORK_CANNOT_SUPPORT_STP), false, true);
     }
 
     @Test
     public void noStpWhenNonVmNetwork() throws Exception {
-        stpTest(ValidationResult.VALID, false, false);
+        stpTest(isValid(), false, false);
     }
 
-    private void mtuValidTest(ValidationResult expected, int mtu, boolean featureSupported) {
+    private void mtuValidTest(Matcher<ValidationResult> matcher, int mtu, boolean featureSupported) {
         mockConfigRule.mockConfigValue(ConfigValues.MTUOverrideSupported,
                 dataCenter.getcompatibility_version(),
                 featureSupported);
         when(network.getMtu()).thenReturn(mtu);
 
-        assertEquals(expected, validator.mtuValid());
+        assertThat(validator.mtuValid(), matcher);
     }
 
     @Test
     public void nonZeroMtuWhenSupported() throws Exception {
-        mtuValidTest(ValidationResult.VALID, 1, true);
+        mtuValidTest(isValid(), 1, true);
     }
 
     @Test
     public void nonZeroMtuWhenNotSupported() throws Exception {
-        mtuValidTest(new ValidationResult(VdcBllMessages.NETWORK_MTU_OVERRIDE_NOT_SUPPORTED), 1, false);
+        mtuValidTest(failsWith(VdcBllMessages.NETWORK_MTU_OVERRIDE_NOT_SUPPORTED), 1, false);
     }
 
     @Test
     public void zeroMtuWhenSupported() throws Exception {
-        mtuValidTest(ValidationResult.VALID, 0, true);
+        mtuValidTest(isValid(), 0, true);
     }
 
     @Test
     public void zeroMtuWhenNotSupported() throws Exception {
-        mtuValidTest(ValidationResult.VALID, 0, false);
+        mtuValidTest(isValid(), 0, false);
     }
 
-    private void networkPrefixValidTest(ValidationResult expected, String networkName) {
+    private void networkPrefixValidTest(Matcher<ValidationResult> matcher, String networkName) {
         when(network.getName()).thenReturn(networkName);
 
-        assertEquals(expected, validator.networkPrefixValid());
+        assertThat(validator.networkPrefixValid(), matcher);
     }
 
     @Test
     public void networkPrefixBond() throws Exception {
-        networkPrefixValidTest(new ValidationResult(VdcBllMessages.NETWORK_CANNOT_CONTAIN_BOND_NAME), "bond0");
+        networkPrefixValidTest(failsWith(VdcBllMessages.NETWORK_CANNOT_CONTAIN_BOND_NAME), "bond0");
     }
 
     @Test
     public void networkPrefixInnocent() throws Exception {
-        networkPrefixValidTest(ValidationResult.VALID, DEFAULT_NETWORK_NAME);
+        networkPrefixValidTest(isValid(), DEFAULT_NETWORK_NAME);
     }
 
-    private void vlanIdAvailableTest(ValidationResult expected, List<Network> networks) {
+    private void vlanIdAvailableTest(Matcher<ValidationResult> matcher, List<Network> networks) {
         this.networks.addAll(networks);
         when(network.getVlanId()).thenReturn(DEFAULT_VLAN_ID);
         when(network.getId()).thenReturn(DEFAULT_GUID);
 
-        assertEquals(expected.getMessage(), validator.vlanIdNotUsed().getMessage());
+        assertThat(validator.vlanIdNotUsed(), matcher);
     }
 
     private List<Network> getSingletonVlanNetworkList(int vlanId, Guid networkId) {
@@ -231,31 +233,31 @@ private List<Network> getSingletonVlanNetworkList(int vlanId, Guid networkId) {
 
     @Test
     public void vlanIdNoNetworks() throws Exception {
-        vlanIdAvailableTest(ValidationResult.VALID, Collections.<Network> emptyList());
+        vlanIdAvailableTest(isValid(), Collections.<Network> emptyList());
     }
 
     @Test
     public void vlanIdAvailable() throws Exception {
-        vlanIdAvailableTest(ValidationResult.VALID, getSingletonVlanNetworkList(OTHER_VLAN_ID, OTHER_GUID));
+        vlanIdAvailableTest(isValid(), getSingletonVlanNetworkList(OTHER_VLAN_ID, OTHER_GUID));
     }
 
     @Test
     public void vlanIdTakenByDifferentNetwork() throws Exception {
-        vlanIdAvailableTest(new ValidationResult(VdcBllMessages.NETWORK_VLAN_IN_USE),
+        vlanIdAvailableTest(failsWith(VdcBllMessages.NETWORK_VLAN_IN_USE),
                 getSingletonVlanNetworkList(DEFAULT_VLAN_ID, OTHER_GUID));
     }
 
     @Test
     public void vlanIdTakenBySameNetwork() throws Exception {
-        vlanIdAvailableTest(ValidationResult.VALID, getSingletonVlanNetworkList(DEFAULT_VLAN_ID, DEFAULT_GUID));
+        vlanIdAvailableTest(isValid(), getSingletonVlanNetworkList(DEFAULT_VLAN_ID, DEFAULT_GUID));
     }
 
-    private void networkNameAvailableTest(ValidationResult expected, List<Network> networks) {
+    private void networkNameAvailableTest(Matcher<ValidationResult> matcher, List<Network> networks) {
         this.networks.addAll(networks);
         when(network.getName()).thenReturn(DEFAULT_NETWORK_NAME);
         when(network.getId()).thenReturn(DEFAULT_GUID);
 
-        assertEquals(expected, validator.networkNameNotUsed());
+        assertThat(validator.networkNameNotUsed(), matcher);
     }
 
     private List<Network> getSingletonNamedNetworkList(String networkName, Guid networkId) {
@@ -267,92 +269,93 @@ private List<Network> getSingletonNamedNetworkList(String networkName, Guid netw
 
     @Test
     public void networkNameNoNetworks() throws Exception {
-        networkNameAvailableTest(ValidationResult.VALID, Collections.<Network> emptyList());
+        networkNameAvailableTest(isValid(), Collections.<Network> emptyList());
     }
 
     @Test
     public void networkNameAvailable() throws Exception {
-        networkNameAvailableTest(ValidationResult.VALID, getSingletonNamedNetworkList(OTHER_NETWORK_NAME, OTHER_GUID));
+        networkNameAvailableTest(isValid(), getSingletonNamedNetworkList(OTHER_NETWORK_NAME, OTHER_GUID));
     }
 
     @Test
     public void networkNameTakenByDifferentNetwork() throws Exception {
-        networkNameAvailableTest(new ValidationResult(VdcBllMessages.ACTION_TYPE_FAILED_NETWORK_NAME_IN_USE),
+        networkNameAvailableTest(failsWith(VdcBllMessages.ACTION_TYPE_FAILED_NETWORK_NAME_IN_USE),
                 getSingletonNamedNetworkList(DEFAULT_NETWORK_NAME, OTHER_GUID));
     }
 
     @Test
     public void networkNameTakenCaseSensitivelyByDifferentNetwork() throws Exception {
-        networkNameAvailableTest(ValidationResult.VALID,
+        networkNameAvailableTest(isValid(),
                 getSingletonNamedNetworkList(DEFAULT_NETWORK_NAME.toUpperCase(), OTHER_GUID));
     }
 
     @Test
     public void networkNameTakenBySameNetwork() throws Exception {
-        networkNameAvailableTest(ValidationResult.VALID,
+        networkNameAvailableTest(isValid(),
                 getSingletonNamedNetworkList(DEFAULT_NETWORK_NAME, DEFAULT_GUID));
     }
 
-    private void networkNotUsedByVmsTest(ValidationResult expected, List<VM> vms) {
+    private Matcher<ValidationResult> failsWithNetworkInUse() {
+        return failsWith(VdcBllMessages.ACTION_TYPE_FAILED_NETWORK_IN_USE);
+    }
+
+    private void networkNotUsedByVmsTest(Matcher<ValidationResult> matcher, List<VM> vms) {
         VmDAO vmDao = mock(VmDAO.class);
         when(vmDao.getAllForNetwork(any(Guid.class))).thenReturn(vms);
         when(dbFacade.getVmDao()).thenReturn(vmDao);
-        assertEquals(expected.getMessage(), validator.networkNotUsedByVms().getMessage());
+        assertThat(validator.networkNotUsedByVms(), matcher);
     }
 
     @Test
     public void networkNotInUseByVms() throws Exception {
-        networkNotUsedByVmsTest(ValidationResult.VALID, Collections.<VM> emptyList());
+        networkNotUsedByVmsTest(isValid(), Collections.<VM> emptyList());
     }
 
     @Test
     public void networkInUseByVms() throws Exception {
         VM vm = mock(VM.class);
         when(vm.getName()).thenReturn(NAMEABLE_NAME);
 
-        networkNotUsedByVmsTest(new ValidationResult(VdcBllMessages.ACTION_TYPE_FAILED_NETWORK_IN_USE),
-                Collections.singletonList(vm));
+        networkNotUsedByVmsTest(failsWithNetworkInUse(), Collections.singletonList(vm));
     }
 
-    private void networkNotUsedByHostsTest(ValidationResult expected, List<VDS> hosts) {
+    private void networkNotUsedByHostsTest(Matcher<ValidationResult> matcher, List<VDS> hosts) {
         VdsDAO hostDao = mock(VdsDAO.class);
         when(hostDao.getAllForNetwork(any(Guid.class))).thenReturn(hosts);
         when(dbFacade.getVdsDao()).thenReturn(hostDao);
-        assertEquals(expected.getMessage(), validator.networkNotUsedByHosts().getMessage());
+        assertThat(validator.networkNotUsedByHosts(), matcher);
     }
 
     @Test
     public void networkNotInUseByHosts() throws Exception {
-        networkNotUsedByHostsTest(ValidationResult.VALID, Collections.<VDS> emptyList());
+        networkNotUsedByHostsTest(isValid(), Collections.<VDS> emptyList());
     }
 
     @Test
     public void networkInUseByHosts() throws Exception {
         VDS host = mock(VDS.class);
         when(host.getName()).thenReturn(NAMEABLE_NAME);
 
-        networkNotUsedByHostsTest(new ValidationResult(VdcBllMessages.ACTION_TYPE_FAILED_NETWORK_IN_USE),
-                Collections.singletonList(host));
+        networkNotUsedByHostsTest(failsWithNetworkInUse(), Collections.singletonList(host));
     }
 
-    private void networkNotUsedByTemplatesTest(ValidationResult expected, List<VmTemplate> templates) {
+    private void networkNotUsedByTemplatesTest(Matcher<ValidationResult> matcher, List<VmTemplate> templates) {
         VmTemplateDAO templateDao = mock(VmTemplateDAO.class);
         when(templateDao.getAllForNetwork(any(Guid.class))).thenReturn(templates);
         when(dbFacade.getVmTemplateDao()).thenReturn(templateDao);
-        assertEquals(expected.getMessage(), validator.networkNotUsedByTemplates().getMessage());
+        assertThat(validator.networkNotUsedByTemplates(), matcher);
     }
 
     @Test
     public void networkNotInUseByTemplates() throws Exception {
-        networkNotUsedByTemplatesTest(ValidationResult.VALID, Collections.<VmTemplate> emptyList());
+        networkNotUsedByTemplatesTest(isValid(), Collections.<VmTemplate> emptyList());
     }
 
     @Test
     public void networkInUseByTemplates() throws Exception {
         VmTemplate template = mock(VmTemplate.class);
         when(template.getName()).thenReturn(NAMEABLE_NAME);
 
-        networkNotUsedByTemplatesTest(new ValidationResult(VdcBllMessages.ACTION_TYPE_FAILED_NETWORK_IN_USE),
-                Collections.singletonList(template));
+        networkNotUsedByTemplatesTest(failsWithNetworkInUse(), Collections.singletonList(template));
     }
 }
```

## Row 19
commit_url: https://github.com/martint/jmxutils/commit/b8e0398069cde724652b12e58ffeb20276345d3f
rm_type: Change Method Access Modifier
rm_description: Change Method Access Modifier private to protected in method protected getAttributeInfo(info MBeanInfo, attributeName String) : MBeanAttributeInfo from class org.weakref.jmx.AbstractMbeanTest
file_path: src/test/java/org/weakref/jmx/AbstractMbeanTest.java; src/test/java/org/weakref/jmx/TestMBeanBuilder.java
left_side: [{"filePath": "src/test/java/org/weakref/jmx/TestMBeanBuilder.java", "startLine": 136, "endLine": 144, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "private getAttributeInfo(info MBeanInfo, attributeName String) : MBeanAttributeInfo"}]
right_side: [{"filePath": "src/test/java/org/weakref/jmx/AbstractMbeanTest.java", "startLine": 112, "endLine": 120, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "method declaration with changed access modifier", "codeElement": "protected getAttributeInfo(info MBeanInfo, attributeName String) : MBeanAttributeInfo"}]

### Patch: src/test/java/org/weakref/jmx/AbstractMbeanTest.java
```diff
@@ -1,11 +1,124 @@
 package org.weakref.jmx;
 
+import org.testng.Assert;
 import org.testng.annotations.DataProvider;
+import org.testng.annotations.Test;
+
+import javax.management.MBeanAttributeInfo;
+import javax.management.MBeanInfo;
+import java.lang.reflect.Method;
+import java.util.List;
+
+import static org.testng.Assert.assertEquals;
+import static org.testng.Assert.assertFalse;
+import static org.testng.Assert.assertNotNull;
+import static org.testng.Assert.assertTrue;
 
 public abstract class AbstractMbeanTest<T>
 {
+    protected List<T> objects;
+
     protected abstract Object getObject(T t);
 
+    protected abstract MBeanInfo getMBeanInfo(T t)
+            throws Exception;
+
+    @Test(dataProvider = "fixtures")
+    public void testGetterAttributeInfo(String attribute, boolean isIs, Object[] values, Class<?> clazz)
+            throws Exception
+    {
+        String methodName = "set" + attribute;
+        for (T t : objects) {
+            String attributeName = toFeatureName(attribute, t);
+            SimpleObject simpleObject = toSimpleObject(t);
+            Method setter = simpleObject.getClass().getMethod(methodName, clazz);
+
+            MBeanInfo info = getMBeanInfo(t);
+            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
+            Assert.assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
+            Assert.assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
+            Assert.assertEquals(attributeInfo.getType(), setter.getParameterTypes()[0].getName(), "Attribute type for " + attributeName);
+            Assert.assertEquals(attributeInfo.isIs(), isIs, "Attribute isIs for " + attributeName);
+            Assert.assertTrue(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
+        }
+    }
+
+    @Test(dataProvider = "fixtures")
+    public void testSetterAttributeInfo(String attribute, boolean isIs, Object[] values, Class<?> clazz)
+            throws Exception
+    {
+        String methodName = (isIs ? "is" : "get") + attribute;
+
+        for (T t : objects) {
+            String attributeName = toFeatureName(attribute, t);
+            SimpleObject simpleObject = toSimpleObject(t);
+            Method getter = simpleObject.getClass().getMethod(methodName);
+
+            MBeanInfo info = getMBeanInfo(t);
+            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
+            Assert.assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
+            Assert.assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
+            Assert.assertEquals(attributeInfo.getType(), getter.getReturnType().getName(), "Attribute Type for " + attributeName);
+            Assert.assertTrue(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
+        }
+    }
+
+    @Test
+    public void testNotManagedAttributeInfo()
+            throws Exception
+    {
+
+        for (T t : objects) {
+            MBeanInfo info = getMBeanInfo(t);
+            String attributeName = toFeatureName("NotManaged", t);
+            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
+            Assert.assertNull(attributeInfo, "AttributeInfo for " + attributeName);
+        }
+    }
+
+    @Test
+    public void testReadOnlyAttributeInfo()
+            throws Exception
+    {
+        for (T t : objects) {
+            MBeanInfo info = getMBeanInfo(t);
+
+            String attributeName = toFeatureName("ReadOnly", t);
+            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
+            assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
+            assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
+            assertEquals(attributeInfo.getType(), "int", "Attribute Type for " + attributeName);
+            assertTrue(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
+            assertFalse(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
+        }
+    }
+
+    @Test
+    public void testWriteOnlyAttributeInfo()
+            throws Exception
+    {
+        for (T t : objects) {
+            MBeanInfo info = getMBeanInfo(t);
+            String attributeName = toFeatureName("WriteOnly", t);
+            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
+            Assert.assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
+            Assert.assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
+            Assert.assertEquals(attributeInfo.getType(), "int", "Attribute Type for " + attributeName);
+            Assert.assertFalse(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
+            Assert.assertTrue(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
+        }
+    }
+
+    protected MBeanAttributeInfo getAttributeInfo(MBeanInfo info, String attributeName)
+    {
+        for (MBeanAttributeInfo attributeInfo : info.getAttributes()) {
+            if (attributeInfo.getName().equals(attributeName)) {
+                return attributeInfo;
+            }
+        }
+        return null;
+    }
+
     @DataProvider(name = "fixtures")
     Object[][] getFixtures()
     {
```
### Patch: src/test/java/org/weakref/jmx/TestMBeanBuilder.java
```diff
@@ -13,7 +13,6 @@
 import javax.management.MBeanOperationInfo;
 import javax.management.MBeanParameterInfo;
 import javax.management.MalformedObjectNameException;
-import javax.management.ObjectName;
 import javax.management.ReflectionException;
 import java.io.IOException;
 import java.lang.reflect.InvocationTargetException;
@@ -28,10 +27,9 @@
 
 public class TestMBeanBuilder extends AbstractMbeanTest<Object>
 {
-    private final List<Object> objects = new ArrayList<Object>();
-
     public TestMBeanBuilder()
     {
+        objects = new ArrayList<Object>();
         objects.add(new SimpleObject());
         objects.add(new CustomAnnotationObject());
         objects.add(new FlattenObject());
@@ -45,102 +43,10 @@ protected Object getObject(Object o) {
         return o;
     }
 
-    @Test(dataProvider = "fixtures")
-    public void testGetterAttributeInfo(String attribute, boolean isIs, Object[] values, Class<?> clazz)
-            throws Exception
-    {
-        String methodName = "set" + attribute;
-        for (Object object : objects) {
-            MBeanInfo info = MBeanBuilder.from(object).build().getMBeanInfo();
-
-            String attributeName = toFeatureName(attribute, object);
-            SimpleObject simpleObject = toSimpleObject(object);
-            Method setter = simpleObject.getClass().getMethod(methodName, clazz);
-
-            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
-            assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
-            assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
-            assertEquals(attributeInfo.getType(), setter.getParameterTypes()[0].getName(), "Attribute type for " + attributeName);
-            assertEquals(attributeInfo.isIs(), isIs, "Attribute isIs for " + attributeName);
-            assertTrue(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
-        }
-    }
-
-    @Test(dataProvider = "fixtures")
-    public void testSetterAttributeInfo(String attribute, boolean isIs, Object[] values, Class<?> clazz)
-            throws Exception
-    {
-        String methodName = (isIs ? "is" : "get") + attribute;
-
-        for (Object object : objects) {
-            String attributeName = toFeatureName(attribute, object);
-            SimpleObject simpleObject = toSimpleObject(object);
-            Method getter = simpleObject.getClass().getMethod(methodName);
-
-            MBeanInfo info = MBeanBuilder.from(object).build().getMBeanInfo();
-            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
-            assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
-            assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
-            assertEquals(attributeInfo.getType(), getter.getReturnType().getName(), "Attribute Type for " + attributeName);
-            assertTrue(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
-        }
-    }
-
-    @Test
-    public void testNotManagedAttributeInfo()
-            throws Exception
-    {
-        for (Object object : objects) {
-            MBeanInfo info = MBeanBuilder.from(object).build().getMBeanInfo();
-
-            String attributeName = toFeatureName("NotManaged", object);
-            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
-            Assert.assertNull(attributeInfo, "AttributeInfo for " + attributeName);
-        }
-    }
-
-    @Test
-    public void testReadOnlyAttributeInfo()
-            throws Exception
-    {
-        for (Object object : objects) {
-            MBeanInfo info = MBeanBuilder.from(object).build().getMBeanInfo();
-
-            String attributeName = toFeatureName("ReadOnly", object);
-            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
-            assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
-            assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
-            assertEquals(attributeInfo.getType(), "int", "Attribute Type for " + attributeName);
-            assertTrue(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
-            assertFalse(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
-        }
-    }
-
-    @Test
-    public void testWriteOnlyAttributeInfo()
-            throws Exception
-    {
-        for (Object object : objects) {
-            MBeanInfo info = MBeanBuilder.from(object).build().getMBeanInfo();
-
-            String attributeName = toFeatureName("WriteOnly", object);
-            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
-            assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
-            assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
-            assertEquals(attributeInfo.getType(), "int", "Attribute Type for " + attributeName);
-            assertFalse(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
-            assertTrue(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
-        }
-    }
-
-    private MBeanAttributeInfo getAttributeInfo(MBeanInfo info, String attributeName)
+    @Override
+    protected MBeanInfo getMBeanInfo(Object object)
     {
-        for (MBeanAttributeInfo attributeInfo : info.getAttributes()) {
-            if (attributeInfo.getName().equals(attributeName)) {
-                return attributeInfo;
-            }
-        }
-        return null;
+        return MBeanBuilder.from(object).build().getMBeanInfo();
     }
 
     @Test(dataProvider = "fixtures")
@@ -150,7 +56,7 @@ public void testOperationInfo(String attribute, boolean isIs, Object[] values, C
         for (Object object : objects) {
             String operationName = toFeatureName("echo", object);
 
-            MBeanInfo beanInfo = MBeanBuilder.from(object).build().getMBeanInfo();
+            MBeanInfo beanInfo = getMBeanInfo(object);
             MBeanOperationInfo operationInfo = null;
             for (MBeanOperationInfo info : beanInfo.getOperations()) {
                 if (info.getName().equals(operationName)) {
@@ -296,7 +202,7 @@ public void testDescription()
     {
         for (Object object : objects) {
             boolean described = false;
-            MBeanInfo mbeanInfo = MBeanBuilder.from(object).build().getMBeanInfo();
+            MBeanInfo mbeanInfo = getMBeanInfo(object);
 
             for (MBeanAttributeInfo info : mbeanInfo.getAttributes()) {
                 String attributeName = toFeatureName("DescribedInt", object);
```

## Row 20
commit_url: https://github.com/dita-ot/dita-ot/commit/0ffdfe45362559a28ec7edf3371add90bed4fdcb
rm_type: Add Parameter
rm_description: Add Parameter file : Path in method public testWrite(file Path, map Path) : void from class org.dita.dost.writer.KeyrefPaserTest
file_path: src/test/java/org/dita/dost/writer/KeyrefPaserTest.java
left_side: [{"filePath": "src/test/java/org/dita/dost/writer/KeyrefPaserTest.java", "startLine": 116, "endLine": 129, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testMapWrite() : void"}]
right_side: [{"filePath": "src/test/java/org/dita/dost/writer/KeyrefPaserTest.java", "startLine": 45, "endLine": 45, "startColumn": 25, "endColumn": 34, "codeElementType": "SINGLE_VARIABLE_DECLARATION", "description": "added parameter", "codeElement": "file : Path"}, {"filePath": "src/test/java/org/dita/dost/writer/KeyrefPaserTest.java", "startLine": 43, "endLine": 60, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "method declaration with added parameter", "codeElement": "public testWrite(file Path, map Path) : void"}]

### Patch: src/test/java/org/dita/dost/writer/KeyrefPaserTest.java
```diff
@@ -8,13 +8,12 @@
 package org.dita.dost.writer;
 
 import static org.dita.dost.TestUtils.assertXMLEqual;
-import static org.dita.dost.TestUtils.createTempDir;
 
 import java.io.File;
-import java.io.IOException;
 import java.net.URI;
 import java.nio.file.Path;
 import java.nio.file.Paths;
+import java.util.stream.Stream;
 import javax.xml.transform.stream.StreamSource;
 import net.sf.saxon.s9api.SaxonApiException;
 import net.sf.saxon.s9api.XdmNode;
@@ -24,9 +23,10 @@
 import org.dita.dost.util.Job;
 import org.dita.dost.util.KeyScope;
 import org.dita.dost.util.XMLUtils;
-import org.junit.jupiter.api.AfterEach;
-import org.junit.jupiter.api.BeforeEach;
-import org.junit.jupiter.api.Test;
+import org.junit.jupiter.api.io.TempDir;
+import org.junit.jupiter.params.ParameterizedTest;
+import org.junit.jupiter.params.provider.Arguments;
+import org.junit.jupiter.params.provider.MethodSource;
 import org.xml.sax.InputSource;
 
 public class KeyrefPaserTest {
@@ -36,125 +36,39 @@ public class KeyrefPaserTest {
   private static final File expDir = new File(resourceDir, "exp");
 
   private final XMLUtils xmlUtils = new XMLUtils();
-  private KeyScope keyDefinition;
+
+  @TempDir
   private File tempDir;
 
-  @BeforeEach
-  public void setUp() throws Exception {
-    tempDir = createTempDir(KeyrefPaserTest.class);
+  @ParameterizedTest
+  @MethodSource("testWriteArguments")
+  public void testWrite(Path file, Path map) throws Exception {
     TestUtils.copy(srcDir, tempDir);
 
-    keyDefinition = readKeyMap(Paths.get("keys.ditamap"));
-  }
-
-  @AfterEach
-  public void tearDown() throws IOException {
-    TestUtils.forceDelete(tempDir);
-  }
-
-  @Test
-  public void testTopicWrite() throws Exception {
-    final KeyrefPaser parser = new KeyrefPaser();
-    parser.setLogger(new TestUtils.TestLogger());
-    parser.setJob(new Job(tempDir, new StreamStore(tempDir, new XMLUtils())));
-    parser.setKeyDefinition(keyDefinition);
-    parser.setCurrentFile(new File(tempDir, "a.xml").toURI());
-    parser.write(new File(tempDir, "a.xml"));
-
-    assertXMLEqual(
-      new InputSource(new File(expDir, "a.xml").toURI().toString()),
-      new InputSource(new File(tempDir, "a.xml").toURI().toString())
-    );
-  }
-
-  @Test
-  public void testTopicWriteSubdir() throws Exception {
-    final KeyrefPaser parser = new KeyrefPaser();
-    parser.setLogger(new TestUtils.TestLogger());
-    parser.setJob(new Job(tempDir, new StreamStore(tempDir, new XMLUtils())));
-    parser.setKeyDefinition(keyDefinition);
-    final String tempSubDir = tempDir + File.separator + "subdir";
-    parser.setCurrentFile(new File(tempSubDir, "subdirtopic.xml").toURI());
-    parser.write(new File(tempSubDir, "subdirtopic.xml"));
-
-    assertXMLEqual(
-      new InputSource(new File(expDir + File.separator + "subdir", "subdirtopic.xml").toURI().toString()),
-      new InputSource(new File(tempSubDir, "subdirtopic.xml").toURI().toString())
-    );
-  }
-
-  @Test
-  public void testFragment() throws Exception {
+    final KeyScope keyDefinition = readKeyMap(map);
     final KeyrefPaser parser = new KeyrefPaser();
     parser.setLogger(new TestUtils.TestLogger());
     parser.setJob(new Job(tempDir, new StreamStore(tempDir, new XMLUtils())));
     parser.setKeyDefinition(keyDefinition);
-    parser.setCurrentFile(new File(tempDir, "id.xml").toURI());
-    parser.write(new File(tempDir, "id.xml"));
+    parser.setCurrentFile(Paths.get(tempDir.getAbsolutePath(), file.toString()).toUri());
+    parser.write(Paths.get(tempDir.getAbsolutePath(), file.toString()).toFile());
 
     assertXMLEqual(
-      new InputSource(new File(expDir, "id.xml").toURI().toString()),
-      new InputSource(new File(tempDir, "id.xml").toURI().toString())
+      new InputSource(Paths.get(expDir.getAbsolutePath(), file.toString()).toUri().toString()),
+      new InputSource(Paths.get(tempDir.getAbsolutePath(), file.toString()).toUri().toString())
     );
   }
 
-  @Test
-  public void testFallback() throws Exception {
-    final KeyrefPaser parser = new KeyrefPaser();
-    parser.setLogger(new TestUtils.TestLogger());
-    parser.setJob(new Job(tempDir, new StreamStore(tempDir, new XMLUtils())));
-    parser.setKeyDefinition(keyDefinition);
-    parser.setCurrentFile(new File(tempDir, "fallback.xml").toURI());
-    parser.write(new File(tempDir, "fallback.xml"));
-
-    assertXMLEqual(
-      new InputSource(new File(expDir, "fallback.xml").toURI().toString()),
-      new InputSource(new File(tempDir, "fallback.xml").toURI().toString())
-    );
-  }
-
-  @Test
-  public void testMapWrite() throws Exception {
-    final KeyrefPaser parser = new KeyrefPaser();
-    parser.setLogger(new TestUtils.TestLogger());
-    parser.setJob(new Job(tempDir, new StreamStore(tempDir, new XMLUtils())));
-    parser.setKeyDefinition(keyDefinition);
-    parser.setCurrentFile(new File(tempDir, "b.ditamap").toURI());
-    parser.write(new File(tempDir, "b.ditamap"));
-
-    assertXMLEqual(
-      new InputSource(new File(expDir, "b.ditamap").toURI().toString()),
-      new InputSource(new File(tempDir, "b.ditamap").toURI().toString())
-    );
-  }
-
-  @Test
-  public void testUpLevelMapWrite() throws Exception {
-    final KeyrefPaser parser = new KeyrefPaser();
-    parser.setLogger(new TestUtils.TestLogger());
-    parser.setJob(new Job(tempDir, new StreamStore(tempDir, new XMLUtils())));
-    parser.setKeyDefinition(readKeyMap(Paths.get("subdir", "c.ditamap")));
-    parser.setCurrentFile(new File(tempDir, "subdir" + File.separator + "c.ditamap").toURI());
-    parser.write(new File(tempDir, "subdir" + File.separator + "c.ditamap"));
-
-    assertXMLEqual(
-      new InputSource(new File(expDir, "subdir" + File.separator + "c.ditamap").toURI().toString()),
-      new InputSource(new File(tempDir, "subdir" + File.separator + "c.ditamap").toURI().toString())
-    );
-  }
-
-  @Test
-  public void testMapWithKeyScopes() throws Exception {
-    final KeyrefPaser parser = new KeyrefPaser();
-    parser.setLogger(new TestUtils.TestLogger());
-    parser.setJob(new Job(tempDir, new StreamStore(tempDir, new XMLUtils())));
-    parser.setKeyDefinition(keyDefinition);
-    parser.setCurrentFile(new File(tempDir, "d.ditamap").toURI());
-    parser.write(new File(tempDir, "d.ditamap"));
-
-    assertXMLEqual(
-      new InputSource(new File(expDir, "d.ditamap").toURI().toString()),
-      new InputSource(new File(tempDir, "d.ditamap").toURI().toString())
+  private static Stream<Arguments> testWriteArguments() {
+    return Stream.of(
+      Arguments.of(Paths.get("a.xml"), Paths.get("keys.ditamap")),
+      Arguments.of(Paths.get("subdir", "subdirtopic.xml"), Paths.get("keys.ditamap")),
+      Arguments.of(Paths.get("id.xml"), Paths.get("keys.ditamap")),
+      Arguments.of(Paths.get("fallback.xml"), Paths.get("keys.ditamap")),
+      Arguments.of(Paths.get("b.ditamap"), Paths.get("keys.ditamap")),
+      Arguments.of(Paths.get("d.ditamap"), Paths.get("keys.ditamap")),
+      Arguments.of(Paths.get("copy-to-keys.ditamap"), Paths.get("keys.ditamap")),
+      Arguments.of(Paths.get("subdir", "c.ditamap"), Paths.get("subdir", "c.ditamap"))
     );
   }
 
@@ -177,20 +91,4 @@ private XdmNode parse(final URI in) {
       throw new RuntimeException(e);
     }
   }
-
-  @Test
-  public void testTopicWriteCopyTo() throws Exception {
-    final KeyrefPaser parser = new KeyrefPaser();
-    parser.setLogger(new TestUtils.TestLogger());
-    parser.setJob(new Job(tempDir, new StreamStore(tempDir, new XMLUtils())));
-    KeyScope kd = readKeyMap(Paths.get("copy-to-keys.ditamap"));
-    parser.setKeyDefinition(kd);
-    parser.setCurrentFile(new File(tempDir, "copy-to-keys.dita").toURI());
-    parser.write(new File(tempDir, "copy-to-keys.dita"));
-
-    assertXMLEqual(
-      new InputSource(new File(expDir, "copy-to-keys.dita").toURI().toString()),
-      new InputSource(new File(tempDir, "copy-to-keys.dita").toURI().toString())
-    );
-  }
 }
```

## Row 21
commit_url: https://github.com/agrestio/agrest/commit/828f993e3312fa246cfdb9bb6cf33a6728b08863
rm_type: Change Variable Type
rm_description: Change Variable Type t4 : ResourceEntity<E1> to t4 : ResourceEntity<Tr> in method public testConstrainResponse_FetchLimit() : void from class io.agrest.runtime.constraints.ConstraintsHandlerTest
file_path: agrest/src/test/java/io/agrest/runtime/constraints/ConstraintsHandlerTest.java
left_side: [{"filePath": "agrest/src/test/java/io/agrest/runtime/constraints/ConstraintsHandlerTest.java", "startLine": 150, "endLine": 150, "startColumn": 28, "endColumn": 69, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "original variable declaration", "codeElement": "t4 : ResourceEntity<E1>"}, {"filePath": "agrest/src/test/java/io/agrest/runtime/constraints/ConstraintsHandlerTest.java", "startLine": 151, "endLine": 151, "startColumn": 9, "endColumn": 29, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "agrest/src/test/java/io/agrest/runtime/constraints/ConstraintsHandlerTest.java", "startLine": 152, "endLine": 152, "startColumn": 9, "endColumn": 59, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "agrest/src/test/java/io/agrest/runtime/constraints/ConstraintsHandlerTest.java", "startLine": 153, "endLine": 153, "startColumn": 9, "endColumn": 45, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}]
right_side: [{"filePath": "agrest/src/test/java/io/agrest/runtime/constraints/ConstraintsHandlerTest.java", "startLine": 110, "endLine": 110, "startColumn": 28, "endColumn": 71, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "changed-type variable declaration", "codeElement": "t4 : ResourceEntity<Tr>"}, {"filePath": "agrest/src/test/java/io/agrest/runtime/constraints/ConstraintsHandlerTest.java", "startLine": 111, "endLine": 111, "startColumn": 9, "endColumn": 29, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the variable with changed type", "codeElement": null}, {"filePath": "agrest/src/test/java/io/agrest/runtime/constraints/ConstraintsHandlerTest.java", "startLine": 112, "endLine": 112, "startColumn": 9, "endColumn": 60, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the variable with changed type", "codeElement": null}, {"filePath": "agrest/src/test/java/io/agrest/runtime/constraints/ConstraintsHandlerTest.java", "startLine": 113, "endLine": 113, "startColumn": 9, "endColumn": 45, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the variable with changed type", "codeElement": null}]

### Patch: agrest/src/test/java/io/agrest/runtime/constraints/ConstraintsHandlerTest.java
```diff
@@ -1,325 +1,431 @@
 package io.agrest.runtime.constraints;
 
-import io.agrest.EntityConstraint;
 import io.agrest.NestedResourceEntity;
 import io.agrest.ResourceEntity;
 import io.agrest.RootResourceEntity;
 import io.agrest.SizeConstraints;
+import io.agrest.annotation.AgAttribute;
+import io.agrest.annotation.AgId;
+import io.agrest.annotation.AgRelationship;
 import io.agrest.constraints.Constraint;
-import io.agrest.it.fixture.cayenne.E1;
-import io.agrest.it.fixture.cayenne.E2;
-import io.agrest.it.fixture.cayenne.E3;
-import io.agrest.it.fixture.cayenne.E4;
-import io.agrest.it.fixture.cayenne.E5;
 import io.agrest.meta.AgEntity;
-import io.agrest.meta.AgRelationship;
 import io.agrest.meta.DefaultAgAttribute;
+import io.agrest.meta.compiler.AgEntityCompiler;
+import io.agrest.meta.compiler.PojoEntityCompiler;
 import io.agrest.property.BeanPropertyReader;
-import org.apache.cayenne.exp.Expression;
+import io.agrest.runtime.meta.IMetadataService;
+import io.agrest.runtime.meta.MetadataService;
 import org.apache.cayenne.exp.parser.ASTObjPath;
-import org.junit.Before;
+import org.junit.BeforeClass;
 import org.junit.Test;
 
 import java.util.Collections;
 import java.util.List;
 
 import static org.apache.cayenne.exp.ExpressionFactory.exp;
 import static org.junit.Assert.*;
-import static org.mockito.Mockito.mock;
-import static org.mockito.Mockito.when;
 
 public class ConstraintsHandlerTest {
 
-    private ConstraintsHandler constraintHandler;
-
-    private AgEntity<E1> age0;
-    private AgEntity<E2> age1;
-    private AgEntity<E3> age2;
-    private AgEntity<E4> age3;
-    private AgEntity<E5> age4;
-
-    @SuppressWarnings("unchecked")
-    @Before
-    public void before() {
-
-        age0 = mock(AgEntity.class);
-        when(age0.getName()).thenReturn("E1");
-        when(age0.getType()).thenReturn(E1.class);
-        AgRelationship r1 = mock(AgRelationship.class);
-        when(age0.getRelationship("r1")).thenReturn(r1);
-        when(r1.getName()).thenReturn("r1");
-        when(r1.getTargetEntity()).then(invocation -> age1);
-
-        AgRelationship r2 = mock(AgRelationship.class);
-        when(age0.getRelationship("r2")).thenReturn(r2);
-        when(r2.getName()).thenReturn("r2");
-        when(r2.getTargetEntity()).then(invocation -> age3);
-
-        age1 = mock(AgEntity.class);
-        when(age1.getName()).thenReturn("E2");
-        when(age1.getType()).thenReturn(E2.class);
-
-        AgRelationship r11 = mock(AgRelationship.class);
-        when(age1.getRelationship("r11")).thenReturn(r11);
-        when(r11.getName()).thenReturn("r11");
-        when(r11.getTargetEntity()).then(invocation -> age2);
-
-        age2 = mock(AgEntity.class);
-        when(age2.getName()).thenReturn("E3");
-        when(age2.getType()).thenReturn(E3.class);
-
-        age3 = mock(AgEntity.class);
-        when(age3.getName()).thenReturn("E4");
-        when(age3.getType()).thenReturn(E4.class);
-
-        age4 = mock(AgEntity.class);
-        when(age4.getName()).thenReturn("E5");
-        when(age4.getType()).thenReturn(E5.class);
-
-        List<EntityConstraint> r = Collections.emptyList();
-        List<EntityConstraint> w = Collections.emptyList();
-        this.constraintHandler = new ConstraintsHandler(r, w);
+    private static ConstraintsHandler constraintsHandler;
+    private static IMetadataService metadata;
+
+    @BeforeClass
+    public static void before() {
+        AgEntityCompiler compiler = new PojoEntityCompiler(Collections.emptyMap());
+        metadata = new MetadataService(Collections.singletonList(compiler));
+        constraintsHandler = new ConstraintsHandler(Collections.emptyList(), Collections.emptyList());
     }
 
     @Test
-    public void testApply_FetchOffset() {
+    public void testConstrainResponse_FetchOffset() {
+
+        AgEntity<Tr> entity = metadata.getAgEntity(Tr.class);
 
         SizeConstraints s1 = new SizeConstraints().fetchOffset(5);
         SizeConstraints s2 = new SizeConstraints().fetchOffset(0);
 
-        ResourceEntity<E1> t1 = new RootResourceEntity<>(age0, null);
+        ResourceEntity<Tr> t1 = new RootResourceEntity<>(entity, null);
         t1.setFetchOffset(0);
-        constraintHandler.constrainResponse(t1, s1, null);
+        constraintsHandler.constrainResponse(t1, s1, null);
         assertEquals(0, t1.getFetchOffset());
         assertEquals(5, s1.getFetchOffset());
 
-        ResourceEntity<E1> t2 = new RootResourceEntity<>(age0, null);
+        ResourceEntity<Tr> t2 = new RootResourceEntity<>(entity, null);
         t2.setFetchOffset(3);
-        constraintHandler.constrainResponse(t2, s1, null);
+        constraintsHandler.constrainResponse(t2, s1, null);
         assertEquals(3, t2.getFetchOffset());
         assertEquals(5, s1.getFetchOffset());
 
-        ResourceEntity<E1> t3 = new RootResourceEntity<>(age0, null);
+        ResourceEntity<Tr> t3 = new RootResourceEntity<>(entity, null);
         t3.setFetchOffset(6);
-        constraintHandler.constrainResponse(t3, s1, null);
+        constraintsHandler.constrainResponse(t3, s1, null);
         assertEquals(5, t3.getFetchOffset());
         assertEquals(5, s1.getFetchOffset());
 
-        ResourceEntity<E1> t4 = new RootResourceEntity<>(age0, null);
+        ResourceEntity<Tr> t4 = new RootResourceEntity<>(entity, null);
         t4.setFetchOffset(6);
-        constraintHandler.constrainResponse(t4, s2, null);
+        constraintsHandler.constrainResponse(t4, s2, null);
         assertEquals(6, t4.getFetchOffset());
         assertEquals(0, s2.getFetchOffset());
     }
 
     @Test
-    public void testApply_FetchLimit() {
+    public void testConstrainResponse_FetchLimit() {
+
+        AgEntity<Tr> entity = metadata.getAgEntity(Tr.class);
 
         SizeConstraints s1 = new SizeConstraints().fetchLimit(5);
         SizeConstraints s2 = new SizeConstraints().fetchLimit(0);
 
-        ResourceEntity<E1> t1 = new RootResourceEntity<>(age0, null);
-        constraintHandler.constrainResponse(t1, s1, null);
+        ResourceEntity<Tr> t1 = new RootResourceEntity<>(entity, null);
+        constraintsHandler.constrainResponse(t1, s1, null);
         assertEquals(5, t1.getFetchLimit());
         assertEquals(5, s1.getFetchLimit());
 
-        ResourceEntity<E1> t1_1 = new RootResourceEntity<>(age0, null);
+        ResourceEntity<Tr> t1_1 = new RootResourceEntity<>(entity, null);
         t1_1.setFetchLimit(0);
-        constraintHandler.constrainResponse(t1_1, s1, null);
+        constraintsHandler.constrainResponse(t1_1, s1, null);
         assertEquals(5, t1_1.getFetchLimit());
         assertEquals(5, s1.getFetchLimit());
 
-        ResourceEntity<E1> t1_2 = new RootResourceEntity<>(age0, null);
+        ResourceEntity<Tr> t1_2 = new RootResourceEntity<>(entity, null);
         t1_2.setFetchLimit(-1);
-        constraintHandler.constrainResponse(t1_2, s1, null);
+        constraintsHandler.constrainResponse(t1_2, s1, null);
         assertEquals(5, t1_2.getFetchLimit());
         assertEquals(5, s1.getFetchLimit());
 
-        ResourceEntity<E1> t2 = new RootResourceEntity<>(age0, null);
+        ResourceEntity<Tr> t2 = new RootResourceEntity<>(entity, null);
         t2.setFetchLimit(3);
-        constraintHandler.constrainResponse(t2, s1, null);
+        constraintsHandler.constrainResponse(t2, s1, null);
         assertEquals(3, t2.getFetchLimit());
         assertEquals(5, s1.getFetchLimit());
 
-        ResourceEntity<E1> t3 = new RootResourceEntity<>(age0, null);
+        ResourceEntity<Tr> t3 = new RootResourceEntity<>(entity, null);
         t3.setFetchLimit(6);
-        constraintHandler.constrainResponse(t3, s1, null);
+        constraintsHandler.constrainResponse(t3, s1, null);
         assertEquals(5, t3.getFetchLimit());
         assertEquals(5, s1.getFetchLimit());
 
-        ResourceEntity<E1> t4 = new RootResourceEntity<>(age0, null);
+        ResourceEntity<Tr> t4 = new RootResourceEntity<>(entity, null);
         t4.setFetchLimit(6);
-        constraintHandler.constrainResponse(t4, s2, null);
+        constraintsHandler.constrainResponse(t4, s2, null);
         assertEquals(6, t4.getFetchLimit());
         assertEquals(0, s2.getFetchLimit());
     }
 
     @Test
-    public void testApply_ResourceEntity_NoTargetRel() {
+    public void testConstrainResponse_ResourceEntity_NoTargetRel() {
 
-        Constraint<E1> tc1 = Constraint.excludeAll(E1.class).attributes("a", "b");
+        AgEntity<Tr> entityTr = metadata.getAgEntity(Tr.class);
+        AgEntity<Ts> entityTs = metadata.getAgEntity(Ts.class);
 
-        ResourceEntity<E1> te1 = new RootResourceEntity<>(age0, null);
+        Constraint<Tr> tc1 = Constraint.excludeAll(Tr.class).attributes("a", "b");
+
+        ResourceEntity<Tr> te1 = new RootResourceEntity<>(entityTr, null);
         appendAttribute(te1, "c");
         appendAttribute(te1, "b");
 
-        NestedResourceEntity<?> te11 = new NestedResourceEntity<>(age2, null, null, mock(AgRelationship.class));
+        NestedResourceEntity<Ts> te11 = new NestedResourceEntity<>(entityTs, null, te1, entityTr.getRelationship("rts"));
         appendAttribute(te11, "a1");
         appendAttribute(te11, "b1");
         te1.getChildren().put("d", te11);
 
-        constraintHandler.constrainResponse(te1, null, tc1);
+        constraintsHandler.constrainResponse(te1, null, tc1);
         assertEquals(1, te1.getAttributes().size());
         assertTrue(te1.getAttributes().containsKey("b"));
         assertTrue(te1.getChildren().isEmpty());
     }
 
     @Test
-    public void testApply_ResourceEntity_TargetRel() {
+    public void testConstrainResponse_ResourceEntity_TargetRel() {
+
+        AgEntity<Tr> entityTr = metadata.getAgEntity(Tr.class);
+        AgEntity<Ts> entityTs = metadata.getAgEntity(Ts.class);
+        AgEntity<Tv> entityTv = metadata.getAgEntity(Tv.class);
+
+        Constraint<Tr> constraint = Constraint.excludeAll(Tr.class).attributes("a", "b")
+                .path("rts", Constraint.excludeAll(Ts.class).attributes("n", "m"))
+                .path("rts.rtt", Constraint.excludeAll(Tt.class).attributes("p", "r"))
+                .path("rtu", Constraint.excludeAll(Tu.class).attributes("k", "l"));
+
+        ResourceEntity<Tr> tr = new RootResourceEntity<>(entityTr, null);
+        appendAttribute(tr, "c");
+        appendAttribute(tr, "b");
+
+        NestedResourceEntity<Ts> ts = new NestedResourceEntity<>(entityTs, null, tr, entityTr.getRelationship("rts"));
+        appendAttribute(ts, "m");
+        appendAttribute(ts, "z");
+        tr.getChildren().put("rts", ts);
+
+        NestedResourceEntity<Tv> tv = new NestedResourceEntity<>(entityTv, null, tr, entityTr.getRelationship("rtv"));
+        appendAttribute(tv, "p");
+        appendAttribute(tv, "z");
+        tr.getChildren().put("rtv", tv);
+
+        constraintsHandler.constrainResponse(tr, null, constraint);
+        assertEquals(1, tr.getAttributes().size());
+        assertTrue(tr.getAttributes().containsKey("b"));
+        assertEquals(1, tr.getChildren().size());
+
+        ResourceEntity<?> mergedTs = tr.getChildren().get("rts");
+        assertNotNull(mergedTs);
+        assertTrue(mergedTs.getChildren().isEmpty());
+        assertEquals(1, mergedTs.getAttributes().size());
+        assertTrue(mergedTs.getAttributes().containsKey("m"));
+    }
 
-        Constraint<E1> tc1 = Constraint.excludeAll(E1.class).attributes("a", "b")
-                .path("r1", Constraint.excludeAll(E2.class).attributes("n", "m"))
-                .path("r1.r11", Constraint.excludeAll(E3.class).attributes("p", "r"))
-                .path("r2", Constraint.excludeAll(E4.class).attributes("k", "l"));
+    @Test
+    public void testConstrainResponse_ResourceEntity_Id() {
 
-        ResourceEntity<E1> te1 = new RootResourceEntity<>(age0, null);
-        appendAttribute(te1, "c");
-        appendAttribute(te1, "b");
+        AgEntity<Tr> entity = metadata.getAgEntity(Tr.class);
 
-        NestedResourceEntity<?> te11 = new NestedResourceEntity<>(age1, null, te1, mock(AgRelationship.class));
-        appendAttribute(te11, "m");
-        appendAttribute(te11, "z");
-        te1.getChildren().put("r1", te11);
+        Constraint<Tr> constraint1 = Constraint.excludeAll(Tr.class).excludeId();
+        Constraint<Tr> constraint2 = Constraint.excludeAll(Tr.class).includeId();
 
-        NestedResourceEntity<?> te21 = new NestedResourceEntity<>(age4, null, te1, mock(AgRelationship.class));
-        appendAttribute(te21, "p");
-        appendAttribute(te21, "z");
-        te1.getChildren().put("r3", te21);
+        ResourceEntity<Tr> e1 = new RootResourceEntity<>(entity, null);
+        e1.includeId();
+        constraintsHandler.constrainResponse(e1, null, constraint1);
+        assertFalse(e1.isIdIncluded());
 
-        constraintHandler.constrainResponse(te1, null, tc1);
-        assertEquals(1, te1.getAttributes().size());
-        assertTrue(te1.getAttributes().containsKey("b"));
-        assertEquals(1, te1.getChildren().size());
+        ResourceEntity<Tr> e2 = new RootResourceEntity<>(entity, null);
+        e2.includeId();
+        constraintsHandler.constrainResponse(e2, null, constraint2);
+        assertTrue(e2.isIdIncluded());
 
-        ResourceEntity<?> mergedTe11 = te1.getChildren().get("r1");
-        assertNotNull(mergedTe11);
-        assertTrue(mergedTe11.getChildren().isEmpty());
-        assertEquals(1, mergedTe11.getAttributes().size());
-        assertTrue(mergedTe11.getAttributes().containsKey("m"));
+        ResourceEntity<Tr> e3 = new RootResourceEntity<>(entity, null);
+        e3.excludeId();
+        constraintsHandler.constrainResponse(e3, null, constraint2);
+        assertFalse(e3.isIdIncluded());
     }
 
     @Test
-    public void testMerge_ResourceEntity_Id() {
+    public void testConstrainResponse_CayenneExp() {
 
-        Constraint<E1> tc1 = Constraint.excludeAll(E1.class).excludeId();
-        Constraint<E1> tc2 = Constraint.excludeAll(E1.class).includeId();
+        AgEntity<Tr> entity = metadata.getAgEntity(Tr.class);
+        Constraint<Tr> constraint = Constraint.excludeAll(Tr.class).and(exp("a = 5"));
 
-        ResourceEntity<E1> te1 = new RootResourceEntity<>(age0, null);
-        te1.includeId();
-        constraintHandler.constrainResponse(te1, null, tc1);
-        assertFalse(te1.isIdIncluded());
+        ResourceEntity<Tr> e1 = new RootResourceEntity<>(entity, null);
+        constraintsHandler.constrainResponse(e1, null, constraint);
+        assertEquals(exp("a = 5"), e1.getQualifier());
 
-        ResourceEntity<E1> te2 = new RootResourceEntity<>(age0, null);
-        te2.includeId();
-        constraintHandler.constrainResponse(te2, null, tc2);
-        assertTrue(te2.isIdIncluded());
-
-        ResourceEntity<E1> te3 = new RootResourceEntity<>(age0, null);
-        te3.excludeId();
-        constraintHandler.constrainResponse(te3, null, tc2);
-        assertFalse(te3.isIdIncluded());
+        ResourceEntity<Tr> e2 = new RootResourceEntity<>(entity, null);
+        e2.andQualifier(exp("b = 'd'"));
+        constraintsHandler.constrainResponse(e2, null, constraint);
+        assertEquals(exp("b = 'd' and a = 5"), e2.getQualifier());
     }
 
     @Test
-    public void testMerge_CayenneExp() {
-
-        Expression q1 = exp("a = 5");
+    public void testConstrainResponse_MapByAttribute_Excluded() {
 
-        Constraint<E1> tc1 = Constraint.excludeAll(E1.class).and(q1);
+        AgEntity<Tr> entityTr = metadata.getAgEntity(Tr.class);
+        AgEntity<Ts> entityTs = metadata.getAgEntity(Ts.class);
 
-        ResourceEntity<E1> te1 = new RootResourceEntity<>(age0, null);
-        constraintHandler.constrainResponse(te1, null, tc1);
-        assertEquals(exp("a = 5"), te1.getQualifier());
+        Constraint<Tr> constraint = Constraint
+                .excludeAll(Tr.class)
+                .path("rts", Constraint.excludeAll(Ts.class).attribute("m"));
 
-        ResourceEntity<E1> te2 = new RootResourceEntity<>(age0, null);
-        te2.andQualifier(exp("b = 'd'"));
-        constraintHandler.constrainResponse(te2, null, tc1);
-        assertEquals(exp("b = 'd' and a = 5"), te2.getQualifier());
-    }
-
-    @Test
-    public void testMerge_MapBy() {
+        ResourceEntity<Ts> tsMapBy = new RootResourceEntity<>(entityTs, null);
+        appendAttribute(tsMapBy, "m");
+        appendAttribute(tsMapBy, "n");
 
-        Constraint<E1> tc1 = Constraint.excludeAll(E1.class).path("r1",
-                Constraint.excludeAll(E2.class).attribute("a"));
+        NestedResourceEntity<Tr> trMapBy = new NestedResourceEntity<>(entityTr, null, tsMapBy, entityTr.getRelationship("rts"));
+        appendAttribute(trMapBy, "a");
+        appendAttribute(trMapBy, "b");
+        tsMapBy.getChildren().put("rts", trMapBy);
 
-        ResourceEntity<E2> te1MapBy = new RootResourceEntity<>(age1, null);
+        ResourceEntity<Tr> e = new RootResourceEntity<>(entityTr, null);
+        e.mapBy(tsMapBy, "rts.n");
 
-        NestedResourceEntity<E1> te1MapByTarget = new NestedResourceEntity<>(age0, null, te1MapBy, mock(AgRelationship.class));
-        appendAttribute(te1MapByTarget, "b");
-        te1MapBy.getChildren().put("r1", te1MapByTarget);
+        constraintsHandler.constrainResponse(e, null, constraint);
+        assertNull(e.getMapBy());
+        assertNull(e.getMapByPath());
+    }
 
-        ResourceEntity<E1> te1 = new RootResourceEntity<>(age0, null);
-        te1.mapBy(te1MapBy, "r1.b");
+    @Test
+    public void testConstrainResponse_MapByAttribute_Included() {
+        AgEntity<Tr> entityTr = metadata.getAgEntity(Tr.class);
+        AgEntity<Ts> entityTs = metadata.getAgEntity(Ts.class);
 
-        constraintHandler.constrainResponse(te1, null, tc1);
-        assertNull(te1.getMapBy());
-        assertNull(te1.getMapByPath());
+        Constraint<Tr> constraint = Constraint
+                .excludeAll(Tr.class)
+                .path("rts", Constraint.excludeAll(Ts.class).attribute("m"));
 
-        NestedResourceEntity<E2> te2MapByTarget = new NestedResourceEntity<>(age1, null, te1MapBy, mock(AgRelationship.class));
-        appendAttribute(te2MapByTarget, "a");
+        ResourceEntity<Ts> tsMapBy = new RootResourceEntity<>(entityTs, null);
+        appendAttribute(tsMapBy, "m");
+        appendAttribute(tsMapBy, "n");
 
-        ResourceEntity<E1> te2MapBy = new RootResourceEntity<>(age0, null);
-        te1MapBy.getChildren().put("r1", te2MapByTarget);
+        NestedResourceEntity<Tr> trMapBy = new NestedResourceEntity<>(entityTr, null, tsMapBy, entityTs.getRelationship("rtrs"));
+        appendAttribute(trMapBy, "a");
+        appendAttribute(trMapBy, "b");
+        tsMapBy.getChildren().put("rts", trMapBy);
 
-        ResourceEntity<E1> te2 = new RootResourceEntity<>(age0, null);
-        te2.mapBy(te2MapBy, "r1.a");
+        ResourceEntity<Tr> e = new RootResourceEntity<>(entityTr, null);
+        e.mapBy(tsMapBy, "rts.m");
 
-        constraintHandler.constrainResponse(te2, null, tc1);
-        assertSame(te2MapBy, te2.getMapBy());
-        assertEquals("r1.a", te2.getMapByPath());
+        constraintsHandler.constrainResponse(e, null, constraint);
+        assertSame(tsMapBy, e.getMapBy());
+        assertEquals("rts.m", e.getMapByPath());
     }
 
     @Test
-    public void testMerge_MapById_Exclude() {
+    public void testConstrainResponse_MapById_Excluded() {
 
-        Constraint<E1> tc1 = Constraint.excludeAll(E1.class).path("r1", Constraint.excludeAll(E2.class).excludeId());
+        AgEntity<Tr> entityTr = metadata.getAgEntity(Tr.class);
+        AgEntity<Ts> entityTs = metadata.getAgEntity(Ts.class);
 
-        ResourceEntity<E2> te1MapBy = new RootResourceEntity<>(age1, null);
-        NestedResourceEntity<E1> te1MapByTarget = new NestedResourceEntity<>(age0, null, te1MapBy, mock(AgRelationship.class));
+        Constraint<Tr> constraint = Constraint
+                .excludeAll(Tr.class)
+                .path("rts", Constraint.excludeAll(Ts.class).excludeId());
+
+        ResourceEntity<Ts> te1MapBy = new RootResourceEntity<>(entityTs, null);
+        NestedResourceEntity<Tr> te1MapByTarget = new NestedResourceEntity<>(entityTr, null, te1MapBy, entityTs.getRelationship("rtrs"));
         te1MapByTarget.includeId();
 
-        te1MapBy.getChildren().put("r1", te1MapByTarget);
+        te1MapBy.getChildren().put("rtrs", te1MapByTarget);
 
-        ResourceEntity<E1> te1 = new RootResourceEntity<>(age0, null);
-        te1.mapBy(te1MapBy, "r1");
+        ResourceEntity<Tr> te1 = new RootResourceEntity<>(entityTr, null);
+        te1.mapBy(te1MapBy, "rts");
 
-        constraintHandler.constrainResponse(te1, null, tc1);
+        constraintsHandler.constrainResponse(te1, null, constraint);
         assertNull(te1.getMapBy());
         assertNull(te1.getMapByPath());
 
     }
 
     @Test
-    public void testMerge_MapById_Include() {
+    public void testConstrainResponse_MapById_Included() {
 
-        Constraint<E1> tc1 = Constraint.excludeAll(E1.class).path("r1", Constraint.excludeAll(E2.class).includeId());
+        AgEntity<Tr> entityTr = metadata.getAgEntity(Tr.class);
+        AgEntity<Ts> entityTs = metadata.getAgEntity(Ts.class);
 
-        ResourceEntity<E1> te1MapBy = new RootResourceEntity<>(age0, null);
-        NestedResourceEntity<E2> te1MapByTarget = new NestedResourceEntity<>(age1, null, te1MapBy, mock(AgRelationship.class));
-        te1MapByTarget.includeId();
+        Constraint<Tr> constraint = Constraint
+                .excludeAll(Tr.class)
+                .path("rts", Constraint.excludeAll(Ts.class).includeId());
 
-        te1MapBy.getChildren().put("r1", te1MapByTarget);
+        ResourceEntity<Tr> te1MapBy = new RootResourceEntity<>(entityTr, null);
+        NestedResourceEntity<Ts> te1MapByTarget = new NestedResourceEntity<>(entityTs, null, te1MapBy, entityTr.getRelationship("rts"));
+        te1MapByTarget.includeId();
+        te1MapBy.getChildren().put("rts", te1MapByTarget);
 
-        ResourceEntity<E1> te1 = new RootResourceEntity<>(age0, null);
-        te1.mapBy(te1MapBy, "r1");
+        ResourceEntity<Tr> te1 = new RootResourceEntity<>(entityTr, null);
+        te1.mapBy(te1MapBy, "rts");
 
-        constraintHandler.constrainResponse(te1, null, tc1);
+        constraintsHandler.constrainResponse(te1, null, constraint);
         assertSame(te1MapBy, te1.getMapBy());
-        assertEquals("r1", te1.getMapByPath());
+        assertEquals("rts", te1.getMapByPath());
     }
 
     protected void appendAttribute(ResourceEntity<?> entity, String name) {
         entity.getAttributes().put(name, new DefaultAgAttribute(name, String.class, new ASTObjPath(name), BeanPropertyReader.reader()));
     }
+
+    public static class Tr {
+
+        @AgId
+        public int getId() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgAttribute
+        public String getA() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgAttribute
+        public String getB() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgAttribute
+        public String getC() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgRelationship
+        public Ts getRts() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgRelationship
+        public Tu getRtu() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgRelationship
+        public Tv getRtv() {
+            throw new UnsupportedOperationException();
+        }
+    }
+
+    public static class Ts {
+
+        @AgId
+        public int getId() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgAttribute
+        public String getN() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgAttribute
+        public String getM() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgAttribute
+        public String getZ() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgRelationship
+        public Tt getRtt() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgRelationship
+        public List<Tr> getRtrs() {
+            throw new UnsupportedOperationException();
+        }
+    }
+
+    public static class Tt {
+        @AgAttribute
+        public String getP() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgAttribute
+        public String getR() {
+            throw new UnsupportedOperationException();
+        }
+    }
+
+    public static class Tu {
+
+        @AgAttribute
+        public String getK() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgAttribute
+        public String getL() {
+            throw new UnsupportedOperationException();
+        }
+    }
+
+    public static class Tv {
+
+        @AgAttribute
+        public String getP() {
+            throw new UnsupportedOperationException();
+        }
+
+        @AgAttribute
+        public String getZ() {
+            throw new UnsupportedOperationException();
+        }
+    }
 }
```

## Row 22
commit_url: https://github.com/jMetal/jMetal/commit/50758e9b1ce75481dbb6f24abde08ec7ec66b346
rm_type: Remove Class Annotation
rm_description: Remove Class Annotation @RunWith(MockitoJUnitRunner.class) in class org.uma.jmetal.operator.selection.BinaryTournamentSelectionTest
file_path: jmetal-core/src/test/java/org/uma/jmetal/operator/selection/BinaryTournamentSelectionTest.java
left_side: [{"filePath": "jmetal-core/src/test/java/org/uma/jmetal/operator/selection/BinaryTournamentSelectionTest.java", "startLine": 33, "endLine": 33, "startColumn": 0, "endColumn": 35, "codeElementType": "ANNOTATION", "description": "removed annotation", "codeElement": "@RunWith(MockitoJUnitRunner.class)"}, {"filePath": "jmetal-core/src/test/java/org/uma/jmetal/operator/selection/BinaryTournamentSelectionTest.java", "startLine": 29, "endLine": 113, "startColumn": 0, "endColumn": 2, "codeElementType": "TYPE_DECLARATION", "description": "original class declaration", "codeElement": "org.uma.jmetal.operator.selection.BinaryTournamentSelectionTest"}]
right_side: [{"filePath": "jmetal-core/src/test/java/org/uma/jmetal/operator/selection/BinaryTournamentSelectionTest.java", "startLine": 27, "endLine": 91, "startColumn": 0, "endColumn": 2, "codeElementType": "TYPE_DECLARATION", "description": "class declaration with removed annotation", "codeElement": "org.uma.jmetal.operator.selection.BinaryTournamentSelectionTest"}]

### Patch: jmetal-core/src/test/java/org/uma/jmetal/operator/selection/BinaryTournamentSelectionTest.java
```diff
@@ -1,9 +1,7 @@
 package org.uma.jmetal.operator.selection;
 
 import org.hamcrest.Matchers;
-import org.junit.After;
-import org.junit.Test;
-import org.junit.runner.RunWith;
+import org.junit.jupiter.api.Test;
 import org.mockito.Mock;
 import org.mockito.Mockito;
 import org.mockito.junit.MockitoJUnitRunner;
@@ -12,6 +10,7 @@
 import org.uma.jmetal.solution.Solution;
 import org.uma.jmetal.solution.doublesolution.DoubleSolution;
 import org.uma.jmetal.util.checking.exception.EmptyCollectionException;
+import org.uma.jmetal.util.checking.exception.InvalidConditionException;
 import org.uma.jmetal.util.checking.exception.NullParameterException;
 
 import java.util.ArrayList;
@@ -21,61 +20,47 @@
 
 import static junit.framework.TestCase.assertNotNull;
 import static org.hamcrest.MatcherAssert.assertThat;
-import static org.junit.Assert.assertEquals;
-import static org.junit.Assert.assertSame;
-import static org.mockito.Matchers.any;
+import static org.junit.Assert.*;
+import static org.junit.Assert.assertThrows;
 import static org.mockito.Mockito.*;
 
 /**
  * @author Antonio J. Nebro
  * @version 1.0
  */
-@RunWith(MockitoJUnitRunner.class)
 public class BinaryTournamentSelectionTest {
-  private static final int POPULATION_SIZE = 20 ;
 
-  @Mock private Problem<Solution<Object>> problem ;
-  private List<Solution<Object>> population ;
-
-  @Test (expected = NullParameterException.class)
+  @Test
   public void shouldExecuteRaiseAnExceptionIfTheListOfSolutionsIsNull() {
-    population = null ;
     BinaryTournamentSelection<Solution<Object>> selection = new BinaryTournamentSelection<Solution<Object>>() ;
-    selection.execute(population) ;
+    assertThrows(NullParameterException.class, () -> selection.execute(null)) ;
   }
 
-  @Test (expected = EmptyCollectionException.class)
+  @Test
   public void shouldExecuteRaiseAnExceptionIfTheListOfSolutionsIsEmpty() {
-    population = new ArrayList<>(0) ;
     BinaryTournamentSelection<Solution<Object>> selection = new BinaryTournamentSelection<Solution<Object>>() ;
-    selection.execute(population) ;
+    assertThrows(EmptyCollectionException.class, () -> selection.execute(new ArrayList<>(0))) ;
   }
 
   @Test
   public void shouldExecuteReturnAValidSolutionIsWithCorrectParameters() {
 	  @SuppressWarnings("unchecked")
-	  Solution<Object> solution = mock(Solution.class) ;
+    Solution<Object> solution1 = Mockito.mock(Solution.class) ;
+    Solution<Object> solution2 = Mockito.mock(Solution.class) ;
+    Solution<Object> solution3 = Mockito.mock(Solution.class) ;
 
-    Mockito.when(problem.createSolution()).thenReturn(solution) ;
+    List<Solution<Object>> population = List.of(solution1, solution2, solution3) ;
 
-    population = new ArrayList<>(POPULATION_SIZE) ;
-    for (int i = 0 ; i < POPULATION_SIZE; i++) {
-      population.add(problem.createSolution());
-    }
     BinaryTournamentSelection<Solution<Object>> selection = new BinaryTournamentSelection<Solution<Object>>() ;
     assertNotNull(selection.execute(population));
-    verify(problem, times(POPULATION_SIZE)).createSolution();
   }
 
   @Test
-  public void shouldExecuteReturnTheSameSolutionIfTheListContainsOneSolution() {
+  public void shouldExecuteRaiseAnExceptionIfTheListContainsOneSolution() {
 	  @SuppressWarnings("unchecked")
 	  Solution<Object> solution = mock(Solution.class) ;
 
-    population = new ArrayList<>(1) ;
-    population.add(solution) ;
-    BinaryTournamentSelection<Solution<Object>> selection = new BinaryTournamentSelection<Solution<Object>>() ;
-    assertSame(solution, selection.execute(population));
+    assertThrows(InvalidConditionException.class, () -> new BinaryTournamentSelection<Solution<Object>>().execute(List.of(solution))) ;
   }
 
   @Test
@@ -85,8 +70,7 @@ public void shouldExecuteReturnTwoSolutionsIfTheListContainsTwoSolutions() {
     @SuppressWarnings("unchecked")
     Solution<Object> solution2 = mock(Solution.class) ;
 
-    population = Arrays.asList(solution1, solution2) ;
-    assertEquals(2, population.size());
+    assertEquals(2, Arrays.asList(solution1, solution2));
   }
 
   @Test
@@ -99,15 +83,9 @@ public void shouldExecuteWorkProperlyIfTheTwoSolutionsInTheListAreNondominated()
     List<DoubleSolution> population = Arrays.<DoubleSolution>asList(solution1, solution2);
 
     BinaryTournamentSelection<DoubleSolution> selection = new BinaryTournamentSelection<DoubleSolution>(comparator) ;
-    DoubleSolution result = (DoubleSolution) selection.execute(population);
+    DoubleSolution result = selection.execute(population);
 
     assertThat(result, Matchers.either(Matchers.is(solution1)).or(Matchers.is(solution2))) ;
     verify(comparator).compare(any(DoubleSolution.class), any(DoubleSolution.class));
   }
-
-  @After
-  public void tearDown() {
-    population = null ;
-    problem = null ;
-  }
 }
```

## Row 23
commit_url: https://github.com/locationtech/jts/commit/78feb6c98c332eb1d1c6da2c584bbc51aae47dc7
rm_type: Extract Class
rm_description: Extract Class org.locationtech.jts.operation.overlayng.OverlayNGEmptyDisjointTest from class org.locationtech.jts.operation.overlayng.OverlayNGTest
file_path: modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java; modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java
left_side: [{"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 25, "endLine": 647, "startColumn": 0, "endColumn": 2, "codeElementType": "TYPE_DECLARATION", "description": "original type declaration", "codeElement": "org.locationtech.jts.operation.overlayng.OverlayNGTest"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 33, "endLine": 39, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testEmptyGCBothIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 41, "endLine": 47, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testEmptyAPolygonIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 49, "endLine": 55, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testEmptyBIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 57, "endLine": 63, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testEmptyABIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 65, "endLine": 71, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testEmptyADifference() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 73, "endLine": 79, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testEmptyAUnion() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 81, "endLine": 87, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testEmptyASymDifference() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 89, "endLine": 95, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testEmptyLinePolygonIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 97, "endLine": 103, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testEmptyLinePolygonDifference() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 105, "endLine": 111, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testEmptyPointPolygonIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 113, "endLine": 119, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testDisjointIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 121, "endLine": 127, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testDisjointIntersectionNoOpt() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 639, "endLine": 644, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public intersectionNoOpt(a Geometry, b Geometry, scaleFactor double) : Geometry"}]
right_side: [{"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java", "startLine": 25, "endLine": 546, "startColumn": 0, "endColumn": 2, "codeElementType": "TYPE_DECLARATION", "description": "type declaration after extraction", "codeElement": "org.locationtech.jts.operation.overlayng.OverlayNGTest"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 21, "endLine": 132, "startColumn": 0, "endColumn": 2, "codeElementType": "TYPE_DECLARATION", "description": "extracted type declaration", "codeElement": "org.locationtech.jts.operation.overlayng.OverlayNGEmptyDisjointTest"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 29, "endLine": 35, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testEmptyGCBothIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 37, "endLine": 43, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testEmptyAPolygonIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 45, "endLine": 51, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testEmptyBIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 53, "endLine": 59, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testEmptyABIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 61, "endLine": 67, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testEmptyADifference() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 69, "endLine": 75, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testEmptyAUnion() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 77, "endLine": 83, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testEmptyASymDifference() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 85, "endLine": 91, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testEmptyLinePolygonIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 93, "endLine": 99, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testEmptyLinePolygonDifference() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 101, "endLine": 107, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testEmptyPointPolygonIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 109, "endLine": 115, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testDisjointIntersection() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 117, "endLine": 123, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public testDisjointIntersectionNoOpt() : void"}, {"filePath": "modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java", "startLine": 125, "endLine": 130, "startColumn": 3, "endColumn": 5, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public intersectionNoOpt(a Geometry, b Geometry, scaleFactor double) : Geometry"}]

### Patch: modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGEmptyDisjointTest.java
```diff
@@ -0,0 +1,132 @@
+/*
+ * Copyright (c) 2019 Martin Davis.
+ *
+ * All rights reserved. This program and the accompanying materials
+ * are made available under the terms of the Eclipse Public License 2.0
+ * and Eclipse Distribution License v. 1.0 which accompanies this distribution.
+ * The Eclipse Public License is available at http://www.eclipse.org/legal/epl-v20.html
+ * and the Eclipse Distribution License is available at
+ *
+ * http://www.eclipse.org/org/documents/edl-v10.php.
+ */
+package org.locationtech.jts.operation.overlayng;
+
+import static org.locationtech.jts.operation.overlayng.OverlayNG.INTERSECTION;
+
+import org.locationtech.jts.geom.Geometry;
+import org.locationtech.jts.geom.PrecisionModel;
+
+import junit.textui.TestRunner;
+
+public class OverlayNGEmptyDisjointTest extends OverlayNGTestCase {
+
+  public static void main(String args[]) {
+    TestRunner.run(OverlayNGEmptyDisjointTest.class);
+  }
+
+  public OverlayNGEmptyDisjointTest(String name) { super(name); }
+  
+  public void testEmptyGCBothIntersection() {
+    Geometry a = read("GEOMETRYCOLLECTION EMPTY");
+    Geometry b = read("GEOMETRYCOLLECTION EMPTY");
+    Geometry expected = read("GEOMETRYCOLLECTION EMPTY");
+    Geometry actual = intersection(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testEmptyAPolygonIntersection() {
+    Geometry a = read("POLYGON EMPTY");
+    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
+    Geometry expected = read("POLYGON EMPTY");
+    Geometry actual = intersection(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testEmptyBIntersection() {
+    Geometry a = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
+    Geometry b = read("POLYGON EMPTY");
+    Geometry expected = read("POLYGON EMPTY");
+    Geometry actual = intersection(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testEmptyABIntersection() {
+    Geometry a = read("POLYGON EMPTY");
+    Geometry b = read("POLYGON EMPTY");
+    Geometry expected = read("POLYGON EMPTY");
+    Geometry actual = intersection(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testEmptyADifference() {
+    Geometry a = read("POLYGON EMPTY");
+    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
+    Geometry expected = read("POLYGON EMPTY");
+    Geometry actual = difference(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testEmptyAUnion() {
+    Geometry a = read("POLYGON EMPTY");
+    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
+    Geometry expected = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
+    Geometry actual = union(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testEmptyASymDifference() {
+    Geometry a = read("POLYGON EMPTY");
+    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
+    Geometry expected = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
+    Geometry actual = symDifference(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testEmptyLinePolygonIntersection() {
+    Geometry a = read("LINESTRING EMPTY");
+    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
+    Geometry expected = read("LINESTRING EMPTY");
+    Geometry actual = intersection(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testEmptyLinePolygonDifference() {
+    Geometry a = read("LINESTRING EMPTY");
+    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
+    Geometry expected = read("LINESTRING EMPTY");
+    Geometry actual = difference(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testEmptyPointPolygonIntersection() {
+    Geometry a = read("POINT EMPTY");
+    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
+    Geometry expected = read("POINT EMPTY");
+    Geometry actual = intersection(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testDisjointIntersection() {
+    Geometry a = read("POLYGON ((60 90, 90 90, 90 60, 60 60, 60 90))");
+    Geometry b = read("POLYGON ((200 300, 300 300, 300 200, 200 200, 200 300))");
+    Geometry expected = read("POLYGON EMPTY");
+    Geometry actual = intersection(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public void testDisjointIntersectionNoOpt() {
+    Geometry a = read("POLYGON ((60 90, 90 90, 90 60, 60 60, 60 90))");
+    Geometry b = read("POLYGON ((200 300, 300 300, 300 200, 200 200, 200 300))");
+    Geometry expected = read("POLYGON EMPTY");
+    Geometry actual = intersectionNoOpt(a, b, 1);
+    checkEqual(expected, actual);
+  }
+  
+  public static Geometry intersectionNoOpt(Geometry a, Geometry b, double scaleFactor) {
+	    PrecisionModel pm = new PrecisionModel(scaleFactor);
+	    OverlayNG ov = new OverlayNG(a, b, pm, INTERSECTION);
+	    ov.setOptimized(false);
+	    return ov.getResult();
+	  }
+  
+}
```
### Patch: modules/core/src/test/java/org/locationtech/jts/operation/overlayng/OverlayNGTest.java
```diff
@@ -30,102 +30,6 @@ public static void main(String args[]) {
 
   public OverlayNGTest(String name) { super(name); }
   
-  public void testEmptyGCBothIntersection() {
-    Geometry a = read("GEOMETRYCOLLECTION EMPTY");
-    Geometry b = read("GEOMETRYCOLLECTION EMPTY");
-    Geometry expected = read("GEOMETRYCOLLECTION EMPTY");
-    Geometry actual = intersection(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testEmptyAPolygonIntersection() {
-    Geometry a = read("POLYGON EMPTY");
-    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
-    Geometry expected = read("POLYGON EMPTY");
-    Geometry actual = intersection(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testEmptyBIntersection() {
-    Geometry a = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
-    Geometry b = read("POLYGON EMPTY");
-    Geometry expected = read("POLYGON EMPTY");
-    Geometry actual = intersection(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testEmptyABIntersection() {
-    Geometry a = read("POLYGON EMPTY");
-    Geometry b = read("POLYGON EMPTY");
-    Geometry expected = read("POLYGON EMPTY");
-    Geometry actual = intersection(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testEmptyADifference() {
-    Geometry a = read("POLYGON EMPTY");
-    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
-    Geometry expected = read("POLYGON EMPTY");
-    Geometry actual = difference(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testEmptyAUnion() {
-    Geometry a = read("POLYGON EMPTY");
-    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
-    Geometry expected = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
-    Geometry actual = union(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testEmptyASymDifference() {
-    Geometry a = read("POLYGON EMPTY");
-    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
-    Geometry expected = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
-    Geometry actual = symDifference(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testEmptyLinePolygonIntersection() {
-    Geometry a = read("LINESTRING EMPTY");
-    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
-    Geometry expected = read("LINESTRING EMPTY");
-    Geometry actual = intersection(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testEmptyLinePolygonDifference() {
-    Geometry a = read("LINESTRING EMPTY");
-    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
-    Geometry expected = read("LINESTRING EMPTY");
-    Geometry actual = difference(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testEmptyPointPolygonIntersection() {
-    Geometry a = read("POINT EMPTY");
-    Geometry b = read("POLYGON ((1 0, 2 5, 3 0, 1 0))");
-    Geometry expected = read("POINT EMPTY");
-    Geometry actual = intersection(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testDisjointIntersection() {
-    Geometry a = read("POLYGON ((60 90, 90 90, 90 60, 60 60, 60 90))");
-    Geometry b = read("POLYGON ((200 300, 300 300, 300 200, 200 200, 200 300))");
-    Geometry expected = read("POLYGON EMPTY");
-    Geometry actual = intersection(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
-  public void testDisjointIntersectionNoOpt() {
-    Geometry a = read("POLYGON ((60 90, 90 90, 90 60, 60 60, 60 90))");
-    Geometry b = read("POLYGON ((200 300, 300 300, 300 200, 200 200, 200 300))");
-    Geometry expected = read("POLYGON EMPTY");
-    Geometry actual = intersectionNoOpt(a, b, 1);
-    checkEqual(expected, actual);
-  }
-  
   public void testAreaLineIntersection() {
     Geometry a = read("POLYGON ((360 200, 220 200, 220 180, 300 180, 300 160, 300 140, 360 200))");
     Geometry b = read("MULTIPOLYGON (((280 180, 280 160, 300 160, 300 180, 280 180)), ((220 230, 240 230, 240 180, 220 180, 220 230)))");
@@ -636,12 +540,7 @@ public static Geometry union(Geometry a, Geometry b) {
     return OverlayNG.overlay(a, b, UNION, pm);
   }
   
-  public static Geometry intersectionNoOpt(Geometry a, Geometry b, double scaleFactor) {
-    PrecisionModel pm = new PrecisionModel(scaleFactor);
-    OverlayNG ov = new OverlayNG(a, b, pm, INTERSECTION);
-    ov.setOptimized(false);
-    return ov.getResult();
-  }
+
   
   
 }
```

## Row 24
commit_url: https://github.com/NitorCreations/nflow/commit/39a2a85f995c83c658c173898783217be849bf86
rm_type: Inline Variable
rm_description: Inline Variable client : WebClient in method protected getInstanceIdResource(instanceId long) : WebClient from class io.nflow.tests.AbstractNflowTest
file_path: nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java
left_side: [{"filePath": "nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java", "startLine": 118, "endLine": 118, "startColumn": 15, "endColumn": 100, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "inlined variable declaration", "codeElement": "client : WebClient"}, {"filePath": "nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java", "startLine": 119, "endLine": 119, "startColumn": 5, "endColumn": 19, "codeElementType": "RETURN_STATEMENT", "description": "statement with the name of the inlined variable", "codeElement": null}]
right_side: [{"filePath": "nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java", "startLine": 121, "endLine": 121, "startColumn": 5, "endColumn": 89, "codeElementType": "RETURN_STATEMENT", "description": "statement with the initializer of the inlined variable", "codeElement": null}]

### Patch: nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java
```diff
@@ -49,11 +49,11 @@
 @ExtendWith({ NflowServerExtension.class, SpringExtension.class, SkipTestMethodsAfterFirstFailureExtension.class })
 @ContextConfiguration(classes = { RestClientConfiguration.class, PropertiesConfiguration.class })
 public abstract class AbstractNflowTest {
-  protected WebClient workflowInstanceResource;
-  protected WebClient workflowInstanceIdResource;
-  protected WebClient workflowDefinitionResource;
-  protected WebClient statisticsResource;
-  protected WebClient maintenanceResource;
+  private WebClient workflowInstanceResource;
+  private WebClient workflowInstanceIdResource;
+  private WebClient workflowDefinitionResource;
+  private WebClient statisticsResource;
+  private WebClient maintenanceResource;
 
   private final NflowServerConfig server;
 
@@ -109,24 +109,24 @@ protected SetSignalResponse setSignal(long instanceId, int signal, String reason
     return getInstanceResource(instanceId).path("signal").put(request, SetSignalResponse.class);
   }
 
-  private WebClient getInstanceResource(long instanceId) {
-    WebClient client = fromClient(workflowInstanceResource, true).path(Long.toString(instanceId));
-    return client;
+  protected WebClient getInstanceResource() {
+    return fromClient(workflowInstanceResource, true);
+  }
+
+  protected WebClient getInstanceResource(long instanceId) {
+    return getInstanceResource().path(Long.toString(instanceId));
   }
 
   protected WebClient getInstanceIdResource(long instanceId) {
-    WebClient client = fromClient(workflowInstanceIdResource, true).path(Long.toString(instanceId));
-    return client;
+    return fromClient(workflowInstanceIdResource, true).path(Long.toString(instanceId));
   }
 
   protected ListWorkflowDefinitionResponse[] getWorkflowDefinitions() {
-    WebClient client = fromClient(workflowDefinitionResource, true);
-    return client.get(ListWorkflowDefinitionResponse[].class);
+    return fromClient(workflowDefinitionResource, true).get(ListWorkflowDefinitionResponse[].class);
   }
 
   public StatisticsResponse getStatistics() {
-    WebClient client = fromClient(statisticsResource, true);
-    return client.get(StatisticsResponse.class);
+    return fromClient(statisticsResource, true).get(StatisticsResponse.class);
   }
 
   public WorkflowDefinitionStatisticsResponse getDefinitionStatistics(String definitionType) {
@@ -173,7 +173,7 @@ public void validate(ListWorkflowInstanceResponse workflowInstance) {
   }
 
   protected CreateWorkflowInstanceResponse createWorkflowInstance(CreateWorkflowInstanceRequest request) {
-    return makeWorkflowInstanceQuery(request, CreateWorkflowInstanceResponse.class);
+    return fromClient(workflowInstanceResource, true).put(request, CreateWorkflowInstanceResponse.class);
   }
 
   protected ObjectMapper nflowObjectMapper() {
@@ -183,33 +183,21 @@ protected ObjectMapper nflowObjectMapper() {
     return mapper;
   }
 
-  protected MaintenanceResponse archiveAllFinishedWorkflows() {
-    MaintenanceRequest req = new MaintenanceRequest();
-    req.archiveWorkflows = new MaintenanceRequestItem();
-    req.archiveWorkflows.olderThanPeriod = seconds(0);
-    return assertTimeoutPreemptively(ofSeconds(15),
-        () -> fromClient(maintenanceResource).type(APPLICATION_JSON_TYPE).post(req, MaintenanceResponse.class));
-  }
-
   protected MaintenanceResponse deleteAllFinishedWorkflows() {
     MaintenanceRequest req = new MaintenanceRequest();
     req.deleteWorkflows = new MaintenanceRequestItem();
     req.deleteWorkflows.olderThanPeriod = seconds(0);
     req.deleteArchivedWorkflows = req.deleteWorkflows;
-    return assertTimeoutPreemptively(ofSeconds(15),
-        () -> fromClient(maintenanceResource).type(APPLICATION_JSON_TYPE).post(req, MaintenanceResponse.class));
-  }
-
-  protected long insertWorkflow(CreateWorkflowInstanceRequest req) {
-    return fromClient(workflowInstanceResource, true).put(req, CreateWorkflowInstanceResponse.class).id;
+    return doMaintenance(req);
   }
 
-  protected String updateWorkflowInstance(long instanceId, UpdateWorkflowInstanceRequest request) {
-    return getInstanceIdResource(instanceId).put(request, String.class);
+  protected MaintenanceResponse doMaintenance(MaintenanceRequest req) {
+    return assertTimeoutPreemptively(ofSeconds(15),
+        () -> fromClient(maintenanceResource).type(APPLICATION_JSON_TYPE).post(req, MaintenanceResponse.class));
   }
 
-  private <T> T makeWorkflowInstanceQuery(CreateWorkflowInstanceRequest request, Class<T> responseClass) {
-    return fromClient(workflowInstanceResource, true).put(request, responseClass);
+  protected <T> T updateWorkflowInstance(long instanceId, UpdateWorkflowInstanceRequest request, Class<T> responseClass) {
+    return getInstanceIdResource(instanceId).put(request, responseClass);
   }
 
   public interface WorkflowInstanceValidator {
```

## Row 25
commit_url: https://github.com/google/ExoPlayer/commit/9b6c30525ec438ad8bc03e5a6afbff442b2f941a
rm_type: Split Class
rm_description: Split Class com.google.android.exoplayer.extractor.webm.WebmExtractorTest.TestOutput split to [com.google.android.exoplayer.extractor.webm.WebmExtractorTest.TestExtractorOutput, com.google.android.exoplayer.extractor.webm.WebmExtractorTest.TestTrackOutput]
file_path: library/src/test/java/com/google/android/exoplayer/extractor/webm/WebmExtractorTest.java
left_side: [{"filePath": "library/src/test/java/com/google/android/exoplayer/extractor/webm/WebmExtractorTest.java", "startLine": 716, "endLine": 775, "startColumn": 3, "endColumn": 4, "codeElementType": "TYPE_DECLARATION", "description": "original type declaration", "codeElement": "com.google.android.exoplayer.extractor.webm.WebmExtractorTest.TestOutput"}]
right_side: [{"filePath": "library/src/test/java/com/google/android/exoplayer/extractor/webm/WebmExtractorTest.java", "startLine": 855, "endLine": 885, "startColumn": 3, "endColumn": 4, "codeElementType": "TYPE_DECLARATION", "description": "split type declaration", "codeElement": "com.google.android.exoplayer.extractor.webm.WebmExtractorTest.TestExtractorOutput"}, {"filePath": "library/src/test/java/com/google/android/exoplayer/extractor/webm/WebmExtractorTest.java", "startLine": 887, "endLine": 922, "startColumn": 3, "endColumn": 4, "codeElementType": "TYPE_DECLARATION", "description": "split type declaration", "codeElement": "com.google.android.exoplayer.extractor.webm.WebmExtractorTest.TestTrackOutput"}]

### Patch: library/src/test/java/com/google/android/exoplayer/extractor/webm/WebmExtractorTest.java
```diff
@@ -70,64 +70,114 @@ public class WebmExtractorTest extends InstrumentationTestCase {
   private static final int ID_VP9 = 0;
   private static final int ID_OPUS = 1;
   private static final int ID_VORBIS = 2;
+  private static final int ID_DUMMY = 3;
 
   private WebmExtractor extractor;
-  private TestOutput output;
+  private TestExtractorOutput extractorOutput;
+  private TestTrackOutput audioOutput;
+  private TestTrackOutput videoOutput;
 
   @Override
   public void setUp() {
     extractor = new WebmExtractor();
-    output = new TestOutput();
-    extractor.init(output);
+    extractorOutput = new TestExtractorOutput();
+    audioOutput = new TestTrackOutput();
+    videoOutput = new TestTrackOutput();
+    extractor.init(extractorOutput);
   }
 
   @Override
   public void tearDown() {
     extractor = null;
-    output = null;
+    extractorOutput = null;
+    audioOutput = null;
+    videoOutput = null;
   }
 
   public void testReadInitializationSegment() throws IOException, InterruptedException {
-    consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null));
-    assertFormat();
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, null));
+    assertVideoFormat();
     assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
   }
 
   public void testPrepareOpus() throws IOException, InterruptedException {
-    consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_OPUS, null));
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_OPUS}, null));
     assertAudioFormat(ID_OPUS);
     assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
   }
 
   public void testPrepareVorbis() throws IOException, InterruptedException {
-    consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VORBIS, null));
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VORBIS}, null));
+    assertAudioFormat(ID_VORBIS);
+    assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
+  }
+
+  public void testPrepareTwoTracks() throws IOException, InterruptedException {
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9, ID_OPUS}, null));
+    assertEquals(2, extractorOutput.numberOfTracks);
+    assertVideoFormat();
+    assertAudioFormat(ID_OPUS);
+    assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
+  }
+
+  public void testPrepareThreeTracks() throws IOException, InterruptedException {
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9, ID_DUMMY, ID_OPUS}, null));
+    // Eventhough the input stream has 3 tracks, only 2 of them are supported and will be reported.
+    assertEquals(2, extractorOutput.numberOfTracks);
+    assertVideoFormat();
+    assertAudioFormat(ID_OPUS);
+    assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
+  }
+
+  public void testPrepareFourTracks() throws IOException, InterruptedException {
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9, ID_VORBIS, ID_VP9, ID_OPUS}, null));
+    // Eventhough the input stream has 4 supported tracks, only the first video and audio track will
+    // be reported.
+    assertEquals(2, extractorOutput.numberOfTracks);
+    assertVideoFormat();
     assertAudioFormat(ID_VORBIS);
     assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
   }
 
   public void testPrepareContentEncodingEncryption() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 1, 5, 1);
-    consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
-    assertFormat();
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, settings));
+    assertVideoFormat();
     assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
-    DrmInitData drmInitData = output.drmInitData;
-    assertNotNull(output.drmInitData);
+    DrmInitData drmInitData = extractorOutput.drmInitData;
+    assertNotNull(drmInitData);
     android.test.MoreAsserts.assertEquals(TEST_ENCRYPTION_KEY_ID, drmInitData.get(WIDEVINE_UUID));
     android.test.MoreAsserts.assertEquals(TEST_ENCRYPTION_KEY_ID, drmInitData.get(ZERO_UUID));
   }
 
   public void testPrepareThreeCuePoints() throws IOException, InterruptedException {
-    consume(createInitializationSegment(3, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null));
-    assertFormat();
+    consume(
+        createInitializationSegment(3, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, null));
+    assertVideoFormat();
     assertIndex(
         new IndexPoint(0, 0, 10000),
         new IndexPoint(10000, 0, 10000),
         new IndexPoint(20000, 0, TEST_DURATION_US - 20000));
   }
 
   public void testPrepareCustomTimecodeScale() throws IOException, InterruptedException {
-    consume(createInitializationSegment(3, 0, true, 1000, ID_VP9, null));
-    assertFormat();
+    consume(createInitializationSegment(3, 0, true, 1000, new int[] {ID_VP9}, null));
+    assertVideoFormat();
     assertIndex(
         new IndexPoint(0, 0, 10),
         new IndexPoint(10, 0, 10),
@@ -136,7 +186,9 @@ public void testPrepareCustomTimecodeScale() throws IOException, InterruptedExce
 
   public void testPrepareNoCuePoints() throws IOException, InterruptedException {
     try {
-      consume(createInitializationSegment(0, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null));
+      consume(
+          createInitializationSegment(0, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, null));
       fail();
     } catch (ParserException exception) {
       assertEquals("Invalid/missing cue points", exception.getMessage());
@@ -145,7 +197,9 @@ public void testPrepareNoCuePoints() throws IOException, InterruptedException {
 
   public void testPrepareInvalidDocType() throws IOException, InterruptedException {
     try {
-      consume(createInitializationSegment(1, 0, false, DEFAULT_TIMECODE_SCALE, ID_VP9, null));
+      consume(
+          createInitializationSegment(1, 0, false, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, null));
       fail();
     } catch (ParserException exception) {
       assertEquals("DocType webB not supported", exception.getMessage());
@@ -155,7 +209,9 @@ public void testPrepareInvalidDocType() throws IOException, InterruptedException
   public void testPrepareInvalidContentEncodingOrder() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(1, 1, 1, 5, 1);
     try {
-      consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
+      consume(
+          createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, settings));
       fail();
     } catch (ParserException exception) {
       assertEquals("ContentEncodingOrder 1 not supported", exception.getMessage());
@@ -165,7 +221,9 @@ public void testPrepareInvalidContentEncodingOrder() throws IOException, Interru
   public void testPrepareInvalidContentEncodingScope() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 0, 1, 5, 1);
     try {
-      consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
+      consume(
+          createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, settings));
       fail();
     } catch (ParserException exception) {
       assertEquals("ContentEncodingScope 0 not supported", exception.getMessage());
@@ -175,7 +233,9 @@ public void testPrepareInvalidContentEncodingScope() throws IOException, Interru
   public void testPrepareInvalidContentEncodingType() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 0, 5, 1);
     try {
-      consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
+      consume(
+          createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, settings));
       fail();
     } catch (ParserException exception) {
       assertEquals("ContentEncodingType 0 not supported", exception.getMessage());
@@ -185,7 +245,9 @@ public void testPrepareInvalidContentEncodingType() throws IOException, Interrup
   public void testPrepareInvalidContentEncAlgo() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 1, 4, 1);
     try {
-      consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
+      consume(
+          createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, settings));
       fail();
     } catch (ParserException exception) {
       assertEquals("ContentEncAlgo 4 not supported", exception.getMessage());
@@ -195,54 +257,104 @@ public void testPrepareInvalidContentEncAlgo() throws IOException, InterruptedEx
   public void testPrepareInvalidAESSettingsCipherMode() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 1, 5, 0);
     try {
-      consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
+      consume(
+          createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, settings));
       fail();
     } catch (ParserException exception) {
       assertEquals("AESSettingsCipherMode 0 not supported", exception.getMessage());
     }
   }
 
   public void testReadSampleKeyframe() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, true, false, false);
+    MediaSegment mediaSegment =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, null),
         mediaSegment.clusterBytes);
     consume(testInputData);
-    assertFormat();
-    assertSample(mediaSegment, 0, true, false, false);
+    assertVideoFormat();
+    assertSample(mediaSegment, 0, true, false, false, videoOutput);
+  }
+
+  public void testReadTwoTrackSamples() throws IOException, InterruptedException {
+    MediaSegment mediaSegmentAudio =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 2);
+    MediaSegment mediaSegmentVideo =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 1);
+    byte[] testInputData = joinByteArrays(
+        createInitializationSegment(
+            1, mediaSegmentAudio.clusterBytes.length + mediaSegmentVideo.clusterBytes.length,
+            true, DEFAULT_TIMECODE_SCALE, new int[] {ID_VP9, ID_OPUS}, null),
+        mediaSegmentVideo.clusterBytes, mediaSegmentAudio.clusterBytes);
+    consume(testInputData);
+    assertEquals(2, extractorOutput.numberOfTracks);
+    assertVideoFormat();
+    assertAudioFormat(ID_OPUS);
+    assertSample(mediaSegmentVideo, 0, true, false, false, videoOutput);
+    assertSample(mediaSegmentAudio, 0, true, false, false, audioOutput);
+  }
+
+  public void testReadTwoTrackSamplesWithSkippedTrack() throws IOException, InterruptedException {
+    MediaSegment mediaSegmentAudio =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 2);
+    MediaSegment mediaSegmentVideo =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 1);
+    MediaSegment mediaSegmentDummy =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 17);
+    byte[] testInputData = joinByteArrays(
+        createInitializationSegment(
+            1,
+            mediaSegmentAudio.clusterBytes.length + mediaSegmentVideo.clusterBytes.length
+                + mediaSegmentDummy.clusterBytes.length,
+            true, DEFAULT_TIMECODE_SCALE, new int[] {ID_DUMMY, ID_VP9, ID_OPUS}, null),
+        mediaSegmentVideo.clusterBytes,
+        mediaSegmentDummy.clusterBytes,
+        mediaSegmentAudio.clusterBytes);
+    consume(testInputData);
+    assertEquals(2, extractorOutput.numberOfTracks);
+    assertVideoFormat();
+    assertAudioFormat(ID_OPUS);
+    assertSample(mediaSegmentVideo, 0, true, false, false, videoOutput);
+    assertSample(mediaSegmentAudio, 0, true, false, false, audioOutput);
   }
 
   public void testReadBlock() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, false, false, false);
+    MediaSegment mediaSegment =
+        createMediaSegment(100, 0, 0, true, false, false, false, false, 2);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_OPUS, null),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_OPUS}, null),
         mediaSegment.clusterBytes);
     consume(testInputData);
     assertAudioFormat(ID_OPUS);
-    assertSample(mediaSegment, 0, true, false, false);
+    assertSample(mediaSegment, 0, true, false, false, audioOutput);
   }
 
   public void testReadEncryptedFrame() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, true, true, true);
+    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, true, true, true, 1);
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 1, 5, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, settings),
         mediaSegment.clusterBytes);
     consume(testInputData);
-    assertFormat();
-    assertSample(mediaSegment, 0, true, false, true);
+    assertVideoFormat();
+    assertSample(mediaSegment, 0, true, false, true, videoOutput);
   }
 
   public void testReadEncryptedFrameWithInvalidSignalByte()
       throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, true, true, false);
+    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, true, true, false, 1);
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 1, 5, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, settings),
         mediaSegment.clusterBytes);
     try {
       consume(testInputData);
@@ -253,36 +365,41 @@ public void testReadEncryptedFrameWithInvalidSignalByte()
   }
 
   public void testReadSampleInvisible() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 12, 13, false, true, true, false, false);
+    MediaSegment mediaSegment =
+        createMediaSegment(100, 12, 13, false, true, true, false, false, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, null),
         mediaSegment.clusterBytes);
     consume(testInputData);
-    assertFormat();
-    assertSample(mediaSegment, 25000, false, true, false);
+    assertVideoFormat();
+    assertSample(mediaSegment, 25000, false, true, false, videoOutput);
   }
 
   public void testReadSampleCustomTimescale() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 12, 13, false, false, true, false, false);
+    MediaSegment mediaSegment =
+        createMediaSegment(100, 12, 13, false, false, true, false, false, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, 1000, ID_VP9, null),
+            1, mediaSegment.clusterBytes.length, true, 1000, new int[] {ID_VP9}, null),
         mediaSegment.clusterBytes);
     consume(testInputData);
-    assertFormat();
-    assertSample(mediaSegment, 25, false, false, false);
+    assertVideoFormat();
+    assertSample(mediaSegment, 25, false, false, false, videoOutput);
   }
 
   public void testReadSampleNegativeSimpleBlockTimecode() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 13, -12, true, true, true, false, false);
+    MediaSegment mediaSegment =
+        createMediaSegment(100, 13, -12, true, true, true, false, false, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, null),
         mediaSegment.clusterBytes);
     consume(testInputData);
-    assertFormat();
-    assertSample(mediaSegment, 1000, true, true, false);
+    assertVideoFormat();
+    assertSample(mediaSegment, 1000, true, true, false, videoOutput);
   }
 
   private void consume(byte[] data) throws IOException, InterruptedException {
@@ -301,15 +418,15 @@ private static ExtractorInput createTestInput(byte[] data) throws IOException {
     return input;
   }
 
-  private void assertFormat() {
-    MediaFormat format = output.format;
+  private void assertVideoFormat() {
+    MediaFormat format = videoOutput.format;
     assertEquals(TEST_WIDTH, format.width);
     assertEquals(TEST_HEIGHT, format.height);
     assertEquals(MimeTypes.VIDEO_VP9, format.mimeType);
   }
 
   private void assertAudioFormat(int codecId) {
-    MediaFormat format = output.format;
+    MediaFormat format = audioOutput.format;
     assertEquals(TEST_CHANNEL_COUNT, format.channelCount);
     assertEquals(TEST_SAMPLE_RATE, format.sampleRate);
     if (codecId == ID_OPUS) {
@@ -327,7 +444,7 @@ private void assertAudioFormat(int codecId) {
   }
 
   private void assertIndex(IndexPoint... indexPoints) {
-    ChunkIndex index = (ChunkIndex) output.seekMap;
+    ChunkIndex index = (ChunkIndex) extractorOutput.seekMap;
     assertEquals(indexPoints.length, index.length);
     for (int i = 0; i < indexPoints.length; i++) {
       IndexPoint indexPoint = indexPoints[i];
@@ -338,8 +455,8 @@ private void assertIndex(IndexPoint... indexPoints) {
   }
 
   private void assertSample(MediaSegment mediaSegment, int timeUs, boolean keyframe,
-      boolean invisible, boolean encrypted) {
-    byte[] expectedOutput = mediaSegment.videoBytes;
+      boolean invisible, boolean encrypted, TestTrackOutput output) {
+    byte[] expectedOutput = mediaSegment.data;
     if (encrypted) {
       expectedOutput = joinByteArrays(new byte[] {(byte) TEST_INITIALIZATION_VECTOR.length},
           TEST_INITIALIZATION_VECTOR, expectedOutput);
@@ -353,24 +470,11 @@ private void assertSample(MediaSegment mediaSegment, int timeUs, boolean keyfram
   }
 
   private byte[] createInitializationSegment(int cuePoints, int mediaSegmentSize,
-      boolean docTypeIsWebm, int timecodeScale, int codecId,
+      boolean docTypeIsWebm, int timecodeScale, int[] codecIds,
       ContentEncodingSettings contentEncodingSettings) {
-    byte[] tracksElement = null;
-    switch (codecId) {
-      case ID_VP9:
-        tracksElement = createTracksElementWithVideo(
-            true, TEST_WIDTH, TEST_HEIGHT, contentEncodingSettings);
-        break;
-      case ID_OPUS:
-        tracksElement = createTracksElementWithOpusAudio(TEST_CHANNEL_COUNT);
-        break;
-      case ID_VORBIS:
-        tracksElement = createTracksElementWithVorbisAudio(TEST_CHANNEL_COUNT);
-        break;
-    }
+    byte[] tracksElement = createTracksElement(codecIds, contentEncodingSettings);
     byte[] infoElement = createInfoElement(timecodeScale);
     byte[] cuesElement = createCuesElement(CUE_POINT_ELEMENT_BYTE_SIZE * cuePoints);
-
     int initalizationSegmentSize = infoElement.length + tracksElement.length
         + cuesElement.length + CUE_POINT_ELEMENT_BYTE_SIZE * cuePoints;
     byte[] segmentElement = createSegmentElement(initalizationSegmentSize + mediaSegmentSize);
@@ -382,20 +486,47 @@ private byte[] createInitializationSegment(int cuePoints, int mediaSegmentSize,
     return bytes;
   }
 
-  private static MediaSegment createMediaSegment(int videoBytesLength, int clusterTimecode,
+  private byte[] createTracksElement(int[] codecIds,
+      ContentEncodingSettings contentEncodingSettings) {
+    byte[] trackBytes = new byte[0];
+    for (int codecId : codecIds) {
+      switch (codecId) {
+        case ID_VP9:
+          trackBytes = joinByteArrays(trackBytes,
+              createVideoTrackEntry(true, TEST_WIDTH, TEST_HEIGHT, contentEncodingSettings));
+          break;
+        case ID_OPUS:
+          trackBytes = joinByteArrays(trackBytes, createOpusAudioTrackEntry(TEST_CHANNEL_COUNT));
+          break;
+        case ID_VORBIS:
+          trackBytes = joinByteArrays(trackBytes, createVorbisAudioTrackEntry(TEST_CHANNEL_COUNT));
+          break;
+        case ID_DUMMY:
+          trackBytes = joinByteArrays(trackBytes, createUnsupportedTrackEntry());
+          break;
+      }
+    }
+    byte[] tracksSize = getIntegerBytes(trackBytes.length);
+    byte[] tracksHeader = createByteArray(
+        0x16, 0x54, 0xAE, 0x6B, // Tracks
+        0x01, 0x00, 0x00, 0x00, tracksSize[0], tracksSize[1], tracksSize[2], tracksSize[3]);
+    return joinByteArrays(tracksHeader, trackBytes);
+  }
+
+  private static MediaSegment createMediaSegment(int dataLength, int clusterTimecode,
       int blockTimecode, boolean keyframe, boolean invisible, boolean simple,
-      boolean encrypted, boolean validSignalByte) {
-    byte[] videoBytes = createVideoBytes(videoBytesLength);
+      boolean encrypted, boolean validSignalByte, int trackNumber) {
+    byte[] data = createFrameData(dataLength);
     byte[] blockBytes;
     if (simple) {
-      blockBytes = createSimpleBlockElement(videoBytes.length, blockTimecode,
-          keyframe, invisible, true, encrypted, validSignalByte);
+      blockBytes = createSimpleBlockElement(data.length, blockTimecode,
+          keyframe, invisible, true, encrypted, validSignalByte, trackNumber);
     } else {
-      blockBytes = createBlockElement(videoBytes.length, blockTimecode, invisible, true);
+      blockBytes = createBlockElement(data.length, blockTimecode, invisible, true, trackNumber);
     }
     byte[] clusterBytes =
-        createClusterElement(blockBytes.length + videoBytes.length, clusterTimecode);
-    return new MediaSegment(joinByteArrays(clusterBytes, blockBytes, videoBytes), videoBytes);
+        createClusterElement(blockBytes.length + data.length, clusterTimecode);
+    return new MediaSegment(joinByteArrays(clusterBytes, blockBytes, data), data);
   }
 
   private static byte[] joinByteArrays(byte[]... byteArrays) {
@@ -443,7 +574,7 @@ private static byte[] createInfoElement(int timecodeScale) {
         0x88, 0x40, 0xC3, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00); // size=8 value=9920.0
   }
 
-  private static byte[] createTracksElementWithVideo(
+  private static byte[] createVideoTrackEntry(
       boolean codecIsVp9, int pixelWidth, int pixelHeight,
       ContentEncodingSettings contentEncodingSettings) {
     byte[] widthBytes = getIntegerBytes(pixelWidth);
@@ -455,8 +586,6 @@ private static byte[] createTracksElementWithVideo(
       byte[] algorithmBytes = getIntegerBytes(contentEncodingSettings.algorithm);
       byte[] cipherModeBytes = getIntegerBytes(contentEncodingSettings.aesCipherMode);
       return createByteArray(
-          0x16, 0x54, 0xAE, 0x6B, // Tracks
-          0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4E, // size=78
           0xAE, // TrackEntry
           0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x45, // size=69
           0x86, // CodecID
@@ -495,10 +624,8 @@ private static byte[] createTracksElementWithVideo(
           0x82, heightBytes[2], heightBytes[3]); // size=2
     } else {
       return createByteArray(
-          0x16, 0x54, 0xAE, 0x6B, // Tracks
-          0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2A, // size=42
           0xAE, // TrackEntry
-          0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x21, // size=33
+          0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1E, // size=30
           0x86, // CodecID
           0x85, 0x56, 0x5F, 0x56, 0x50, codecIsVp9 ? 0x39 : 0x30, // size=5 value=V_VP9/0
           0xD7, // TrackNumber
@@ -514,17 +641,15 @@ private static byte[] createTracksElementWithVideo(
     }
   }
 
-  private static byte[] createTracksElementWithOpusAudio(int channelCount) {
+  private static byte[] createOpusAudioTrackEntry(int channelCount) {
     byte[] channelCountBytes = getIntegerBytes(channelCount);
     return createByteArray(
-        0x16, 0x54, 0xAE, 0x6B, // Tracks
-        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3F, // size=63
         0xAE, // TrackEntry
         0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x36, // size=54
         0x86, // CodecID
         0x86, 0x41, 0x5F, 0x4F, 0x50, 0x55, 0x53, // size=6 value=A_OPUS
         0xD7, // TrackNumber
-        0x81, 0x01, // size=1 value=1
+        0x81, 0x02, // size=1 value=2
         0x83, // TrackType
         0x81, 0x02, // size=1 value=2
         0x56, 0xAA, // CodecDelay
@@ -541,17 +666,15 @@ private static byte[] createTracksElementWithOpusAudio(int channelCount) {
         0x82, 0x00, 0x00); // size=2
   }
 
-  private byte[] createTracksElementWithVorbisAudio(int channelCount) {
+  private byte[] createVorbisAudioTrackEntry(int channelCount) {
     byte[] channelCountBytes = getIntegerBytes(channelCount);
     byte[] tracksElement = createByteArray(
-        0x16, 0x54, 0xAE, 0x6B, // Tracks
-        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0xA2, // size=4258
         0xAE, // TrackEntry
         0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x99, // size=4249 (42+4207)
         0x86, // CodecID
         0x88, 0x41, 0x5f, 0x56, 0x4f, 0x52, 0x42, 0x49, 0x53, // size=8 value=A_VORBIS
         0xD7, // TrackNumber
-        0x81, 0x01, // size=1 value=1
+        0x81, 0x02, // size=1 value=2
         0x83, // TrackType
         0x81, 0x02, // size=1 value=2
         0xE1, // Audio
@@ -572,6 +695,20 @@ private byte[] createTracksElementWithVorbisAudio(int channelCount) {
     return joinByteArrays(tracksElement, codecPrivate);
   }
 
+  private static byte[] createUnsupportedTrackEntry() {
+    return createByteArray(
+        0xAE, // TrackEntry
+        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, // size=32
+        0x86, // CodecID
+        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, // size =17
+        0x44, 0x5f, 0x57, 0x45, 0x42, 0x56, 0x54, 0x54,
+        0x2f, 0x6d, 0x65, 0x74, 0x61, 0x64, 0x61, 0x74, 0x61, // value=D_WEBVTT/metadata
+        0xD7, // TrackNumber
+        0x81, 0x03, // size=1 value=3
+        0x83, // TrackType
+        0x81, 0x11); // size=1 value=11
+  }
+
   private static byte[] createCuesElement(int size) {
     byte[] sizeBytes = getIntegerBytes(size);
     return createByteArray(
@@ -605,15 +742,16 @@ private static byte[] createClusterElement(int size, int timecode) {
 
   private static byte[] createSimpleBlockElement(
       int size, int timecode, boolean keyframe, boolean invisible, boolean noLacing,
-      boolean encrypted, boolean validSignalByte) {
-    byte[] sizeBytes = getIntegerBytes(size + 4 + (encrypted ? 9 : 0));
+      boolean encrypted, boolean validSignalByte, int trackNumber) {
+    byte[] sizeBytes = getIntegerBytes(size + 5 + (encrypted ? 9 : 0));
     byte[] timeBytes = getIntegerBytes(timecode);
+    byte[] trackNumberBytes = getIntegerBytes(trackNumber);
     byte flags = (byte)
         ((keyframe ? 0x80 : 0x00) | (invisible ? 0x08 : 0x00) | (noLacing ? 0x00 : 0x06));
     byte[] simpleBlock = createByteArray(
         0xA3, // SimpleBlock
         0x01, 0x00, 0x00, 0x00, sizeBytes[0], sizeBytes[1], sizeBytes[2], sizeBytes[3],
-        0x81, // Track number value=1
+        0x40, trackNumberBytes[3], // Track number size=2
         timeBytes[2], timeBytes[3], flags); // Timecode and flags
     if (encrypted) {
       simpleBlock = joinByteArrays(
@@ -624,10 +762,11 @@ simpleBlock, createByteArray(validSignalByte ? 0x01 : 0x80),
   }
 
   private static byte[] createBlockElement(
-      int size, int timecode, boolean invisible, boolean noLacing) {
-    int blockSize = size + 4;
+      int size, int timecode, boolean invisible, boolean noLacing, int trackNumber) {
+    int blockSize = size + 5;
     byte[] blockSizeBytes = getIntegerBytes(blockSize);
     byte[] timeBytes = getIntegerBytes(timecode);
+    byte[] trackNumberBytes = getIntegerBytes(trackNumber);
     int blockElementSize = 1 + 8 + blockSize; // id + size + length of data
     byte[] sizeBytes = getIntegerBytes(blockElementSize);
     byte flags = (byte) ((invisible ? 0x08 : 0x00) | (noLacing ? 0x00 : 0x06));
@@ -637,16 +776,16 @@ private static byte[] createBlockElement(
         0xA1, // Block
         0x01, 0x00, 0x00, 0x00,
         blockSizeBytes[0], blockSizeBytes[1], blockSizeBytes[2], blockSizeBytes[3],
-        0x81, // Track number value=1
+        0x40, trackNumberBytes[3], // Track number size=2
         timeBytes[2], timeBytes[3], flags); // Timecode and flags
   }
 
-  private static byte[] createVideoBytes(int size) {
-    byte[] videoBytes = new byte[size];
+  private static byte[] createFrameData(int size) {
+    byte[] data = new byte[size];
     for (int i = 0; i < size; i++) {
-      videoBytes[i] = (byte) i;
+      data[i] = (byte) i;
     }
-    return videoBytes;
+    return data;
   }
 
   private static byte[] getIntegerBytes(int value) {
@@ -669,11 +808,11 @@ private static byte[] createByteArray(int... intArray) {
   private static final class MediaSegment {
 
     private final byte[] clusterBytes;
-    private final byte[] videoBytes;
+    private final byte[] data;
 
-    private MediaSegment(byte[] clusterBytes, byte[] videoBytes) {
+    private MediaSegment(byte[] clusterBytes, byte[] data) {
       this.clusterBytes = clusterBytes;
-      this.videoBytes = videoBytes;
+      this.data = data;
     }
 
   }
@@ -713,21 +852,19 @@ private ContentEncodingSettings(int order, int scope, int type, int algorithm,
 
   }
 
-  /** Implements {@link ExtractorOutput} and {@link TrackOutput} for test purposes. */
-  public static class TestOutput implements ExtractorOutput, TrackOutput {
+  /** Implements {@link ExtractorOutput} for test purposes. */
+  public class TestExtractorOutput implements ExtractorOutput {
 
     public boolean tracksEnded;
     public SeekMap seekMap;
     public DrmInitData drmInitData;
-
-    public MediaFormat format;
-    private long sampleTimeUs;
-    private int sampleFlags;
-    private byte[] sampleData;
+    public int numberOfTracks;
 
     @Override
     public TrackOutput track(int trackId) {
-      return this;
+      numberOfTracks++;
+      // In the test samples, track number 1 is always video and track number 2 is always audio.
+      return (trackId == 1) ? videoOutput : audioOutput;
     }
 
     @Override
@@ -745,6 +882,16 @@ public void drmInitData(DrmInitData drmInitData) {
       this.drmInitData = drmInitData;
     }
 
+  }
+
+  /** Implements {@link TrackOutput} for test purposes. */
+  public static class TestTrackOutput implements TrackOutput {
+
+    public MediaFormat format;
+    private long sampleTimeUs;
+    private int sampleFlags;
+    private byte[] sampleData;
+
     @Override
     public void format(MediaFormat format) {
       this.format = format;
```

## Row 26
commit_url: https://github.com/AICP/frameworks_base/commit/2fc27ebaec26afd1537499c972ddbaa724886817
rm_type: Add Class Annotation
rm_description: Add Class Annotation @RunWith(AndroidJUnit4.class) in class com.android.server.pm.UserManagerTest
file_path: services/tests/servicestests/src/com/android/server/pm/UserManagerTest.java
left_side: [{"filePath": "services/tests/servicestests/src/com/android/server/pm/UserManagerTest.java", "startLine": 47, "endLine": 856, "startColumn": 0, "endColumn": 2, "codeElementType": "TYPE_DECLARATION", "description": "original class declaration", "codeElement": "com.android.server.pm.UserManagerTest"}]
right_side: [{"filePath": "services/tests/servicestests/src/com/android/server/pm/UserManagerTest.java", "startLine": 60, "endLine": 60, "startColumn": 0, "endColumn": 30, "codeElementType": "ANNOTATION", "description": "added annotation", "codeElement": "@RunWith(AndroidJUnit4.class)"}, {"filePath": "services/tests/servicestests/src/com/android/server/pm/UserManagerTest.java", "startLine": 59, "endLine": 906, "startColumn": 0, "endColumn": 2, "codeElementType": "TYPE_DECLARATION", "description": "class declaration with added annotation", "codeElement": "com.android.server.pm.UserManagerTest"}]

### Patch: services/tests/servicestests/src/com/android/server/pm/UserManagerTest.java
```diff
@@ -16,6 +16,12 @@
 
 package com.android.server.pm;
 
+import static com.google.common.truth.Truth.assertThat;
+import static com.google.common.truth.Truth.assertWithMessage;
+
+import static org.junit.Assert.fail;
+import static org.junit.Assume.assumeTrue;
+
 import android.annotation.UserIdInt;
 import android.app.ActivityManager;
 import android.content.BroadcastReceiver;
@@ -29,23 +35,30 @@
 import android.os.UserHandle;
 import android.os.UserManager;
 import android.provider.Settings;
-import android.test.AndroidTestCase;
 import android.test.suitebuilder.annotation.LargeTest;
 import android.test.suitebuilder.annotation.MediumTest;
 import android.test.suitebuilder.annotation.SmallTest;
 
-import com.android.internal.util.ArrayUtils;
+import androidx.test.InstrumentationRegistry;
+import androidx.test.runner.AndroidJUnit4;
+
+import com.google.common.collect.Range;
+
+import org.junit.After;
+import org.junit.Before;
+import org.junit.Test;
+import org.junit.runner.RunWith;
 
 import java.util.ArrayList;
-import java.util.Arrays;
 import java.util.List;
 import java.util.concurrent.ExecutorService;
 import java.util.concurrent.Executors;
 import java.util.concurrent.TimeUnit;
 import java.util.concurrent.atomic.AtomicInteger;
 
 /** Test {@link UserManager} functionality. */
-public class UserManagerTest extends AndroidTestCase {
+@RunWith(AndroidJUnit4.class)
+public final class UserManagerTest {
     // Taken from UserManagerService
     private static final long EPOCH_PLUS_30_YEARS = 30L * 365 * 24 * 60 * 60 * 1000L; // 30 years
 
@@ -58,22 +71,23 @@ public class UserManagerTest extends AndroidTestCase {
             "com.android.egg"
     };
 
+    private final Context mContext = InstrumentationRegistry.getInstrumentation().getContext();
+
     private final Object mUserRemoveLock = new Object();
     private final Object mUserSwitchLock = new Object();
 
     private UserManager mUserManager = null;
     private PackageManager mPackageManager;
     private List<Integer> usersToRemove;
 
-    @Override
+    @Before
     public void setUp() throws Exception {
-        super.setUp();
-        mUserManager = UserManager.get(getContext());
-        mPackageManager = getContext().getPackageManager();
+        mUserManager = UserManager.get(mContext);
+        mPackageManager = mContext.getPackageManager();
 
         IntentFilter filter = new IntentFilter(Intent.ACTION_USER_REMOVED);
         filter.addAction(Intent.ACTION_USER_SWITCHED);
-        getContext().registerReceiver(new BroadcastReceiver() {
+        mContext.registerReceiver(new BroadcastReceiver() {
             @Override
             public void onReceive(Context context, Intent intent) {
                 switch (intent.getAction()) {
@@ -95,12 +109,11 @@ public void onReceive(Context context, Intent intent) {
         usersToRemove = new ArrayList<>();
     }
 
-    @Override
-    protected void tearDown() throws Exception {
+    @After
+    public void tearDown() throws Exception {
         for (Integer userId : usersToRemove) {
             removeUser(userId);
         }
-        super.tearDown();
     }
 
     private void removeExistingUsers() {
@@ -115,14 +128,16 @@ private void removeExistingUsers() {
     }
 
     @SmallTest
+    @Test
     public void testHasSystemUser() throws Exception {
-        assertTrue(findUser(UserHandle.USER_SYSTEM));
+        assertThat(findUser(UserHandle.USER_SYSTEM)).isTrue();
     }
 
     @MediumTest
+    @Test
     public void testAddGuest() throws Exception {
         UserInfo userInfo = createUser("Guest 1", UserInfo.FLAG_GUEST);
-        assertTrue(userInfo != null);
+        assertThat(userInfo).isNotNull();
 
         List<UserInfo> list = mUserManager.getUsers();
         boolean found = false;
@@ -133,35 +148,39 @@ public void testAddGuest() throws Exception {
                     && !user.isPrimary()) {
                 found = true;
                 Bundle restrictions = mUserManager.getUserRestrictions(user.getUserHandle());
-                assertTrue("Guest user should have DISALLOW_CONFIG_WIFI=true by default",
-                        restrictions.getBoolean(UserManager.DISALLOW_CONFIG_WIFI));
+                assertWithMessage("Guest user should have DISALLOW_CONFIG_WIFI=true by default")
+                        .that(restrictions.getBoolean(UserManager.DISALLOW_CONFIG_WIFI))
+                        .isTrue();
             }
         }
-        assertTrue(found);
+        assertThat(found).isTrue();
     }
 
     @MediumTest
+    @Test
     public void testAdd2Users() throws Exception {
         UserInfo user1 = createUser("Guest 1", UserInfo.FLAG_GUEST);
         UserInfo user2 = createUser("User 2", UserInfo.FLAG_ADMIN);
 
-        assertTrue(user1 != null);
-        assertTrue(user2 != null);
+        assertThat(user1).isNotNull();
+        assertThat(user2).isNotNull();
 
-        assertTrue(findUser(UserHandle.USER_SYSTEM));
-        assertTrue(findUser(user1.id));
-        assertTrue(findUser(user2.id));
+        assertThat(findUser(UserHandle.USER_SYSTEM)).isTrue();
+        assertThat(findUser(user1.id)).isTrue();
+        assertThat(findUser(user2.id)).isTrue();
     }
 
     @MediumTest
+    @Test
     public void testRemoveUser() throws Exception {
         UserInfo userInfo = createUser("Guest 1", UserInfo.FLAG_GUEST);
         removeUser(userInfo.id);
 
-        assertFalse(findUser(userInfo.id));
+        assertThat(findUser(userInfo.id)).isFalse();
     }
 
     @MediumTest
+    @Test
     public void testRemoveUserByHandle() {
         UserInfo userInfo = createUser("Guest 1", UserInfo.FLAG_GUEST);
         final UserHandle user = userInfo.getUserHandle();
@@ -181,10 +200,11 @@ public void testRemoveUserByHandle() {
             }
         }
 
-        assertFalse(findUser(userInfo.id));
+        assertThat(findUser(userInfo.id)).isFalse();
     }
 
     @MediumTest
+    @Test
     public void testRemoveUserByHandle_ThrowsException() {
         synchronized (mUserRemoveLock) {
             try {
@@ -198,6 +218,7 @@ public void testRemoveUserByHandle_ThrowsException() {
 
     /** Tests creating a FULL user via specifying userType. */
     @MediumTest
+    @Test
     public void testCreateUserViaTypes() throws Exception {
         createUserWithTypeAndCheckFlags(UserManager.USER_TYPE_FULL_GUEST,
                 UserInfo.FLAG_GUEST | UserInfo.FLAG_FULL);
@@ -211,6 +232,7 @@ public void testCreateUserViaTypes() throws Exception {
 
     /** Tests creating a FULL user via specifying user flags. */
     @MediumTest
+    @Test
     public void testCreateUserViaFlags() throws Exception {
         createUserWithFlagsAndCheckType(UserInfo.FLAG_GUEST, UserManager.USER_TYPE_FULL_GUEST,
                 UserInfo.FLAG_FULL);
@@ -229,10 +251,9 @@ public void testCreateUserViaFlags() throws Exception {
     private void createUserWithTypeAndCheckFlags(String userType,
             @UserIdInt int requiredFlags) {
         final UserInfo userInfo = createUser("Name", userType, 0);
-        assertEquals("Wrong user type", userType, userInfo.userType);
-        assertEquals(
-                "Flags " + userInfo.flags + " did not contain expected " + requiredFlags,
-                requiredFlags, userInfo.flags & requiredFlags);
+        assertWithMessage("Wrong user type").that(userInfo.userType).isEqualTo(userType);
+        assertWithMessage("Flags %s did not contain expected %s", userInfo.flags, requiredFlags)
+                .that(userInfo.flags & requiredFlags).isEqualTo(requiredFlags);
         removeUser(userInfo.id);
     }
 
@@ -243,179 +264,187 @@ private void createUserWithTypeAndCheckFlags(String userType,
     private void createUserWithFlagsAndCheckType(@UserIdInt int flags, String expectedUserType,
             @UserIdInt int additionalRequiredFlags) {
         final UserInfo userInfo = createUser("Name", flags);
-        assertEquals("Wrong user type", expectedUserType, userInfo.userType);
+        assertWithMessage("Wrong user type").that(userInfo.userType).isEqualTo(expectedUserType);
         additionalRequiredFlags |= flags;
-        assertEquals(
-                "Flags " + userInfo.flags + " did not contain expected " + additionalRequiredFlags,
-                additionalRequiredFlags, userInfo.flags & additionalRequiredFlags);
+        assertWithMessage("Flags %s did not contain expected %s", userInfo.flags,
+                additionalRequiredFlags).that(userInfo.flags & additionalRequiredFlags)
+                        .isEqualTo(additionalRequiredFlags);
         removeUser(userInfo.id);
     }
 
 
     @MediumTest
+    @Test
     public void testThereCanBeOnlyOneGuest() throws Exception {
         UserInfo userInfo1 = createUser("Guest 1", UserInfo.FLAG_GUEST);
-        assertNotNull(userInfo1);
+        assertThat(userInfo1).isNotNull();
         UserInfo userInfo2 = createUser("Guest 2", UserInfo.FLAG_GUEST);
-        assertNull(userInfo2);
+        assertThat(userInfo2).isNull();
     }
 
     @MediumTest
+    @Test
     public void testFindExistingGuest_guestExists() throws Exception {
         UserInfo userInfo1 = createUser("Guest", UserInfo.FLAG_GUEST);
+        assertThat(userInfo1).isNotNull();
         UserInfo foundGuest = mUserManager.findCurrentGuestUser();
-        assertNotNull(foundGuest);
+        assertThat(foundGuest).isNotNull();
     }
 
     @SmallTest
+    @Test
     public void testFindExistingGuest_guestDoesNotExist() throws Exception {
         UserInfo foundGuest = mUserManager.findCurrentGuestUser();
-        assertNull(foundGuest);
+        assertThat(foundGuest).isNull();
     }
 
     @MediumTest
+    @Test
     public void testSetUserAdmin() throws Exception {
         UserInfo userInfo = createUser("SecondaryUser", /*flags=*/ 0);
-        assertFalse(userInfo.isAdmin());
+        assertThat(userInfo.isAdmin()).isFalse();
 
         mUserManager.setUserAdmin(userInfo.id);
 
         userInfo = mUserManager.getUserInfo(userInfo.id);
-        assertTrue(userInfo.isAdmin());
+        assertThat(userInfo.isAdmin()).isTrue();
     }
 
     @MediumTest
+    @Test
     public void testGetProfileParent() throws Exception {
-        if (!supportsManagedProfiles()) return;
+        assumeManagedUsersSupported();
         final int primaryUserId = mUserManager.getPrimaryUser().id;
 
         UserInfo userInfo = createProfileForUser("Profile",
                 UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId);
-        assertNotNull(userInfo);
-        assertNull(mUserManager.getProfileParent(primaryUserId));
+        assertThat(userInfo).isNotNull();
+        assertThat(mUserManager.getProfileParent(primaryUserId)).isNull();
         UserInfo parentProfileInfo = mUserManager.getProfileParent(userInfo.id);
-        assertNotNull(parentProfileInfo);
-        assertEquals(parentProfileInfo.id, primaryUserId);
+        assertThat(parentProfileInfo).isNotNull();
+        assertThat(primaryUserId).isEqualTo(parentProfileInfo.id);
         removeUser(userInfo.id);
-        assertNull(mUserManager.getProfileParent(primaryUserId));
+        assertThat(mUserManager.getProfileParent(primaryUserId)).isNull();
     }
 
     /** Test that UserManager returns the correct badge information for a managed profile. */
     @MediumTest
+    @Test
     public void testProfileTypeInformation() throws Exception {
-        if (!supportsManagedProfiles()) return;
+        assumeManagedUsersSupported();
         final UserTypeDetails userTypeDetails =
                 UserTypeFactory.getUserTypes().get(UserManager.USER_TYPE_PROFILE_MANAGED);
-        assertNotNull("No " + UserManager.USER_TYPE_PROFILE_MANAGED + " type on device",
-                userTypeDetails);
-        assertEquals(UserManager.USER_TYPE_PROFILE_MANAGED, userTypeDetails.getName());
+        assertWithMessage("No %s type on device", UserManager.USER_TYPE_PROFILE_MANAGED)
+                .that(userTypeDetails).isNotNull();
+        assertThat(userTypeDetails.getName()).isEqualTo(UserManager.USER_TYPE_PROFILE_MANAGED);
 
         final int primaryUserId = mUserManager.getPrimaryUser().id;
         UserInfo userInfo = createProfileForUser("Managed",
                 UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId);
-        assertNotNull(userInfo);
+        assertThat(userInfo).isNotNull();
         final int userId = userInfo.id;
         final UserHandle userHandle = new UserHandle(userId);
 
-        assertEquals(userTypeDetails.hasBadge(),
-                mUserManager.hasBadge(userId));
-        assertEquals(userTypeDetails.getIconBadge(),
-                mUserManager.getUserIconBadgeResId(userId));
-        assertEquals(userTypeDetails.getBadgePlain(),
-                mUserManager.getUserBadgeResId(userId));
-        assertEquals(userTypeDetails.getBadgeNoBackground(),
-                mUserManager.getUserBadgeNoBackgroundResId(userId));
-        assertEquals(userTypeDetails.isProfile(),
-                mUserManager.isProfile(userId));
-        assertEquals(userTypeDetails.getName(),
-                mUserManager.getUserTypeForUser(userHandle));
+        assertThat(mUserManager.hasBadge(userId)).isEqualTo(userTypeDetails.hasBadge());
+        assertThat(mUserManager.getUserIconBadgeResId(userId))
+                .isEqualTo(userTypeDetails.getIconBadge());
+        assertThat(mUserManager.getUserBadgeResId(userId))
+                .isEqualTo(userTypeDetails.getBadgePlain());
+        assertThat(mUserManager.getUserBadgeNoBackgroundResId(userId))
+                .isEqualTo(userTypeDetails.getBadgeNoBackground());
+        assertThat(mUserManager.isProfile(userId)).isEqualTo(userTypeDetails.isProfile());
+        assertThat(mUserManager.getUserTypeForUser(userHandle))
+                .isEqualTo(userTypeDetails.getName());
 
         final int badgeIndex = userInfo.profileBadge;
-        assertEquals(
-                Resources.getSystem().getColor(userTypeDetails.getBadgeColor(badgeIndex), null),
-                mUserManager.getUserBadgeColor(userId));
-        assertEquals(
-                Resources.getSystem().getString(userTypeDetails.getBadgeLabel(badgeIndex), "Test"),
-                mUserManager.getBadgedLabelForUser("Test", userHandle));
+        assertThat(mUserManager.getUserBadgeColor(userId)).isEqualTo(
+                Resources.getSystem().getColor(userTypeDetails.getBadgeColor(badgeIndex), null));
+        assertThat(mUserManager.getBadgedLabelForUser("Test", userHandle)).isEqualTo(
+                Resources.getSystem().getString(userTypeDetails.getBadgeLabel(badgeIndex), "Test"));
     }
 
     // Make sure only one managed profile can be created
     @MediumTest
+    @Test
     public void testAddManagedProfile() throws Exception {
-        if (!supportsManagedProfiles()) return;
+        assumeManagedUsersSupported();
         final int primaryUserId = mUserManager.getPrimaryUser().id;
         UserInfo userInfo1 = createProfileForUser("Managed 1",
                 UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId);
         UserInfo userInfo2 = createProfileForUser("Managed 2",
                 UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId);
 
-        assertNotNull(userInfo1);
-        assertNull(userInfo2);
+        assertThat(userInfo1).isNotNull();
+        assertThat(userInfo2).isNull();
 
-        assertEquals(userInfo1.userType, UserManager.USER_TYPE_PROFILE_MANAGED);
+        assertThat(userInfo1.userType).isEqualTo(UserManager.USER_TYPE_PROFILE_MANAGED);
         int requiredFlags = UserInfo.FLAG_MANAGED_PROFILE | UserInfo.FLAG_PROFILE;
-        assertEquals("Wrong flags " + userInfo1.flags, requiredFlags,
-                userInfo1.flags & requiredFlags);
+        assertWithMessage("Wrong flags %s", userInfo1.flags).that(userInfo1.flags & requiredFlags)
+                .isEqualTo(requiredFlags);
 
         // Verify that current user is not a managed profile
-        assertFalse(mUserManager.isManagedProfile());
+        assertThat(mUserManager.isManagedProfile()).isFalse();
     }
 
     // Verify that disallowed packages are not installed in the managed profile.
     @MediumTest
+    @Test
     public void testAddManagedProfile_withDisallowedPackages() throws Exception {
-        if (!supportsManagedProfiles()) return;
+        assumeManagedUsersSupported();
         final int primaryUserId = mUserManager.getPrimaryUser().id;
         UserInfo userInfo1 = createProfileForUser("Managed1",
                 UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId);
         // Verify that the packagesToVerify are installed by default.
         for (String pkg : PACKAGES) {
-            assertTrue("Package should be installed in managed profile: " + pkg,
-                    isPackageInstalledForUser(pkg, userInfo1.id));
+            assertWithMessage("Package should be installed in managed profile: %s", pkg)
+                    .that(isPackageInstalledForUser(pkg, userInfo1.id)).isTrue();
         }
         removeUser(userInfo1.id);
 
         UserInfo userInfo2 = createProfileForUser("Managed2",
                 UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId, PACKAGES);
         // Verify that the packagesToVerify are not installed by default.
         for (String pkg : PACKAGES) {
-            assertFalse("Package should not be installed in managed profile when disallowed: "
-                    + pkg, isPackageInstalledForUser(pkg, userInfo2.id));
+            assertWithMessage(
+                    "Package should not be installed in managed profile when disallowed: %s", pkg)
+                            .that(isPackageInstalledForUser(pkg, userInfo2.id)).isFalse();
         }
     }
 
     // Verify that if any packages are disallowed to install during creation of managed profile can
     // still be installed later.
     @MediumTest
+    @Test
     public void testAddManagedProfile_disallowedPackagesInstalledLater() throws Exception {
-        if (!supportsManagedProfiles()) return;
+        assumeManagedUsersSupported();
         final int primaryUserId = mUserManager.getPrimaryUser().id;
         UserInfo userInfo = createProfileForUser("Managed",
                 UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId, PACKAGES);
         // Verify that the packagesToVerify are not installed by default.
         for (String pkg : PACKAGES) {
-            assertFalse("Package should not be installed in managed profile when disallowed: "
-                    + pkg, isPackageInstalledForUser(pkg, userInfo.id));
+            assertWithMessage("Pkg should not be installed in managed profile when disallowed: %s",
+                    pkg).that(isPackageInstalledForUser(pkg, userInfo.id)).isFalse();
         }
 
         // Verify that the disallowed packages during profile creation can be installed now.
         for (String pkg : PACKAGES) {
-            assertEquals("Package could not be installed: " + pkg,
-                    PackageManager.INSTALL_SUCCEEDED,
-                    mPackageManager.installExistingPackageAsUser(pkg, userInfo.id));
+            assertWithMessage("Package could not be installed: %s", pkg)
+                    .that(mPackageManager.installExistingPackageAsUser(pkg, userInfo.id))
+                    .isEqualTo(PackageManager.INSTALL_SUCCEEDED);
         }
     }
 
     // Make sure createUser would fail if we have DISALLOW_ADD_USER.
     @MediumTest
+    @Test
     public void testCreateUser_disallowAddUser() throws Exception {
         final int creatorId = isAutomotive() ? ActivityManager.getCurrentUser()
                 : mUserManager.getPrimaryUser().id;
         final UserHandle creatorHandle = new UserHandle(creatorId);
         mUserManager.setUserRestriction(UserManager.DISALLOW_ADD_USER, true, creatorHandle);
         try {
             UserInfo createadInfo = createUser("SecondaryUser", /*flags=*/ 0);
-            assertNull(createadInfo);
+            assertThat(createadInfo).isNull();
         } finally {
             mUserManager.setUserRestriction(UserManager.DISALLOW_ADD_USER, false,
                     creatorHandle);
@@ -424,16 +453,17 @@ public void testCreateUser_disallowAddUser() throws Exception {
 
     // Make sure createProfile would fail if we have DISALLOW_ADD_MANAGED_PROFILE.
     @MediumTest
+    @Test
     public void testCreateProfileForUser_disallowAddManagedProfile() throws Exception {
-        if (!supportsManagedProfiles()) return;
+        assumeManagedUsersSupported();
         final int primaryUserId = mUserManager.getPrimaryUser().id;
         final UserHandle primaryUserHandle = new UserHandle(primaryUserId);
         mUserManager.setUserRestriction(UserManager.DISALLOW_ADD_MANAGED_PROFILE, true,
                 primaryUserHandle);
         try {
             UserInfo userInfo = createProfileForUser("Managed",
                     UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId);
-            assertNull(userInfo);
+            assertThat(userInfo).isNull();
         } finally {
             mUserManager.setUserRestriction(UserManager.DISALLOW_ADD_MANAGED_PROFILE, false,
                     primaryUserHandle);
@@ -442,16 +472,17 @@ public void testCreateProfileForUser_disallowAddManagedProfile() throws Exceptio
 
     // Make sure createProfileEvenWhenDisallowedForUser bypass DISALLOW_ADD_MANAGED_PROFILE.
     @MediumTest
+    @Test
     public void testCreateProfileForUserEvenWhenDisallowed() throws Exception {
-        if (!supportsManagedProfiles()) return;
+        assumeManagedUsersSupported();
         final int primaryUserId = mUserManager.getPrimaryUser().id;
         final UserHandle primaryUserHandle = new UserHandle(primaryUserId);
         mUserManager.setUserRestriction(UserManager.DISALLOW_ADD_MANAGED_PROFILE, true,
                 primaryUserHandle);
         try {
             UserInfo userInfo = createProfileEvenWhenDisallowedForUser("Managed",
                     UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId);
-            assertNotNull(userInfo);
+            assertThat(userInfo).isNotNull();
         } finally {
             mUserManager.setUserRestriction(UserManager.DISALLOW_ADD_MANAGED_PROFILE, false,
                     primaryUserHandle);
@@ -460,92 +491,102 @@ public void testCreateProfileForUserEvenWhenDisallowed() throws Exception {
 
     // createProfile succeeds even if DISALLOW_ADD_USER is set
     @MediumTest
+    @Test
     public void testCreateProfileForUser_disallowAddUser() throws Exception {
-        if (!supportsManagedProfiles()) return;
+        assumeManagedUsersSupported();
         final int primaryUserId = mUserManager.getPrimaryUser().id;
         final UserHandle primaryUserHandle = new UserHandle(primaryUserId);
         mUserManager.setUserRestriction(UserManager.DISALLOW_ADD_USER, true, primaryUserHandle);
         try {
             UserInfo userInfo = createProfileForUser("Managed",
                     UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId);
-            assertNotNull(userInfo);
+            assertThat(userInfo).isNotNull();
         } finally {
             mUserManager.setUserRestriction(UserManager.DISALLOW_ADD_USER, false,
                     primaryUserHandle);
         }
     }
 
     @MediumTest
+    @Test
     public void testAddRestrictedProfile() throws Exception {
         if (isAutomotive()) return;
-        assertFalse("There should be no associated restricted profiles before the test",
-                mUserManager.hasRestrictedProfiles());
+        assertWithMessage("There should be no associated restricted profiles before the test")
+                .that(mUserManager.hasRestrictedProfiles()).isFalse();
         UserInfo userInfo = createRestrictedProfile("Profile");
-        assertNotNull(userInfo);
+        assertThat(userInfo).isNotNull();
 
         Bundle restrictions = mUserManager.getUserRestrictions(UserHandle.of(userInfo.id));
-        assertTrue("Restricted profile should have DISALLOW_MODIFY_ACCOUNTS restriction by default",
-                restrictions.getBoolean(UserManager.DISALLOW_MODIFY_ACCOUNTS));
-        assertTrue("Restricted profile should have DISALLOW_SHARE_LOCATION restriction by default",
-                restrictions.getBoolean(UserManager.DISALLOW_SHARE_LOCATION));
-
-        int locationMode = Settings.Secure.getIntForUser(getContext().getContentResolver(),
+        assertWithMessage(
+                "Restricted profile should have DISALLOW_MODIFY_ACCOUNTS restriction by default")
+                        .that(restrictions.getBoolean(UserManager.DISALLOW_MODIFY_ACCOUNTS))
+                        .isTrue();
+        assertWithMessage(
+                "Restricted profile should have DISALLOW_SHARE_LOCATION restriction by default")
+                        .that(restrictions.getBoolean(UserManager.DISALLOW_SHARE_LOCATION))
+                        .isTrue();
+
+        int locationMode = Settings.Secure.getIntForUser(mContext.getContentResolver(),
                 Settings.Secure.LOCATION_MODE,
                 Settings.Secure.LOCATION_MODE_HIGH_ACCURACY,
                 userInfo.id);
-        assertEquals("Restricted profile should have setting LOCATION_MODE set to "
-                + "LOCATION_MODE_OFF by default", locationMode, Settings.Secure.LOCATION_MODE_OFF);
+        assertWithMessage("Restricted profile should have setting LOCATION_MODE set to "
+                + "LOCATION_MODE_OFF by default").that(locationMode)
+                        .isEqualTo(Settings.Secure.LOCATION_MODE_OFF);
 
-        assertTrue("Newly created profile should be associated with the current user",
-                mUserManager.hasRestrictedProfiles());
+        assertWithMessage("Newly created profile should be associated with the current user")
+                .that(mUserManager.hasRestrictedProfiles()).isTrue();
     }
 
     @MediumTest
+    @Test
     public void testGetUserCreationTime() throws Exception {
         // TODO: should add a regular user instead of a profile, so it can be tested everywhere
-        if (!supportsManagedProfiles()) return;
+        assumeManagedUsersSupported();
         final int primaryUserId = mUserManager.getPrimaryUser().id;
         final long startTime = System.currentTimeMillis();
         UserInfo profile = createProfileForUser("Managed 1",
                 UserManager.USER_TYPE_PROFILE_MANAGED, primaryUserId);
         final long endTime = System.currentTimeMillis();
-        assertNotNull(profile);
+        assertThat(profile).isNotNull();
         if (System.currentTimeMillis() > EPOCH_PLUS_30_YEARS) {
-            assertTrue("creationTime must be set when the profile is created",
-                    profile.creationTime >= startTime && profile.creationTime <= endTime);
+            assertWithMessage("creationTime must be set when the profile is created")
+                    .that(profile.creationTime).isIn(Range.closed(startTime, endTime));
         } else {
-            assertTrue("creationTime must be 0 if the time is not > EPOCH_PLUS_30_years",
-                    profile.creationTime == 0);
+            assertWithMessage("creationTime must be 0 if the time is not > EPOCH_PLUS_30_years")
+                    .that(profile.creationTime).isEqualTo(0);
         }
-        assertEquals(profile.creationTime, mUserManager.getUserCreationTime(
-                new UserHandle(profile.id)));
+        assertThat(mUserManager.getUserCreationTime(
+                new UserHandle(profile.id))).isEqualTo(profile.creationTime);
 
         long ownerCreationTime = mUserManager.getUserInfo(primaryUserId).creationTime;
-        assertEquals(ownerCreationTime, mUserManager.getUserCreationTime(
-                new UserHandle(primaryUserId)));
+        assertThat(mUserManager.getUserCreationTime(
+                new UserHandle(primaryUserId))).isEqualTo(ownerCreationTime);
     }
 
     @SmallTest
+    @Test
     public void testGetUserCreationTime_nonExistentUser() throws Exception {
         try {
             int noSuchUserId = 100500;
             mUserManager.getUserCreationTime(new UserHandle(noSuchUserId));
             fail("SecurityException should be thrown for nonexistent user");
         } catch (Exception e) {
-            assertTrue("SecurityException should be thrown for nonexistent user, but was: " + e,
-                    e instanceof SecurityException);
+            assertWithMessage("SecurityException should be thrown for nonexistent user").that(e)
+                    .isInstanceOf(SecurityException.class);
         }
     }
 
     @SmallTest
+    @Test
     public void testGetUserCreationTime_otherUser() throws Exception {
         UserInfo user = createUser("User 1", 0);
         try {
             mUserManager.getUserCreationTime(new UserHandle(user.id));
             fail("SecurityException should be thrown for other user");
         } catch (Exception e) {
-            assertTrue("SecurityException should be thrown for other user, but was: " + e,
-                    e instanceof SecurityException);
+            assertWithMessage("SecurityException should be thrown for other user").that(e)
+                    .isInstanceOf(SecurityException.class);
         }
     }
 
@@ -561,56 +602,58 @@ private boolean findUser(int id) {
     }
 
     @MediumTest
+    @Test
     public void testSerialNumber() {
         UserInfo user1 = createUser("User 1", 0);
         int serialNumber1 = user1.serialNumber;
-        assertEquals(serialNumber1, mUserManager.getUserSerialNumber(user1.id));
-        assertEquals(user1.id, mUserManager.getUserHandle(serialNumber1));
+        assertThat(mUserManager.getUserSerialNumber(user1.id)).isEqualTo(serialNumber1);
+        assertThat(mUserManager.getUserHandle(serialNumber1)).isEqualTo(user1.id);
         UserInfo user2 = createUser("User 2", 0);
         int serialNumber2 = user2.serialNumber;
-        assertFalse(serialNumber1 == serialNumber2);
-        assertEquals(serialNumber2, mUserManager.getUserSerialNumber(user2.id));
-        assertEquals(user2.id, mUserManager.getUserHandle(serialNumber2));
+        assertThat(serialNumber1 == serialNumber2).isFalse();
+        assertThat(mUserManager.getUserSerialNumber(user2.id)).isEqualTo(serialNumber2);
+        assertThat(mUserManager.getUserHandle(serialNumber2)).isEqualTo(user2.id);
     }
 
     @MediumTest
+    @Test
     public void testGetSerialNumbersOfUsers() {
         UserInfo user1 = createUser("User 1", 0);
         UserInfo user2 = createUser("User 2", 0);
         long[] serialNumbersOfUsers = mUserManager.getSerialNumbersOfUsers(false);
-        String errMsg = "Array " + Arrays.toString(serialNumbersOfUsers) + " should contain ";
-        assertTrue(errMsg + user1.serialNumber,
-                ArrayUtils.contains(serialNumbersOfUsers, user1.serialNumber));
-        assertTrue(errMsg + user2.serialNumber,
-                ArrayUtils.contains(serialNumbersOfUsers, user2.serialNumber));
+        assertThat(serialNumbersOfUsers).asList().containsAllOf(
+                (long) user1.serialNumber, (long) user2.serialNumber);
     }
 
     @MediumTest
+    @Test
     public void testMaxUsers() {
         int N = UserManager.getMaxSupportedUsers();
         int count = mUserManager.getUsers().size();
         // Create as many users as permitted and make sure creation passes
         while (count < N) {
             UserInfo ui = createUser("User " + count, 0);
-            assertNotNull(ui);
+            assertThat(ui).isNotNull();
             count++;
         }
         // Try to create one more user and make sure it fails
         UserInfo extra = createUser("One more", 0);
-        assertNull(extra);
+        assertThat(extra).isNull();
     }
 
     @MediumTest
+    @Test
     public void testGetUserCount() {
         int count = mUserManager.getUsers().size();
         UserInfo user1 = createUser("User 1", 0);
-        assertNotNull(user1);
+        assertThat(user1).isNotNull();
         UserInfo user2 = createUser("User 2", 0);
-        assertNotNull(user2);
-        assertEquals(count + 2, mUserManager.getUserCount());
+        assertThat(user2).isNotNull();
+        assertThat(mUserManager.getUserCount()).isEqualTo(count + 2);
     }
 
     @MediumTest
+    @Test
     public void testRestrictions() {
         UserInfo testUser = createUser("User 1", 0);
 
@@ -621,12 +664,13 @@ public void testRestrictions() {
 
         Bundle stored = mUserManager.getUserRestrictions(new UserHandle(testUser.id));
         // Note this will fail if DO already sets those restrictions.
-        assertEquals(stored.getBoolean(UserManager.DISALLOW_CONFIG_WIFI), false);
-        assertEquals(stored.getBoolean(UserManager.DISALLOW_UNINSTALL_APPS), false);
-        assertEquals(stored.getBoolean(UserManager.DISALLOW_INSTALL_APPS), true);
+        assertThat(stored.getBoolean(UserManager.DISALLOW_CONFIG_WIFI)).isFalse();
+        assertThat(stored.getBoolean(UserManager.DISALLOW_UNINSTALL_APPS)).isFalse();
+        assertThat(stored.getBoolean(UserManager.DISALLOW_INSTALL_APPS)).isTrue();
     }
 
     @MediumTest
+    @Test
     public void testDefaultRestrictionsApplied() throws Exception {
         final UserInfo userInfo = createUser("Useroid", UserManager.USER_TYPE_FULL_SECONDARY, 0);
         final UserTypeDetails userTypeDetails =
@@ -635,13 +679,14 @@ public void testDefaultRestrictionsApplied() throws Exception {
         // Note this can fail if DO unset those restrictions.
         for (String restriction : expectedRestrictions.keySet()) {
             if (expectedRestrictions.getBoolean(restriction)) {
-                assertTrue(
-                        mUserManager.hasUserRestriction(restriction, UserHandle.of(userInfo.id)));
+                assertThat(mUserManager.hasUserRestriction(restriction, UserHandle.of(userInfo.id)))
+                        .isTrue();
             }
         }
     }
 
     @MediumTest
+    @Test
     public void testSetDefaultGuestRestrictions() {
         final Bundle origGuestRestrictions = mUserManager.getDefaultGuestRestrictions();
         Bundle restrictions = new Bundle();
@@ -650,48 +695,52 @@ public void testSetDefaultGuestRestrictions() {
 
         try {
             UserInfo guest = createUser("Guest", UserInfo.FLAG_GUEST);
-            assertNotNull(guest);
-            assertTrue(mUserManager.hasUserRestriction(UserManager.DISALLOW_FUN,
-                    guest.getUserHandle()));
+            assertThat(guest).isNotNull();
+            assertThat(mUserManager.hasUserRestriction(UserManager.DISALLOW_FUN,
+                    guest.getUserHandle())).isTrue();
         } finally {
             mUserManager.setDefaultGuestRestrictions(origGuestRestrictions);
         }
     }
 
+    @Test
     public void testGetUserSwitchability() {
         int userSwitchable = mUserManager.getUserSwitchability();
-        assertEquals("Expected users to be switchable", UserManager.SWITCHABILITY_STATUS_OK,
-                userSwitchable);
+        assertWithMessage("Expected users to be switchable").that(userSwitchable)
+                .isEqualTo(UserManager.SWITCHABILITY_STATUS_OK);
     }
 
     @LargeTest
+    @Test
     public void testSwitchUser() {
-        ActivityManager am = getContext().getSystemService(ActivityManager.class);
+        ActivityManager am = mContext.getSystemService(ActivityManager.class);
         final int startUser = am.getCurrentUser();
         UserInfo user = createUser("User", 0);
-        assertNotNull(user);
+        assertThat(user).isNotNull();
         // Switch to the user just created.
         switchUser(user.id, null, true);
         // Switch back to the starting user.
         switchUser(startUser, null, true);
     }
 
     @LargeTest
+    @Test
     public void testSwitchUserByHandle() {
-        ActivityManager am = getContext().getSystemService(ActivityManager.class);
+        ActivityManager am = mContext.getSystemService(ActivityManager.class);
         final int startUser = am.getCurrentUser();
         UserInfo user = createUser("User", 0);
-        assertNotNull(user);
+        assertThat(user).isNotNull();
         // Switch to the user just created.
         switchUser(-1, user.getUserHandle(), false);
         // Switch back to the starting user.
         switchUser(-1, UserHandle.of(startUser), false);
     }
 
+    @Test
     public void testSwitchUserByHandle_ThrowsException() {
         synchronized (mUserSwitchLock) {
             try {
-                ActivityManager am = getContext().getSystemService(ActivityManager.class);
+                ActivityManager am = mContext.getSystemService(ActivityManager.class);
                 am.switchUser(null);
                 fail("Expected IllegalArgumentException on passing in a null UserHandle.");
             } catch (IllegalArgumentException expected) {
@@ -701,6 +750,7 @@ public void testSwitchUserByHandle_ThrowsException() {
     }
 
     @MediumTest
+    @Test
     public void testConcurrentUserCreate() throws Exception {
         int userCount = mUserManager.getUserCount();
         int maxSupportedUsers = UserManager.getMaxSupportedUsers();
@@ -723,11 +773,12 @@ public void testConcurrentUserCreate() throws Exception {
         }
         es.shutdown();
         es.awaitTermination(20, TimeUnit.SECONDS);
-        assertEquals(maxSupportedUsers, mUserManager.getUserCount());
-        assertEquals(canBeCreatedCount, created.get());
+        assertThat(mUserManager.getUserCount()).isEqualTo(maxSupportedUsers);
+        assertThat(created.get()).isEqualTo(canBeCreatedCount);
     }
 
     @MediumTest
+    @Test
     public void testGetUserHandles_createNewUser_shouldFindNewUser() {
         UserInfo user = createUser("Guest 1", UserManager.USER_TYPE_FULL_GUEST, /*flags*/ 0);
 
@@ -739,7 +790,7 @@ public void testGetUserHandles_createNewUser_shouldFindNewUser() {
             }
         }
 
-        assertTrue(found);
+        assertThat(found).isTrue();
     }
 
     private boolean isPackageInstalledForUser(String packageName, int userId) {
@@ -758,7 +809,7 @@ private boolean isPackageInstalledForUser(String packageName, int userId) {
      */
     private void switchUser(int userId, UserHandle user, boolean ignoreHandle) {
         synchronized (mUserSwitchLock) {
-            ActivityManager am = getContext().getSystemService(ActivityManager.class);
+            ActivityManager am = mContext.getSystemService(ActivityManager.class);
             if (ignoreHandle) {
                 am.switchUser(userId);
             } else {
@@ -844,10 +895,9 @@ private UserInfo createRestrictedProfile(String name) {
         return profile;
     }
 
-    // TODO: use assumeTrue() instead (doesn't currently work because JUnit3 tests fail when test
-    // throws AssumptionViolatedException)
-    private boolean supportsManagedProfiles() {
-        return mPackageManager.hasSystemFeature(PackageManager.FEATURE_MANAGED_USERS);
+    private void assumeManagedUsersSupported() {
+        assumeTrue("device doesn't support managed users",
+                mPackageManager.hasSystemFeature(PackageManager.FEATURE_MANAGED_USERS));
     }
 
     private boolean isAutomotive() {
```

## Row 27
commit_url: https://github.com/ftsrg/theta/commit/fc1af6246a233c2603cc7e97ccdc4b522b514ca8
rm_type: Move Code
rm_description: Move Code from public testBV2() : void to public setup() : void in class hu.bme.mit.theta.solver.z3.Z3SolverTest
file_path: subprojects/solver-z3/src/test/java/hu/bme/mit/theta/solver/z3/Z3SolverTest.java
left_side: [{"filePath": "subprojects/solver-z3/src/test/java/hu/bme/mit/theta/solver/z3/Z3SolverTest.java", "startLine": 208, "endLine": 228, "startColumn": 2, "endColumn": 3, "codeElementType": "METHOD_DECLARATION", "description": "source method declaration", "codeElement": "public testBV2() : void"}, {"filePath": "subprojects/solver-z3/src/test/java/hu/bme/mit/theta/solver/z3/Z3SolverTest.java", "startLine": 210, "endLine": 210, "startColumn": 3, "endColumn": 70, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "moved code from source method declaration", "codeElement": null}]
right_side: [{"filePath": "subprojects/solver-z3/src/test/java/hu/bme/mit/theta/solver/z3/Z3SolverTest.java", "startLine": 67, "endLine": 70, "startColumn": 2, "endColumn": 3, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration", "codeElement": "public setup() : void"}, {"filePath": "subprojects/solver-z3/src/test/java/hu/bme/mit/theta/solver/z3/Z3SolverTest.java", "startLine": 69, "endLine": 69, "startColumn": 3, "endColumn": 57, "codeElementType": "EXPRESSION_STATEMENT", "description": "moved code to target method declaration", "codeElement": null}]

### Patch: subprojects/solver-z3/src/test/java/hu/bme/mit/theta/solver/z3/Z3SolverTest.java
```diff
@@ -43,6 +43,7 @@
 import hu.bme.mit.theta.core.utils.BvUtils;
 import hu.bme.mit.theta.solver.Solver;
 import hu.bme.mit.theta.solver.SolverStatus;
+import org.junit.Before;
 import org.junit.Test;
 
 import java.math.BigInteger;
@@ -61,11 +62,15 @@
 import static org.junit.Assert.assertTrue;
 
 public final class Z3SolverTest {
+	private Solver solver;
+
+	@Before
+	public void setup() {
+		solver = Z3SolverFactory.getInstance().createSolver();
+	}
 
 	@Test
 	public void testSimple() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		// Create two integer constants x and y
 		final ConstDecl<IntType> cx = Const("x", Int());
 		final ConstDecl<IntType> cy = Const("y", Int());
@@ -87,8 +92,6 @@ public void testSimple() {
 
 	@Test
 	public void testTrack() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BoolType> ca = Const("a", BoolExprs.Bool());
 		final Expr<BoolType> expr = BoolExprs.And(ca.getRef(), True());
 
@@ -109,7 +112,6 @@ public void testTrack() {
 	@Test
 	public void testFunc() {
 		// Arrange
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
 		final ConstDecl<FuncType<IntType, IntType>> ca = Const("a", Func(Int(), Int()));
 		final Expr<FuncType<IntType, IntType>> a = ca.getRef();
 		final ParamDecl<IntType> px = Param("x", Int());
@@ -131,8 +133,6 @@ public void testFunc() {
 
 	@Test
 	public void testArray() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
         final ConstDecl<ArrayType<IntType, IntType>> arr = Const("arr", Array(Int(), Int()));
 
         solver.add(ArrayExprs.Eq(Write(arr.getRef(), Int(0), Int(1)), arr.getRef()));
@@ -154,8 +154,6 @@ public void testArray() {
 
 	@Test
 	public void testReset() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<IntType> cx = Const("x", Int());
 		final ConstDecl<IntType> cy = Const("y", Int());
 
@@ -178,7 +176,6 @@ public void testReset() {
 
 	@Test(expected = IllegalArgumentException.class)
 	public void testResetStack() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
 		solver.push();
 		solver.push();
 		solver.pop();
@@ -188,8 +185,6 @@ public void testResetStack() {
 
 	@Test
 	public void testBV1() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -207,8 +202,6 @@ public void testBV1() {
 
 	@Test
 	public void testBV2() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cz = Const("z", BvType(4));
 
@@ -229,8 +222,6 @@ public void testBV2() {
 
 	@Test
 	public void testBV3() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -251,8 +242,6 @@ public void testBV3() {
 
 	@Test
 	public void testBV4() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -273,8 +262,6 @@ public void testBV4() {
 
 	@Test
 	public void testBV5() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -295,8 +282,6 @@ public void testBV5() {
 
 	@Test
 	public void testBV6() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -317,8 +302,6 @@ public void testBV6() {
 
 	@Test
 	public void testBV7() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -339,8 +322,6 @@ public void testBV7() {
 
 	@Test
 	public void testBV8() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -361,8 +342,6 @@ public void testBV8() {
 
 	@Test
 	public void testBV9() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -383,8 +362,6 @@ public void testBV9() {
 
 	@Test
 	public void testBV10() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -405,8 +382,6 @@ public void testBV10() {
 
 	@Test
 	public void testBV11() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -427,8 +402,6 @@ public void testBV11() {
 
 	@Test
 	public void testBV12() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
-
 		final ConstDecl<BvType> cx = Const("x", BvType(4));
 		final ConstDecl<BvType> cy = Const("y", BvType(4));
 
@@ -448,7 +421,6 @@ public void testBV12() {
 	}
 
 	public void testBV13() {
-		final Solver solver = Z3SolverFactory.getInstance().createSolver();
 		solver.push();
 
 		solver.add(BvExprs.Eq(uint16ToBvLitExpr(4), BvExprs.Add(List.of(uint16ToBvLitExpr(1), uint16ToBvLitExpr(3)))));
@@ -457,7 +429,6 @@ public void testBV13() {
 		solver.add(BvExprs.Eq(uint16ToBvLitExpr(4), BvExprs.SDiv(uint16ToBvLitExpr(12), uint16ToBvLitExpr(3))));
 		solver.add(BvExprs.Eq(uint16ToBvLitExpr(1), BvExprs.SMod(uint16ToBvLitExpr(13), uint16ToBvLitExpr(3))));
 		solver.add(BvExprs.Eq(uint16ToBvLitExpr(1), BvExprs.SRem(uint16ToBvLitExpr(13), uint16ToBvLitExpr(3))));
-
 	}
 
 	private static BvLitExpr uint16ToBvLitExpr(int value) {
```

## Row 28
commit_url: https://github.com/google/ExoPlayer/commit/9b6c30525ec438ad8bc03e5a6afbff442b2f941a
rm_type: Move Method
rm_description: Move Method public endTracks() : void from class com.google.android.exoplayer.extractor.webm.WebmExtractorTest.TestOutput to public endTracks() : void from class com.google.android.exoplayer.extractor.webm.WebmExtractorTest.TestExtractorOutput
file_path: library/src/test/java/com/google/android/exoplayer/extractor/webm/WebmExtractorTest.java
left_side: [{"filePath": "library/src/test/java/com/google/android/exoplayer/extractor/webm/WebmExtractorTest.java", "startLine": 733, "endLine": 736, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public endTracks() : void"}]
right_side: [{"filePath": "library/src/test/java/com/google/android/exoplayer/extractor/webm/WebmExtractorTest.java", "startLine": 870, "endLine": 873, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "moved method declaration", "codeElement": "public endTracks() : void"}]

### Patch: library/src/test/java/com/google/android/exoplayer/extractor/webm/WebmExtractorTest.java
```diff
@@ -70,64 +70,114 @@ public class WebmExtractorTest extends InstrumentationTestCase {
   private static final int ID_VP9 = 0;
   private static final int ID_OPUS = 1;
   private static final int ID_VORBIS = 2;
+  private static final int ID_DUMMY = 3;
 
   private WebmExtractor extractor;
-  private TestOutput output;
+  private TestExtractorOutput extractorOutput;
+  private TestTrackOutput audioOutput;
+  private TestTrackOutput videoOutput;
 
   @Override
   public void setUp() {
     extractor = new WebmExtractor();
-    output = new TestOutput();
-    extractor.init(output);
+    extractorOutput = new TestExtractorOutput();
+    audioOutput = new TestTrackOutput();
+    videoOutput = new TestTrackOutput();
+    extractor.init(extractorOutput);
   }
 
   @Override
   public void tearDown() {
     extractor = null;
-    output = null;
+    extractorOutput = null;
+    audioOutput = null;
+    videoOutput = null;
   }
 
   public void testReadInitializationSegment() throws IOException, InterruptedException {
-    consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null));
-    assertFormat();
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, null));
+    assertVideoFormat();
     assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
   }
 
   public void testPrepareOpus() throws IOException, InterruptedException {
-    consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_OPUS, null));
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_OPUS}, null));
     assertAudioFormat(ID_OPUS);
     assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
   }
 
   public void testPrepareVorbis() throws IOException, InterruptedException {
-    consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VORBIS, null));
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VORBIS}, null));
+    assertAudioFormat(ID_VORBIS);
+    assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
+  }
+
+  public void testPrepareTwoTracks() throws IOException, InterruptedException {
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9, ID_OPUS}, null));
+    assertEquals(2, extractorOutput.numberOfTracks);
+    assertVideoFormat();
+    assertAudioFormat(ID_OPUS);
+    assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
+  }
+
+  public void testPrepareThreeTracks() throws IOException, InterruptedException {
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9, ID_DUMMY, ID_OPUS}, null));
+    // Eventhough the input stream has 3 tracks, only 2 of them are supported and will be reported.
+    assertEquals(2, extractorOutput.numberOfTracks);
+    assertVideoFormat();
+    assertAudioFormat(ID_OPUS);
+    assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
+  }
+
+  public void testPrepareFourTracks() throws IOException, InterruptedException {
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9, ID_VORBIS, ID_VP9, ID_OPUS}, null));
+    // Eventhough the input stream has 4 supported tracks, only the first video and audio track will
+    // be reported.
+    assertEquals(2, extractorOutput.numberOfTracks);
+    assertVideoFormat();
     assertAudioFormat(ID_VORBIS);
     assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
   }
 
   public void testPrepareContentEncodingEncryption() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 1, 5, 1);
-    consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
-    assertFormat();
+    consume(
+        createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, settings));
+    assertVideoFormat();
     assertIndex(new IndexPoint(0, 0, TEST_DURATION_US));
-    DrmInitData drmInitData = output.drmInitData;
-    assertNotNull(output.drmInitData);
+    DrmInitData drmInitData = extractorOutput.drmInitData;
+    assertNotNull(drmInitData);
     android.test.MoreAsserts.assertEquals(TEST_ENCRYPTION_KEY_ID, drmInitData.get(WIDEVINE_UUID));
     android.test.MoreAsserts.assertEquals(TEST_ENCRYPTION_KEY_ID, drmInitData.get(ZERO_UUID));
   }
 
   public void testPrepareThreeCuePoints() throws IOException, InterruptedException {
-    consume(createInitializationSegment(3, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null));
-    assertFormat();
+    consume(
+        createInitializationSegment(3, 0, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, null));
+    assertVideoFormat();
     assertIndex(
         new IndexPoint(0, 0, 10000),
         new IndexPoint(10000, 0, 10000),
         new IndexPoint(20000, 0, TEST_DURATION_US - 20000));
   }
 
   public void testPrepareCustomTimecodeScale() throws IOException, InterruptedException {
-    consume(createInitializationSegment(3, 0, true, 1000, ID_VP9, null));
-    assertFormat();
+    consume(createInitializationSegment(3, 0, true, 1000, new int[] {ID_VP9}, null));
+    assertVideoFormat();
     assertIndex(
         new IndexPoint(0, 0, 10),
         new IndexPoint(10, 0, 10),
@@ -136,7 +186,9 @@ public void testPrepareCustomTimecodeScale() throws IOException, InterruptedExce
 
   public void testPrepareNoCuePoints() throws IOException, InterruptedException {
     try {
-      consume(createInitializationSegment(0, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null));
+      consume(
+          createInitializationSegment(0, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, null));
       fail();
     } catch (ParserException exception) {
       assertEquals("Invalid/missing cue points", exception.getMessage());
@@ -145,7 +197,9 @@ public void testPrepareNoCuePoints() throws IOException, InterruptedException {
 
   public void testPrepareInvalidDocType() throws IOException, InterruptedException {
     try {
-      consume(createInitializationSegment(1, 0, false, DEFAULT_TIMECODE_SCALE, ID_VP9, null));
+      consume(
+          createInitializationSegment(1, 0, false, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, null));
       fail();
     } catch (ParserException exception) {
       assertEquals("DocType webB not supported", exception.getMessage());
@@ -155,7 +209,9 @@ public void testPrepareInvalidDocType() throws IOException, InterruptedException
   public void testPrepareInvalidContentEncodingOrder() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(1, 1, 1, 5, 1);
     try {
-      consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
+      consume(
+          createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, settings));
       fail();
     } catch (ParserException exception) {
       assertEquals("ContentEncodingOrder 1 not supported", exception.getMessage());
@@ -165,7 +221,9 @@ public void testPrepareInvalidContentEncodingOrder() throws IOException, Interru
   public void testPrepareInvalidContentEncodingScope() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 0, 1, 5, 1);
     try {
-      consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
+      consume(
+          createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, settings));
       fail();
     } catch (ParserException exception) {
       assertEquals("ContentEncodingScope 0 not supported", exception.getMessage());
@@ -175,7 +233,9 @@ public void testPrepareInvalidContentEncodingScope() throws IOException, Interru
   public void testPrepareInvalidContentEncodingType() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 0, 5, 1);
     try {
-      consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
+      consume(
+          createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, settings));
       fail();
     } catch (ParserException exception) {
       assertEquals("ContentEncodingType 0 not supported", exception.getMessage());
@@ -185,7 +245,9 @@ public void testPrepareInvalidContentEncodingType() throws IOException, Interrup
   public void testPrepareInvalidContentEncAlgo() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 1, 4, 1);
     try {
-      consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
+      consume(
+          createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, settings));
       fail();
     } catch (ParserException exception) {
       assertEquals("ContentEncAlgo 4 not supported", exception.getMessage());
@@ -195,54 +257,104 @@ public void testPrepareInvalidContentEncAlgo() throws IOException, InterruptedEx
   public void testPrepareInvalidAESSettingsCipherMode() throws IOException, InterruptedException {
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 1, 5, 0);
     try {
-      consume(createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings));
+      consume(
+          createInitializationSegment(1, 0, true, DEFAULT_TIMECODE_SCALE,
+              new int[] {ID_VP9}, settings));
       fail();
     } catch (ParserException exception) {
       assertEquals("AESSettingsCipherMode 0 not supported", exception.getMessage());
     }
   }
 
   public void testReadSampleKeyframe() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, true, false, false);
+    MediaSegment mediaSegment =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, null),
         mediaSegment.clusterBytes);
     consume(testInputData);
-    assertFormat();
-    assertSample(mediaSegment, 0, true, false, false);
+    assertVideoFormat();
+    assertSample(mediaSegment, 0, true, false, false, videoOutput);
+  }
+
+  public void testReadTwoTrackSamples() throws IOException, InterruptedException {
+    MediaSegment mediaSegmentAudio =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 2);
+    MediaSegment mediaSegmentVideo =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 1);
+    byte[] testInputData = joinByteArrays(
+        createInitializationSegment(
+            1, mediaSegmentAudio.clusterBytes.length + mediaSegmentVideo.clusterBytes.length,
+            true, DEFAULT_TIMECODE_SCALE, new int[] {ID_VP9, ID_OPUS}, null),
+        mediaSegmentVideo.clusterBytes, mediaSegmentAudio.clusterBytes);
+    consume(testInputData);
+    assertEquals(2, extractorOutput.numberOfTracks);
+    assertVideoFormat();
+    assertAudioFormat(ID_OPUS);
+    assertSample(mediaSegmentVideo, 0, true, false, false, videoOutput);
+    assertSample(mediaSegmentAudio, 0, true, false, false, audioOutput);
+  }
+
+  public void testReadTwoTrackSamplesWithSkippedTrack() throws IOException, InterruptedException {
+    MediaSegment mediaSegmentAudio =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 2);
+    MediaSegment mediaSegmentVideo =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 1);
+    MediaSegment mediaSegmentDummy =
+        createMediaSegment(100, 0, 0, true, false, true, false, false, 17);
+    byte[] testInputData = joinByteArrays(
+        createInitializationSegment(
+            1,
+            mediaSegmentAudio.clusterBytes.length + mediaSegmentVideo.clusterBytes.length
+                + mediaSegmentDummy.clusterBytes.length,
+            true, DEFAULT_TIMECODE_SCALE, new int[] {ID_DUMMY, ID_VP9, ID_OPUS}, null),
+        mediaSegmentVideo.clusterBytes,
+        mediaSegmentDummy.clusterBytes,
+        mediaSegmentAudio.clusterBytes);
+    consume(testInputData);
+    assertEquals(2, extractorOutput.numberOfTracks);
+    assertVideoFormat();
+    assertAudioFormat(ID_OPUS);
+    assertSample(mediaSegmentVideo, 0, true, false, false, videoOutput);
+    assertSample(mediaSegmentAudio, 0, true, false, false, audioOutput);
   }
 
   public void testReadBlock() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, false, false, false);
+    MediaSegment mediaSegment =
+        createMediaSegment(100, 0, 0, true, false, false, false, false, 2);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_OPUS, null),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_OPUS}, null),
         mediaSegment.clusterBytes);
     consume(testInputData);
     assertAudioFormat(ID_OPUS);
-    assertSample(mediaSegment, 0, true, false, false);
+    assertSample(mediaSegment, 0, true, false, false, audioOutput);
   }
 
   public void testReadEncryptedFrame() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, true, true, true);
+    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, true, true, true, 1);
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 1, 5, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, settings),
         mediaSegment.clusterBytes);
     consume(testInputData);
-    assertFormat();
-    assertSample(mediaSegment, 0, true, false, true);
+    assertVideoFormat();
+    assertSample(mediaSegment, 0, true, false, true, videoOutput);
   }
 
   public void testReadEncryptedFrameWithInvalidSignalByte()
       throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, true, true, false);
+    MediaSegment mediaSegment = createMediaSegment(100, 0, 0, true, false, true, true, false, 1);
     ContentEncodingSettings settings = new ContentEncodingSettings(0, 1, 1, 5, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_VP9, settings),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, settings),
         mediaSegment.clusterBytes);
     try {
       consume(testInputData);
@@ -253,36 +365,41 @@ public void testReadEncryptedFrameWithInvalidSignalByte()
   }
 
   public void testReadSampleInvisible() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 12, 13, false, true, true, false, false);
+    MediaSegment mediaSegment =
+        createMediaSegment(100, 12, 13, false, true, true, false, false, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, null),
         mediaSegment.clusterBytes);
     consume(testInputData);
-    assertFormat();
-    assertSample(mediaSegment, 25000, false, true, false);
+    assertVideoFormat();
+    assertSample(mediaSegment, 25000, false, true, false, videoOutput);
   }
 
   public void testReadSampleCustomTimescale() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 12, 13, false, false, true, false, false);
+    MediaSegment mediaSegment =
+        createMediaSegment(100, 12, 13, false, false, true, false, false, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, 1000, ID_VP9, null),
+            1, mediaSegment.clusterBytes.length, true, 1000, new int[] {ID_VP9}, null),
         mediaSegment.clusterBytes);
     consume(testInputData);
-    assertFormat();
-    assertSample(mediaSegment, 25, false, false, false);
+    assertVideoFormat();
+    assertSample(mediaSegment, 25, false, false, false, videoOutput);
   }
 
   public void testReadSampleNegativeSimpleBlockTimecode() throws IOException, InterruptedException {
-    MediaSegment mediaSegment = createMediaSegment(100, 13, -12, true, true, true, false, false);
+    MediaSegment mediaSegment =
+        createMediaSegment(100, 13, -12, true, true, true, false, false, 1);
     byte[] testInputData = joinByteArrays(
         createInitializationSegment(
-            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE, ID_VP9, null),
+            1, mediaSegment.clusterBytes.length, true, DEFAULT_TIMECODE_SCALE,
+            new int[] {ID_VP9}, null),
         mediaSegment.clusterBytes);
     consume(testInputData);
-    assertFormat();
-    assertSample(mediaSegment, 1000, true, true, false);
+    assertVideoFormat();
+    assertSample(mediaSegment, 1000, true, true, false, videoOutput);
   }
 
   private void consume(byte[] data) throws IOException, InterruptedException {
@@ -301,15 +418,15 @@ private static ExtractorInput createTestInput(byte[] data) throws IOException {
     return input;
   }
 
-  private void assertFormat() {
-    MediaFormat format = output.format;
+  private void assertVideoFormat() {
+    MediaFormat format = videoOutput.format;
     assertEquals(TEST_WIDTH, format.width);
     assertEquals(TEST_HEIGHT, format.height);
     assertEquals(MimeTypes.VIDEO_VP9, format.mimeType);
   }
 
   private void assertAudioFormat(int codecId) {
-    MediaFormat format = output.format;
+    MediaFormat format = audioOutput.format;
     assertEquals(TEST_CHANNEL_COUNT, format.channelCount);
     assertEquals(TEST_SAMPLE_RATE, format.sampleRate);
     if (codecId == ID_OPUS) {
@@ -327,7 +444,7 @@ private void assertAudioFormat(int codecId) {
   }
 
   private void assertIndex(IndexPoint... indexPoints) {
-    ChunkIndex index = (ChunkIndex) output.seekMap;
+    ChunkIndex index = (ChunkIndex) extractorOutput.seekMap;
     assertEquals(indexPoints.length, index.length);
     for (int i = 0; i < indexPoints.length; i++) {
       IndexPoint indexPoint = indexPoints[i];
@@ -338,8 +455,8 @@ private void assertIndex(IndexPoint... indexPoints) {
   }
 
   private void assertSample(MediaSegment mediaSegment, int timeUs, boolean keyframe,
-      boolean invisible, boolean encrypted) {
-    byte[] expectedOutput = mediaSegment.videoBytes;
+      boolean invisible, boolean encrypted, TestTrackOutput output) {
+    byte[] expectedOutput = mediaSegment.data;
     if (encrypted) {
       expectedOutput = joinByteArrays(new byte[] {(byte) TEST_INITIALIZATION_VECTOR.length},
           TEST_INITIALIZATION_VECTOR, expectedOutput);
@@ -353,24 +470,11 @@ private void assertSample(MediaSegment mediaSegment, int timeUs, boolean keyfram
   }
 
   private byte[] createInitializationSegment(int cuePoints, int mediaSegmentSize,
-      boolean docTypeIsWebm, int timecodeScale, int codecId,
+      boolean docTypeIsWebm, int timecodeScale, int[] codecIds,
       ContentEncodingSettings contentEncodingSettings) {
-    byte[] tracksElement = null;
-    switch (codecId) {
-      case ID_VP9:
-        tracksElement = createTracksElementWithVideo(
-            true, TEST_WIDTH, TEST_HEIGHT, contentEncodingSettings);
-        break;
-      case ID_OPUS:
-        tracksElement = createTracksElementWithOpusAudio(TEST_CHANNEL_COUNT);
-        break;
-      case ID_VORBIS:
-        tracksElement = createTracksElementWithVorbisAudio(TEST_CHANNEL_COUNT);
-        break;
-    }
+    byte[] tracksElement = createTracksElement(codecIds, contentEncodingSettings);
     byte[] infoElement = createInfoElement(timecodeScale);
     byte[] cuesElement = createCuesElement(CUE_POINT_ELEMENT_BYTE_SIZE * cuePoints);
-
     int initalizationSegmentSize = infoElement.length + tracksElement.length
         + cuesElement.length + CUE_POINT_ELEMENT_BYTE_SIZE * cuePoints;
     byte[] segmentElement = createSegmentElement(initalizationSegmentSize + mediaSegmentSize);
@@ -382,20 +486,47 @@ private byte[] createInitializationSegment(int cuePoints, int mediaSegmentSize,
     return bytes;
   }
 
-  private static MediaSegment createMediaSegment(int videoBytesLength, int clusterTimecode,
+  private byte[] createTracksElement(int[] codecIds,
+      ContentEncodingSettings contentEncodingSettings) {
+    byte[] trackBytes = new byte[0];
+    for (int codecId : codecIds) {
+      switch (codecId) {
+        case ID_VP9:
+          trackBytes = joinByteArrays(trackBytes,
+              createVideoTrackEntry(true, TEST_WIDTH, TEST_HEIGHT, contentEncodingSettings));
+          break;
+        case ID_OPUS:
+          trackBytes = joinByteArrays(trackBytes, createOpusAudioTrackEntry(TEST_CHANNEL_COUNT));
+          break;
+        case ID_VORBIS:
+          trackBytes = joinByteArrays(trackBytes, createVorbisAudioTrackEntry(TEST_CHANNEL_COUNT));
+          break;
+        case ID_DUMMY:
+          trackBytes = joinByteArrays(trackBytes, createUnsupportedTrackEntry());
+          break;
+      }
+    }
+    byte[] tracksSize = getIntegerBytes(trackBytes.length);
+    byte[] tracksHeader = createByteArray(
+        0x16, 0x54, 0xAE, 0x6B, // Tracks
+        0x01, 0x00, 0x00, 0x00, tracksSize[0], tracksSize[1], tracksSize[2], tracksSize[3]);
+    return joinByteArrays(tracksHeader, trackBytes);
+  }
+
+  private static MediaSegment createMediaSegment(int dataLength, int clusterTimecode,
       int blockTimecode, boolean keyframe, boolean invisible, boolean simple,
-      boolean encrypted, boolean validSignalByte) {
-    byte[] videoBytes = createVideoBytes(videoBytesLength);
+      boolean encrypted, boolean validSignalByte, int trackNumber) {
+    byte[] data = createFrameData(dataLength);
     byte[] blockBytes;
     if (simple) {
-      blockBytes = createSimpleBlockElement(videoBytes.length, blockTimecode,
-          keyframe, invisible, true, encrypted, validSignalByte);
+      blockBytes = createSimpleBlockElement(data.length, blockTimecode,
+          keyframe, invisible, true, encrypted, validSignalByte, trackNumber);
     } else {
-      blockBytes = createBlockElement(videoBytes.length, blockTimecode, invisible, true);
+      blockBytes = createBlockElement(data.length, blockTimecode, invisible, true, trackNumber);
     }
     byte[] clusterBytes =
-        createClusterElement(blockBytes.length + videoBytes.length, clusterTimecode);
-    return new MediaSegment(joinByteArrays(clusterBytes, blockBytes, videoBytes), videoBytes);
+        createClusterElement(blockBytes.length + data.length, clusterTimecode);
+    return new MediaSegment(joinByteArrays(clusterBytes, blockBytes, data), data);
   }
 
   private static byte[] joinByteArrays(byte[]... byteArrays) {
@@ -443,7 +574,7 @@ private static byte[] createInfoElement(int timecodeScale) {
         0x88, 0x40, 0xC3, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00); // size=8 value=9920.0
   }
 
-  private static byte[] createTracksElementWithVideo(
+  private static byte[] createVideoTrackEntry(
       boolean codecIsVp9, int pixelWidth, int pixelHeight,
       ContentEncodingSettings contentEncodingSettings) {
     byte[] widthBytes = getIntegerBytes(pixelWidth);
@@ -455,8 +586,6 @@ private static byte[] createTracksElementWithVideo(
       byte[] algorithmBytes = getIntegerBytes(contentEncodingSettings.algorithm);
       byte[] cipherModeBytes = getIntegerBytes(contentEncodingSettings.aesCipherMode);
       return createByteArray(
-          0x16, 0x54, 0xAE, 0x6B, // Tracks
-          0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4E, // size=78
           0xAE, // TrackEntry
           0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x45, // size=69
           0x86, // CodecID
@@ -495,10 +624,8 @@ private static byte[] createTracksElementWithVideo(
           0x82, heightBytes[2], heightBytes[3]); // size=2
     } else {
       return createByteArray(
-          0x16, 0x54, 0xAE, 0x6B, // Tracks
-          0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2A, // size=42
           0xAE, // TrackEntry
-          0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x21, // size=33
+          0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1E, // size=30
           0x86, // CodecID
           0x85, 0x56, 0x5F, 0x56, 0x50, codecIsVp9 ? 0x39 : 0x30, // size=5 value=V_VP9/0
           0xD7, // TrackNumber
@@ -514,17 +641,15 @@ private static byte[] createTracksElementWithVideo(
     }
   }
 
-  private static byte[] createTracksElementWithOpusAudio(int channelCount) {
+  private static byte[] createOpusAudioTrackEntry(int channelCount) {
     byte[] channelCountBytes = getIntegerBytes(channelCount);
     return createByteArray(
-        0x16, 0x54, 0xAE, 0x6B, // Tracks
-        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3F, // size=63
         0xAE, // TrackEntry
         0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x36, // size=54
         0x86, // CodecID
         0x86, 0x41, 0x5F, 0x4F, 0x50, 0x55, 0x53, // size=6 value=A_OPUS
         0xD7, // TrackNumber
-        0x81, 0x01, // size=1 value=1
+        0x81, 0x02, // size=1 value=2
         0x83, // TrackType
         0x81, 0x02, // size=1 value=2
         0x56, 0xAA, // CodecDelay
@@ -541,17 +666,15 @@ private static byte[] createTracksElementWithOpusAudio(int channelCount) {
         0x82, 0x00, 0x00); // size=2
   }
 
-  private byte[] createTracksElementWithVorbisAudio(int channelCount) {
+  private byte[] createVorbisAudioTrackEntry(int channelCount) {
     byte[] channelCountBytes = getIntegerBytes(channelCount);
     byte[] tracksElement = createByteArray(
-        0x16, 0x54, 0xAE, 0x6B, // Tracks
-        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0xA2, // size=4258
         0xAE, // TrackEntry
         0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x99, // size=4249 (42+4207)
         0x86, // CodecID
         0x88, 0x41, 0x5f, 0x56, 0x4f, 0x52, 0x42, 0x49, 0x53, // size=8 value=A_VORBIS
         0xD7, // TrackNumber
-        0x81, 0x01, // size=1 value=1
+        0x81, 0x02, // size=1 value=2
         0x83, // TrackType
         0x81, 0x02, // size=1 value=2
         0xE1, // Audio
@@ -572,6 +695,20 @@ private byte[] createTracksElementWithVorbisAudio(int channelCount) {
     return joinByteArrays(tracksElement, codecPrivate);
   }
 
+  private static byte[] createUnsupportedTrackEntry() {
+    return createByteArray(
+        0xAE, // TrackEntry
+        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, // size=32
+        0x86, // CodecID
+        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, // size =17
+        0x44, 0x5f, 0x57, 0x45, 0x42, 0x56, 0x54, 0x54,
+        0x2f, 0x6d, 0x65, 0x74, 0x61, 0x64, 0x61, 0x74, 0x61, // value=D_WEBVTT/metadata
+        0xD7, // TrackNumber
+        0x81, 0x03, // size=1 value=3
+        0x83, // TrackType
+        0x81, 0x11); // size=1 value=11
+  }
+
   private static byte[] createCuesElement(int size) {
     byte[] sizeBytes = getIntegerBytes(size);
     return createByteArray(
@@ -605,15 +742,16 @@ private static byte[] createClusterElement(int size, int timecode) {
 
   private static byte[] createSimpleBlockElement(
       int size, int timecode, boolean keyframe, boolean invisible, boolean noLacing,
-      boolean encrypted, boolean validSignalByte) {
-    byte[] sizeBytes = getIntegerBytes(size + 4 + (encrypted ? 9 : 0));
+      boolean encrypted, boolean validSignalByte, int trackNumber) {
+    byte[] sizeBytes = getIntegerBytes(size + 5 + (encrypted ? 9 : 0));
     byte[] timeBytes = getIntegerBytes(timecode);
+    byte[] trackNumberBytes = getIntegerBytes(trackNumber);
     byte flags = (byte)
         ((keyframe ? 0x80 : 0x00) | (invisible ? 0x08 : 0x00) | (noLacing ? 0x00 : 0x06));
     byte[] simpleBlock = createByteArray(
         0xA3, // SimpleBlock
         0x01, 0x00, 0x00, 0x00, sizeBytes[0], sizeBytes[1], sizeBytes[2], sizeBytes[3],
-        0x81, // Track number value=1
+        0x40, trackNumberBytes[3], // Track number size=2
         timeBytes[2], timeBytes[3], flags); // Timecode and flags
     if (encrypted) {
       simpleBlock = joinByteArrays(
@@ -624,10 +762,11 @@ simpleBlock, createByteArray(validSignalByte ? 0x01 : 0x80),
   }
 
   private static byte[] createBlockElement(
-      int size, int timecode, boolean invisible, boolean noLacing) {
-    int blockSize = size + 4;
+      int size, int timecode, boolean invisible, boolean noLacing, int trackNumber) {
+    int blockSize = size + 5;
     byte[] blockSizeBytes = getIntegerBytes(blockSize);
     byte[] timeBytes = getIntegerBytes(timecode);
+    byte[] trackNumberBytes = getIntegerBytes(trackNumber);
     int blockElementSize = 1 + 8 + blockSize; // id + size + length of data
     byte[] sizeBytes = getIntegerBytes(blockElementSize);
     byte flags = (byte) ((invisible ? 0x08 : 0x00) | (noLacing ? 0x00 : 0x06));
@@ -637,16 +776,16 @@ private static byte[] createBlockElement(
         0xA1, // Block
         0x01, 0x00, 0x00, 0x00,
         blockSizeBytes[0], blockSizeBytes[1], blockSizeBytes[2], blockSizeBytes[3],
-        0x81, // Track number value=1
+        0x40, trackNumberBytes[3], // Track number size=2
         timeBytes[2], timeBytes[3], flags); // Timecode and flags
   }
 
-  private static byte[] createVideoBytes(int size) {
-    byte[] videoBytes = new byte[size];
+  private static byte[] createFrameData(int size) {
+    byte[] data = new byte[size];
     for (int i = 0; i < size; i++) {
-      videoBytes[i] = (byte) i;
+      data[i] = (byte) i;
     }
-    return videoBytes;
+    return data;
   }
 
   private static byte[] getIntegerBytes(int value) {
@@ -669,11 +808,11 @@ private static byte[] createByteArray(int... intArray) {
   private static final class MediaSegment {
 
     private final byte[] clusterBytes;
-    private final byte[] videoBytes;
+    private final byte[] data;
 
-    private MediaSegment(byte[] clusterBytes, byte[] videoBytes) {
+    private MediaSegment(byte[] clusterBytes, byte[] data) {
       this.clusterBytes = clusterBytes;
-      this.videoBytes = videoBytes;
+      this.data = data;
     }
 
   }
@@ -713,21 +852,19 @@ private ContentEncodingSettings(int order, int scope, int type, int algorithm,
 
   }
 
-  /** Implements {@link ExtractorOutput} and {@link TrackOutput} for test purposes. */
-  public static class TestOutput implements ExtractorOutput, TrackOutput {
+  /** Implements {@link ExtractorOutput} for test purposes. */
+  public class TestExtractorOutput implements ExtractorOutput {
 
     public boolean tracksEnded;
     public SeekMap seekMap;
     public DrmInitData drmInitData;
-
-    public MediaFormat format;
-    private long sampleTimeUs;
-    private int sampleFlags;
-    private byte[] sampleData;
+    public int numberOfTracks;
 
     @Override
     public TrackOutput track(int trackId) {
-      return this;
+      numberOfTracks++;
+      // In the test samples, track number 1 is always video and track number 2 is always audio.
+      return (trackId == 1) ? videoOutput : audioOutput;
     }
 
     @Override
@@ -745,6 +882,16 @@ public void drmInitData(DrmInitData drmInitData) {
       this.drmInitData = drmInitData;
     }
 
+  }
+
+  /** Implements {@link TrackOutput} for test purposes. */
+  public static class TestTrackOutput implements TrackOutput {
+
+    public MediaFormat format;
+    private long sampleTimeUs;
+    private int sampleFlags;
+    private byte[] sampleData;
+
     @Override
     public void format(MediaFormat format) {
       this.format = format;
```

## Row 29
commit_url: https://github.com/NitorCreations/nflow/commit/39a2a85f995c83c658c173898783217be849bf86
rm_type: Extract And Move Method
rm_description: Extract And Move Method protected getInstanceResource() : WebClient extracted from public queryDemoWorkflowWithMultipleStatuses() : void in class io.nflow.tests.DemoWorkflowTest & moved to class io.nflow.tests.AbstractNflowTest
file_path: nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java; nflow-tests/src/test/java/io/nflow/tests/DemoWorkflowTest.java
left_side: [{"filePath": "nflow-tests/src/test/java/io/nflow/tests/DemoWorkflowTest.java", "startLine": 82, "endLine": 88, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "source method declaration before extraction", "codeElement": "public queryDemoWorkflowWithMultipleStatuses() : void"}, {"filePath": "nflow-tests/src/test/java/io/nflow/tests/DemoWorkflowTest.java", "startLine": 85, "endLine": 86, "startColumn": 5, "endColumn": 106, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "extracted code from source method declaration", "codeElement": null}]
right_side: [{"filePath": "nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java", "startLine": 112, "endLine": 114, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "protected getInstanceResource() : WebClient"}, {"filePath": "nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java", "startLine": 113, "endLine": 113, "startColumn": 5, "endColumn": 55, "codeElementType": "RETURN_STATEMENT", "description": "extracted code to extracted method declaration", "codeElement": null}, {"filePath": "nflow-tests/src/test/java/io/nflow/tests/DemoWorkflowTest.java", "startLine": 81, "endLine": 87, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "source method declaration after extraction", "codeElement": "public queryDemoWorkflowWithMultipleStatuses() : void"}, {"filePath": "nflow-tests/src/test/java/io/nflow/tests/DemoWorkflowTest.java", "startLine": 84, "endLine": 84, "startColumn": 48, "endColumn": 69, "codeElementType": "METHOD_INVOCATION", "description": "extracted method invocation", "codeElement": "getInstanceResource()"}]

### Patch: nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java
```diff
@@ -49,11 +49,11 @@
 @ExtendWith({ NflowServerExtension.class, SpringExtension.class, SkipTestMethodsAfterFirstFailureExtension.class })
 @ContextConfiguration(classes = { RestClientConfiguration.class, PropertiesConfiguration.class })
 public abstract class AbstractNflowTest {
-  protected WebClient workflowInstanceResource;
-  protected WebClient workflowInstanceIdResource;
-  protected WebClient workflowDefinitionResource;
-  protected WebClient statisticsResource;
-  protected WebClient maintenanceResource;
+  private WebClient workflowInstanceResource;
+  private WebClient workflowInstanceIdResource;
+  private WebClient workflowDefinitionResource;
+  private WebClient statisticsResource;
+  private WebClient maintenanceResource;
 
   private final NflowServerConfig server;
 
@@ -109,24 +109,24 @@ protected SetSignalResponse setSignal(long instanceId, int signal, String reason
     return getInstanceResource(instanceId).path("signal").put(request, SetSignalResponse.class);
   }
 
-  private WebClient getInstanceResource(long instanceId) {
-    WebClient client = fromClient(workflowInstanceResource, true).path(Long.toString(instanceId));
-    return client;
+  protected WebClient getInstanceResource() {
+    return fromClient(workflowInstanceResource, true);
+  }
+
+  protected WebClient getInstanceResource(long instanceId) {
+    return getInstanceResource().path(Long.toString(instanceId));
   }
 
   protected WebClient getInstanceIdResource(long instanceId) {
-    WebClient client = fromClient(workflowInstanceIdResource, true).path(Long.toString(instanceId));
-    return client;
+    return fromClient(workflowInstanceIdResource, true).path(Long.toString(instanceId));
   }
 
   protected ListWorkflowDefinitionResponse[] getWorkflowDefinitions() {
-    WebClient client = fromClient(workflowDefinitionResource, true);
-    return client.get(ListWorkflowDefinitionResponse[].class);
+    return fromClient(workflowDefinitionResource, true).get(ListWorkflowDefinitionResponse[].class);
   }
 
   public StatisticsResponse getStatistics() {
-    WebClient client = fromClient(statisticsResource, true);
-    return client.get(StatisticsResponse.class);
+    return fromClient(statisticsResource, true).get(StatisticsResponse.class);
   }
 
   public WorkflowDefinitionStatisticsResponse getDefinitionStatistics(String definitionType) {
@@ -173,7 +173,7 @@ public void validate(ListWorkflowInstanceResponse workflowInstance) {
   }
 
   protected CreateWorkflowInstanceResponse createWorkflowInstance(CreateWorkflowInstanceRequest request) {
-    return makeWorkflowInstanceQuery(request, CreateWorkflowInstanceResponse.class);
+    return fromClient(workflowInstanceResource, true).put(request, CreateWorkflowInstanceResponse.class);
   }
 
   protected ObjectMapper nflowObjectMapper() {
@@ -183,33 +183,21 @@ protected ObjectMapper nflowObjectMapper() {
     return mapper;
   }
 
-  protected MaintenanceResponse archiveAllFinishedWorkflows() {
-    MaintenanceRequest req = new MaintenanceRequest();
-    req.archiveWorkflows = new MaintenanceRequestItem();
-    req.archiveWorkflows.olderThanPeriod = seconds(0);
-    return assertTimeoutPreemptively(ofSeconds(15),
-        () -> fromClient(maintenanceResource).type(APPLICATION_JSON_TYPE).post(req, MaintenanceResponse.class));
-  }
-
   protected MaintenanceResponse deleteAllFinishedWorkflows() {
     MaintenanceRequest req = new MaintenanceRequest();
     req.deleteWorkflows = new MaintenanceRequestItem();
     req.deleteWorkflows.olderThanPeriod = seconds(0);
     req.deleteArchivedWorkflows = req.deleteWorkflows;
-    return assertTimeoutPreemptively(ofSeconds(15),
-        () -> fromClient(maintenanceResource).type(APPLICATION_JSON_TYPE).post(req, MaintenanceResponse.class));
-  }
-
-  protected long insertWorkflow(CreateWorkflowInstanceRequest req) {
-    return fromClient(workflowInstanceResource, true).put(req, CreateWorkflowInstanceResponse.class).id;
+    return doMaintenance(req);
   }
 
-  protected String updateWorkflowInstance(long instanceId, UpdateWorkflowInstanceRequest request) {
-    return getInstanceIdResource(instanceId).put(request, String.class);
+  protected MaintenanceResponse doMaintenance(MaintenanceRequest req) {
+    return assertTimeoutPreemptively(ofSeconds(15),
+        () -> fromClient(maintenanceResource).type(APPLICATION_JSON_TYPE).post(req, MaintenanceResponse.class));
   }
 
-  private <T> T makeWorkflowInstanceQuery(CreateWorkflowInstanceRequest request, Class<T> responseClass) {
-    return fromClient(workflowInstanceResource, true).put(request, responseClass);
+  protected <T> T updateWorkflowInstance(long instanceId, UpdateWorkflowInstanceRequest request, Class<T> responseClass) {
+    return getInstanceIdResource(instanceId).put(request, responseClass);
   }
 
   public interface WorkflowInstanceValidator {
```
### Patch: nflow-tests/src/test/java/io/nflow/tests/DemoWorkflowTest.java
```diff
@@ -5,7 +5,6 @@
 import static javax.ws.rs.core.MediaType.APPLICATION_JSON_TYPE;
 import static javax.ws.rs.core.Response.Status.NOT_FOUND;
 import static javax.ws.rs.core.Response.Status.NO_CONTENT;
-import static org.apache.cxf.jaxrs.client.WebClient.fromClient;
 import static org.hamcrest.MatcherAssert.assertThat;
 import static org.hamcrest.Matchers.empty;
 import static org.hamcrest.Matchers.greaterThanOrEqualTo;
@@ -53,7 +52,7 @@ public void startDemoWorkflow() {
     CreateWorkflowInstanceRequest req = new CreateWorkflowInstanceRequest();
     req.type = "demo";
     req.businessKey = "1";
-    resp = fromClient(workflowInstanceResource, true).put(req, CreateWorkflowInstanceResponse.class);
+    resp = createWorkflowInstance(req);
     assertThat(resp.id, notNullValue());
   }
 
@@ -64,8 +63,8 @@ public void queryDemoWorkflowHistory() {
       ListWorkflowInstanceResponse wf = null;
       do {
         sleep(200);
-        ListWorkflowInstanceResponse[] instances = fromClient(workflowInstanceResource, true).query("type", "demo")
-            .query("include", "actions").get(ListWorkflowInstanceResponse[].class);
+        ListWorkflowInstanceResponse[] instances = getInstanceResource().query("type", "demo").query("include", "actions")
+            .get(ListWorkflowInstanceResponse[].class);
         assertThat(instances.length, greaterThanOrEqualTo(1));
         for (ListWorkflowInstanceResponse instance : instances) {
           if (instance.id == resp.id && "done".equals(instance.state) && instance.nextActivation == null) {
@@ -82,8 +81,8 @@ public void queryDemoWorkflowHistory() {
   @Test
   @Order(3)
   public void queryDemoWorkflowWithMultipleStatuses() {
-    ListWorkflowInstanceResponse[] instances = fromClient(workflowInstanceResource, true).query("type", "demo")
-        .query("status", "finished").query("status", "manual").get(ListWorkflowInstanceResponse[].class);
+    ListWorkflowInstanceResponse[] instances = getInstanceResource().query("type", "demo").query("status", "finished")
+        .query("status", "manual").get(ListWorkflowInstanceResponse[].class);
     assertThat(instances.length, greaterThanOrEqualTo(1));
   }
 
@@ -103,8 +102,7 @@ public void queryWorkflowWithActionsReturnsEmptyActions() {
   @Test
   @Order(5)
   public void queryWorkflowWithoutActionsReturnsNullActions() {
-    ListWorkflowInstanceResponse instance = fromClient(workflowInstanceIdResource, true).path(Long.toString(resp.id))
-        .get(ListWorkflowInstanceResponse.class);
+    ListWorkflowInstanceResponse instance = getInstanceIdResource(resp.id).get(ListWorkflowInstanceResponse.class);
 
     assertThat(instance.actions, is(nullValue()));
   }
@@ -115,7 +113,7 @@ public void updateWorkflowReturnsNoContentWhenInstanceIsUpdated() {
     UpdateWorkflowInstanceRequest req = new UpdateWorkflowInstanceRequest();
     req.nextActivationTime = now().plusDays(1);
 
-    try (Response response = getInstanceIdResource(resp.id).put(req)) {
+    try (Response response = updateWorkflowInstance(resp.id, req, Response.class)) {
       assertThat(response.getStatus(), is(NO_CONTENT.getStatusCode()));
       assertThat(response.readEntity(String.class), is(""));
     }
@@ -127,7 +125,7 @@ public void updateWorkflowReturnsNotFoundWhenInstanceIsNotFound() {
     UpdateWorkflowInstanceRequest req = new UpdateWorkflowInstanceRequest();
     req.nextActivationTime = now().plusDays(2);
 
-    try (Response response = getInstanceIdResource(-1).put(req)) {
+    try (Response response = updateWorkflowInstance(-1, req, Response.class)) {
       assertThat(response.getStatus(), is(NOT_FOUND.getStatusCode()));
       assertThat(response.getMediaType(), is(APPLICATION_JSON_TYPE));
       assertThat(response.readEntity(ErrorResponse.class).error, is("Workflow instance -1 not found"));
```

## Row 30
commit_url: https://github.com/virtualsatellite/VirtualSatellite4-Core/commit/730abe93f6b064e8a9998a9324f3ccdfda869c01
rm_type: Inline Method
rm_description: Inline Method private generateRandomTreeWithReferences(n int) : void inlined to public testSaveAndLoad() : void in class de.dlr.sc.virsat.performance.PerformanceTest
file_path: de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java
left_side: [{"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 297, "endLine": 324, "startColumn": 2, "endColumn": 3, "codeElementType": "METHOD_DECLARATION", "description": "inlined method declaration", "codeElement": "private generateRandomTreeWithReferences(n int) : void"}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 304, "endLine": 304, "startColumn": 3, "endColumn": 60, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "inlined code from inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 305, "endLine": 305, "startColumn": 3, "endColumn": 66, "codeElementType": "EXPRESSION_STATEMENT", "description": "inlined code from inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 319, "endLine": 319, "startColumn": 4, "endColumn": 39, "codeElementType": "EXPRESSION_STATEMENT", "description": "inlined code from inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 306, "endLine": 306, "startColumn": 3, "endColumn": 17, "codeElementType": "EXPRESSION_STATEMENT", "description": "inlined code from inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 310, "endLine": 323, "startColumn": 35, "endColumn": 4, "codeElementType": "BLOCK", "description": "inlined code from inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 163, "endLine": 185, "startColumn": 2, "endColumn": 3, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration before inline", "codeElement": "public testSaveAndLoad() : void"}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 167, "endLine": 167, "startColumn": 3, "endColumn": 57, "codeElementType": "METHOD_INVOCATION", "description": "inlined method invocation", "codeElement": "generateRandomTreeWithReferences(testNumberOfElements)"}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 303, "endLine": 303, "startColumn": 3, "endColumn": 49, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 307, "endLine": 307, "startColumn": 3, "endColumn": 29, "codeElementType": "EXPRESSION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 308, "endLine": 308, "startColumn": 3, "endColumn": 63, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 309, "endLine": 309, "startColumn": 3, "endColumn": 25, "codeElementType": "EXPRESSION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 311, "endLine": 311, "startColumn": 4, "endColumn": 70, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 312, "endLine": 312, "startColumn": 4, "endColumn": 108, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 313, "endLine": 313, "startColumn": 4, "endColumn": 27, "codeElementType": "EXPRESSION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 315, "endLine": 315, "startColumn": 4, "endColumn": 113, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 316, "endLine": 316, "startColumn": 4, "endColumn": 86, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 317, "endLine": 317, "startColumn": 4, "endColumn": 44, "codeElementType": "EXPRESSION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 318, "endLine": 318, "startColumn": 4, "endColumn": 67, "codeElementType": "EXPRESSION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 320, "endLine": 320, "startColumn": 4, "endColumn": 24, "codeElementType": "EXPRESSION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 322, "endLine": 322, "startColumn": 4, "endColumn": 32, "codeElementType": "EXPRESSION_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 310, "endLine": 323, "startColumn": 3, "endColumn": 4, "codeElementType": "FOR_STATEMENT", "description": "deleted statement in inlined method declaration", "codeElement": null}]
right_side: [{"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 140, "endLine": 177, "startColumn": 2, "endColumn": 3, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration after inline", "codeElement": "public testSaveAndLoad() : void"}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 151, "endLine": 151, "startColumn": 5, "endColumn": 62, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "inlined code in target method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 152, "endLine": 152, "startColumn": 5, "endColumn": 68, "codeElementType": "EXPRESSION_STATEMENT", "description": "inlined code in target method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 153, "endLine": 153, "startColumn": 5, "endColumn": 83, "codeElementType": "EXPRESSION_STATEMENT", "description": "inlined code in target method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 155, "endLine": 155, "startColumn": 5, "endColumn": 18, "codeElementType": "EXPRESSION_STATEMENT", "description": "inlined code in target method declaration", "codeElement": null}, {"filePath": "de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java", "startLine": 148, "endLine": 157, "startColumn": 65, "endColumn": 5, "codeElementType": "BLOCK", "description": "inlined code in target method declaration", "codeElement": null}]

### Patch: de.dlr.sc.virsat.performance.test/src/de/dlr/sc/virsat/performance/PerformanceTest.java
```diff
@@ -26,7 +26,6 @@
 import org.eclipse.core.runtime.CoreException;
 import org.eclipse.emf.common.util.EList;
 import org.junit.AfterClass;
-import org.junit.Before;
 import org.junit.BeforeClass;
 import org.junit.Test;
 import org.junit.runner.RunWith;
@@ -36,6 +35,7 @@
 
 import de.dlr.sc.virsat.apps.api.external.ModelAPI;
 import de.dlr.sc.virsat.concept.unittest.util.test.AConceptProjectTestCase;
+import de.dlr.sc.virsat.model.concept.types.structural.IBeanStructuralElementInstance;
 import de.dlr.sc.virsat.model.dvlm.categories.CategoryAssignment;
 import de.dlr.sc.virsat.model.dvlm.concepts.Concept;
 import de.dlr.sc.virsat.model.dvlm.structural.StructuralElementInstance;
@@ -51,7 +51,21 @@ public class PerformanceTest extends AConceptProjectTestCase {
     public static final int MIN_STUDY_SIZE = 200;
     public static final int MAX_STUDY_SIZE = 10000;
     public static final int STUDY_SIZE_INCREASE_STEP = 200;
-    
+
+	protected ModelAPI modelAPI;
+	protected Concept testConcept;
+
+    /**
+	 * (Study size -> (Measure -> Elapsed Time))
+     */
+    protected static Map<Integer, Map<String, Long>> performanceMeasures;
+
+	/**
+	 * For injecting parameters of a parameterized test
+	 */
+	@Parameter
+	public int testNumberOfElements;
+
     /**
      * Collection of study sizes for parameterized test. These values will be injected into field testNumberOfElements
      * @return collection of arrays of size one containing study sizes
@@ -65,20 +79,7 @@ public static Collection<Object[]> data() {
         return studySizes;
     }
 
-	/*
-	 * (Study size -> (Measure -> Elapsed Time))
-	 */
-	private static Map<Integer, Map<String, Long>> performanceMeasures;
-	
-	private ModelAPI modelAPI;
-	private Concept testConcept;
-
 	@Override
-	public void initializeTimeOutRule() {
-		// No timeout
-	}
-	
-	@Before
 	public void setUp() throws CoreException {
 		super.setUp();
 		addEditingDomainAndRepository();
@@ -96,45 +97,29 @@ public String getCurrentProjectAbsolutePath() {
 		};
 	}
 
-	/**
-	 * method to create new structural element
-	 * @param name name of the structural element
-	 * @return structural element
-	 * @throws IOException 
-	 */
-	public TestStructuralElement createSE(String name) throws IOException {
-		TestStructuralElement se = new TestStructuralElement(testConcept);
-		se.setName(name);
-		modelAPI.createSeiStorage(se);
-		return se;
+	@Override
+	public void initializeTimeOutRule() {
+		// No timeout
 	}
 
-	@Parameter
-	//CHECKSTYLE:OFF
-	// For injecting parameters of a parameterized test
-	public int testNumberOfElements;
-	//CHECKSTYLE:ON
-	
 	/**
-	 * Before the tests are executed prepare a storage for timing of all tests
+	 * Prepare storage for timing results of all tests
 	 */
 	@BeforeClass
 	public static void init() {
 		performanceMeasures = new LinkedHashMap<>();
 	}
 	
 	/**
-	 * Logs a performance measurement result
+	 * After the tests are executed write the test timings into a file
+	 * @throws IOException 
 	 */
-	private void logTime(String measure, long value) {
-		if (!performanceMeasures.containsKey(testNumberOfElements)) {
-			performanceMeasures.put(testNumberOfElements, new LinkedHashMap<>());
-		}
-		assertFalse("No duplicate measures", performanceMeasures.get(testNumberOfElements).containsKey(measure));
-		performanceMeasures.get(testNumberOfElements).put(measure, value);
+	@AfterClass
+	public static void end() throws IOException {
+		Files.write(Paths.get("performanceTestReport.csv"), getPerformanceReportCsv());
 	}
 
-	private static List<String> getPerformanceReportCsv() {
+	protected static List<String> getPerformanceReportCsv() {
 		List<String> result = new ArrayList<>();
 		List<String> measures = new ArrayList<>(performanceMeasures.get(MIN_STUDY_SIZE).keySet());
 		String header = "Number of elements," + String.join(",", measures);
@@ -151,20 +136,27 @@ private static List<String> getPerformanceReportCsv() {
 		return result;
 	}
 
-	/**
-	 * After the tests are executed write the test timings into a file
-	 * @throws IOException 
-	 */
-	@AfterClass
-	public static void end() throws IOException {
-		Files.write(Paths.get("performanceTestReport.csv"), getPerformanceReportCsv());
-	}
-	
+
 	@Test
 	public final void testSaveAndLoad() throws CoreException, IOException {
 		long start = System.currentTimeMillis();
-		
-		generateRandomTreeWithReferences(testNumberOfElements);
+
+		// Add a category with random values to all SEIs
+		new StudyGenerator() {
+			
+			@Override
+			public IBeanStructuralElementInstance createSei(String name) {
+				IBeanStructuralElementInstance sei = super.createSei(name);
+
+				TestCategoryBase cat = new TestCategoryBase(testConcept);
+				cat.setTestBaseProperty(ThreadLocalRandom.current().nextInt());
+				cat.setTestReference(getRandomPreviousSei().getFirst(TestCategoryBase.class));
+
+				sei.add(cat);
+				return sei;
+			}
+		}
+		.generate();
 		
 		long timestampCreated = System.currentTimeMillis();
 		modelAPI.performInheritance();
@@ -186,7 +178,29 @@ public final void testSaveAndLoad() throws CoreException, IOException {
 
 	@Test
 	public final void testInheritance() throws CoreException, IOException {
-		generateRandomTreeWithInheritance(testNumberOfElements);
+
+		// Add random inheritance to the generated SEIs, and a CA only to the root SEI
+		new StudyGenerator() {
+			
+			public IBeanStructuralElementInstance createRootSei(String name) {
+				IBeanStructuralElementInstance sei = super.createSei(name);
+
+				TestCategoryBase cat = new TestCategoryBase(testConcept);
+				cat.setTestBaseProperty(ThreadLocalRandom.current().nextInt());
+				cat.setTestReference((TestCategoryBase) getRandomPreviousSei());
+				sei.add(cat);
+
+				return sei;
+			};
+			
+			public IBeanStructuralElementInstance createSei(String name) {
+				IBeanStructuralElementInstance sei = super.createSei(name);
+				IBeanStructuralElementInstance superSei = getRandomPreviousSei();
+				sei.addSuperSei(superSei);
+				return sei;
+			}
+		}
+		.generate();
 		
 		long timestampCreated = System.currentTimeMillis();
 		modelAPI.performInheritance();
@@ -212,44 +226,57 @@ public final void testInheritance() throws CoreException, IOException {
 		logTime("Reload With Inheritance", timestampAllLoaded - timestampAllSaved);
 	}
 	
+		
 	/**
-	 * Make sure that after changing random inheritance parameters some values are different
-	 * from root super SEI value
+	 * Logs a performance measurement result
 	 */
-	private void assertNotAllSeisHaveSameInheritedValue() {
+	private void logTime(String measure, long value) {
+		if (!performanceMeasures.containsKey(testNumberOfElements)) {
+			performanceMeasures.put(testNumberOfElements, new LinkedHashMap<>());
+		}
+		assertFalse("No duplicate measures", performanceMeasures.get(testNumberOfElements).containsKey(measure));
+		performanceMeasures.get(testNumberOfElements).put(measure, value);
+	}
+	
+
+	/**
+	 * Make sure that all SEIs have inherited the same value from root super SEI
+	 */
+	private void assertAllSeisHaveSameInheritedValue() {
 		TestStructuralElement rootSei = modelAPI.getRootSeis(TestStructuralElement.class).get(0);
 		TestCategoryBase rootCat = rootSei.getAll(TestCategoryBase.class).get(0);
 		long rootValue = rootCat.getTestBaseProperty();
 		EList<StructuralElementInstance> allInherited = rootSei.getStructuralElementInstance().getDeepChildren();
 		assertEquals(testNumberOfElements - 1, allInherited.size());
-		boolean differentValue = false;
 		for (StructuralElementInstance sei : allInherited) {
 			assertEquals(1, sei.getCategoryAssignments().size());
 			CategoryAssignment ca = sei.getCategoryAssignments().get(0);
 			TestCategoryBase caBean = new TestCategoryBase(ca);
-			if (rootValue != caBean.getTestBaseProperty()) {
-				differentValue = true;
-				break;
-			}
+			assertEquals(rootValue, caBean.getTestBaseProperty());
 		}
-		assertTrue(differentValue);
 	}
 
 	/**
-	 * Make sure that all SEIs have inherited the same value from root super SEI
+	 * Make sure that after changing random inheritance parameters some values are different
+	 * from root super SEI value
 	 */
-	private void assertAllSeisHaveSameInheritedValue() {
+	private void assertNotAllSeisHaveSameInheritedValue() {
 		TestStructuralElement rootSei = modelAPI.getRootSeis(TestStructuralElement.class).get(0);
 		TestCategoryBase rootCat = rootSei.getAll(TestCategoryBase.class).get(0);
 		long rootValue = rootCat.getTestBaseProperty();
 		EList<StructuralElementInstance> allInherited = rootSei.getStructuralElementInstance().getDeepChildren();
 		assertEquals(testNumberOfElements - 1, allInherited.size());
+		boolean differentValue = false;
 		for (StructuralElementInstance sei : allInherited) {
 			assertEquals(1, sei.getCategoryAssignments().size());
 			CategoryAssignment ca = sei.getCategoryAssignments().get(0);
 			TestCategoryBase caBean = new TestCategoryBase(ca);
-			assertEquals(rootValue, caBean.getTestBaseProperty());
+			if (rootValue != caBean.getTestBaseProperty()) {
+				differentValue = true;
+				break;
+			}
 		}
+		assertTrue(differentValue);
 	}
 
 	private void changeRandomInheritanceParameters() {
@@ -292,60 +319,55 @@ public void assertProjectHasElements() {
 		}
 		assertEquals(testNumberOfElements, elementCount);
 	}
-	
-	
+
+
 	/**
-	 * method to create random tree with structural element
-	 * @param n size of the tree
-	 * @throws IOException 
+	 * Generator of a study for the test cases
 	 */
-	private void generateRandomTreeWithReferences(int n) throws IOException {
-		TestStructuralElement root = createSE("root");
-		TestCategoryBase cat = new TestCategoryBase(testConcept);
-		cat.setTestBaseProperty(ThreadLocalRandom.current().nextInt());
-		root.add(cat);
-		modelAPI.addRootSei(root);
-		List<TestStructuralElement> allElements = new ArrayList<>();
-		allElements.add(root);
-		for (int i = 0; i < n - 1; i++) {
-			TestStructuralElement newElement = createSE("element_" + (i + 1));
-			TestStructuralElement parent = allElements.get(ThreadLocalRandom.current().nextInt(allElements.size()));
-			parent.add(newElement);
-
-			TestStructuralElement referenceTo = allElements.get(ThreadLocalRandom.current().nextInt(allElements.size()));
-			TestCategoryBase referencedCa = referenceTo.getAll(TestCategoryBase.class).get(0);
-			cat = new TestCategoryBase(testConcept);
-			cat.setTestBaseProperty(ThreadLocalRandom.current().nextInt());
-			cat.setTestReference(referencedCa);
-			newElement.add(cat);
-			
-			allElements.add(newElement);
+	class StudyGenerator {
+		protected List<IBeanStructuralElementInstance> addedElements;
+
+
+		public IBeanStructuralElementInstance createRootSei(String name) {
+			TestStructuralElement sei = new TestStructuralElement(testConcept);
+			sei.setName(name);
+			return sei;
 		}
-	}
 
-	/**
-	 * method to create random tree with inheritance
-	 * @param n size of the tree
-	 * @throws IOException 
-	 */
-	private void generateRandomTreeWithInheritance(int n) throws IOException {
-		TestStructuralElement root = createSE("root");
-		TestCategoryBase cat = new TestCategoryBase(testConcept);
-		cat.setTestBaseProperty(ThreadLocalRandom.current().nextInt());
-		root.add(cat);
-		modelAPI.addRootSei(root);
-		List<TestStructuralElement> allElements = new ArrayList<>();
-		allElements.add(root);
-		for (int i = 0; i < n - 1; i++) {
-			TestStructuralElement newElement = createSE("element_" + (i + 1));
-			TestStructuralElement parent = allElements.get(ThreadLocalRandom.current().nextInt(allElements.size()));
-			parent.add(newElement);
-
-			TestStructuralElement inheritsFrom = allElements.get(ThreadLocalRandom.current().nextInt(allElements.size()));
-			newElement.addSuperSei(inheritsFrom);
+		public IBeanStructuralElementInstance createSei(String name) {
+			TestStructuralElement se = new TestStructuralElement(testConcept);
+			se.setName(name);
+			return se;
+		}
+		
+		public void generate() throws IOException {
+			addedElements = new ArrayList<>();
+
+			IBeanStructuralElementInstance root = createRootSei("root");
+			modelAPI.createSeiStorage(root);
+			modelAPI.addRootSei(root);
+			addedElements.add(root);
+
+			for (int i = 0; i < testNumberOfElements - 1; i++) {
+				IBeanStructuralElementInstance newElement = createSei("element_" + (i + 1));
+				modelAPI.createSeiStorage(newElement);
+
+				IBeanStructuralElementInstance parent = getRandomPreviousSei();
+				parent.add(newElement);
+
+				addedElements.add(newElement);
+			}
 			
-			allElements.add(newElement);
+		}
+		
+		/**
+		 * @return one of previously generated SEIs or null if nothing has been generated yet
+		 */
+		public IBeanStructuralElementInstance getRandomPreviousSei() {
+			if (addedElements.isEmpty()) {
+				return null;
+			}
+			return addedElements.get(ThreadLocalRandom.current().nextInt(addedElements.size()));
 		}
 	}
-
 }
```

## Row 31
commit_url: https://github.com/bmwcarit/joynr/commit/fbc436acfaa6e7aeba393e8e33e93076779eae83
rm_type: Extract Method
rm_description: Extract Method private createGCDClientWithProperties(properties Properties) : GlobalCapabilitiesDirectoryClient extracted from public setup() : void in class io.joynr.capabilities.GlobalCapabilitiesDirectoryClientTest
file_path: java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java
left_side: [{"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 99, "endLine": 123, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "source method declaration before extraction", "codeElement": "public setup() : void"}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 111, "endLine": 111, "startColumn": 17, "endColumn": 85, "codeElementType": "EXPRESSION_STATEMENT", "description": "extracted code from source method declaration", "codeElement": null}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 112, "endLine": 113, "startColumn": 17, "endColumn": 93, "codeElementType": "EXPRESSION_STATEMENT", "description": "extracted code from source method declaration", "codeElement": null}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 108, "endLine": 115, "startColumn": 9, "endColumn": 51, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "extracted code from source method declaration", "codeElement": null}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 116, "endLine": 116, "startColumn": 9, "endColumn": 81, "codeElementType": "EXPRESSION_STATEMENT", "description": "extracted code from source method declaration", "codeElement": null}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 110, "endLine": 114, "startColumn": 37, "endColumn": 14, "codeElementType": "BLOCK", "description": "extracted code from source method declaration", "codeElement": null}]
right_side: [{"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 122, "endLine": 135, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "private createGCDClientWithProperties(properties Properties) : GlobalCapabilitiesDirectoryClient"}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 126, "endLine": 126, "startColumn": 17, "endColumn": 85, "codeElementType": "EXPRESSION_STATEMENT", "description": "extracted code to extracted method declaration", "codeElement": null}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 127, "endLine": 128, "startColumn": 17, "endColumn": 93, "codeElementType": "EXPRESSION_STATEMENT", "description": "extracted code to extracted method declaration", "codeElement": null}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 123, "endLine": 132, "startColumn": 9, "endColumn": 51, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "extracted code to extracted method declaration", "codeElement": null}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 134, "endLine": 134, "startColumn": 9, "endColumn": 78, "codeElementType": "RETURN_STATEMENT", "description": "extracted code to extracted method declaration", "codeElement": null}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 125, "endLine": 131, "startColumn": 37, "endColumn": 14, "codeElementType": "BLOCK", "description": "extracted code to extracted method declaration", "codeElement": null}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 99, "endLine": 120, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "source method declaration after extraction", "codeElement": "public setup() : void"}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 108, "endLine": 108, "startColumn": 19, "endColumn": 60, "codeElementType": "METHOD_INVOCATION", "description": "extracted method invocation", "codeElement": "createGCDClientWithProperties(properties)"}, {"filePath": "java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java", "startLine": 129, "endLine": 130, "startColumn": 17, "endColumn": 79, "codeElementType": "EXPRESSION_STATEMENT", "description": "added statement in extracted method declaration", "codeElement": null}]

### Patch: java/core/libjoynr/src/test/java/io/joynr/capabilities/GlobalCapabilitiesDirectoryClientTest.java
```diff
@@ -105,50 +105,49 @@ public void setup() {
         properties.put(PROPERTY_CAPABILITIES_FRESHNESS_UPDATE_INTERVAL_MS,
                        String.valueOf(FRESHNESS_UPDATE_INTERVAL_MS));
 
-        Injector injector = Guice.createInjector(new AbstractModule() {
-            @Override
-            public void configure() {
-                bind(ProxyBuilderFactory.class).toInstance(proxyBuilderFactoryMock);
-                bind(GlobalDiscoveryEntry.class).annotatedWith(Names.named(MessagingPropertyKeys.CAPABILITIES_DIRECTORY_DISCOVERY_ENTRY))
-                                                .toInstance(capabilitiesDirectoryEntryMock);
-            }
-        }, new JoynrPropertiesModule(properties));
-        subject = injector.getInstance(GlobalCapabilitiesDirectoryClient.class);
+        subject = createGCDClientWithProperties(properties);
 
         when(proxyBuilderFactoryMock.get(domainMock,
                                          GlobalCapabilitiesDirectoryProxy.class)).thenReturn(capabilitiesProxyBuilderMock);
         when(capabilitiesProxyBuilderMock.setDiscoveryQos(any(DiscoveryQos.class))).thenReturn(capabilitiesProxyBuilderMock);
         when(capabilitiesProxyBuilderMock.setMessagingQos(any(MessagingQos.class))).thenReturn(capabilitiesProxyBuilderMock);
         when(capabilitiesProxyBuilderMock.build()).thenReturn(globalCapabilitiesDirectoryProxyMock);
-    }
 
-    @Test
-    public void testAdd() {
-        messagingQos.setTtl_ms(DEFAULT_TTL_ADD_AND_REMOVE);
-        GlobalDiscoveryEntry capabilitiesDirectoryEntryMock = mock(GlobalDiscoveryEntry.class);
-        subject.add(callbackMock, capabilitiesDirectoryEntryMock);
-        verify(capabilitiesProxyBuilderMock).setMessagingQos(eq(messagingQos));
-        verify(globalCapabilitiesDirectoryProxyMock).add(eq(callbackMock), eq(capabilitiesDirectoryEntryMock));
+        // expect default ttl if not changed in the test case
+        expectedGcdCallMessagingQos.setTtl_ms(DEFAULT_TTL_ADD_AND_REMOVE);
+        // expect the default backend in the custom header if not changed in the test case
+        expectedGcdCallMessagingQos.putCustomMessageHeader(Message.CUSTOM_HEADER_GBID_KEY, GBID_DEFAULT_BACKEND);
     }
 
-
-    private GlobalCapabilitiesDirectoryClient getClientWithCustomTTL(long ttl) {
-        Properties properties = new Properties();
-        properties.put(ConfigurableMessagingSettings.PROPERTY_DISCOVERY_GLOBAL_ADD_AND_REMOVE_TTL_MS,
-                       String.valueOf(ttl));
-
+    private GlobalCapabilitiesDirectoryClient createGCDClientWithProperties(final Properties properties) {
         Injector injector = Guice.createInjector(new AbstractModule() {
             @Override
             public void configure() {
                 bind(ProxyBuilderFactory.class).toInstance(proxyBuilderFactoryMock);
                 bind(GlobalDiscoveryEntry.class).annotatedWith(Names.named(MessagingPropertyKeys.CAPABILITIES_DIRECTORY_DISCOVERY_ENTRY))
                                                 .toInstance(capabilitiesDirectoryEntryMock);
+                bind(String[].class).annotatedWith(Names.named(MessagingPropertyKeys.GBID_ARRAY))
+                                    .toInstance(GBIDS_ARRAY_PROPERTY_SETTING);
             }
         }, new JoynrPropertiesModule(properties));
 
         return injector.getInstance(GlobalCapabilitiesDirectoryClient.class);
     }
 
+    @Test
+    public void testAdd() {
+        // given some discovery entry
+        GlobalDiscoveryEntry capabilitiesDirectoryEntryMock = mock(GlobalDiscoveryEntry.class);
+
+        // when we call the add method with it
+        subject.add(callbackMock, capabilitiesDirectoryEntryMock);
+
+        // then the GCD proxy is called with the expected parameters and QoS
+        verify(globalCapabilitiesDirectoryProxyMock).add(eq(callbackMock),
+                                                         eq(capabilitiesDirectoryEntryMock),
+                                                         eq(expectedGcdCallMessagingQos));
+    }
+
     @Test
     public void testAddWithCustomTTL() {
         GlobalCapabilitiesDirectoryClient subjectInject = getClientWithCustomTTL(CUSTOM_TTL);
```

## Row 32
commit_url: https://github.com/martint/jmxutils/commit/b8e0398069cde724652b12e58ffeb20276345d3f
rm_type: Pull Up Method
rm_description: Pull Up Method public testNotManagedAttributeInfo() : void from class org.weakref.jmx.TestExporter to public testNotManagedAttributeInfo() : void from class org.weakref.jmx.AbstractMbeanTest
file_path: src/test/java/org/weakref/jmx/AbstractMbeanTest.java; src/test/java/org/weakref/jmx/TestExporter.java
left_side: [{"filePath": "src/test/java/org/weakref/jmx/TestExporter.java", "startLine": 153, "endLine": 164, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testNotManagedAttributeInfo() : void"}]
right_side: [{"filePath": "src/test/java/org/weakref/jmx/AbstractMbeanTest.java", "startLine": 66, "endLine": 77, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "pulled up method declaration", "codeElement": "public testNotManagedAttributeInfo() : void"}]

### Patch: src/test/java/org/weakref/jmx/AbstractMbeanTest.java
```diff
@@ -1,11 +1,124 @@
 package org.weakref.jmx;
 
+import org.testng.Assert;
 import org.testng.annotations.DataProvider;
+import org.testng.annotations.Test;
+
+import javax.management.MBeanAttributeInfo;
+import javax.management.MBeanInfo;
+import java.lang.reflect.Method;
+import java.util.List;
+
+import static org.testng.Assert.assertEquals;
+import static org.testng.Assert.assertFalse;
+import static org.testng.Assert.assertNotNull;
+import static org.testng.Assert.assertTrue;
 
 public abstract class AbstractMbeanTest<T>
 {
+    protected List<T> objects;
+
     protected abstract Object getObject(T t);
 
+    protected abstract MBeanInfo getMBeanInfo(T t)
+            throws Exception;
+
+    @Test(dataProvider = "fixtures")
+    public void testGetterAttributeInfo(String attribute, boolean isIs, Object[] values, Class<?> clazz)
+            throws Exception
+    {
+        String methodName = "set" + attribute;
+        for (T t : objects) {
+            String attributeName = toFeatureName(attribute, t);
+            SimpleObject simpleObject = toSimpleObject(t);
+            Method setter = simpleObject.getClass().getMethod(methodName, clazz);
+
+            MBeanInfo info = getMBeanInfo(t);
+            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
+            Assert.assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
+            Assert.assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
+            Assert.assertEquals(attributeInfo.getType(), setter.getParameterTypes()[0].getName(), "Attribute type for " + attributeName);
+            Assert.assertEquals(attributeInfo.isIs(), isIs, "Attribute isIs for " + attributeName);
+            Assert.assertTrue(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
+        }
+    }
+
+    @Test(dataProvider = "fixtures")
+    public void testSetterAttributeInfo(String attribute, boolean isIs, Object[] values, Class<?> clazz)
+            throws Exception
+    {
+        String methodName = (isIs ? "is" : "get") + attribute;
+
+        for (T t : objects) {
+            String attributeName = toFeatureName(attribute, t);
+            SimpleObject simpleObject = toSimpleObject(t);
+            Method getter = simpleObject.getClass().getMethod(methodName);
+
+            MBeanInfo info = getMBeanInfo(t);
+            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
+            Assert.assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
+            Assert.assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
+            Assert.assertEquals(attributeInfo.getType(), getter.getReturnType().getName(), "Attribute Type for " + attributeName);
+            Assert.assertTrue(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
+        }
+    }
+
+    @Test
+    public void testNotManagedAttributeInfo()
+            throws Exception
+    {
+
+        for (T t : objects) {
+            MBeanInfo info = getMBeanInfo(t);
+            String attributeName = toFeatureName("NotManaged", t);
+            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
+            Assert.assertNull(attributeInfo, "AttributeInfo for " + attributeName);
+        }
+    }
+
+    @Test
+    public void testReadOnlyAttributeInfo()
+            throws Exception
+    {
+        for (T t : objects) {
+            MBeanInfo info = getMBeanInfo(t);
+
+            String attributeName = toFeatureName("ReadOnly", t);
+            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
+            assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
+            assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
+            assertEquals(attributeInfo.getType(), "int", "Attribute Type for " + attributeName);
+            assertTrue(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
+            assertFalse(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
+        }
+    }
+
+    @Test
+    public void testWriteOnlyAttributeInfo()
+            throws Exception
+    {
+        for (T t : objects) {
+            MBeanInfo info = getMBeanInfo(t);
+            String attributeName = toFeatureName("WriteOnly", t);
+            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
+            Assert.assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
+            Assert.assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
+            Assert.assertEquals(attributeInfo.getType(), "int", "Attribute Type for " + attributeName);
+            Assert.assertFalse(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
+            Assert.assertTrue(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
+        }
+    }
+
+    protected MBeanAttributeInfo getAttributeInfo(MBeanInfo info, String attributeName)
+    {
+        for (MBeanAttributeInfo attributeInfo : info.getAttributes()) {
+            if (attributeInfo.getName().equals(attributeName)) {
+                return attributeInfo;
+            }
+        }
+        return null;
+    }
+
     @DataProvider(name = "fixtures")
     Object[][] getFixtures()
     {
```
### Patch: src/test/java/org/weakref/jmx/TestExporter.java
```diff
@@ -23,7 +23,6 @@
 
 import javax.management.AttributeNotFoundException;
 import javax.management.InstanceNotFoundException;
-import javax.management.IntrospectionException;
 import javax.management.InvalidAttributeValueException;
 import javax.management.MBeanAttributeInfo;
 import javax.management.MBeanException;
@@ -47,8 +46,6 @@ public class TestExporter extends AbstractMbeanTest<TestExporter.NamedObject>
 {
     private MBeanServer server;
 
-    private List<NamedObject> objects;
-
     static class NamedObject
     {
         final ObjectName objectName;
@@ -72,6 +69,13 @@ protected Object getObject(NamedObject namedObject)
         return namedObject.object;
     }
 
+    @Override
+    protected MBeanInfo getMBeanInfo(NamedObject namedObject)
+            throws Exception
+    {
+        return server.getMBeanInfo(namedObject.objectName);
+    }
+
     @BeforeMethod
     void setup()
             throws IOException, MalformedObjectNameException, NotBoundException
@@ -110,109 +114,14 @@ void setup()
 //        }
 //    }
 
-    @Test(dataProvider = "fixtures")
-    public void testGetterAttributeInfo(String attribute, boolean isIs, Object[] values, Class<?> clazz)
-            throws Exception
-    {
-        String methodName = "set" + attribute;
-        for (NamedObject namedObject : objects) {
-            String attributeName = toFeatureName(attribute, namedObject);
-            SimpleObject simpleObject = toSimpleObject(namedObject);
-            Method setter = simpleObject.getClass().getMethod(methodName, clazz);
-
-            MBeanInfo info = server.getMBeanInfo(namedObject.objectName);
-            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
-            Assert.assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
-            Assert.assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
-            Assert.assertEquals(attributeInfo.getType(), setter.getParameterTypes()[0].getName(), "Attribute type for " + attributeName);
-            Assert.assertEquals(attributeInfo.isIs(), isIs, "Attribute isIs for " + attributeName);
-            Assert.assertTrue(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
-        }
-    }
-
-    @Test(dataProvider = "fixtures")
-    public void testSetterAttributeInfo(String attribute, boolean isIs, Object[] values, Class<?> clazz)
-            throws Exception
-    {
-        String methodName = (isIs ? "is" : "get") + attribute;
-
-        for (NamedObject namedObject : objects) {
-            String attributeName = toFeatureName(attribute, namedObject);
-            SimpleObject simpleObject = toSimpleObject(namedObject);
-            Method getter = simpleObject.getClass().getMethod(methodName);
-
-            MBeanInfo info = server.getMBeanInfo(namedObject.objectName);
-            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
-            Assert.assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
-            Assert.assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
-            Assert.assertEquals(attributeInfo.getType(), getter.getReturnType().getName(), "Attribute Type for " + attributeName);
-            Assert.assertTrue(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
-        }
-    }
-
-    @Test
-    public void testNotManagedAttributeInfo()
-            throws Exception
-    {
-
-        for (NamedObject namedObject : objects) {
-            MBeanInfo info = server.getMBeanInfo(namedObject.objectName);
-            String attributeName = toFeatureName("NotManaged", namedObject);
-            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
-            Assert.assertNull(attributeInfo, "AttributeInfo for " + attributeName);
-        }
-    }
-
-    @Test
-    public void testReadOnlyAttributeInfo()
-            throws Exception
-    {
-        for (NamedObject namedObject : objects) {
-            MBeanInfo info = server.getMBeanInfo(namedObject.objectName);
-            String attributeName = toFeatureName("ReadOnly", namedObject);
-            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
-            Assert.assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
-            Assert.assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
-            Assert.assertEquals(attributeInfo.getType(), "int", "Attribute Type for " + attributeName);
-            Assert.assertTrue(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
-            Assert.assertFalse(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
-        }
-    }
-
-    @Test
-    public void testWriteOnlyAttributeInfo()
-            throws Exception
-    {
-        for (NamedObject namedObject : objects) {
-            MBeanInfo info = server.getMBeanInfo(namedObject.objectName);
-            String attributeName = toFeatureName("WriteOnly", namedObject);
-            MBeanAttributeInfo attributeInfo = getAttributeInfo(info, attributeName);
-            Assert.assertNotNull(attributeInfo, "AttributeInfo for " + attributeName);
-            Assert.assertEquals(attributeInfo.getName(), attributeName, "Attribute Name for " + attributeName);
-            Assert.assertEquals(attributeInfo.getType(), "int", "Attribute Type for " + attributeName);
-            Assert.assertFalse(attributeInfo.isReadable(), "Attribute Readable for " + attributeName);
-            Assert.assertTrue(attributeInfo.isWritable(), "Attribute Writable for " + attributeName);
-        }
-    }
-
-    private MBeanAttributeInfo getAttributeInfo(MBeanInfo info, String attributeName)
-    {
-        for (MBeanAttributeInfo attributeInfo : info.getAttributes()) {
-            if (attributeInfo.getName().equals(attributeName)) {
-                return attributeInfo;
-            }
-        }
-        return null;
-    }
-
     @Test(dataProvider = "fixtures")
     public void testOperationInfo(String attribute, boolean isIs, Object[] values, Class<?> clazz)
             throws Exception
     {
         for (NamedObject namedObject : objects) {
             String operationName = toFeatureName("echo", namedObject);
 
-            MBeanInfo beanInfo = server.getMBeanInfo(namedObject.objectName);
+            MBeanInfo beanInfo = getMBeanInfo(namedObject);
             MBeanOperationInfo operationInfo = null;
             for (MBeanOperationInfo info : beanInfo.getOperations()) {
                 if (info.getName().equals(operationName)) {
@@ -347,11 +256,11 @@ public void testSetFailsOnReadOnly()
 
     @Test
     public void testDescription()
-            throws IntrospectionException, InstanceNotFoundException, ReflectionException
+            throws Exception
     {
         for (NamedObject namedObject : objects) {
             boolean described = false;
-            for (MBeanAttributeInfo info : server.getMBeanInfo(namedObject.objectName).getAttributes()) {
+            for (MBeanAttributeInfo info : getMBeanInfo(namedObject).getAttributes()) {
                 String attributeName = toFeatureName("DescribedInt", namedObject);
                 if (info.getName().equals(attributeName)) {
                     Assert.assertEquals("epic description", info.getDescription());
```

## Row 33
commit_url: https://github.com/FasterXML/jackson-modules-java8/commit/3956c030f7d334e827da5c2d4f8da68cef5c8d2c
rm_type: Move Class
rm_description: Move Class com.fasterxml.jackson.datatype.jsr310.TestInstantSerialization.Wrapper moved to com.fasterxml.jackson.datatype.jsr310.deser.InstantDeserTest.Wrapper
file_path: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/TestInstantSerialization.java; datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/InstantDeserTest.java
left_side: [{"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/TestInstantSerialization.java", "startLine": 46, "endLine": 60, "startColumn": 5, "endColumn": 6, "codeElementType": "TYPE_DECLARATION", "description": "original type declaration", "codeElement": "com.fasterxml.jackson.datatype.jsr310.TestInstantSerialization.Wrapper"}]
right_side: [{"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/InstantDeserTest.java", "startLine": 32, "endLine": 45, "startColumn": 5, "endColumn": 6, "codeElementType": "TYPE_DECLARATION", "description": "moved type declaration", "codeElement": "com.fasterxml.jackson.datatype.jsr310.deser.InstantDeserTest.Wrapper"}]

### Patch: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/TestInstantSerialization.java
```diff
@@ -17,62 +17,23 @@
 package com.fasterxml.jackson.datatype.jsr310;
 
 import com.fasterxml.jackson.annotation.JsonFormat;
-import com.fasterxml.jackson.databind.DeserializationFeature;
 import com.fasterxml.jackson.databind.ObjectMapper;
 import com.fasterxml.jackson.databind.SerializationFeature;
 import org.junit.Test;
 
-import java.time.DateTimeException;
 import java.time.Instant;
-import java.time.LocalDate;
-import java.time.ZoneId;
-import java.time.ZoneOffset;
-import java.time.ZonedDateTime;
 import java.time.format.DateTimeFormatter;
-import java.time.temporal.ChronoUnit;
 import java.time.temporal.Temporal;
 
 import static org.junit.Assert.assertEquals;
 import static org.junit.Assert.assertNotNull;
-import static org.junit.Assert.assertTrue;
 
 public class TestInstantSerialization extends ModuleTestBase
 {
     private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ISO_INSTANT;
-    private static final String CUSTOM_PATTERN = "yyyy-MM-dd HH:mm:ss";
 
     private final ObjectMapper MAPPER = newMapper();
 
-    static class Wrapper {
-        @JsonFormat(
-                /* 22-Jun-2015, tatu: I'll be damned if I understand why pattern does not
-                 *    work here... but it doesn't. Someone with better date-fu has to come
-                 *    and fix this; until then I will only verify that we can force textual
-                 *    representation here
-                 */
-                //pattern="YYYY-mm-dd",
-                shape=JsonFormat.Shape.STRING
-        )
-        public Instant value;
-
-        public Wrapper() { }
-        public Wrapper(Instant v) { value = v; }
-    }
-
-    static class WrapperWithCustomPattern {
-        @JsonFormat(
-                pattern = CUSTOM_PATTERN,
-                shape=JsonFormat.Shape.STRING,
-                timezone = "UTC"
-        )
-        public Instant valueInUTC;
-
-        public WrapperWithCustomPattern() { }
-        public WrapperWithCustomPattern(Instant v) {
-            valueInUTC = v;
-        }
-    }
-
     @Test
     public void testSerializationAsTimestamp01Nanoseconds() throws Exception
     {
@@ -207,385 +168,5 @@ public void testSerializationWithTypeInfo03() throws Exception
                 "[\"" + Instant.class.getName() + "\",\"" + FORMATTER.format(date) + "\"]", value);
     }
 
-    @Test
-    public void testDeserializationAsFloat01() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(0L);
-        Instant value = MAPPER.readValue("0.000000000", Instant.class);
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationAsFloat02() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(123456789L, 183917322);
-        Instant value = MAPPER.readValue("123456789.183917322", Instant.class);
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationAsFloat03() throws Exception
-    {
-        Instant date = Instant.now();
-        Instant value = MAPPER.readValue(
-                DecimalUtils.toDecimal(date.getEpochSecond(), date.getNano()), Instant.class
-                );
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    /**
-     * Test the upper-bound of Instant.
-     */
-    @Test
-    public void testDeserializationAsFloatEdgeCase01() throws Exception
-    {
-        String input = Instant.MAX.getEpochSecond() + ".999999999";
-        Instant value = MAPPER.readValue(input, Instant.class);
-        assertEquals(value, Instant.MAX);
-        assertEquals(Instant.MAX.getEpochSecond(), value.getEpochSecond());
-        assertEquals(999999999, value.getNano());
-    }
-
-    /**
-     * Test the lower-bound of Instant.
-     */
-    @Test
-    public void testDeserializationAsFloatEdgeCase02() throws Exception
-    {
-        String input = Instant.MIN.getEpochSecond() + ".0";
-        Instant value = MAPPER.readValue(input, Instant.class);
-        assertEquals(value, Instant.MIN);
-        assertEquals(Instant.MIN.getEpochSecond(), value.getEpochSecond());
-        assertEquals(0, value.getNano());
-    }
-
-    @Test(expected = DateTimeException.class)
-    public void testDeserializationAsFloatEdgeCase03() throws Exception
-    {
-        // Instant can't go this low
-        String input = Instant.MIN.getEpochSecond() + ".1";
-        MAPPER.readValue(input, Instant.class);
-    }
-
-    /*
-     * InstantDeserializer currently uses BigDecimal.longValue() which has surprising behavior
-     * for numbers outside the range of Long.  Numbers less than 1e64 will result in the lower 64 bits.
-     * Numbers at or above 1e64 will always result in zero.
-     */
-
-    @Test(expected = DateTimeException.class)
-    public void testDeserializationAsFloatEdgeCase04() throws Exception
-    {
-        // 1ns beyond the upper-bound of Instant.
-        String input = (Instant.MAX.getEpochSecond() + 1) + ".0";
-        MAPPER.readValue(input, Instant.class);
-    }
-
-    @Test(expected = DateTimeException.class)
-    public void testDeserializationAsFloatEdgeCase05() throws Exception
-    {
-        // 1ns beyond the lower-bound of Instant.
-        String input = (Instant.MIN.getEpochSecond() - 1) + ".0";
-        MAPPER.readValue(input, Instant.class);
-    }
-
-    @Test
-    public void testDeserializationAsFloatEdgeCase06() throws Exception
-    {
-        // Into the positive zone where everything becomes zero.
-        String input = "1e64";
-        Instant value = MAPPER.readValue(input, Instant.class);
-        assertEquals(0, value.getEpochSecond());
-    }
-
-    @Test
-    public void testDeserializationAsFloatEdgeCase07() throws Exception
-    {
-        // Into the negative zone where everything becomes zero.
-        String input = "-1e64";
-        Instant value = MAPPER.readValue(input, Instant.class);
-        assertEquals(0, value.getEpochSecond());
-    }
-
-    /**
-     * Numbers with very large exponents can take a long time, but still result in zero.
-     * https://github.com/FasterXML/jackson-databind/issues/2141
-     */
-    @Test(timeout = 100)
-    public void testDeserializationAsFloatEdgeCase08() throws Exception
-    {
-        String input = "1e10000000";
-        Instant value = MAPPER.readValue(input, Instant.class);
-        assertEquals(0, value.getEpochSecond());
-    }
-
-    @Test(timeout = 100)
-    public void testDeserializationAsFloatEdgeCase09() throws Exception
-    {
-        String input = "-1e10000000";
-        Instant value = MAPPER.readValue(input, Instant.class);
-        assertEquals(0, value.getEpochSecond());
-    }
-
-    /**
-     * Same for large negative exponents.
-     */
-    @Test(timeout = 100)
-    public void testDeserializationAsFloatEdgeCase10() throws Exception
-    {
-        String input = "1e-10000000";
-        Instant value = MAPPER.readValue(input, Instant.class);
-        assertEquals(0, value.getEpochSecond());
-    }
-
-    @Test(timeout = 100)
-    public void testDeserializationAsFloatEdgeCase11() throws Exception
-    {
-        String input = "-1e-10000000";
-        Instant value = MAPPER.readValue(input, Instant.class);
-        assertEquals(0, value.getEpochSecond());
-    }
-
-
-    @Test
-    public void testDeserializationAsInt01Nanoseconds() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(0L);
-        Instant value = MAPPER.readerFor(Instant.class)
-                .with(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
-                .readValue("0");
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationAsInt01Milliseconds() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(0L);
-        Instant value = MAPPER.readerFor(Instant.class)
-                .without(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
-                .readValue("0");
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationAsInt02Nanoseconds() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(123456789L, 0);
-        Instant value = MAPPER.readerFor(Instant.class)
-                .with(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
-                .readValue("123456789");
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationAsInt02Milliseconds() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(123456789L, 422000000);
-        Instant value = MAPPER.readerFor(Instant.class)
-                .without(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
-                .readValue("123456789422");
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationAsInt03Nanoseconds() throws Exception
-    {
-        Instant date = Instant.now();
-        date = date.minus(date.getNano(), ChronoUnit.NANOS);
-
-        Instant value = MAPPER.readerFor(Instant.class)
-                .with(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
-                .readValue(Long.toString(date.getEpochSecond()));
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationAsInt03Milliseconds() throws Exception
-    {
-        Instant date = Instant.now();
-        date = date.minus(date.getNano(), ChronoUnit.NANOS);
-
-        Instant value = MAPPER.readerFor(Instant.class)
-                .without(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
-                .readValue(Long.toString(date.toEpochMilli()));
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationAsString01() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(0L);
-        Instant value = MAPPER.readValue('"' + FORMATTER.format(date) + '"', Instant.class);
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationAsString02() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(123456789L, 183917322);
-        Instant value = MAPPER.readValue('"' + FORMATTER.format(date) + '"', Instant.class);
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationAsString03() throws Exception
-    {
-        Instant date = Instant.now();
-
-        Instant value = MAPPER.readValue('"' + FORMATTER.format(date) + '"', Instant.class);
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationWithTypeInfo01() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(123456789L, 183917322);
-        ObjectMapper m = newMapper()
-                .addMixIn(Temporal.class, MockObjectConfiguration.class);
-        Temporal value = m.readValue(
-                "[\"" + Instant.class.getName() + "\",123456789.183917322]", Temporal.class
-                );
-        assertTrue("The value should be an Instant.", value instanceof Instant);
-        assertEquals("The value is not correct.", date, value);
-    }
 
-    @Test
-    public void testDeserializationWithTypeInfo02() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(123456789L, 0);
-        ObjectMapper m = newMapper()
-                .enable(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
-                .addMixIn(Temporal.class, MockObjectConfiguration.class);
-        Temporal value = m.readValue(
-                "[\"" + Instant.class.getName() + "\",123456789]", Temporal.class
-                );
-        assertTrue("The value should be an Instant.", value instanceof Instant);
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationWithTypeInfo03() throws Exception
-    {
-        Instant date = Instant.ofEpochSecond(123456789L, 422000000);
-        ObjectMapper m = newMapper()
-                .disable(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
-                .addMixIn(Temporal.class, MockObjectConfiguration.class);
-        Temporal value = m.readValue(
-                "[\"" + Instant.class.getName() + "\",123456789422]", Temporal.class
-                );
-
-        assertTrue("The value should be an Instant.", value instanceof Instant);
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testDeserializationWithTypeInfo04() throws Exception
-    {
-        Instant date = Instant.now();
-        ObjectMapper m = newMapper()
-                .addMixIn(Temporal.class, MockObjectConfiguration.class);
-        Temporal value = m.readValue(
-                "[\"" + Instant.class.getName() + "\",\"" + FORMATTER.format(date) + "\"]", Temporal.class
-                );
-        assertTrue("The value should be an Instant.", value instanceof Instant);
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    @Test
-    public void testCustomPatternWithAnnotations01() throws Exception
-    {
-        final Wrapper input = new Wrapper(Instant.ofEpochMilli(0));
-        String json = MAPPER.writeValueAsString(input);
-        assertEquals(aposToQuotes("{'value':'1970-01-01T00:00:00Z'}"), json);
-
-        Wrapper result = MAPPER.readValue(json, Wrapper.class);
-        assertEquals(input.value, result.value);
-    }
-
-    // [datatype-jsr310#69]
-    @Test
-    public void testCustomPatternWithAnnotations02() throws Exception
-    {
-        //Test date is pushed one year after start of the epoch just to avoid possible issues with UTC-X TZs which could
-        //push the instant before tha start of the epoch
-        final Instant instant = ZonedDateTime.ofInstant(Instant.ofEpochMilli(0), ZoneId.of("UTC")).plusYears(1).toInstant();
-        final DateTimeFormatter formatter = DateTimeFormatter.ofPattern(CUSTOM_PATTERN);
-        final String valueInUTC = formatter.withZone(ZoneId.of("UTC")).format(instant);
-
-        final WrapperWithCustomPattern input = new WrapperWithCustomPattern(instant);
-        String json = MAPPER.writeValueAsString(input);
-
-        assertTrue("Instant in UTC timezone was not serialized as expected.",
-                json.contains(aposToQuotes("'valueInUTC':'" + valueInUTC + "'")));
-
-        WrapperWithCustomPattern result = MAPPER.readValue(json, WrapperWithCustomPattern.class);
-        assertEquals("Instant in UTC timezone was not deserialized as expected.",
-                input.valueInUTC, result.valueInUTC);
-    }
-
-    // [datatype-jsr310#16]
-    @Test
-    public void testDeserializationFromStringAsNumber() throws Exception
-    {
-        // First, baseline test with floating-point numbers
-        Instant inst = Instant.now();
-        String json = MAPPER.writer()
-                .with(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
-                .with(SerializationFeature.WRITE_DATE_TIMESTAMPS_AS_NANOSECONDS)
-                .writeValueAsString(inst);
-        Instant result = MAPPER.readValue(json, Instant.class);
-        assertNotNull(result);
-        assertEquals(result, inst);
-
-        // but then quoted as JSON String
-        result = MAPPER.readValue(String.format("\"%s\"", json),
-                Instant.class);
-        assertNotNull(result);
-        assertEquals(result, inst);
-    }
-
-    // [datatype-jsr310#79]
-    @Test
-    public void testRoundTripOfInstantAndJavaUtilDate() throws Exception
-    {
-        ObjectMapper mapper = newMapper();
-        mapper.configure(SerializationFeature.WRITE_DATE_TIMESTAMPS_AS_NANOSECONDS, false);
-        mapper.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
-        mapper.configure(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS, false);
-
-        Instant givenInstant = LocalDate.of(2016, 1, 1).atStartOfDay().atZone(ZoneOffset.UTC).toInstant();
-        String json = mapper.writeValueAsString(java.util.Date.from(givenInstant));
-        Instant actual = mapper.readValue(json, Instant.class);
-
-        assertEquals(givenInstant, actual);
-    }
-
-    // [jackson-modules-java8#18]
-    @Test
-    public void testDeserializationFromStringWithZeroZoneOffset01() throws Exception {
-        Instant date = Instant.now();
-        String json = formatWithZeroZoneOffset(date, "+00:00");
-        Instant result = MAPPER.readValue(json, Instant.class);
-        assertEquals("The value is not correct.", date, result);
-    }
-
-    @Test
-    public void testDeserializationFromStringWithZeroZoneOffset02() throws Exception {
-        Instant date = Instant.now();
-        String json = formatWithZeroZoneOffset(date, "+0000");
-        Instant result = MAPPER.readValue(json, Instant.class);
-        assertEquals("The value is not correct.", date, result);
-    }
-
-    @Test
-    public void testDeserializationFromStringWithZeroZoneOffset03() throws Exception {
-        Instant date = Instant.now();
-        String json = formatWithZeroZoneOffset(date, "+00");
-        Instant result = MAPPER.readValue(json, Instant.class);
-        assertEquals("The value is not correct.", date, result);
-    }
-
-    private String formatWithZeroZoneOffset(Instant date, String offset){
-        return '"' + FORMATTER.format(date).replaceFirst("Z$", offset) + '"';
-    }
 }
```
### Patch: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/InstantDeserTest.java
```diff
@@ -0,0 +1,443 @@
+package com.fasterxml.jackson.datatype.jsr310.deser;
+
+import static org.junit.Assert.assertEquals;
+import static org.junit.Assert.assertNotNull;
+import static org.junit.Assert.assertTrue;
+
+import java.time.DateTimeException;
+import java.time.Instant;
+import java.time.LocalDate;
+import java.time.ZoneId;
+import java.time.ZoneOffset;
+import java.time.ZonedDateTime;
+import java.time.format.DateTimeFormatter;
+import java.time.temporal.ChronoUnit;
+import java.time.temporal.Temporal;
+
+import org.junit.Test;
+
+import com.fasterxml.jackson.annotation.JsonFormat;
+import com.fasterxml.jackson.databind.DeserializationFeature;
+import com.fasterxml.jackson.databind.ObjectMapper;
+import com.fasterxml.jackson.databind.SerializationFeature;
+import com.fasterxml.jackson.datatype.jsr310.DecimalUtils;
+import com.fasterxml.jackson.datatype.jsr310.MockObjectConfiguration;
+import com.fasterxml.jackson.datatype.jsr310.ModuleTestBase;
+
+public class InstantDeserTest extends ModuleTestBase
+{
+    private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ISO_INSTANT;
+    private static final String CUSTOM_PATTERN = "yyyy-MM-dd HH:mm:ss";
+
+    static class Wrapper {
+        @JsonFormat(
+                // 22-Jun-2015, tatu: I'll be damned if I understand why pattern does not
+                //    work here... but it doesn't. Someone with better date-fu has to come
+                //   and fix this; until then I will only verify that we can force textual
+                //    representation here
+                //pattern="YYYY-mm-dd",
+                shape=JsonFormat.Shape.STRING
+        )
+        public Instant value;
+
+        public Wrapper() { }
+        public Wrapper(Instant v) { value = v; }
+    }
+
+    static class WrapperWithCustomPattern {
+        @JsonFormat(
+                pattern = CUSTOM_PATTERN,
+                shape=JsonFormat.Shape.STRING,
+                timezone = "UTC"
+        )
+        public Instant valueInUTC;
+
+        public WrapperWithCustomPattern() { }
+        public WrapperWithCustomPattern(Instant v) {
+            valueInUTC = v;
+        }
+    }
+    
+    private final ObjectMapper MAPPER = newMapper();
+
+    @Test
+    public void testDeserializationAsFloat01() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(0L);
+        Instant value = MAPPER.readValue("0.000000000", Instant.class);
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationAsFloat02() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(123456789L, 183917322);
+        Instant value = MAPPER.readValue("123456789.183917322", Instant.class);
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationAsFloat03() throws Exception
+    {
+        Instant date = Instant.now();
+        Instant value = MAPPER.readValue(
+                DecimalUtils.toDecimal(date.getEpochSecond(), date.getNano()), Instant.class
+                );
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    /**
+     * Test the upper-bound of Instant.
+     */
+    @Test
+    public void testDeserializationAsFloatEdgeCase01() throws Exception
+    {
+        String input = Instant.MAX.getEpochSecond() + ".999999999";
+        Instant value = MAPPER.readValue(input, Instant.class);
+        assertEquals(value, Instant.MAX);
+        assertEquals(Instant.MAX.getEpochSecond(), value.getEpochSecond());
+        assertEquals(999999999, value.getNano());
+    }
+
+    /**
+     * Test the lower-bound of Instant.
+     */
+    @Test
+    public void testDeserializationAsFloatEdgeCase02() throws Exception
+    {
+        String input = Instant.MIN.getEpochSecond() + ".0";
+        Instant value = MAPPER.readValue(input, Instant.class);
+        assertEquals(value, Instant.MIN);
+        assertEquals(Instant.MIN.getEpochSecond(), value.getEpochSecond());
+        assertEquals(0, value.getNano());
+    }
+
+    @Test(expected = DateTimeException.class)
+    public void testDeserializationAsFloatEdgeCase03() throws Exception
+    {
+        // Instant can't go this low
+        String input = Instant.MIN.getEpochSecond() + ".1";
+        MAPPER.readValue(input, Instant.class);
+    }
+
+    /*
+     * InstantDeserializer currently uses BigDecimal.longValue() which has surprising behavior
+     * for numbers outside the range of Long.  Numbers less than 1e64 will result in the lower 64 bits.
+     * Numbers at or above 1e64 will always result in zero.
+     */
+
+    @Test(expected = DateTimeException.class)
+    public void testDeserializationAsFloatEdgeCase04() throws Exception
+    {
+        // 1ns beyond the upper-bound of Instant.
+        String input = (Instant.MAX.getEpochSecond() + 1) + ".0";
+        MAPPER.readValue(input, Instant.class);
+    }
+
+    @Test(expected = DateTimeException.class)
+    public void testDeserializationAsFloatEdgeCase05() throws Exception
+    {
+        // 1ns beyond the lower-bound of Instant.
+        String input = (Instant.MIN.getEpochSecond() - 1) + ".0";
+        MAPPER.readValue(input, Instant.class);
+    }
+
+    @Test
+    public void testDeserializationAsFloatEdgeCase06() throws Exception
+    {
+        // Into the positive zone where everything becomes zero.
+        String input = "1e64";
+        Instant value = MAPPER.readValue(input, Instant.class);
+        assertEquals(0, value.getEpochSecond());
+    }
+
+    @Test
+    public void testDeserializationAsFloatEdgeCase07() throws Exception
+    {
+        // Into the negative zone where everything becomes zero.
+        String input = "-1e64";
+        Instant value = MAPPER.readValue(input, Instant.class);
+        assertEquals(0, value.getEpochSecond());
+    }
+
+    /**
+     * Numbers with very large exponents can take a long time, but still result in zero.
+     * https://github.com/FasterXML/jackson-databind/issues/2141
+     */
+    @Test(timeout = 100)
+    public void testDeserializationAsFloatEdgeCase08() throws Exception
+    {
+        String input = "1e10000000";
+        Instant value = MAPPER.readValue(input, Instant.class);
+        assertEquals(0, value.getEpochSecond());
+    }
+
+    @Test(timeout = 100)
+    public void testDeserializationAsFloatEdgeCase09() throws Exception
+    {
+        String input = "-1e10000000";
+        Instant value = MAPPER.readValue(input, Instant.class);
+        assertEquals(0, value.getEpochSecond());
+    }
+
+    /**
+     * Same for large negative exponents.
+     */
+    @Test(timeout = 100)
+    public void testDeserializationAsFloatEdgeCase10() throws Exception
+    {
+        String input = "1e-10000000";
+        Instant value = MAPPER.readValue(input, Instant.class);
+        assertEquals(0, value.getEpochSecond());
+    }
+
+    @Test(timeout = 100)
+    public void testDeserializationAsFloatEdgeCase11() throws Exception
+    {
+        String input = "-1e-10000000";
+        Instant value = MAPPER.readValue(input, Instant.class);
+        assertEquals(0, value.getEpochSecond());
+    }
+
+    @Test
+    public void testDeserializationAsInt01Nanoseconds() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(0L);
+        Instant value = MAPPER.readerFor(Instant.class)
+                .with(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
+                .readValue("0");
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationAsInt01Milliseconds() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(0L);
+        Instant value = MAPPER.readerFor(Instant.class)
+                .without(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
+                .readValue("0");
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationAsInt02Nanoseconds() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(123456789L, 0);
+        Instant value = MAPPER.readerFor(Instant.class)
+                .with(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
+                .readValue("123456789");
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationAsInt02Milliseconds() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(123456789L, 422000000);
+        Instant value = MAPPER.readerFor(Instant.class)
+                .without(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
+                .readValue("123456789422");
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationAsInt03Nanoseconds() throws Exception
+    {
+        Instant date = Instant.now();
+        date = date.minus(date.getNano(), ChronoUnit.NANOS);
+
+        Instant value = MAPPER.readerFor(Instant.class)
+                .with(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
+                .readValue(Long.toString(date.getEpochSecond()));
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationAsInt03Milliseconds() throws Exception
+    {
+        Instant date = Instant.now();
+        date = date.minus(date.getNano(), ChronoUnit.NANOS);
+
+        Instant value = MAPPER.readerFor(Instant.class)
+                .without(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
+                .readValue(Long.toString(date.toEpochMilli()));
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationAsString01() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(0L);
+        Instant value = MAPPER.readValue('"' + FORMATTER.format(date) + '"', Instant.class);
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationAsString02() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(123456789L, 183917322);
+        Instant value = MAPPER.readValue('"' + FORMATTER.format(date) + '"', Instant.class);
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationAsString03() throws Exception
+    {
+        Instant date = Instant.now();
+
+        Instant value = MAPPER.readValue('"' + FORMATTER.format(date) + '"', Instant.class);
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationWithTypeInfo01() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(123456789L, 183917322);
+        ObjectMapper m = newMapper()
+                .addMixIn(Temporal.class, MockObjectConfiguration.class);
+        Temporal value = m.readValue(
+                "[\"" + Instant.class.getName() + "\",123456789.183917322]", Temporal.class
+                );
+        assertTrue("The value should be an Instant.", value instanceof Instant);
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationWithTypeInfo02() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(123456789L, 0);
+        ObjectMapper m = newMapper()
+                .enable(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
+                .addMixIn(Temporal.class, MockObjectConfiguration.class);
+        Temporal value = m.readValue(
+                "[\"" + Instant.class.getName() + "\",123456789]", Temporal.class
+                );
+        assertTrue("The value should be an Instant.", value instanceof Instant);
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationWithTypeInfo03() throws Exception
+    {
+        Instant date = Instant.ofEpochSecond(123456789L, 422000000);
+        ObjectMapper m = newMapper()
+                .disable(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS)
+                .addMixIn(Temporal.class, MockObjectConfiguration.class);
+        Temporal value = m.readValue(
+                "[\"" + Instant.class.getName() + "\",123456789422]", Temporal.class
+                );
+
+        assertTrue("The value should be an Instant.", value instanceof Instant);
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testDeserializationWithTypeInfo04() throws Exception
+    {
+        Instant date = Instant.now();
+        ObjectMapper m = newMapper()
+                .addMixIn(Temporal.class, MockObjectConfiguration.class);
+        Temporal value = m.readValue(
+                "[\"" + Instant.class.getName() + "\",\"" + FORMATTER.format(date) + "\"]", Temporal.class
+                );
+        assertTrue("The value should be an Instant.", value instanceof Instant);
+        assertEquals("The value is not correct.", date, value);
+    }
+
+    @Test
+    public void testCustomPatternWithAnnotations01() throws Exception
+    {
+        final Wrapper input = new Wrapper(Instant.ofEpochMilli(0));
+        String json = MAPPER.writeValueAsString(input);
+        assertEquals(aposToQuotes("{'value':'1970-01-01T00:00:00Z'}"), json);
+
+        Wrapper result = MAPPER.readValue(json, Wrapper.class);
+        assertEquals(input.value, result.value);
+    }
+
+    // [datatype-jsr310#69]
+    @Test
+    public void testCustomPatternWithAnnotations02() throws Exception
+    {
+        //Test date is pushed one year after start of the epoch just to avoid possible issues with UTC-X TZs which could
+        //push the instant before tha start of the epoch
+        final Instant instant = ZonedDateTime.ofInstant(Instant.ofEpochMilli(0), ZoneId.of("UTC")).plusYears(1).toInstant();
+        final DateTimeFormatter formatter = DateTimeFormatter.ofPattern(CUSTOM_PATTERN);
+        final String valueInUTC = formatter.withZone(ZoneId.of("UTC")).format(instant);
+
+        final WrapperWithCustomPattern input = new WrapperWithCustomPattern(instant);
+        String json = MAPPER.writeValueAsString(input);
+
+        assertTrue("Instant in UTC timezone was not serialized as expected.",
+                json.contains(aposToQuotes("'valueInUTC':'" + valueInUTC + "'")));
+
+        WrapperWithCustomPattern result = MAPPER.readValue(json, WrapperWithCustomPattern.class);
+        assertEquals("Instant in UTC timezone was not deserialized as expected.",
+                input.valueInUTC, result.valueInUTC);
+    }
+
+    // [datatype-jsr310#16]
+    @Test
+    public void testDeserializationFromStringAsNumber() throws Exception
+    {
+        // First, baseline test with floating-point numbers
+        Instant inst = Instant.now();
+        String json = MAPPER.writer()
+                .with(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
+                .with(SerializationFeature.WRITE_DATE_TIMESTAMPS_AS_NANOSECONDS)
+                .writeValueAsString(inst);
+        Instant result = MAPPER.readValue(json, Instant.class);
+        assertNotNull(result);
+        assertEquals(result, inst);
+
+        // but then quoted as JSON String
+        result = MAPPER.readValue(String.format("\"%s\"", json),
+                Instant.class);
+        assertNotNull(result);
+        assertEquals(result, inst);
+    }
+
+    // [datatype-jsr310#79]
+    @Test
+    public void testRoundTripOfInstantAndJavaUtilDate() throws Exception
+    {
+        ObjectMapper mapper = newMapper();
+        mapper.configure(SerializationFeature.WRITE_DATE_TIMESTAMPS_AS_NANOSECONDS, false);
+        mapper.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
+        mapper.configure(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS, false);
+
+        Instant givenInstant = LocalDate.of(2016, 1, 1).atStartOfDay().atZone(ZoneOffset.UTC).toInstant();
+        String json = mapper.writeValueAsString(java.util.Date.from(givenInstant));
+        Instant actual = mapper.readValue(json, Instant.class);
+
+        assertEquals(givenInstant, actual);
+    }
+
+    // [jackson-modules-java8#18]
+    @Test
+    public void testDeserializationFromStringWithZeroZoneOffset01() throws Exception {
+        Instant date = Instant.now();
+        String json = formatWithZeroZoneOffset(date, "+00:00");
+        Instant result = MAPPER.readValue(json, Instant.class);
+        assertEquals("The value is not correct.", date, result);
+    }
+
+    @Test
+    public void testDeserializationFromStringWithZeroZoneOffset02() throws Exception {
+        Instant date = Instant.now();
+        String json = formatWithZeroZoneOffset(date, "+0000");
+        Instant result = MAPPER.readValue(json, Instant.class);
+        assertEquals("The value is not correct.", date, result);
+    }
+
+    @Test
+    public void testDeserializationFromStringWithZeroZoneOffset03() throws Exception {
+        Instant date = Instant.now();
+        String json = formatWithZeroZoneOffset(date, "+00");
+        Instant result = MAPPER.readValue(json, Instant.class);
+        assertEquals("The value is not correct.", date, result);
+    }
+
+    private String formatWithZeroZoneOffset(Instant date, String offset){
+        return '"' + FORMATTER.format(date).replaceFirst("Z$", offset) + '"';
+    }
+}
```

## Row 34
commit_url: https://github.com/mangstadt/ez-vcard/commit/dbd2518ee5bf6668bfa163fc44f7d6eb23592c3d
rm_type: Change Class Access Modifier
rm_description: Change Class Access Modifier public to private in class ezvcard.parameters.MediaTypeParameterTest.OtherTextMediaType
file_path: src/test/java/ezvcard/parameters/MediaTypeParameterTest.java
left_side: [{"filePath": "src/test/java/ezvcard/parameters/MediaTypeParameterTest.java", "startLine": 67, "endLine": 73, "startColumn": 2, "endColumn": 3, "codeElementType": "TYPE_DECLARATION", "description": "original class declaration", "codeElement": "ezvcard.parameters.MediaTypeParameterTest.OtherTextMediaType"}]
right_side: [{"filePath": "src/test/java/ezvcard/parameters/MediaTypeParameterTest.java", "startLine": 81, "endLine": 87, "startColumn": 2, "endColumn": 3, "codeElementType": "TYPE_DECLARATION", "description": "class declaration with changed access modifier", "codeElement": "ezvcard.parameters.MediaTypeParameterTest.OtherTextMediaType"}]

### Patch: src/test/java/ezvcard/parameters/MediaTypeParameterTest.java
```diff
@@ -1,10 +1,13 @@
 package ezvcard.parameters;
 
+import static org.junit.Assert.assertFalse;
+import static org.junit.Assert.assertNull;
+import static org.junit.Assert.assertTrue;
+
 import org.junit.Test;
-import static org.junit.Assert.*;
 
 /*
- Copyright (c) 2012, Michael Angstadt
+ Copyright (c) 2013, Michael Angstadt
  All rights reserved.
 
  Redistribution and use in source and binary forms, with or without
@@ -38,34 +41,45 @@
 public class MediaTypeParameterTest {
 	@Test
 	public void findByMediaType() {
-		TextMediaType expected = TextMediaType.xml;
-		TextMediaType actual = TextMediaType.findByMediaType("TEXT/xml", TextMediaType.class);
-		assertEquals(expected, actual);
+		TextMediaType param = MediaTypeParameter.findByMediaType("text/xml", TextMediaType.class);
+		assertTrue(TextMediaType.XML == param);
+	}
+
+	@Test
+	public void findByMediaType_not_found() {
+		TextMediaType param = MediaTypeParameter.findByMediaType("text/rtf", TextMediaType.class);
+		assertNull(param);
+	}
 
-		actual = TextMediaType.findByMediaType("text/rtf", TextMediaType.class);
-		assertNull(actual);
+	@Test
+	public void findByMediaType_case_insensitive() {
+		TextMediaType param = MediaTypeParameter.findByMediaType("tExT/xml", TextMediaType.class);
+		assertTrue(TextMediaType.XML == param);
 	}
 
 	@Test
 	public void equals() {
 		TextMediaType html = new TextMediaType("html", "text/html", "html");
-		assertTrue(html.equals(TextMediaType.html));
+		assertTrue(html.equals(TextMediaType.HTML));
+	}
 
-		assertFalse(TextMediaType.plain.equals(OtherTextMediaType.plain));
+	@Test
+	public void equals_same_values_different_class() {
+		assertFalse(TextMediaType.PLAIN.equals(OtherTextMediaType.PLAIN));
 	}
 
-	public static class TextMediaType extends MediaTypeParameter {
-		public static final TextMediaType plain = new TextMediaType("plain", "text/plain", "txt");
-		public static final TextMediaType xml = new TextMediaType("xml", "text/xml", "xml");
-		public static final TextMediaType html = new TextMediaType("html", "text/html", "html");
+	private static class TextMediaType extends MediaTypeParameter {
+		public static final TextMediaType PLAIN = new TextMediaType("plain", "text/plain", "txt");
+		public static final TextMediaType XML = new TextMediaType("xml", "text/xml", "xml");
+		public static final TextMediaType HTML = new TextMediaType("html", "text/html", "html");
 
 		public TextMediaType(String value, String mediaType, String extension) {
 			super(value, mediaType, extension);
 		}
 	}
 
-	public static class OtherTextMediaType extends MediaTypeParameter {
-		public static final OtherTextMediaType plain = new OtherTextMediaType("plain", "text/plain", "txt");
+	private static class OtherTextMediaType extends MediaTypeParameter {
+		public static final OtherTextMediaType PLAIN = new OtherTextMediaType("plain", "text/plain", "txt");
 
 		public OtherTextMediaType(String value, String mediaType, String extension) {
 			super(value, mediaType, extension);
```

## Row 35
commit_url: https://github.com/PixelExperience/frameworks_base/commit/11ac7831e3ad143a2337953487b69f5a78988dc6
rm_type: Parameterize Variable
rm_description: Parameterize Variable canonicalCallback : ISoundTriggerHw2.ModelCallback to canonicalCallback : ISoundTriggerHw2.ModelCallback in method private loadPhraseModel_2_0(canonicalCallback ISoundTriggerHw2.ModelCallback) : int from class com.android.server.soundtrigger_middleware.SoundHw2CompatTest
file_path: services/tests/servicestests/src/com/android/server/soundtrigger_middleware/SoundHw2CompatTest.java
left_side: [{"filePath": "services/tests/servicestests/src/com/android/server/soundtrigger_middleware/SoundHw2CompatTest.java", "startLine": 382, "endLine": 383, "startColumn": 40, "endColumn": 54, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "original variable declaration", "codeElement": "canonicalCallback : ISoundTriggerHw2.ModelCallback"}, {"filePath": "services/tests/servicestests/src/com/android/server/soundtrigger_middleware/SoundHw2CompatTest.java", "startLine": 384, "endLine": 385, "startColumn": 9, "endColumn": 37, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "services/tests/servicestests/src/com/android/server/soundtrigger_middleware/SoundHw2CompatTest.java", "startLine": 392, "endLine": 392, "startColumn": 9, "endColumn": 76, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}]
right_side: [{"filePath": "services/tests/servicestests/src/com/android/server/soundtrigger_middleware/SoundHw2CompatTest.java", "startLine": 368, "endLine": 368, "startColumn": 37, "endColumn": 85, "codeElementType": "SINGLE_VARIABLE_DECLARATION", "description": "renamed variable declaration", "codeElement": "canonicalCallback : ISoundTriggerHw2.ModelCallback"}, {"filePath": "services/tests/servicestests/src/com/android/server/soundtrigger_middleware/SoundHw2CompatTest.java", "startLine": 389, "endLine": 390, "startColumn": 9, "endColumn": 37, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}, {"filePath": "services/tests/servicestests/src/com/android/server/soundtrigger_middleware/SoundHw2CompatTest.java", "startLine": 397, "endLine": 397, "startColumn": 9, "endColumn": 76, "codeElementType": "EXPRESSION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}]

### Patch: services/tests/servicestests/src/com/android/server/soundtrigger_middleware/SoundHw2CompatTest.java
```diff
@@ -187,7 +187,8 @@ public void testGetProperties() throws Exception {
         }
     }
 
-    private void testLoadGenericModel_2_0() throws Exception {
+    private int loadGenericModel_2_0(ISoundTriggerHw2.ModelCallback canonicalCallback)
+            throws Exception {
         final int handle = 29;
         ArgumentCaptor<android.hardware.soundtrigger.V2_0.ISoundTriggerHw.SoundModel>
                 modelCaptor =
@@ -207,8 +208,6 @@ private void testLoadGenericModel_2_0() throws Exception {
             return null;
         }).when(mHalDriver).loadSoundModel(any(), any(), anyInt(), any());
 
-        ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
-                ISoundTriggerHw2.ModelCallback.class);
         assertEquals(handle, mCanonical.loadSoundModel(TestUtil.createGenericSoundModel_2_1(),
                 canonicalCallback));
 
@@ -217,9 +216,11 @@ private void testLoadGenericModel_2_0() throws Exception {
 
         TestUtil.validateGenericSoundModel_2_0(modelCaptor.getValue());
         validateCallback_2_0(callbackCaptor.getValue(), canonicalCallback);
+        return handle;
     }
 
-    private void testLoadGenericModel_2_1() throws Exception {
+    private int loadGenericModel_2_1(ISoundTriggerHw2.ModelCallback canonicalCallback)
+            throws Exception {
         final android.hardware.soundtrigger.V2_1.ISoundTriggerHw driver_2_1 =
                 (android.hardware.soundtrigger.V2_1.ISoundTriggerHw) mHalDriver;
 
@@ -242,8 +243,6 @@ private void testLoadGenericModel_2_1() throws Exception {
             return null;
         }).when(driver_2_1).loadSoundModel_2_1(any(), any(), anyInt(), any());
 
-        ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
-                ISoundTriggerHw2.ModelCallback.class);
         assertEquals(handle, mCanonical.loadSoundModel(TestUtil.createGenericSoundModel_2_1(),
                 canonicalCallback));
 
@@ -253,9 +252,11 @@ private void testLoadGenericModel_2_1() throws Exception {
 
         TestUtil.validateGenericSoundModel_2_1(modelCaptor.getValue());
         validateCallback_2_1(callbackCaptor.getValue(), canonicalCallback);
+        return handle;
     }
 
-    private void testLoadGenericModel_2_4() throws Exception {
+    private int loadGenericModel_2_4(ISoundTriggerHw2.ModelCallback canonicalCallback)
+            throws Exception {
         final android.hardware.soundtrigger.V2_4.ISoundTriggerHw driver_2_4 =
                 (android.hardware.soundtrigger.V2_4.ISoundTriggerHw) mHalDriver;
 
@@ -278,8 +279,6 @@ private void testLoadGenericModel_2_4() throws Exception {
             return null;
         }).when(driver_2_4).loadSoundModel_2_4(any(), any(), any());
 
-        ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
-                ISoundTriggerHw2.ModelCallback.class);
         assertEquals(handle, mCanonical.loadSoundModel(TestUtil.createGenericSoundModel_2_1(),
                 canonicalCallback));
 
@@ -288,36 +287,43 @@ private void testLoadGenericModel_2_4() throws Exception {
 
         TestUtil.validateGenericSoundModel_2_1(modelCaptor.getValue());
         validateCallback_2_4(callbackCaptor.getValue(), canonicalCallback);
+        return handle;
     }
 
-    @Test
-    public void testLoadGenericModel() throws Exception {
+    private int loadGenericModel(ISoundTriggerHw2.ModelCallback canonicalCallback)
+            throws Exception {
         if (mHalDriver instanceof android.hardware.soundtrigger.V2_4.ISoundTriggerHw) {
-            testLoadGenericModel_2_4();
+            return loadGenericModel_2_4(canonicalCallback);
         } else if (mHalDriver instanceof android.hardware.soundtrigger.V2_1.ISoundTriggerHw) {
-            testLoadGenericModel_2_1();
+            return loadGenericModel_2_1(canonicalCallback);
         } else {
-            testLoadGenericModel_2_0();
+            return loadGenericModel_2_0(canonicalCallback);
         }
     }
 
+    @Test
+    public void testLoadGenericModel() throws Exception {
+        ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
+                ISoundTriggerHw2.ModelCallback.class);
+        loadGenericModel(canonicalCallback);
+    }
+
     @Test
     public void testMaxModels() throws Exception {
         assumeFalse(mHalDriver instanceof android.hardware.soundtrigger.V2_4.ISoundTriggerHw);
 
+        ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
+                ISoundTriggerHw2.ModelCallback.class);
         final int maxModels = TestUtil.createDefaultProperties(false).maxSoundModels;
         // Load as many models as we're allowed.
         for (int i = 0; i < maxModels; ++i) {
-            testLoadGenericModel();
+            loadGenericModel(canonicalCallback);
             verifyNoMoreInteractions(mHalDriver);
             clearInvocations(mHalDriver);
         }
 
         // Now try to load an additional one and expect failure without invoking the underlying
         // driver.
-        ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
-                ISoundTriggerHw2.ModelCallback.class);
-
         try {
             mCanonical.loadPhraseSoundModel(TestUtil.createPhraseSoundModel_2_1(),
                     canonicalCallback);
@@ -359,7 +365,8 @@ public void testLoadGenericModelBusy() throws Exception {
         }
     }
 
-    private void testLoadPhraseModel_2_0() throws Exception {
+    private int loadPhraseModel_2_0(ISoundTriggerHw2.ModelCallback canonicalCallback)
+            throws Exception {
         final int handle = 29;
         ArgumentCaptor<android.hardware.soundtrigger.V2_0.ISoundTriggerHw.PhraseSoundModel>
                 modelCaptor =
@@ -379,8 +386,6 @@ private void testLoadPhraseModel_2_0() throws Exception {
             return null;
         }).when(mHalDriver).loadPhraseSoundModel(any(), any(), anyInt(), any());
 
-        ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
-                ISoundTriggerHw2.ModelCallback.class);
         assertEquals(handle, mCanonical.loadPhraseSoundModel(TestUtil.createPhraseSoundModel_2_1(),
                 canonicalCallback));
 
@@ -390,9 +395,11 @@ private void testLoadPhraseModel_2_0() throws Exception {
 
         TestUtil.validatePhraseSoundModel_2_0(modelCaptor.getValue());
         validateCallback_2_0(callbackCaptor.getValue(), canonicalCallback);
+        return handle;
     }
 
-    private void testLoadPhraseModel_2_1() throws Exception {
+    private int loadPhraseModel_2_1(ISoundTriggerHw2.ModelCallback canonicalCallback)
+            throws Exception {
         final android.hardware.soundtrigger.V2_1.ISoundTriggerHw driver_2_1 =
                 (android.hardware.soundtrigger.V2_1.ISoundTriggerHw) mHalDriver;
 
@@ -415,8 +422,6 @@ private void testLoadPhraseModel_2_1() throws Exception {
             return null;
         }).when(driver_2_1).loadPhraseSoundModel_2_1(any(), any(), anyInt(), any());
 
-        ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
-                ISoundTriggerHw2.ModelCallback.class);
         assertEquals(handle, mCanonical.loadPhraseSoundModel(TestUtil.createPhraseSoundModel_2_1(),
                 canonicalCallback));
 
@@ -426,9 +431,11 @@ private void testLoadPhraseModel_2_1() throws Exception {
 
         TestUtil.validatePhraseSoundModel_2_1(modelCaptor.getValue());
         validateCallback_2_1(callbackCaptor.getValue(), canonicalCallback);
+        return handle;
     }
 
-    private void testLoadPhraseModel_2_4() throws Exception {
+    private int loadPhraseModel_2_4(ISoundTriggerHw2.ModelCallback canonicalCallback)
+            throws Exception {
         final android.hardware.soundtrigger.V2_4.ISoundTriggerHw driver_2_4 =
                 (android.hardware.soundtrigger.V2_4.ISoundTriggerHw) mHalDriver;
 
@@ -451,8 +458,6 @@ private void testLoadPhraseModel_2_4() throws Exception {
             return null;
         }).when(driver_2_4).loadPhraseSoundModel_2_4(any(), any(), any());
 
-        ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
-                ISoundTriggerHw2.ModelCallback.class);
         assertEquals(handle, mCanonical.loadPhraseSoundModel(TestUtil.createPhraseSoundModel_2_1(),
                 canonicalCallback));
 
@@ -461,19 +466,26 @@ private void testLoadPhraseModel_2_4() throws Exception {
 
         TestUtil.validatePhraseSoundModel_2_1(modelCaptor.getValue());
         validateCallback_2_4(callbackCaptor.getValue(), canonicalCallback);
+        return handle;
     }
 
-    @Test
-    public void testLoadPhraseModel() throws Exception {
+    public int loadPhraseModel(ISoundTriggerHw2.ModelCallback canonicalCallback) throws Exception {
         if (mHalDriver instanceof android.hardware.soundtrigger.V2_4.ISoundTriggerHw) {
-            testLoadPhraseModel_2_4();
+            return loadPhraseModel_2_4(canonicalCallback);
         } else if (mHalDriver instanceof android.hardware.soundtrigger.V2_1.ISoundTriggerHw) {
-            testLoadPhraseModel_2_1();
+            return loadPhraseModel_2_1(canonicalCallback);
         } else {
-            testLoadPhraseModel_2_0();
+            return loadPhraseModel_2_0(canonicalCallback);
         }
     }
 
+    @Test
+    public void testLoadPhraseModel() throws Exception {
+        ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
+                ISoundTriggerHw2.ModelCallback.class);
+        loadPhraseModel(canonicalCallback);
+    }
+
     private void testLoadPhraseModelBusy_2_4() throws Exception {
         final android.hardware.soundtrigger.V2_4.ISoundTriggerHw driver_2_4 =
                 (android.hardware.soundtrigger.V2_4.ISoundTriggerHw) mHalDriver;
@@ -513,23 +525,10 @@ public void testUnloadModel() throws Exception {
     }
 
     private void testStartRecognition_2_0() throws Exception {
-        final int handle = 65;
-
         // First load (this registers the callback).
-        doAnswer(invocation -> {
-            android.hardware.soundtrigger.V2_0.ISoundTriggerHw.loadSoundModelCallback
-                    resultCallback = invocation.getArgument(3);
-
-            // This is the return of this method.
-            resultCallback.onValues(0, handle);
-            return null;
-        }).when(mHalDriver).loadSoundModel(any(), any(), anyInt(), any());
-
         ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
                 ISoundTriggerHw2.ModelCallback.class);
-        assertEquals(handle, mCanonical.loadSoundModel(TestUtil.createGenericSoundModel_2_1(),
-                canonicalCallback));
-        verify(mHalDriver).loadSoundModel(any(), any(), anyInt(), any());
+        final int handle = loadGenericModel(canonicalCallback);
 
         // Then start.
         ArgumentCaptor<android.hardware.soundtrigger.V2_0.ISoundTriggerHw.RecognitionConfig>
@@ -556,23 +555,10 @@ private void testStartRecognition_2_1() throws Exception {
         final android.hardware.soundtrigger.V2_1.ISoundTriggerHw driver_2_1 =
                 (android.hardware.soundtrigger.V2_1.ISoundTriggerHw) mHalDriver;
 
-        final int handle = 68;
-
         // First load (this registers the callback).
-        doAnswer(invocation -> {
-            android.hardware.soundtrigger.V2_1.ISoundTriggerHw.loadSoundModel_2_1Callback
-                    resultCallback = invocation.getArgument(3);
-
-            // This is the return of this method.
-            resultCallback.onValues(0, handle);
-            return null;
-        }).when(driver_2_1).loadSoundModel_2_1(any(), any(), anyInt(), any());
-
         ISoundTriggerHw2.ModelCallback canonicalCallback = mock(
                 ISoundTriggerHw2.ModelCallback.class);
-        assertEquals(handle, mCanonical.loadSoundModel(TestUtil.createGenericSoundModel_2_1(),
-                canonicalCallback));
-        verify(driver_2_1).loadSoundModel_2_1(any(), any(), anyInt(), any());
+        final int handle = loadGenericModel(canonicalCallback);
 
         // Then start.
         ArgumentCaptor<android.hardware.soundtrigger.V2_1.ISoundTriggerHw.RecognitionConfig>
@@ -876,6 +862,8 @@ private static void validateCallback_2_0(
             TestUtil.validatePhraseRecognitionEvent_2_1(eventCaptor.getValue(), handle, status,
                     666);
         }
+        verifyNoMoreInteractions(canonicalCallback);
+        clearInvocations(canonicalCallback);
     }
 
     private void validateCallback_2_1(
@@ -910,6 +898,8 @@ private void validateCallback_2_1(
             TestUtil.validatePhraseRecognitionEvent_2_1(eventCaptor.getValue(), handle, status,
                     888);
         }
+        verifyNoMoreInteractions(canonicalCallback);
+        clearInvocations(canonicalCallback);
     }
 
     private void validateCallback_2_4(
@@ -950,5 +940,7 @@ private void validateCallback_2_4(
             hwCallback.modelUnloaded(handle);
             verify(canonicalCallback).modelUnloaded(handle);
         }
+        verifyNoMoreInteractions(canonicalCallback);
+        clearInvocations(canonicalCallback);
     }
 }
```

## Row 36
commit_url: https://github.com/NitorCreations/nflow/commit/39a2a85f995c83c658c173898783217be849bf86
rm_type: Change Return Type
rm_description: Change Return Type String to T in method protected updateWorkflowInstance(instanceId long, request UpdateWorkflowInstanceRequest, responseClass Class<T>) : T from class io.nflow.tests.AbstractNflowTest
file_path: nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java
left_side: [{"filePath": "nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java", "startLine": 207, "endLine": 207, "startColumn": 13, "endColumn": 19, "codeElementType": "TYPE", "description": "original return type", "codeElement": "String"}, {"filePath": "nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java", "startLine": 207, "endLine": 209, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "protected updateWorkflowInstance(instanceId long, request UpdateWorkflowInstanceRequest) : String"}]
right_side: [{"filePath": "nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java", "startLine": 199, "endLine": 199, "startColumn": 17, "endColumn": 18, "codeElementType": "TYPE", "description": "changed return type", "codeElement": "T"}, {"filePath": "nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java", "startLine": 199, "endLine": 201, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "method declaration with changed return type", "codeElement": "protected updateWorkflowInstance(instanceId long, request UpdateWorkflowInstanceRequest, responseClass Class<T>) : T"}]

### Patch: nflow-tests/src/test/java/io/nflow/tests/AbstractNflowTest.java
```diff
@@ -49,11 +49,11 @@
 @ExtendWith({ NflowServerExtension.class, SpringExtension.class, SkipTestMethodsAfterFirstFailureExtension.class })
 @ContextConfiguration(classes = { RestClientConfiguration.class, PropertiesConfiguration.class })
 public abstract class AbstractNflowTest {
-  protected WebClient workflowInstanceResource;
-  protected WebClient workflowInstanceIdResource;
-  protected WebClient workflowDefinitionResource;
-  protected WebClient statisticsResource;
-  protected WebClient maintenanceResource;
+  private WebClient workflowInstanceResource;
+  private WebClient workflowInstanceIdResource;
+  private WebClient workflowDefinitionResource;
+  private WebClient statisticsResource;
+  private WebClient maintenanceResource;
 
   private final NflowServerConfig server;
 
@@ -109,24 +109,24 @@ protected SetSignalResponse setSignal(long instanceId, int signal, String reason
     return getInstanceResource(instanceId).path("signal").put(request, SetSignalResponse.class);
   }
 
-  private WebClient getInstanceResource(long instanceId) {
-    WebClient client = fromClient(workflowInstanceResource, true).path(Long.toString(instanceId));
-    return client;
+  protected WebClient getInstanceResource() {
+    return fromClient(workflowInstanceResource, true);
+  }
+
+  protected WebClient getInstanceResource(long instanceId) {
+    return getInstanceResource().path(Long.toString(instanceId));
   }
 
   protected WebClient getInstanceIdResource(long instanceId) {
-    WebClient client = fromClient(workflowInstanceIdResource, true).path(Long.toString(instanceId));
-    return client;
+    return fromClient(workflowInstanceIdResource, true).path(Long.toString(instanceId));
   }
 
   protected ListWorkflowDefinitionResponse[] getWorkflowDefinitions() {
-    WebClient client = fromClient(workflowDefinitionResource, true);
-    return client.get(ListWorkflowDefinitionResponse[].class);
+    return fromClient(workflowDefinitionResource, true).get(ListWorkflowDefinitionResponse[].class);
   }
 
   public StatisticsResponse getStatistics() {
-    WebClient client = fromClient(statisticsResource, true);
-    return client.get(StatisticsResponse.class);
+    return fromClient(statisticsResource, true).get(StatisticsResponse.class);
   }
 
   public WorkflowDefinitionStatisticsResponse getDefinitionStatistics(String definitionType) {
@@ -173,7 +173,7 @@ public void validate(ListWorkflowInstanceResponse workflowInstance) {
   }
 
   protected CreateWorkflowInstanceResponse createWorkflowInstance(CreateWorkflowInstanceRequest request) {
-    return makeWorkflowInstanceQuery(request, CreateWorkflowInstanceResponse.class);
+    return fromClient(workflowInstanceResource, true).put(request, CreateWorkflowInstanceResponse.class);
   }
 
   protected ObjectMapper nflowObjectMapper() {
@@ -183,33 +183,21 @@ protected ObjectMapper nflowObjectMapper() {
     return mapper;
   }
 
-  protected MaintenanceResponse archiveAllFinishedWorkflows() {
-    MaintenanceRequest req = new MaintenanceRequest();
-    req.archiveWorkflows = new MaintenanceRequestItem();
-    req.archiveWorkflows.olderThanPeriod = seconds(0);
-    return assertTimeoutPreemptively(ofSeconds(15),
-        () -> fromClient(maintenanceResource).type(APPLICATION_JSON_TYPE).post(req, MaintenanceResponse.class));
-  }
-
   protected MaintenanceResponse deleteAllFinishedWorkflows() {
     MaintenanceRequest req = new MaintenanceRequest();
     req.deleteWorkflows = new MaintenanceRequestItem();
     req.deleteWorkflows.olderThanPeriod = seconds(0);
     req.deleteArchivedWorkflows = req.deleteWorkflows;
-    return assertTimeoutPreemptively(ofSeconds(15),
-        () -> fromClient(maintenanceResource).type(APPLICATION_JSON_TYPE).post(req, MaintenanceResponse.class));
-  }
-
-  protected long insertWorkflow(CreateWorkflowInstanceRequest req) {
-    return fromClient(workflowInstanceResource, true).put(req, CreateWorkflowInstanceResponse.class).id;
+    return doMaintenance(req);
   }
 
-  protected String updateWorkflowInstance(long instanceId, UpdateWorkflowInstanceRequest request) {
-    return getInstanceIdResource(instanceId).put(request, String.class);
+  protected MaintenanceResponse doMaintenance(MaintenanceRequest req) {
+    return assertTimeoutPreemptively(ofSeconds(15),
+        () -> fromClient(maintenanceResource).type(APPLICATION_JSON_TYPE).post(req, MaintenanceResponse.class));
   }
 
-  private <T> T makeWorkflowInstanceQuery(CreateWorkflowInstanceRequest request, Class<T> responseClass) {
-    return fromClient(workflowInstanceResource, true).put(request, responseClass);
+  protected <T> T updateWorkflowInstance(long instanceId, UpdateWorkflowInstanceRequest request, Class<T> responseClass) {
+    return getInstanceIdResource(instanceId).put(request, responseClass);
   }
 
   public interface WorkflowInstanceValidator {
```

## Row 37
commit_url: https://github.com/errai/errai/commit/058e50b10da2d9fc3fcd7736f2d1215c591f9c42
rm_type: Split Method
rm_description: Split Method public testForeachLoop() : void to [public testForeachLoopWithStringInParameterizedList() : void, public testForeachLoopWithStringInArray() : void] in class org.jboss.errai.ioc.tests.rebind.LoopBuilderTest
file_path: errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/LoopBuilderTest.java
left_side: [{"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/LoopBuilderTest.java", "startLine": 51, "endLine": 89, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public testForeachLoop() : void"}]
right_side: [{"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/LoopBuilderTest.java", "startLine": 50, "endLine": 60, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "split method declaration", "codeElement": "public testForeachLoopWithStringInParameterizedList() : void"}, {"filePath": "errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/LoopBuilderTest.java", "startLine": 62, "endLine": 76, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "split method declaration", "codeElement": "public testForeachLoopWithStringInArray() : void"}]

### Patch: errai-ioc/src/test/java/org/jboss/errai/ioc/tests/rebind/LoopBuilderTest.java
```diff
@@ -30,7 +30,6 @@
 import org.jboss.errai.ioc.rebind.ioc.codegen.Context;
 import org.jboss.errai.ioc.rebind.ioc.codegen.Statement;
 import org.jboss.errai.ioc.rebind.ioc.codegen.Variable;
-import org.jboss.errai.ioc.rebind.ioc.codegen.builder.LoopBuilder;
 import org.jboss.errai.ioc.rebind.ioc.codegen.builder.impl.ContextBuilder;
 import org.jboss.errai.ioc.rebind.ioc.codegen.builder.impl.StatementBuilder;
 import org.jboss.errai.ioc.rebind.ioc.codegen.exception.InvalidExpressionException;
@@ -49,13 +48,7 @@
 public class LoopBuilderTest extends AbstractStatementBuilderTest implements LoopBuilderTestResult {
 
   @Test
-  public void testForeachLoop() throws Exception {
-    Statement createObject = StatementBuilder.create()
-        .newObject(String.class);
-
-    Statement createAnotherObject = StatementBuilder.create()
-        .newObject(Object.class);
-
+  public void testForeachLoopWithStringInParameterizedList() {
     String foreachWithListOfStrings = StatementBuilder.create()
         .addVariable("list", new TypeLiteral<List<String>>() {})
         .loadVariable("list")
@@ -64,7 +57,12 @@ public void testForeachLoop() throws Exception {
 
     assertEquals("failed to generate foreach loop using a List<String>",
         FOREACH_RESULT_STRING_IN_LIST, foreachWithListOfStrings);
-    
+  }
+
+  @Test
+  public void testForeachLoopWithStringInArray() {
+    Statement createObject = StatementBuilder.create().newObject(String.class);
+
     String foreachWithStringArray = StatementBuilder.create()
         .addVariable("list", String[].class)
         .loadVariable("list")
@@ -75,7 +73,13 @@ public void testForeachLoop() throws Exception {
 
     assertEquals("failed to generate foreach loop using a String[]",
         FOREACH_RESULT_STRING_IN_ARRAY_ONE_STATEMENT, foreachWithStringArray);
-    
+  }
+
+  @Test
+  public void testForeachLoopWithStringInList() {
+    Statement createObject = StatementBuilder.create().newObject(String.class);
+    Statement createAnotherObject = StatementBuilder.create().newObject(Object.class);
+
     String foreachWithList = StatementBuilder.create()
         .addVariable("list", List.class)
         .loadVariable("list")
@@ -89,7 +93,7 @@ public void testForeachLoop() throws Exception {
   }
 
   @Test
-  public void testForeachLoopWithUndefinedCollection() throws Exception {
+  public void testForeachLoopWithUndefinedCollection() {
     try {
       StatementBuilder.create()
           .loadVariable("list")
@@ -104,7 +108,7 @@ public void testForeachLoopWithUndefinedCollection() throws Exception {
   }
 
   @Test
-  public void testForeachLoopWithProvidedLoopVarType() throws Exception {
+  public void testForeachLoopWithProvidedLoopVarType() {
     Builder builder = StatementBuilder.create()
         .addVariable("list", new TypeLiteral<List<String>>() {})
         .loadVariable("list")
@@ -129,7 +133,7 @@ public void testForeachLoopWithProvidedLoopVarType() throws Exception {
   }
 
   @Test
-  public void testNestedForeachLoops() throws Exception {
+  public void testNestedForeachLoops() {
     Statement createObject = StatementBuilder.create().newObject(String.class);
 
     Builder outerLoop = StatementBuilder.create()
@@ -150,7 +154,7 @@ public void testNestedForeachLoops() throws Exception {
   }
 
   @Test
-  public void testForeachLoopWithInvalidCollectionType() throws Exception {
+  public void testForeachLoopWithInvalidCollectionType() {
 
     try {
       StatementBuilder.create()
@@ -167,7 +171,7 @@ public void testForeachLoopWithInvalidCollectionType() throws Exception {
   }
 
   @Test
-  public void testForeachLoopWithInvoke() throws Exception {
+  public void testForeachLoopWithInvoke() {
     Builder loop = StatementBuilder.create()
         .addVariable("map", Map.class)
         .loadVariable("map")
@@ -179,29 +183,32 @@ public void testForeachLoopWithInvoke() throws Exception {
   }
 
   @Test
-  public void testForeachLoopWithLiterals() throws Exception {
-    LoopBuilder loopBuilder = StatementBuilder.create()
+  public void testForeachLoopWithLiterals() {
+    String s = StatementBuilder.create()
         .loadLiteral(new String[] { "s1", "s2" })
         .foreach("s")
         .append(StatementBuilder.create().loadVariable("s").invoke("getBytes"))
-        .finish();
+        .finish().toJavaString();
 
     assertEquals("failed to generate foreach loop using a literal String array",
-        FOREACH_RESULT_LITERAL_STRING_ARRAY, loopBuilder.toJavaString());
+        FOREACH_RESULT_LITERAL_STRING_ARRAY, s);
+  }
 
+  @Test
+  public void testForeachLoopWithProvidedContext() {
     Context c = ContextBuilder.create().addVariable(Variable.create("s", String.class)).getContext();
-    loopBuilder = StatementBuilder.create(c)
+    String s = StatementBuilder.create(c)
         .loadLiteral(new String[] { "s1", "s2" })
         .foreach("s")
         .append(StatementBuilder.create().loadVariable("s").invoke("getBytes"))
-        .finish();
+        .finish().toJavaString();
 
     assertEquals("failed to generate foreach loop using a literal String array",
-        FOREACH_RESULT_LITERAL_STRING_ARRAY, loopBuilder.toJavaString());
+        FOREACH_RESULT_LITERAL_STRING_ARRAY, s);
   }
 
   @Test
-  public void testWhileLoopWithInvalidExpressions() {
+  public void testWhileLoopWithInvalidExpression() {
     try {
       StatementBuilder.create()
           .addVariable("n", Integer.class)
@@ -229,72 +236,100 @@ public void testWhileLoopWithInvalidExpressions() {
   }
 
   @Test
-  public void testWhileLoop() {
+  public void testWhileLoopWithEmptyExpressionWithoutBody() {
     String s = StatementBuilder.create()
         .addVariable("b", Boolean.class)
         .loadVariable("b")
         .while_().finish().toJavaString();
 
     assertEquals("failed to generate empty while loop", WHILE_RESULT_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testWhileLoopWithEmptyExpressionWithBody() {
+    String s = StatementBuilder.create()
         .addVariable("b", Boolean.class)
         .loadVariable("b")
         .while_()
           .append(StatementBuilder.create().loadVariable("b").assignValue(false))
         .finish().toJavaString();
 
     assertEquals("failed to generate while loop with body", WHILE_RESULT_WITH_BODY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testWhileLoopWithNullCheck() {
+    String s = StatementBuilder.create()
         .addVariable("str", String.class)
         .loadVariable("str")
         .while_(BooleanOperator.NotEquals, null)
         .finish().toJavaString();
 
-    assertEquals("failed to generate while loop with rhs (null check) and body", 
+    assertEquals("failed to generate while loop with rhs (null check) and no body",
         WHILE_RESULT_RHS_NULL_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testWhileLoopWithExpression() {
+    String s = StatementBuilder.create()
         .addVariable("str", String.class)
         .loadVariable("str")
         .invoke("length")
         .while_(BooleanOperator.GreaterThanOrEqual, 2)
         .finish().toJavaString();
 
-    assertEquals("failed to generate while loop with rhs and body", WHILE_RESULT_RHS_EMPTY, s);
+    assertEquals("failed to generate while loop with rhs and no body", WHILE_RESULT_RHS_EMPTY, s);
+  }
+
+  @Test
+  public void testWhileLoopUnchainedWithExpression() {
+    Context ctx = Context.create().addVariable("str", String.class);
+    String s = StatementBuilder.create(ctx)
+        .while_(Bool.expr(Stmt.create().loadVariable("str").invoke("length"), BooleanOperator.GreaterThanOrEqual, 2))
+        .finish().toJavaString();
 
-    s = StatementBuilder.create()
+    assertEquals("failed to generate while loop with rhs and no body", WHILE_RESULT_RHS_EMPTY, s);
+  }
+
+  @Test
+  public void testWhileLoopWithNestedExpressions() {
+    String s = StatementBuilder.create()
         .addVariable("str", String.class)
         .while_(Bool.expr(
             Bool.expr(Variable.get("str"), BooleanOperator.NotEquals, null),
             BooleanOperator.And,
             Bool.expr(Stmt.create().loadVariable("str").invoke("length"), BooleanOperator.GreaterThan, 0)))
         .finish().toJavaString();
 
-    assertEquals("failed to generate while loop with nested expression", WHILE_RESULT_NESTED_EMPTY, s);
+    assertEquals("failed to generate while loop with nested expression and no body", WHILE_RESULT_NESTED_EMPTY, s);
   }
 
   @Test
-  public void testForLoop() {
+  public void testForLoopWithoutInitializer() {
     String s = StatementBuilder.create()
         .addVariable("i", Integer.class)
         .for_(Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100))
         .finish().toJavaString();
 
     assertEquals("failed to generate for loop without initializer",
         FOR_RESULT_NO_INITIALIZER_NO_COUNTING_EXP_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testForLoopWithInitializer() {
+    String s = StatementBuilder.create()
         .addVariable("i", Integer.class)
         .for_(StatementBuilder.create().loadVariable("i").assignValue(0),
             Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100))
         .finish().toJavaString();
 
     assertEquals("failed to generate for loop with initializer",
         FOR_RESULT_INITIALIZER_NO_COUNTING_EXP_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testForLoopWithInitializerAndCountingExpression() {
+    String s = StatementBuilder.create()
         .addVariable("i", Integer.class)
         .for_(StatementBuilder.create().loadVariable("i").assignValue(0),
             Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100),
@@ -303,17 +338,23 @@ public void testForLoop() {
 
     assertEquals("failed to generate for loop with initializer and counting expression",
         FOR_RESULT_INITIALIZER_COUNTING_EXP_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testForLoopWithInitializerAndChainedLhs() {
+    String s = StatementBuilder.create()
         .addVariable("i", Integer.class, 0)
         .loadVariable("i")
         .for_(Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100))
         .finish().toJavaString();
 
     assertEquals("failed to generate for loop with initializer and chained lhs",
         FOR_RESULT_CHAINED_INITIALIZER_NO_COUNTING_EXP_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testForLoopWithInitializerAndCountingExpressionAndChainedLhs() {
+    String s = StatementBuilder.create()
         .addVariable("i", Integer.class, 0)
         .loadVariable("i")
         .for_(Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100),
@@ -322,8 +363,11 @@ public void testForLoop() {
 
     assertEquals("failed to generate for loop with initializer, counting expression and chained lhs",
         FOR_RESULT_CHAINED_INITIALIZER_COUNTING_EXP_EMPTY, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testForLoopUnchainedWithDeclaringInitializerAndCountingExpression() {
+    String s = StatementBuilder.create()
         .for_(ContextBuilder.create().declareVariable("i", int.class).initializeWith(0),
             Bool.expr(Variable.get("i"), BooleanOperator.LessThan, 100),
             StatementBuilder.create().loadVariable("i").assignValue(AssignmentOperator.PreIncrementAssign, 1))
@@ -335,7 +379,7 @@ public void testForLoop() {
   }
 
   @Test
-  public void testDoWhileLoop() {
+  public void testDoWhileLoopWithoutOperatorAndRhs() {
     String s = StatementBuilder.create()
         .addVariable("b", Boolean.class)
         .do_()
@@ -344,9 +388,27 @@ public void testDoWhileLoop() {
         .while_(Bool.expr(Variable.get("b")))
         .toJavaString();
 
-    assertEquals("failed to generate for do whileloop with simple expression", DOWHILE_RESULT_SIMPLE_EXPRESSION, s);
+    assertEquals("failed to generate for do whileloop with simple expression (no operator and rhs)",
+        DOWHILE_RESULT_SIMPLE_EXPRESSION, s);
+  }
 
-    s = StatementBuilder.create()
+  @Test
+  public void testDoWhileLoopUnchainedWithoutOperatorAndRhs() {
+    Context ctx = Context.create().addVariable("b", Boolean.class);
+    String s = StatementBuilder.create(ctx)
+        .do_()
+          .append(StatementBuilder.create().loadVariable("b").assignValue(false))
+        .finish()
+        .while_(Bool.expr(Variable.get("b")))
+        .toJavaString();
+
+    assertEquals("failed to generate for do whileloop with simple expression (no operator and rhs)",
+        DOWHILE_RESULT_SIMPLE_EXPRESSION, s);
+  }
+
+  @Test
+  public void testDoWhileLoopWithNestedExpressions() {
+    String s = StatementBuilder.create()
         .addVariable("str", String.class)
         .do_()
           .append(StatementBuilder.create().loadStatic(System.class, "out").invoke("println", Variable.get("str")))
```

## Row 38
commit_url: https://github.com/FasterXML/jackson-modules-java8/commit/8c3d032fb564148c39b5fdf1cdd6e314e6af1cb5
rm_type: Move And Inline Method
rm_description: Move And Inline Method private read(reader ObjectReader, json String) : LocalDate moved from class com.fasterxml.jackson.datatype.jsr310.deser.LocalDateDeserTest to class com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserTest & inlined to private expectSuccess(reader ObjectReader, exp Object, json String) : void
file_path: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java; datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java
left_side: [{"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 339, "endLine": 341, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "inlined method declaration", "codeElement": "private read(reader ObjectReader, json String) : LocalDate"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java", "startLine": 340, "endLine": 340, "startColumn": 9, "endColumn": 53, "codeElementType": "RETURN_STATEMENT", "description": "inlined code from inlined method declaration", "codeElement": null}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java", "startLine": 461, "endLine": 465, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration before inline", "codeElement": "private expectSuccess(reader ObjectReader, exp Object, json String) : void"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java", "startLine": 462, "endLine": 462, "startColumn": 37, "endColumn": 55, "codeElementType": "METHOD_INVOCATION", "description": "inlined method invocation", "codeElement": "read(reader,json)"}]
right_side: [{"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java", "startLine": 461, "endLine": 465, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "target method declaration after inline", "codeElement": "private expectSuccess(reader ObjectReader, exp Object, json String) : void"}, {"filePath": "datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java", "startLine": 462, "endLine": 462, "startColumn": 9, "endColumn": 74, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "inlined code in target method declaration", "codeElement": null}]

### Patch: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateDeserTest.java
```diff
@@ -128,7 +128,20 @@ public void testBadDeserializationAsString02() throws Exception
             verifyException(e, "from String \"");
         }
     }
-    
+
+    @Test
+    public void testDeserializationWithTypeInfo01() throws Exception
+    {
+        ObjectMapper mapper = mapperBuilder()
+               .addMixIn(Temporal.class, MockObjectConfiguration.class)
+               .build();
+        LocalDate date = LocalDate.of(2005, Month.NOVEMBER, 5);
+        Temporal value = mapper.readValue(
+                "[\"" + LocalDate.class.getName() + "\",\"" + date.toString() + "\"]", Temporal.class
+                );
+        assertEquals("The value is not correct.", date, value);
+    }
+
     /*
     /**********************************************************
     /* Deserialization from alternate representation: int (number
@@ -170,7 +183,6 @@ public void testStricDeserializeFromInt() throws Exception
     /*
     /**********************************************************
     /* Tests for empty string handling
-     */
     /**********************************************************
      */
 
@@ -227,7 +239,7 @@ public void testStrictDeserializFromEmptyString() throws Exception {
     public void testDeserializationAsArrayDisabled() throws Throwable
     {
         try {
-            read(READER, "[\"2000-01-01\"]");
+            READER.readValue("[\"2000-01-01\"]");
             fail("expected MismatchedInputException");
         } catch (MismatchedInputException e) {
             verifyException(e, "Unexpected token (VALUE_STRING) within Array");
@@ -238,7 +250,41 @@ public void testDeserializationAsArrayDisabled() throws Throwable
     public void testDeserializationAsEmptyArrayDisabled() throws Throwable
     {
         // works even without the feature enabled
-        assertNull(read(READER, "[]"));
+        assertNull(READER.readValue("[]"));
+    }
+
+    @Test
+    public void testDeserializationAsArrayEnabled() throws Throwable
+    {
+        LocalDate actual = READER
+                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS)
+                .readValue("[\"2000-01-01\"]");
+        assertEquals("The value is not correct.", LocalDate.of(2000, 1, 1), actual);
+    }
+
+    @Test
+    public void testDeserializationAsEmptyArrayEnabled() throws Throwable
+    {
+        LocalDate value = READER
+                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS,
+                        DeserializationFeature.ACCEPT_EMPTY_ARRAY_AS_NULL_OBJECT)
+                .readValue("[]");
+        assertNull(value);
+    }
+
+    /*
+    /**********************************************************
+    /* Custom format
+    /**********************************************************
+     */
+
+    // for [datatype-jsr310#37]
+    @Test
+    public void testCustomFormat() throws Exception
+    {
+        Wrapper w = MAPPER.readValue("{\"value\":\"2015_07_28T13:53+0300\"}", Wrapper.class);
+        LocalDate date = w.value; 
+        assertEquals(28, date.getDayOfMonth());
     }
 
     /*
@@ -294,29 +340,10 @@ public void testDeserializationCaseInsensitiveDisabled_InvalidDate() throws Thro
         	expectFailure(reader, json);
         }
     }
-    
-    @Test
-    public void testDeserializationAsArrayEnabled() throws Throwable
-    {
-        LocalDate actual = READER
-                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS)
-                .readValue("[\"2000-01-01\"]");
-        assertEquals("The value is not correct.", LocalDate.of(2000, 1, 1), actual);
-    }
 
-    @Test
-    public void testDeserializationAsEmptyArrayEnabled() throws Throwable
-    {
-        LocalDate value = READER
-                .with(DeserializationFeature.UNWRAP_SINGLE_VALUE_ARRAYS,
-                        DeserializationFeature.ACCEPT_EMPTY_ARRAY_AS_NULL_OBJECT)
-                .readValue("[]");
-        assertNull(value);
-    }
-    
     private void expectFailure(ObjectReader reader, String json) throws Throwable {
         try {
-            read(reader, json);
+            reader.readValue(aposToQuotes(json));
             fail("expected DateTimeParseException");
         } catch (JsonProcessingException e) {
             if (e.getCause() == null) {
@@ -325,56 +352,14 @@ private void expectFailure(ObjectReader reader, String json) throws Throwable {
             if (!(e.getCause() instanceof DateTimeParseException)) {
                 throw e.getCause();
             }
-        } catch (IOException e) {
-            throw e;
         }
     }
 
     private void expectSuccess(ObjectReader reader, Object exp, String json) throws IOException {
-        final LocalDate value = read(reader, json);
-        notNull(value);
-        expect(exp, value);
-    }
-
-    private LocalDate read(ObjectReader reader, final String json) throws IOException {
-        return reader.readValue(aposToQuotes(json));
-    }
-
-    private static void notNull(Object value) {
+        final LocalDate value = reader.readValue(aposToQuotes(json));
         assertNotNull("The value should not be null.", value);
-    }
-
-    private static void expect(Object exp, Object value) {
         assertEquals("The value is not correct.", exp,  value);
     }
-
-    @Test
-    public void testDeserializationWithTypeInfo01() throws Exception
-    {
-        ObjectMapper mapper = mapperBuilder()
-               .addMixIn(Temporal.class, MockObjectConfiguration.class)
-               .build();
-        LocalDate date = LocalDate.of(2005, Month.NOVEMBER, 5);
-        Temporal value = mapper.readValue(
-                "[\"" + LocalDate.class.getName() + "\",\"" + date.toString() + "\"]", Temporal.class
-                );
-        assertEquals("The value is not correct.", date, value);
-    }
-
-    /*
-    /**********************************************************
-    /* Custom format
-    /**********************************************************
-     */
-
-    // for [datatype-jsr310#37]
-    @Test
-    public void testCustomFormat() throws Exception
-    {
-        Wrapper w = MAPPER.readValue("{\"value\":\"2015_07_28T13:53+0300\"}", Wrapper.class);
-        LocalDate date = w.value; 
-        assertEquals(28, date.getDayOfMonth());
-    }
 }
```
### Patch: datetime/src/test/java/com/fasterxml/jackson/datatype/jsr310/deser/LocalDateTimeDeserTest.java
```diff
@@ -459,14 +459,14 @@ public void testDeserializationCaseInsensitiveDisabled_InvalidDate() throws Thro
     }
 
     private void expectSuccess(ObjectReader reader, Object exp, String json) throws IOException {
-        final LocalDateTime value = read(reader, json);
-        notNull(value);
-        expect(exp, value);
+        final LocalDateTime value = reader.readValue(aposToQuotes(json));
+        assertNotNull("The value should not be null.", value);
+        assertEquals("The value is not correct.", exp,  value);
     }
 
     private void expectFailure(ObjectReader reader, String json) throws Throwable {
         try {
-            read(reader, json);
+            reader.readValue(aposToQuotes(json));
             fail("expected DateTimeParseException");
         } catch (JsonProcessingException e) {
             if (e.getCause() == null) {
@@ -475,20 +475,6 @@ private void expectFailure(ObjectReader reader, String json) throws Throwable {
             if (!(e.getCause() instanceof DateTimeParseException)) {
                 throw e.getCause();
             }
-        } catch (IOException e) {
-            throw e;
         }
     }
-
-    private LocalDateTime read(ObjectReader reader, final String json) throws IOException {
-        return reader.readValue(aposToQuotes(json));
-    }
-
-    private void notNull(Object value) {
-        assertNotNull("The value should not be null.", value);
-    }
-
-    private void expect(Object exp, Object value) {
-        assertEquals("The value is not correct.", exp,  value);
-    }
 }
```

## Row 39
commit_url: https://github.com/exadel-inc/etoolbox-authoring-kit/commit/932c817f63f454635d991251b83c62d1d7adf681
rm_type: Change Parameter Type
rm_description: Change Parameter Type answer : List<Orderable> to answer : List<Orderable<String>> in method private assertCommon(answer List<Orderable<String>>, initial List<Orderable<String>>) : void from class com.exadel.aem.toolkit.plugin.util.ordering.TestOrdering
file_path: aem-authoring-toolkit-plugin/src/test/com/exadel/aem/toolkit/plugin/util/ordering/TestOrdering.java
left_side: [{"filePath": "aem-authoring-toolkit-plugin/src/test/com/exadel/aem/toolkit/plugin/util/ordering/TestOrdering.java", "startLine": 193, "endLine": 193, "startColumn": 31, "endColumn": 53, "codeElementType": "SINGLE_VARIABLE_DECLARATION", "description": "original variable declaration", "codeElement": "answer : List<Orderable>"}, {"filePath": "aem-authoring-toolkit-plugin/src/test/com/exadel/aem/toolkit/plugin/util/ordering/TestOrdering.java", "startLine": 195, "endLine": 195, "startColumn": 13, "endColumn": 56, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "aem-authoring-toolkit-plugin/src/test/com/exadel/aem/toolkit/plugin/util/ordering/TestOrdering.java", "startLine": 196, "endLine": 198, "startColumn": 13, "endColumn": 34, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "aem-authoring-toolkit-plugin/src/test/com/exadel/aem/toolkit/plugin/util/ordering/TestOrdering.java", "startLine": 199, "endLine": 201, "startColumn": 13, "endColumn": 21, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}]
right_side: [{"filePath": "aem-authoring-toolkit-plugin/src/test/com/exadel/aem/toolkit/plugin/util/ordering/TestOrdering.java", "startLine": 185, "endLine": 185, "startColumn": 31, "endColumn": 61, "codeElementType": "SINGLE_VARIABLE_DECLARATION", "description": "changed-type variable declaration", "codeElement": "answer : List<Orderable<String>>"}, {"filePath": "aem-authoring-toolkit-plugin/src/test/com/exadel/aem/toolkit/plugin/util/ordering/TestOrdering.java", "startLine": 187, "endLine": 187, "startColumn": 13, "endColumn": 56, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the variable with changed type", "codeElement": null}, {"filePath": "aem-authoring-toolkit-plugin/src/test/com/exadel/aem/toolkit/plugin/util/ordering/TestOrdering.java", "startLine": 188, "endLine": 190, "startColumn": 13, "endColumn": 34, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the variable with changed type", "codeElement": null}, {"filePath": "aem-authoring-toolkit-plugin/src/test/com/exadel/aem/toolkit/plugin/util/ordering/TestOrdering.java", "startLine": 191, "endLine": 193, "startColumn": 13, "endColumn": 21, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the variable with changed type", "codeElement": null}]

### Patch: aem-authoring-toolkit-plugin/src/test/com/exadel/aem/toolkit/plugin/util/ordering/TestOrdering.java
```diff
@@ -16,182 +16,174 @@
 
 
 import java.util.ArrayList;
+import java.util.Arrays;
 import java.util.HashSet;
 import java.util.List;
 import java.util.Random;
-import java.util.Set;
 import java.util.stream.Collectors;
+import java.util.stream.IntStream;
 
 import org.junit.Assert;
-import org.junit.Before;
 import org.junit.Test;
 
 public class TestOrdering {
 
-    int size = 100;
-    List<Orderable> list = new ArrayList<>(size);
+    private static final List<String> expectedTestGraphWithCycleInside1 = Arrays
+        .asList("Handler0", "Handler1", "Handler2", "Handler4", "Handler3");
 
-    // Init list with random nodes
-    @Before
-    public void init() {
-        Random random = new Random();
-        for (int i = 0; i < size; i++) {
-            list.add(Orderable.from("Handler" + i));
-        }
-        for (int i = 0; i < size; i++) {
-            int mode = random.nextInt(4);
-            int iAfter = random.nextInt(size);
-            while (iAfter == i) {
-                iAfter = random.nextInt(size);
-            }
-            int iBefore = random.nextInt(size);
-            while (iBefore == i) {
-                iBefore = random.nextInt(size);
-            }
-            if (mode == 0) {
-                list.get(i).setAfter(list.get(iAfter));
-            } else if (mode == 1) {
-                list.get(i).setBefore(list.get(iBefore));
-            } else if (mode == 2) {
-                list.get(i).setBefore(list.get(iBefore));
-                list.get(i).setBefore(list.get(iAfter));
-            }
-        }
-    }
+    private static final List<String> expectedTestGraphWithCycleInside2 = Arrays
+        .asList("Handler0", "Handler5", "Handler6", "Handler1", "Handler2", "Handler3", "Handler4");
+
+    private static final List<String> expectedTestSimpleCycleGraph = Arrays
+        .asList("Handler0", "Handler1", "Handler2", "Handler3");
+
+    private static final List<String> expectedTestExampleGraph1 = Arrays
+        .asList("Handler1", "Handler3", "Handler8", "Handler9", "Handler2", "Handler5", "Handler4", "Handler6", "Handler0", "Handler7");
+
+    private static final List<String> expectedTestExampleGraph2 = Arrays
+        .asList("Handler0", "Handler1", "Handler2", "Handler3", "Handler4", "Handler5", "Handler6");
 
     // Test, that size will be equal to initial size and ordered list consists of unique nodes
     @Test
     public void testRandomOrderableList() {
-        Graph graph = new Graph(list);
-        List<Orderable> answer = graph.topologicalSort();
-        Assert.assertEquals(size, answer.size());
+        List<Orderable<String>> list = getRandomList(100);
+
+        List<String> answer = sortListToValues(list);
+
+        Assert.assertEquals(list.size(), answer.size());
         assertUnique(answer);
     }
 
     // Test graph with cycle inside
     @Test
     public void testGraphWithCycleInside1() {
-        List<Orderable> list = new ArrayList<>(5);
-        for (int i = 0; i < 5; i++) {
-            list.add(Orderable.from("Handler" + i));
-        }
+        List<Orderable<String>> list = getList(5);
+
         list.get(0).setBefore(list.get(1));
         list.get(1).setBefore(list.get(2));
         list.get(4).setAfter(list.get(1));
         list.get(2).setBefore(list.get(3));
         list.get(3).setBefore(list.get(1));
-        Graph graph = new Graph(list);
-        List<Orderable> answer = graph.topologicalSort();
-
-        List<String> expected = new ArrayList<>(5);
-        expected.add("Handler0");
-        expected.add("Handler1");
-        expected.add("Handler2");
-        expected.add("Handler4");
-        expected.add("Handler3");
-        Assert.assertEquals(5, answer.size());
-        Assert.assertEquals(answer.stream().map(Orderable::getName).collect(Collectors.toList()), expected);
+
+        List<String> answer = sortListToValues(list);
+
+        assertUnique(answer);
+        Assert.assertEquals(expectedTestGraphWithCycleInside1, answer);
     }
 
     // Test graph with cycle inside
     @Test
     public void testGraphWithCycleInside2() {
-        List<Orderable> list = new ArrayList<>(7);
-        for (int i = 0; i < 7; i++) {
-            list.add(Orderable.from("Handler" + i));
-        }
+        List<Orderable<String>> list = getList(7);
+
         list.get(0).setBefore(list.get(1));
         list.get(1).setBefore(list.get(2));
         list.get(2).setBefore(list.get(3));
         list.get(3).setBefore(list.get(4));
         list.get(1).setAfter(list.get(3));
         list.get(5).setBefore(list.get(1));
         list.get(6).setBefore(list.get(1));
-        Graph graph = new Graph(list);
-        List<Orderable> answer = graph.topologicalSort();
 
-        Assert.assertEquals(7, answer.size());
-        assertUnique(answer);
-        List<String> expected = new ArrayList<>(7);
-        expected.add("Handler0");
-        expected.add("Handler5");
-        expected.add("Handler6");
-        expected.add("Handler1");
-        expected.add("Handler2");
-        expected.add("Handler3");
-        expected.add("Handler4");
-        Assert.assertEquals(answer.stream().map(Orderable::getName).collect(Collectors.toList()), expected);
-        assertUnique(answer);
+        List<String> answer = sortListToValues(list);
+
+        Assert.assertEquals(expectedTestGraphWithCycleInside2, answer);
     }
 
     // Test cycle graph
     @Test
     public void testSimpleCycleGraph() {
-        List<Orderable> list = new ArrayList<>(4);
-        for (int i = 0; i < 4; i++) {
-            list.add(Orderable.from("Handler" + i));
-        }
+        List<Orderable<String>> list = getList(4);
+
         list.get(0).setBefore(list.get(1));
         list.get(1).setBefore(list.get(2));
         list.get(2).setBefore(list.get(3));
         list.get(3).setBefore(list.get(0));
-        Graph graph = new Graph(list);
-        List<Orderable> answer = graph.topologicalSort();
 
-        Assert.assertEquals(4, answer.size());
-        assertUnique(answer);
-        Assert.assertEquals(answer, list);
+        List<String> answer = sortListToValues(list);
+
+        Assert.assertEquals(expectedTestSimpleCycleGraph, answer);
     }
 
     @Test
     public void testExampleGraph1() {
-        List<Orderable> list = new ArrayList<>(10);
-        for (int i = 0; i < 10; i++) {
-            list.add(Orderable.from("Handler" + i));
-        }
+        List<Orderable<String>> list = getList(10);
+
         list.get(1).setBefore(list.get(0));
         list.get(2).setBefore(list.get(6));
         list.get(3).setBefore(list.get(2));
         list.get(4).setAfter(list.get(2));
         list.get(6).setBefore(list.get(0));
         list.get(7).setAfter(list.get(6));
         list.get(9).setBefore(list.get(5));
-        Graph graph = new Graph(list);
-        List<Orderable> answer = graph.topologicalSort();
-
-        Assert.assertEquals(10, answer.size());
-        List<String> expected = new ArrayList<>(10);
-        expected.add("Handler1");
-        expected.add("Handler3");
-        expected.add("Handler8");
-        expected.add("Handler9");
-        expected.add("Handler2");
-        expected.add("Handler5");
-        expected.add("Handler4");
-        expected.add("Handler6");
-        expected.add("Handler0");
-        expected.add("Handler7");
-        Assert.assertEquals(expected, answer.stream().map(Orderable::getName).collect(Collectors.toList()));
-        assertUnique(answer);
+
+        List<Orderable<String>> answer = sortList(list);
+        List<String> answerValues = sortListToValues(list);
+
         assertCommon(answer, list);
+        Assert.assertEquals(expectedTestExampleGraph1, answerValues);
     }
 
     // Test graph without edges
     @Test
     public void testExampleGraph2() {
-        List<Orderable> list = new ArrayList<>(7);
-        for (int i = 0; i < 7; i++) {
-            list.add(Orderable.from("Handler" + i));
+        List<Orderable<String>> list = getList(7);
+
+        List<Orderable<String>> answer = sortList(list);
+        List<String> answerValues = sortListToValues(list);
+
+        assertCommon(answer, list);
+        Assert.assertEquals(expectedTestExampleGraph2, answerValues);
+    }
+
+    // Inits list without edges
+    private List<Orderable<String>> getList(int size) {
+        return IntStream.range(0, size)
+            .mapToObj(i -> new Orderable<>("Handler" + i, "Handler" + i))
+            .collect(Collectors.toList());
+    }
+
+    // Inits list with random edges
+    private List<Orderable<String>> getRandomList(int size) {
+        List<Orderable<String>> list = new ArrayList<>(size);
+        Random random = new Random();
+        for (int i = 0; i < size; i++) {
+            list.add(new Orderable<>("Handler" + i, "Handler" + i));
         }
+        for (int i = 0; i < size; i++) {
+            int mode = random.nextInt(3);
+            int iAfter = random.nextInt(size);
+            while (iAfter == i) {
+                iAfter = random.nextInt(size);
+            }
+            int iBefore = random.nextInt(size);
+            while (iBefore == i) {
+                iBefore = random.nextInt(size);
+            }
+            if (mode == 0) {
+                list.get(i).setAfter(list.get(iAfter));
+            } else if (mode == 1) {
+                list.get(i).setBefore(list.get(iBefore));
+            } else {
+                list.get(i).setBefore(list.get(iBefore));
+                list.get(i).setBefore(list.get(iAfter));
+            }
+        }
+        return list;
+    }
+
+    // Gets sorted list
+    private List<Orderable<String>> sortList(List<Orderable<String>> list) {
+        return new Graph<>(list).topologicalSort();
+    }
 
-        Graph graph = new Graph(list);
-        List<Orderable> answer = graph.topologicalSort();
-        Assert.assertEquals(answer, list);
+    // Gets sorted list mapped to their values
+    private List<String> sortListToValues(List<Orderable<String>> list) {
+        return sortList(list).stream().map(Orderable::getValue).collect(Collectors.toList());
     }
 
-    // Assert that before, after rules are achieved
-    private void assertCommon(List<Orderable> answer, List<Orderable> initial) {
-        for (Orderable node : initial) {
+    // Asserts that before, after rules are achieved
+    private void assertCommon(List<Orderable<String>> answer, List<Orderable<String>> initial) {
+        for (Orderable<String> node : initial) {
             int currentPosition = answer.indexOf(node);
             int beforePosition = node.getBefore() != null
                 ? answer.indexOf(node.getBefore())
@@ -204,10 +196,8 @@ private void assertCommon(List<Orderable> answer, List<Orderable> initial) {
         }
     }
 
-    // Assert that ordered list consists of only unique values
-    private void assertUnique(List<Orderable> answer) {
-        Set<Orderable> set = new HashSet<>(answer.size());
-        set.addAll(answer);
-        Assert.assertEquals(answer.size(), set.size());
+    // Asserts that ordered list consists of only unique values
+    private void assertUnique(List<String> answer) {
+        Assert.assertEquals(answer.size(), new HashSet<>(answer).size());
     }
 }
```

## Row 40
commit_url: https://github.com/aehrc/pathling/commit/2f362cb6ba2fec0a40f0fa4dcee8081740ceea69
rm_type: Change Attribute Access Modifier
rm_description: Change Attribute Access Modifier private to public in attribute public CODING_BB_VERSION1 : Coding from class au.csiro.pathling.test.TerminologyTest
file_path: terminology/src/test/java/au/csiro/pathling/terminology/DefaultTerminologyService2Test.java; terminology/src/test/java/au/csiro/pathling/test/TerminologyTest.java
left_side: [{"filePath": "terminology/src/test/java/au/csiro/pathling/terminology/DefaultTerminologyService2Test.java", "startLine": 62, "endLine": 64, "startColumn": 31, "endColumn": 17, "codeElementType": "FIELD_DECLARATION", "description": "original attribute declaration", "codeElement": "private CODING_B_VERSION1 : Coding"}]
right_side: [{"filePath": "terminology/src/test/java/au/csiro/pathling/test/TerminologyTest.java", "startLine": 39, "endLine": 41, "startColumn": 30, "endColumn": 17, "codeElementType": "FIELD_DECLARATION", "description": "attribute declaration with changed access modifier", "codeElement": "public CODING_BB_VERSION1 : Coding"}]

### Patch: terminology/src/test/java/au/csiro/pathling/terminology/DefaultTerminologyService2Test.java
```diff
@@ -21,12 +21,12 @@
 
 import au.csiro.pathling.fhir.TerminologyClient2;
 import au.csiro.pathling.terminology.TerminologyService2.Translation;
+import au.csiro.pathling.test.TerminologyTest;
 import java.util.Collections;
 import java.util.List;
 import javax.annotation.Nonnull;
 import org.hl7.fhir.r4.model.BooleanType;
 import org.hl7.fhir.r4.model.CodeType;
-import org.hl7.fhir.r4.model.Coding;
 import org.hl7.fhir.r4.model.Parameters;
 import org.hl7.fhir.r4.model.Parameters.ParametersParameterComponent;
 import org.hl7.fhir.r4.model.StringType;
@@ -35,46 +35,15 @@
 import org.junit.jupiter.api.BeforeEach;
 import org.junit.jupiter.api.Test;
 
-public class DefaultTerminologyService2Test {
-
-  public static final String SYSTEM_A = "uuid:systemA";
-  public static final String CODE_A = "codeA";
-  private static final String SYSTEM_B = "uuid:systemB";
-  private static final String CODE_B = "codeB";
-
-  private static final Coding CODING_AA = new Coding(SYSTEM_A, CODE_A, "displayAA");
-  private static final Coding CODING_AB = new Coding(SYSTEM_A, CODE_B, "displayAB");
-
-  public static final String VERSION_1 = "version1";
-  public static final String VERSION_2 = "version2";
-
-  private static final Coding CODING_AA_VERSION1 = new Coding(SYSTEM_A, CODE_A,
-      "displayAA").setVersion(
-      VERSION_1);
-  private static final Coding CODING_AB_VERSION1 = new Coding(SYSTEM_A, CODE_B,
-      "displayAB").setVersion(
-      VERSION_1);
-  private static final Coding CODING_AB_VERSION2 = new Coding(SYSTEM_A, CODE_B,
-      "displayAB").setVersion(
-      VERSION_2);
-
-  private static final Coding CODING_B = new Coding(SYSTEM_B, CODE_B, "displayB");
-  private static final Coding CODING_B_VERSION1 = new Coding(SYSTEM_B, CODE_B,
-      "displayB").setVersion(
-      VERSION_1);
+public class DefaultTerminologyService2Test extends TerminologyTest {
 
   private static final String VALUE_SET_X = "uuid:valueSetX";
   private static final String VALUE_SET_Y = "uuid:valueSetY";
 
-
-  private static final Coding INVALID_CODING_0 = new Coding(null, null, "");
-  private static final Coding INVALID_CODING_1 = new Coding("uiid:system", null, "");
-  private static final Coding INVALID_CODING_2 = new Coding(null, "someCode", "");
-
-
   private static final String CONCEPT_MAP_0 = "uuid:conceptMap0";
   private static final String CONCEPT_MAP_1 = "uuid:conceptMap1";
 
+  private static final List<Translation> EMPTY_TRANSLATION = Collections.emptyList();
 
   @Nonnull
   private static Parameters translation(@Nonnull final Translation... entries) {
@@ -92,8 +61,6 @@ private static Parameters translation(@Nonnull final Translation... entries) {
   }
 
 
-  private static final List<Translation> EMPTY_TRANSLATION = Collections.emptyList();
-
   private TerminologyClient2 terminologClient;
   private DefaultTerminologyService2 terminologyService;
 
@@ -123,7 +90,7 @@ public void testValidateVersionedCodingFalse() {
         deepEq(new StringType(VERSION_1)),
         deepEq(new CodeType(CODE_B))
     )).thenReturn(RESULT_FALSE);
-    assertFalse(terminologyService.validate(VALUE_SET_Y, CODING_B_VERSION1));
+    assertFalse(terminologyService.validate(VALUE_SET_Y, CODING_BB_VERSION1));
   }
 
   @Test
@@ -185,7 +152,7 @@ public void testSubsumesDifferentVersions() {
 
   @Test
   public void testSubsumesDifferentSystems() {
-    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_AA, CODING_B_VERSION1));
+    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_AA, CODING_BB_VERSION1));
     verifyNoMoreInteractions(terminologClient);
   }
 
@@ -197,9 +164,9 @@ public void testSubsumesInvalidCodings() {
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_0, CODING_AB));
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_1, CODING_AB));
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_2, CODING_AB));
-    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_B_VERSION1, INVALID_CODING_0));
-    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_B_VERSION1, INVALID_CODING_1));
-    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_B_VERSION1, INVALID_CODING_2));
+    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_BB_VERSION1, INVALID_CODING_0));
+    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_BB_VERSION1, INVALID_CODING_1));
+    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_BB_VERSION1, INVALID_CODING_2));
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_0, INVALID_CODING_1));
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_1, INVALID_CODING_2));
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_2, INVALID_CODING_0));
```
### Patch: terminology/src/test/java/au/csiro/pathling/test/TerminologyTest.java
```diff
@@ -0,0 +1,62 @@
+package au.csiro.pathling.test;
+
+import au.csiro.pathling.fhirpath.encoding.CodingEncoding;
+import java.util.stream.Stream;
+import javax.annotation.Nonnull;
+import org.apache.spark.sql.Row;
+import org.hl7.fhir.r4.model.Coding;
+import scala.collection.mutable.WrappedArray;
+
+public abstract class TerminologyTest {
+
+  public static final String SYSTEM_A = "uuid:systemA";
+  public static final String CODE_A = "codeA";
+  public static final String SYSTEM_B = "uuid:systemB";
+  public static final String CODE_B = "codeB";
+  public static final String SYSTEM_C = "uuid:systemC";
+  public static final String CODE_C = "codeC";
+  public static final String SYSTEM_D = "uuid:systemD";
+  public static final String CODE_D = "codeD";
+
+  public static final Coding CODING_AA = new Coding(SYSTEM_A, CODE_A, "displayAA");
+  public static final Coding CODING_AB = new Coding(SYSTEM_A, CODE_B, "displayAB");
+
+  public static final String VERSION_1 = "version1";
+  public static final String VERSION_2 = "version2";
+
+  public static final Coding CODING_AA_VERSION1 = new Coding(SYSTEM_A, CODE_A,
+      "displayAA").setVersion(
+      VERSION_1);
+  public static final Coding CODING_AB_VERSION1 = new Coding(SYSTEM_A, CODE_B,
+      "displayAB").setVersion(
+      VERSION_1);
+  public static final Coding CODING_AB_VERSION2 = new Coding(SYSTEM_A, CODE_B,
+      "displayAB").setVersion(
+      VERSION_2);
+
+  public static final Coding CODING_BA = new Coding(SYSTEM_B, CODE_A, "displayBA");
+  public static final Coding CODING_BB = new Coding(SYSTEM_B, CODE_B, "displayBB");
+  public static final Coding CODING_BB_VERSION1 = new Coding(SYSTEM_B, CODE_B,
+      "displayB").setVersion(
+      VERSION_1);
+
+  public static final Coding CODING_A = CODING_AA;
+  public static final Coding CODING_B = CODING_BB;
+  public static final Coding CODING_C = new Coding(SYSTEM_C, CODE_C, "displayCC");
+  public static final Coding CODING_D = new Coding(SYSTEM_D, CODE_D, "displayDD");
+
+  public static final Coding INVALID_CODING_0 = new Coding(null, null, "");
+  public static final Coding INVALID_CODING_1 = new Coding("uiid:system", null, "");
+  public static final Coding INVALID_CODING_2 = new Coding(null, "someCode", "");
+
+
+  @Nonnull
+  public static Row[] asArray(@Nonnull final Coding... codings) {
+    return Stream.of(codings).map(CodingEncoding::encode).toArray(Row[]::new);
+  }
+
+  @Nonnull
+  public static WrappedArray<Row> encodeMany(Coding... codings) {
+    return WrappedArray.make(Stream.of(codings).map(CodingEncoding::encode).toArray(Row[]::new));
+  }
+}
```

## Row 41
commit_url: https://github.com/fedex81/helios/commit/1dac09eda579c04545ef76f67045a15eba71addb
rm_type: Add Parameter
rm_description: Add Parameter folderName : String in method public saveToFile(folderName String, saveName String, imgExt String, i Image) : void from class omegadrive.util.TestRenderUtil
file_path: src/test/java/omegadrive/util/TestRenderUtil.java; src/test/java/omegadrive/vdp/VdpRenderCompareTest.java
left_side: [{"filePath": "src/test/java/omegadrive/vdp/VdpRenderCompareTest.java", "startLine": 169, "endLine": 173, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "protected saveToFile(saveName String, i Image) : void"}]
right_side: [{"filePath": "src/test/java/omegadrive/util/TestRenderUtil.java", "startLine": 28, "endLine": 28, "startColumn": 35, "endColumn": 52, "codeElementType": "SINGLE_VARIABLE_DECLARATION", "description": "added parameter", "codeElement": "folderName : String"}, {"filePath": "src/test/java/omegadrive/util/TestRenderUtil.java", "startLine": 28, "endLine": 32, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "method declaration with added parameter", "codeElement": "public saveToFile(folderName String, saveName String, imgExt String, i Image) : void"}]

### Patch: src/test/java/omegadrive/util/TestRenderUtil.java
```diff
@@ -0,0 +1,87 @@
+package omegadrive.util;
+
+import javax.swing.*;
+import java.awt.*;
+import java.awt.image.BufferedImage;
+import java.awt.image.DataBufferInt;
+import java.nio.file.Path;
+import java.nio.file.Paths;
+
+/**
+ * Federico Berti
+ * <p>
+ * Copyright 2021
+ */
+public class TestRenderUtil {
+
+    public static GraphicsDevice gd;
+    static boolean isHeadless;
+
+    static {
+        isHeadless = GraphicsEnvironment.getLocalGraphicsEnvironment().isHeadlessInstance();
+        if (!isHeadless) {
+            gd = GraphicsEnvironment.getLocalGraphicsEnvironment().getDefaultScreenDevice();
+        }
+    }
+
+
+    public static void saveToFile(String folderName, String saveName, String imgExt, Image i) {
+        Path folder = Paths.get(folderName);
+        Path res = TestFileUtil.compressAndSaveToZipFile(saveName + "." + imgExt, folder, i, imgExt);
+        System.out.println("Image saved: " + res.toAbsolutePath().toString());
+    }
+
+    public static BufferedImage convertToBufferedImage(Image image) {
+        BufferedImage newImage = new BufferedImage(
+                image.getWidth(null), image.getHeight(null),
+                BufferedImage.TYPE_INT_RGB);
+        Graphics2D g = newImage.createGraphics();
+        g.drawImage(image, 0, 0, null);
+        g.dispose();
+        return newImage;
+    }
+
+    public static Image scaleImage(Image i, int factor) {
+        return i.getScaledInstance(i.getWidth(null) * factor, i.getHeight(null) * factor, 0);
+    }
+
+    public static boolean isValidImage(int[] screenData) {
+        for (int i = 0; i < screenData.length; i++) {
+            if (screenData[i] > 0) {
+                return true;
+            }
+        }
+        return false;
+    }
+
+    public static Image cloneImage(Image img) {
+        return img.getScaledInstance(-1, -1, Image.SCALE_DEFAULT);
+    }
+
+    public static JFrame showImageFrame(Image bi, String title) {
+        JLabel label = new JLabel();
+        JPanel panel = new JPanel();
+        panel.add(label);
+        JFrame f = new JFrame();
+        f.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
+        f.add(panel);
+        label.setIcon(new ImageIcon(bi));
+        f.setTitle(title);
+        f.pack();
+        f.setVisible(true);
+        return f;
+    }
+
+    public static BufferedImage getImage(VideoMode videoMode) {
+        Dimension d = videoMode.getDimension();
+        BufferedImage bi = gd.getDefaultConfiguration().createCompatibleImage(d.width, d.height);
+        return bi;
+    }
+
+    public static BufferedImage saveRenderToImage(int[] data, VideoMode videoMode) {
+        BufferedImage bi = getImage(videoMode);
+        int[] linear = ((DataBufferInt) bi.getRaster().getDataBuffer()).getData();
+        System.arraycopy(data, 0, linear, 0, linear.length);
+        return bi;
+    }
+}
```
### Patch: src/test/java/omegadrive/vdp/VdpRenderCompareTest.java
```diff
@@ -20,6 +20,7 @@
 package omegadrive.vdp;
 
 import omegadrive.util.TestFileUtil;
+import omegadrive.util.TestRenderUtil;
 import omegadrive.util.Util;
 import org.junit.Assert;
 import org.junit.Before;
@@ -34,38 +35,19 @@
 import java.nio.file.Path;
 import java.nio.file.Paths;
 
+import static omegadrive.util.TestRenderUtil.*;
+
 @Ignore
 @Disabled
 public class VdpRenderCompareTest extends VdpRenderTest {
 
     protected static boolean SHOW_IMAGES_ON_FAILURE = true;
     public static String IMG_EXT = "bmp";
     public static String DOT_EXT = "." + IMG_EXT + ".zip";
-    private static Path compareFolderPath = Paths.get(saveStateFolder, "compare");
+    private static Path compareFolderPath = Paths.get(baseDataFolder, "compare");
     protected static String compareFolder = compareFolderPath.toAbsolutePath().toString();
     private BufferedImage diffImage;
 
-    public static BufferedImage convertToBufferedImage(Image image) {
-        BufferedImage newImage = new BufferedImage(
-                image.getWidth(null), image.getHeight(null),
-                BufferedImage.TYPE_INT_RGB);
-        Graphics2D g = newImage.createGraphics();
-        g.drawImage(image, 0, 0, null);
-        g.dispose();
-        return newImage;
-    }
-
-    public static void main(String[] args) {
-        File[] files = compareFolderPath.getParent().toFile().listFiles();
-        for (File file : files) {
-            if (file.isDirectory()) {
-                continue;
-            }
-            System.out.println("Testing: " + file);
-//            FileUtil.compressAndSaveToZipFile(file.toPath());
-        }
-    }
-
     @Before
     public void beforeTest() {
         System.setProperty("helios.headless", "true");
@@ -76,7 +58,7 @@ public void beforeTest() {
     @Ignore
     public void testCompareAll() {
 //        SHOW_IMAGES_ON_FAILURE = true;
-        File[] files = Paths.get(saveStateFolder).toFile().listFiles();
+        File[] files = Paths.get(baseDataFolder).toFile().listFiles();
         StringBuilder sb = new StringBuilder();
         for (File file : files) {
             if (file.isDirectory()) {
@@ -140,7 +122,7 @@ private boolean compareImage(BufferedImage baseline, BufferedImage actual) {
 
     private void testOverwriteBaselineImage(Path saveFile) {
         Image i = testSavestateViewerSingle(saveFile);
-        saveToFile(saveFile.getFileName().toString(), i);
+        TestRenderUtil.saveToFile(compareFolder, saveFile.getFileName().toString(), IMG_EXT, i);
     }
 
     protected boolean testCompareOne(Path saveFile) {
@@ -165,10 +147,4 @@ protected boolean testCompareOne(String saveName, BufferedImage actual) {
         }
         return false;
     }
-
-    protected void saveToFile(String saveName, Image i) {
-        Path folder = Paths.get(compareFolder);
-        Path res = TestFileUtil.compressAndSaveToZipFile(saveName + "." + IMG_EXT, folder, i, IMG_EXT);
-        System.out.println("Image saved: " + res.toAbsolutePath().toString());
-    }
 }
```

## Row 42
commit_url: https://github.com/ftsrg/theta/commit/8e59264fbc850e14bbb455774d64e70b8dca2862
rm_type: Change Attribute Access Modifier
rm_description: Change Attribute Access Modifier package to private in attribute private ve : VarDecl<IntType> from class hu.bme.mit.theta.core.utils.VarCollectorVisitorTest
file_path: hu.bme.mit.theta.core/src/test/java/hu/bme/mit/theta/core/utils/VarCollectorVisitorTest.java
left_side: [{"filePath": "hu.bme.mit.theta.core/src/test/java/hu/bme/mit/theta/core/utils/VarCollectorVisitorTest.java", "startLine": 38, "endLine": 38, "startColumn": 19, "endColumn": 21, "codeElementType": "FIELD_DECLARATION", "description": "original attribute declaration", "codeElement": "package ve : VarDecl<IntType>"}]
right_side: [{"filePath": "hu.bme.mit.theta.core/src/test/java/hu/bme/mit/theta/core/utils/VarCollectorVisitorTest.java", "startLine": 44, "endLine": 44, "startColumn": 40, "endColumn": 60, "codeElementType": "FIELD_DECLARATION", "description": "attribute declaration with changed access modifier", "codeElement": "private ve : VarDecl<IntType>"}]

### Patch: hu.bme.mit.theta.core/src/test/java/hu/bme/mit/theta/core/utils/VarCollectorVisitorTest.java
```diff
@@ -13,13 +13,18 @@
 import static hu.bme.mit.theta.core.type.impl.Types.Bool;
 import static hu.bme.mit.theta.core.type.impl.Types.Int;
 import static hu.bme.mit.theta.core.type.impl.Types.Rat;
-import static org.junit.Assert.assertTrue;
+import static org.junit.Assert.assertEquals;
 
+import java.util.Arrays;
+import java.util.Collection;
 import java.util.HashSet;
 import java.util.Set;
 
-import org.junit.Before;
 import org.junit.Test;
+import org.junit.runner.RunWith;
+import org.junit.runners.Parameterized;
+import org.junit.runners.Parameterized.Parameter;
+import org.junit.runners.Parameterized.Parameters;
 
 import hu.bme.mit.theta.core.decl.VarDecl;
 import hu.bme.mit.theta.core.expr.Expr;
@@ -29,48 +34,43 @@
 import hu.bme.mit.theta.core.type.Type;
 import hu.bme.mit.theta.core.utils.impl.ExprUtils;
 
+@RunWith(Parameterized.class)
 public class VarCollectorVisitorTest {
 
-	VarDecl<BoolType> va;
-	VarDecl<IntType> vb;
-	VarDecl<RatType> vc;
-	VarDecl<BoolType> vd;
-	VarDecl<IntType> ve;
+	private static final VarDecl<BoolType> va = Var("a", Bool());
+	private static final VarDecl<IntType> vb = Var("b", Int());
+	private static final VarDecl<RatType> vc = Var("c", Rat());
+	private static final VarDecl<BoolType> vd = Var("d", Bool());
+	private static final VarDecl<IntType> ve = Var("e", Int());
 
-	Expr<BoolType> a;
-	Expr<IntType> b;
-	Expr<RatType> c;
-	Expr<BoolType> d;
-	Expr<IntType> e;
+	private static final Expr<BoolType> a = va.getRef();
+	private static final Expr<IntType> b = vb.getRef();
+	private static final Expr<RatType> c = vc.getRef();
+	private static final Expr<BoolType> d = vd.getRef();
+	private static final Expr<IntType> e = ve.getRef();
 
-	@Before
-	public void before() {
-		va = Var("a", Bool());
-		vb = Var("b", Int());
-		vc = Var("c", Rat());
-		vd = Var("d", Bool());
-		ve = Var("e", Int());
+	@Parameter(value = 0)
+	public Expr<? extends Type> expr;
 
-		a = va.getRef();
-		b = vb.getRef();
-		c = vc.getRef();
-		d = vd.getRef();
-		e = ve.getRef();
-	}
+	@Parameter(value = 1)
+	public Set<VarDecl<? extends Type>> expectedVars;
 
-	@Test
-	public void test() {
-		assertTrue(checkExpr(And(True(), False(), Eq(Int(1), Int(2))), of()));
+	@Parameters
+	public static Collection<Object[]> data() {
+		return Arrays.asList(new Object[][] {
 
-		assertTrue(checkExpr(And(a, Not(d)), of(va, vd)));
+				{ And(True(), False(), Eq(Int(1), Int(2))), of() },
 
-		assertTrue(checkExpr(And(Imply(a, d), Eq(c, Sub(b, e))), of(va, vb, vc, vd, ve)));
+				{ And(a, Not(d)), of(va, vd) },
+
+				{ And(Imply(a, d), Eq(c, Sub(b, e))), of(va, vb, vc, vd, ve) }, });
 	}
 
-	private boolean checkExpr(final Expr<? extends Type> expr, final Set<VarDecl<? extends Type>> expectedVars) {
+	@Test
+	public void test() {
 		final Set<VarDecl<? extends Type>> vars = new HashSet<>();
 		ExprUtils.collectVars(expr, vars);
-		return vars.equals(expectedVars);
+		assertEquals(expectedVars, vars);
 	}
 
 }
```

## Row 43
commit_url: https://github.com/hyphanet/fred/commit/2e68720627ae6447ba12d712a9e6e4a123e66b95
rm_type: Extract And Move Method
rm_description: Extract And Move Method public doubleValue() : double extracted from public testDoubleValue() : void in class net.i2p.util.NativeBigIntegerTest & moved to class net.i2p.util.NativeBigIntegerTest.TestIntegers
file_path: test/net/i2p/util/NativeBigIntegerTest.java
left_side: [{"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 82, "endLine": 103, "startColumn": 2, "endColumn": 3, "codeElementType": "METHOD_DECLARATION", "description": "source method declaration before extraction", "codeElement": "public testDoubleValue() : void"}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 88, "endLine": 88, "startColumn": 4, "endColumn": 56, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "extracted code from source method declaration", "codeElement": null}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 93, "endLine": 93, "startColumn": 4, "endColumn": 20, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "extracted code from source method declaration", "codeElement": null}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 91, "endLine": 91, "startColumn": 5, "endColumn": 31, "codeElementType": "EXPRESSION_STATEMENT", "description": "extracted code from source method declaration", "codeElement": null}]
right_side: [{"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 141, "endLine": 150, "startColumn": 3, "endColumn": 4, "codeElementType": "METHOD_DECLARATION", "description": "extracted method declaration", "codeElement": "public doubleValue() : double"}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 142, "endLine": 142, "startColumn": 4, "endColumn": 44, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "extracted code to extracted method declaration", "codeElement": null}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 143, "endLine": 143, "startColumn": 4, "endColumn": 19, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "extracted code to extracted method declaration", "codeElement": null}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 145, "endLine": 145, "startColumn": 5, "endColumn": 25, "codeElementType": "EXPRESSION_STATEMENT", "description": "extracted code to extracted method declaration", "codeElement": null}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 92, "endLine": 102, "startColumn": 2, "endColumn": 3, "codeElementType": "METHOD_DECLARATION", "description": "source method declaration after extraction", "codeElement": "public testDoubleValue() : void"}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 95, "endLine": 95, "startColumn": 21, "endColumn": 43, "codeElementType": "METHOD_INVOCATION", "description": "extracted method invocation", "codeElement": "javaTest.doubleValue()"}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 94, "endLine": 94, "startColumn": 23, "endColumn": 47, "codeElementType": "METHOD_INVOCATION", "description": "extracted method invocation", "codeElement": "nativeTest.doubleValue()"}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 147, "endLine": 147, "startColumn": 4, "endColumn": 11, "codeElementType": "EXPRESSION_STATEMENT", "description": "added statement in extracted method declaration", "codeElement": null}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 148, "endLine": 148, "startColumn": 4, "endColumn": 47, "codeElementType": "EXPRESSION_STATEMENT", "description": "added statement in extracted method declaration", "codeElement": null}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 149, "endLine": 149, "startColumn": 4, "endColumn": 13, "codeElementType": "RETURN_STATEMENT", "description": "added statement in extracted method declaration", "codeElement": null}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 144, "endLine": 146, "startColumn": 4, "endColumn": 5, "codeElementType": "FOR_STATEMENT", "description": "added statement in extracted method declaration", "codeElement": null}, {"filePath": "test/net/i2p/util/NativeBigIntegerTest.java", "startLine": 144, "endLine": 146, "startColumn": 49, "endColumn": 5, "codeElementType": "BLOCK", "description": "added statement in extracted method declaration", "codeElement": null}]

### Patch: test/net/i2p/util/NativeBigIntegerTest.java
```diff
@@ -6,9 +6,10 @@
 import junit.framework.TestCase;
 
 public class NativeBigIntegerTest extends TestCase {
-	// Run with <code>ant -Dbenchmark=true</code> to do benchmark 
+	// Run with <code>ant -Dbenchmark=true</code> to do benchmark
 	private static final boolean BENCHMARK = Boolean.getBoolean("benchmark");
 	private static int numRuns = BENCHMARK ? 200 : 5;
+	private int runsProcessed;
 
 	/*
 	 * the sample numbers are elG generator/prime so we can test with reasonable
@@ -24,13 +25,10 @@ public class NativeBigIntegerTest extends TestCase {
 	        .toByteArray();
 
 	private SecureRandom rand;
-	private int runsProcessed;
-
-	private BigInteger jg;
-	private BigInteger jp;
 
-	private long totalTime = 0;
-	private long javaTime = 0;
+	TestIntegers nativeTest;
+	TestIntegers javaTest;
+	//TestIntegers java7Test;
 
 	protected void setUp() throws Exception {
 		if (!NativeBigInteger.isNative())
@@ -41,64 +39,65 @@ protected void setUp() throws Exception {
 		rand.nextBoolean();
 		printInfo("DEBUG: Random number generator warmed up");
 
-		jg = new BigInteger(_sampleGenerator);
-		jp = new BigInteger(_samplePrime);
+		byte[] randbytes = (new BigInteger(2048, rand)).toByteArray();
+
+		javaTest = new TestIntegers(
+			"java",
+			new BigInteger(_sampleGenerator),
+			new BigInteger(_samplePrime),
+			new BigInteger(randbytes)
+		);
+
+		nativeTest = new TestIntegers(
+			"native",
+			new NativeBigInteger(_sampleGenerator),
+			new NativeBigInteger(_samplePrime),
+			new NativeBigInteger(randbytes)
+		);
+
+		/*java7Test = new TestIntegers7(
+			"java7",
+			new java7.math.BigInteger(_sampleGenerator),
+			new java7.math.BigInteger(_samplePrime),
+			new java7.math.BigInteger(randbytes)
+		);*/
 
-		totalTime = javaTime = 0;
 	}
 
 	protected void tearDown() throws Exception {
-		printInfo("INFO: run time: " + totalTime + "ms (" + (totalTime / (runsProcessed + 1)) + "ms each)");
 		if (numRuns == runsProcessed)
 			printInfo("INFO: " + runsProcessed + " runs complete without any errors");
 		else
 			printError("ERROR: " + runsProcessed + " runs until we got an error");
 
-		printInfo("native run time: \t" + totalTime + "ms (" + (totalTime / (runsProcessed + 1)) + "ms each)");
-		printInfo("java run time:   \t" + javaTime + "ms (" + (javaTime / (runsProcessed + 1)) + "ms each)");
-		printInfo("native = " + ((totalTime * 100.0d) / (double) javaTime) + "% of pure java time");
+		printInfo(nativeTest.getReport());
+		printInfo(javaTest.getReport());
+		//printInfo(java7Test.getReport());
+		printInfo("native = " + (nativeTest.getTime() * 100.0 / javaTest.getTime()) + "% of pure java time");
+		//printInfo("java 7 = " + (java7Test.getTime() * 100.0 / javaTest.getTime()) + "% of pure java time");
 	}
 
 	public void testModPow() {
 		for (runsProcessed = 0; runsProcessed < numRuns; runsProcessed++) {
-			BigInteger bi = new BigInteger(2048, rand);
-			NativeBigInteger g = new NativeBigInteger(_sampleGenerator);
-			NativeBigInteger p = new NativeBigInteger(_samplePrime);
-			NativeBigInteger k = new NativeBigInteger(1, bi.toByteArray());
-
-			long beforeModPow = System.currentTimeMillis();
-			BigInteger myValue = g.modPow(k, p);
-			long afterModPow = System.currentTimeMillis();
-			BigInteger jval = jg.modPow(bi, jp);
-			long afterJavaModPow = System.currentTimeMillis();
-
-			totalTime += (afterModPow - beforeModPow);
-			javaTime += (afterJavaModPow - afterModPow);
+			BigInteger nativeVal = nativeTest.modPow();
+			BigInteger javaVal = javaTest.modPow();
+			//BigInteger java7Val = java7Test.modPow();
 
-			assertEquals(jval, myValue);
+			assertEquals(nativeVal, javaVal);
+			//assertEquals(javaVal, java7Val);
+			//assertEquals(java7Val, nativeVal);
 		}
 	}
 
 	public void testDoubleValue() {
-		BigInteger jg = new BigInteger(_sampleGenerator);
-
-		int MULTIPLICATOR = 50000; //Run the doubleValue() calls within a loop since they are pretty fast.. 
 		for (runsProcessed = 0; runsProcessed < numRuns; runsProcessed++) {
-			NativeBigInteger g = new NativeBigInteger(_sampleGenerator);
-			long beforeDoubleValue = System.currentTimeMillis();
-			double dNative = 0;
-			for (int mult = 0; mult < MULTIPLICATOR; mult++)
-				dNative = g.doubleValue();
-			long afterDoubleValue = System.currentTimeMillis();
-			double jval = 0;
-			for (int mult = 0; mult < MULTIPLICATOR; mult++)
-				jval = jg.doubleValue();
-			long afterJavaDoubleValue = System.currentTimeMillis();
-
-			totalTime += (afterDoubleValue - beforeDoubleValue);
-			javaTime += (afterJavaDoubleValue - afterDoubleValue);
-
-			assertEquals(jval, dNative, 0);
+			double nativeVal = nativeTest.doubleValue();
+			double javaVal = javaTest.doubleValue();
+			//double java7Val = java7Test.doubleValue();
+
+			assertEquals(nativeVal, javaVal);
+			//assertEquals(javaVal, java7Val);
+			//assertEquals(java7Val, nativeVal);
 		}
 	}
 
@@ -111,4 +110,87 @@ private static void printError(String info) {
 		if (BENCHMARK)
 			System.err.println(info);
 	}
+
+	static class TestIntegers {
+
+		final String name;
+		final BigInteger g;
+		final BigInteger p;
+		final BigInteger k;
+
+		protected long time;
+		protected int runs;
+
+		final static int DOUBLE_VAL_TEST_RUNS = 0x10000; // Run the doubleValue() calls within a loop since they are pretty fast..
+
+		public TestIntegers(String n, BigInteger g, BigInteger p, BigInteger k) {
+			name = n;
+			this.g = g;
+			this.p = p;
+			this.k = k;
+		}
+
+		public BigInteger modPow() {
+			long start = System.currentTimeMillis();
+			BigInteger r = g.modPow(p, k);
+			time += System.currentTimeMillis() - start;
+			++runs;
+			return r;
+		}
+
+		public double doubleValue() {
+			long start = System.currentTimeMillis();
+			double r = 0.0;
+			for (int i=0; i < DOUBLE_VAL_TEST_RUNS; ++i) {
+				r = g.doubleValue();
+			}
+			++runs;
+			time += System.currentTimeMillis() - start;
+			return r;
+		}
+
+		public long getTime() {
+			return time;
+		}
+
+		public String getReport() {
+			return name + " run time: \t" + time + "ms (" + (time/runs) + "ms each)";
+		}
+
+	}
+
+	/*static class TestIntegers7 extends TestIntegers {
+
+		final java7.math.BigInteger g;
+		final java7.math.BigInteger p;
+		final java7.math.BigInteger k;
+
+		public TestIntegers7(String name, java7.math.BigInteger g, java7.math.BigInteger p, java7.math.BigInteger k) {
+			super(name, null, null, null);
+			this.g = g;
+			this.p = p;
+			this.k = k;
+		}
+
+		public BigInteger modPow() {
+			long start = System.currentTimeMillis();
+			java7.math.BigInteger r = g.modPow(p, k);
+			time += System.currentTimeMillis() - start;
+			++runs;
+			return new BigInteger(r.toByteArray());
+		}
+
+		public double doubleValue() {
+			long start = System.currentTimeMillis();
+			double r = 0.0;
+			for (int i=0; i < DOUBLE_VAL_TEST_RUNS; ++i) {
+				r = g.doubleValue();
+			}
+			++runs;
+			time += System.currentTimeMillis() - start;
+			return r;
+		}
+
+	}*/
+
 }
```

## Row 44
commit_url: https://github.com/aehrc/pathling/commit/2f362cb6ba2fec0a40f0fa4dcee8081740ceea69
rm_type: Move And Rename Attribute
rm_description: Move And Rename Attribute private CODING_B_VERSION1 : Coding renamed to public CODING_BB_VERSION1 : Coding and moved from class au.csiro.pathling.terminology.DefaultTerminologyService2Test to class au.csiro.pathling.test.TerminologyTest
file_path: terminology/src/test/java/au/csiro/pathling/terminology/DefaultTerminologyService2Test.java; terminology/src/test/java/au/csiro/pathling/test/TerminologyTest.java
left_side: [{"filePath": "terminology/src/test/java/au/csiro/pathling/terminology/DefaultTerminologyService2Test.java", "startLine": 62, "endLine": 64, "startColumn": 31, "endColumn": 17, "codeElementType": "FIELD_DECLARATION", "description": "original attribute declaration", "codeElement": "private CODING_B_VERSION1 : Coding"}]
right_side: [{"filePath": "terminology/src/test/java/au/csiro/pathling/test/TerminologyTest.java", "startLine": 39, "endLine": 41, "startColumn": 30, "endColumn": 17, "codeElementType": "FIELD_DECLARATION", "description": "moved and renamed attribute declaration", "codeElement": "public CODING_BB_VERSION1 : Coding"}]

### Patch: terminology/src/test/java/au/csiro/pathling/terminology/DefaultTerminologyService2Test.java
```diff
@@ -21,12 +21,12 @@
 
 import au.csiro.pathling.fhir.TerminologyClient2;
 import au.csiro.pathling.terminology.TerminologyService2.Translation;
+import au.csiro.pathling.test.TerminologyTest;
 import java.util.Collections;
 import java.util.List;
 import javax.annotation.Nonnull;
 import org.hl7.fhir.r4.model.BooleanType;
 import org.hl7.fhir.r4.model.CodeType;
-import org.hl7.fhir.r4.model.Coding;
 import org.hl7.fhir.r4.model.Parameters;
 import org.hl7.fhir.r4.model.Parameters.ParametersParameterComponent;
 import org.hl7.fhir.r4.model.StringType;
@@ -35,46 +35,15 @@
 import org.junit.jupiter.api.BeforeEach;
 import org.junit.jupiter.api.Test;
 
-public class DefaultTerminologyService2Test {
-
-  public static final String SYSTEM_A = "uuid:systemA";
-  public static final String CODE_A = "codeA";
-  private static final String SYSTEM_B = "uuid:systemB";
-  private static final String CODE_B = "codeB";
-
-  private static final Coding CODING_AA = new Coding(SYSTEM_A, CODE_A, "displayAA");
-  private static final Coding CODING_AB = new Coding(SYSTEM_A, CODE_B, "displayAB");
-
-  public static final String VERSION_1 = "version1";
-  public static final String VERSION_2 = "version2";
-
-  private static final Coding CODING_AA_VERSION1 = new Coding(SYSTEM_A, CODE_A,
-      "displayAA").setVersion(
-      VERSION_1);
-  private static final Coding CODING_AB_VERSION1 = new Coding(SYSTEM_A, CODE_B,
-      "displayAB").setVersion(
-      VERSION_1);
-  private static final Coding CODING_AB_VERSION2 = new Coding(SYSTEM_A, CODE_B,
-      "displayAB").setVersion(
-      VERSION_2);
-
-  private static final Coding CODING_B = new Coding(SYSTEM_B, CODE_B, "displayB");
-  private static final Coding CODING_B_VERSION1 = new Coding(SYSTEM_B, CODE_B,
-      "displayB").setVersion(
-      VERSION_1);
+public class DefaultTerminologyService2Test extends TerminologyTest {
 
   private static final String VALUE_SET_X = "uuid:valueSetX";
   private static final String VALUE_SET_Y = "uuid:valueSetY";
 
-
-  private static final Coding INVALID_CODING_0 = new Coding(null, null, "");
-  private static final Coding INVALID_CODING_1 = new Coding("uiid:system", null, "");
-  private static final Coding INVALID_CODING_2 = new Coding(null, "someCode", "");
-
-
   private static final String CONCEPT_MAP_0 = "uuid:conceptMap0";
   private static final String CONCEPT_MAP_1 = "uuid:conceptMap1";
 
+  private static final List<Translation> EMPTY_TRANSLATION = Collections.emptyList();
 
   @Nonnull
   private static Parameters translation(@Nonnull final Translation... entries) {
@@ -92,8 +61,6 @@ private static Parameters translation(@Nonnull final Translation... entries) {
   }
 
 
-  private static final List<Translation> EMPTY_TRANSLATION = Collections.emptyList();
-
   private TerminologyClient2 terminologClient;
   private DefaultTerminologyService2 terminologyService;
 
@@ -123,7 +90,7 @@ public void testValidateVersionedCodingFalse() {
         deepEq(new StringType(VERSION_1)),
         deepEq(new CodeType(CODE_B))
     )).thenReturn(RESULT_FALSE);
-    assertFalse(terminologyService.validate(VALUE_SET_Y, CODING_B_VERSION1));
+    assertFalse(terminologyService.validate(VALUE_SET_Y, CODING_BB_VERSION1));
   }
 
   @Test
@@ -185,7 +152,7 @@ public void testSubsumesDifferentVersions() {
 
   @Test
   public void testSubsumesDifferentSystems() {
-    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_AA, CODING_B_VERSION1));
+    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_AA, CODING_BB_VERSION1));
     verifyNoMoreInteractions(terminologClient);
   }
 
@@ -197,9 +164,9 @@ public void testSubsumesInvalidCodings() {
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_0, CODING_AB));
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_1, CODING_AB));
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_2, CODING_AB));
-    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_B_VERSION1, INVALID_CODING_0));
-    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_B_VERSION1, INVALID_CODING_1));
-    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_B_VERSION1, INVALID_CODING_2));
+    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_BB_VERSION1, INVALID_CODING_0));
+    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_BB_VERSION1, INVALID_CODING_1));
+    assertEquals(NOTSUBSUMED, terminologyService.subsumes(CODING_BB_VERSION1, INVALID_CODING_2));
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_0, INVALID_CODING_1));
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_1, INVALID_CODING_2));
     assertEquals(NOTSUBSUMED, terminologyService.subsumes(INVALID_CODING_2, INVALID_CODING_0));
```
### Patch: terminology/src/test/java/au/csiro/pathling/test/TerminologyTest.java
```diff
@@ -0,0 +1,62 @@
+package au.csiro.pathling.test;
+
+import au.csiro.pathling.fhirpath.encoding.CodingEncoding;
+import java.util.stream.Stream;
+import javax.annotation.Nonnull;
+import org.apache.spark.sql.Row;
+import org.hl7.fhir.r4.model.Coding;
+import scala.collection.mutable.WrappedArray;
+
+public abstract class TerminologyTest {
+
+  public static final String SYSTEM_A = "uuid:systemA";
+  public static final String CODE_A = "codeA";
+  public static final String SYSTEM_B = "uuid:systemB";
+  public static final String CODE_B = "codeB";
+  public static final String SYSTEM_C = "uuid:systemC";
+  public static final String CODE_C = "codeC";
+  public static final String SYSTEM_D = "uuid:systemD";
+  public static final String CODE_D = "codeD";
+
+  public static final Coding CODING_AA = new Coding(SYSTEM_A, CODE_A, "displayAA");
+  public static final Coding CODING_AB = new Coding(SYSTEM_A, CODE_B, "displayAB");
+
+  public static final String VERSION_1 = "version1";
+  public static final String VERSION_2 = "version2";
+
+  public static final Coding CODING_AA_VERSION1 = new Coding(SYSTEM_A, CODE_A,
+      "displayAA").setVersion(
+      VERSION_1);
+  public static final Coding CODING_AB_VERSION1 = new Coding(SYSTEM_A, CODE_B,
+      "displayAB").setVersion(
+      VERSION_1);
+  public static final Coding CODING_AB_VERSION2 = new Coding(SYSTEM_A, CODE_B,
+      "displayAB").setVersion(
+      VERSION_2);
+
+  public static final Coding CODING_BA = new Coding(SYSTEM_B, CODE_A, "displayBA");
+  public static final Coding CODING_BB = new Coding(SYSTEM_B, CODE_B, "displayBB");
+  public static final Coding CODING_BB_VERSION1 = new Coding(SYSTEM_B, CODE_B,
+      "displayB").setVersion(
+      VERSION_1);
+
+  public static final Coding CODING_A = CODING_AA;
+  public static final Coding CODING_B = CODING_BB;
+  public static final Coding CODING_C = new Coding(SYSTEM_C, CODE_C, "displayCC");
+  public static final Coding CODING_D = new Coding(SYSTEM_D, CODE_D, "displayDD");
+
+  public static final Coding INVALID_CODING_0 = new Coding(null, null, "");
+  public static final Coding INVALID_CODING_1 = new Coding("uiid:system", null, "");
+  public static final Coding INVALID_CODING_2 = new Coding(null, "someCode", "");
+
+
+  @Nonnull
+  public static Row[] asArray(@Nonnull final Coding... codings) {
+    return Stream.of(codings).map(CodingEncoding::encode).toArray(Row[]::new);
+  }
+
+  @Nonnull
+  public static WrappedArray<Row> encodeMany(Coding... codings) {
+    return WrappedArray.make(Stream.of(codings).map(CodingEncoding::encode).toArray(Row[]::new));
+  }
+}
```

## Row 45
commit_url: https://github.com/MovingBlocks/Terasology/commit/c92f14ff5c5c73d849f7d6d0d2980846209ebead
rm_type: Rename Variable
rm_description: Rename Variable n : int to MAX_SET_VALUE_COUNT : int in method public testSetEventCall() : void from class org.terasology.config.flexible.SettingTest.Subscribers
file_path: engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java
left_side: [{"filePath": "engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java", "startLine": 97, "endLine": 97, "startColumn": 23, "endColumn": 29, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "original variable declaration", "codeElement": "n : int"}, {"filePath": "engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java", "startLine": 97, "endLine": 97, "startColumn": 13, "endColumn": 30, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java", "startLine": 100, "endLine": 103, "startColumn": 13, "endColumn": 14, "codeElementType": "FOR_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}]
right_side: [{"filePath": "engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java", "startLine": 99, "endLine": 99, "startColumn": 23, "endColumn": 47, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "renamed variable declaration", "codeElement": "MAX_SET_VALUE_COUNT : int"}, {"filePath": "engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java", "startLine": 99, "endLine": 99, "startColumn": 13, "endColumn": 48, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}, {"filePath": "engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java", "startLine": 102, "endLine": 105, "startColumn": 13, "endColumn": 14, "codeElementType": "FOR_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}]

### Patch: engine-tests/src/test/java/org/terasology/config/flexible/SettingTest.java
```diff
@@ -30,14 +30,16 @@
 
 @RunWith(Enclosed.class)
 public class SettingTest {
+    private static final SimpleUri SETTING_ID = new SimpleUri("engine-tests:TestSetting");
+
     public static class SetValue {
         private Setting<Integer> setting;
 
         private int eventResult;
 
         @Before
         public void setUp() {
-            setting = new SettingImpl<>(new SimpleUri("engine-tests:TestSetting"),
+            setting = new SettingImpl<>(SETTING_ID,
                     50, new RangedNumberValidator<>(0, 100, false, false));
 
             eventResult = -1;
@@ -69,7 +71,7 @@ public static class Subscribers {
 
         @Before
         public void setUp() {
-            setting = new SettingImpl<>(new SimpleUri("engine-tests:TestSetting"),
+            setting = new SettingImpl<>(SETTING_ID,
                     50, new RangedNumberValidator<>(0, 100, false, false));
 
             eventCallCount = 0;
@@ -94,51 +96,49 @@ public void testSetEventCall() {
 
             Random random = new FastRandom();
 
-            final int n = 50;
+            final int MAX_SET_VALUE_COUNT = 50;
             int expectedEventCallCount = 0;
 
-            for (int i = 0; i < n; i++) {
-                int r = random.nextInt(-50, 150);
-                expectedEventCallCount += setting.setValue(r) ? 1 : 0;
+            for (int i = 0; i < MAX_SET_VALUE_COUNT; i++) {
+                int randomInt = random.nextInt(-50, 150);
+                expectedEventCallCount += setting.setValue(randomInt) ? 1 : 0;
             }
 
             assertEquals(expectedEventCallCount, eventCallCount);
         }
 
         @Test
         public void testSubscribe() {
-            final int n = 10;
+            final int SUBSCRIBER_COUNT = 10;
 
-            for (int i = 0; i < n; i++) {
+            for (int i = 0; i < SUBSCRIBER_COUNT; i++) {
                 setting.subscribe(propertyChangeEvent -> eventCallCount++);
             }
 
             setting.setValue(30);
 
-            assertEquals(n, eventCallCount);
+            assertEquals(SUBSCRIBER_COUNT, eventCallCount);
         }
 
         @Test
         public void testUnsubscribe() {
-            int n = 10;
+            int subscriberCount = 10;
 
-            PropertyChangeListener[] listeners = new PropertyChangeListener[n];
+            PropertyChangeListener[] listeners = new PropertyChangeListener[subscriberCount];
 
-            for (int i = 0; i < n; i++) {
+            for (int i = 0; i < subscriberCount; i++) {
                 listeners[i] = propertyChangeEvent -> eventCallCount++;
                 setting.subscribe(listeners[i]);
             }
 
-            int halfN = n / 2;
-
-            for (int i = 0; i < new FastRandom().nextInt(halfN); i++) {
+            for (int i = 0; i < new FastRandom().nextInt(subscriberCount / 2); i++) {
                 setting.unsubscribe(listeners[i]);
-                n--;
+                subscriberCount--;
             }
 
             setting.setValue(30);
 
-            assertEquals(n, eventCallCount);
+            assertEquals(subscriberCount, eventCallCount);
         }
     }
 }
```

## Row 46
commit_url: https://github.com/errai/errai/commit/c9298966bc4a505c6db05a4678308c003048e9af
rm_type: Parameterize Variable
rm_description: Parameterize Variable jarFileName : String to jarFileName : String in method private testJarUrlDecoding(jarFileName String) : void from class org.jboss.errai.common.metadata.MetaDataScannerTest
file_path: errai-common/src/test/java/org/jboss/errai/common/metadata/MetaDataScannerTest.java
left_side: [{"filePath": "errai-common/src/test/java/org/jboss/errai/common/metadata/MetaDataScannerTest.java", "startLine": 56, "endLine": 56, "startColumn": 18, "endColumn": 88, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "original variable declaration", "codeElement": "jarFileName : String"}]
right_side: [{"filePath": "errai-common/src/test/java/org/jboss/errai/common/metadata/MetaDataScannerTest.java", "startLine": 47, "endLine": 47, "startColumn": 35, "endColumn": 53, "codeElementType": "SINGLE_VARIABLE_DECLARATION", "description": "renamed variable declaration", "codeElement": "jarFileName : String"}]

### Patch: errai-common/src/test/java/org/jboss/errai/common/metadata/MetaDataScannerTest.java
```diff
@@ -35,36 +35,25 @@
 public class MetaDataScannerTest {
 
   @Test
-  public void testUrlDecodingWithSimpleName() throws Exception {
-    final String jarFileName = "test.jar";
-
-    URL testJarURL = getClass().getClassLoader().getResource(jarFileName);
-    assertNotNull("Jar file not found:" + testJarURL, testJarURL);
-    
-    ClassLoader loader = URLClassLoader.newInstance(new URL[] { testJarURL }, getClass().getClassLoader());
-
-    List<URL> urls = MetaDataScanner.getConfigUrls(loader);
-    
-    String[] segments = urls.get(0).getPath().split("/");
-    assertTrue("No path segments found", segments.length > 0);
-    assertEquals("URL not properly decoded", jarFileName +"!", segments[segments.length - 1]);
-    assertNotNull("Could not open jar", new ZipDir(urls.get(0)).getFiles());
+  public void testJarUrlDecodingWithSimpleName() throws Exception {
+    testJarUrlDecoding("test.jar");
   }
   
   @Test
-  public void testUrlDecodingWithSpecialCharacters() throws Exception {
-    final String jarFileName = "testjar-\u00e4\u00f6\u00e9\u00f8 +abc!@$%^&*()_+}{.jar";
-
+  public void testJarUrlDecodingWithSpecialCharacters() throws Exception {
+    testJarUrlDecoding("testjar-\u00e4\u00f6\u00e9\u00f8 +abc!@$%^&*()_+}{.jar");
+  }
+   
+  private void testJarUrlDecoding(String jarFileName) {
     URL testJarURL = getClass().getClassLoader().getResource(jarFileName);
     assertNotNull("Jar file not found: " + jarFileName, testJarURL);
 
     ClassLoader loader = URLClassLoader.newInstance(new URL[] { testJarURL }, getClass().getClassLoader());
-
     List<URL> urls = MetaDataScanner.getConfigUrls(loader);
-    
     String[] segments = urls.get(0).getPath().split("/");
-    assertTrue("No path segments found", segments.length > 0);
+    
+    assertTrue("No path segments found in URL", segments.length > 0);
     assertEquals("URL not properly decoded", jarFileName +"!", segments[segments.length - 1]);
     assertNotNull("Could not open jar", new ZipDir(urls.get(0)).getFiles());
   }
-}
+}
\ No newline at end of file
```

## Row 47
commit_url: https://github.com/AICP/frameworks_base/commit/693e21d6052b32ad7815d9c0d7bd01fd6170a608
rm_type: Change Class Access Modifier
rm_description: Change Class Access Modifier package to public in class com.android.mediaframeworktest.integration.CameraDeviceBinderTest.DummyCameraDeviceCallbacks
file_path: media/tests/MediaFrameworkTest/src/com/android/mediaframeworktest/integration/CameraDeviceBinderTest.java
left_side: [{"filePath": "media/tests/MediaFrameworkTest/src/com/android/mediaframeworktest/integration/CameraDeviceBinderTest.java", "startLine": 46, "endLine": 55, "startColumn": 5, "endColumn": 6, "codeElementType": "TYPE_DECLARATION", "description": "original class declaration", "codeElement": "com.android.mediaframeworktest.integration.CameraDeviceBinderTest.DummyCameraDeviceCallbacks"}]
right_side: [{"filePath": "media/tests/MediaFrameworkTest/src/com/android/mediaframeworktest/integration/CameraDeviceBinderTest.java", "startLine": 57, "endLine": 66, "startColumn": 5, "endColumn": 6, "codeElementType": "TYPE_DECLARATION", "description": "class declaration with changed access modifier", "codeElement": "com.android.mediaframeworktest.integration.CameraDeviceBinderTest.DummyCameraDeviceCallbacks"}]

### Patch: media/tests/MediaFrameworkTest/src/com/android/mediaframeworktest/integration/CameraDeviceBinderTest.java
```diff
@@ -31,19 +31,30 @@
 import static android.hardware.camera2.CameraDevice.TEMPLATE_PREVIEW;
 
 import com.android.mediaframeworktest.MediaFrameworkIntegrationTestRunner;
-import com.android.mediaframeworktest.integration.CameraBinderTest.DummyBase;
+
+import org.mockito.ArgumentMatcher;
+import static org.mockito.Mockito.*;
 
 public class CameraDeviceBinderTest extends AndroidTestCase {
     private static String TAG = "CameraDeviceBinderTest";
+    // Number of streaming callbacks need to check.
+    private static int NUM_CALLBACKS_CHECKED = 10;
+    // Wait for capture result timeout value: 1000ms
+    private final static int WAIT_FOR_COMPLETE_TIMEOUT_MS = 1000;
 
     private int mCameraId;
     private ICameraDeviceUser mCameraUser;
     private CameraBinderTestUtils mUtils;
+    private ICameraDeviceCallbacks.Stub mMockCb;
+    private Surface mSurface;
+    // Need hold a Surfacetexture reference during a test execution, otherwise,
+    // it could be GCed during a test, which causes camera run into bad state.
+    private SurfaceTexture mSurfaceTexture;
 
     public CameraDeviceBinderTest() {
     }
 
-    static class DummyCameraDeviceCallbacks extends DummyBase implements ICameraDeviceCallbacks {
+    public class DummyCameraDeviceCallbacks extends ICameraDeviceCallbacks.Stub {
 
         @Override
         public void notifyCallback(int msgType, int ext1, int ext2) throws RemoteException {
@@ -54,23 +65,74 @@ public void onResultReceived(int frameId, CameraMetadata result) throws RemoteEx
         }
     }
 
+    class IsMetadataNotEmpty extends ArgumentMatcher<CameraMetadata> {
+        public boolean matches(Object obj) {
+            return !((CameraMetadata) obj).isEmpty();
+        }
+     }
+
+    private void createDefaultSurface() {
+        mSurfaceTexture = new SurfaceTexture(/* ignored */0);
+        mSurfaceTexture.setDefaultBufferSize(640, 480);
+        mSurface = new Surface(mSurfaceTexture);
+    }
+
+    private CaptureRequest createDefaultRequest(boolean needStream) throws Exception {
+        CameraMetadata metadata = new CameraMetadata();
+        assertTrue(metadata.isEmpty());
+
+        CaptureRequest request = new CaptureRequest();
+        assertTrue(request.isEmpty());
+
+        int status = mCameraUser.createDefaultRequest(TEMPLATE_PREVIEW, /* out */metadata);
+        assertEquals(CameraBinderTestUtils.NO_ERROR, status);
+        assertFalse(metadata.isEmpty());
+
+        request.swap(metadata);
+        assertFalse(request.isEmpty());
+        assertTrue(metadata.isEmpty());
+        if (needStream) {
+            int streamId = mCameraUser.createStream(/* ignored */10, /* ignored */20,
+                    /* ignored */30, mSurface);
+            assertEquals(0, streamId);
+            request.addTarget(mSurface);
+        }
+        return request;
+    }
+
+    private int submitCameraRequest(CaptureRequest request, boolean streaming) throws Exception {
+        int requestId = mCameraUser.submitRequest(request, streaming);
+        assertTrue("Request IDs should be non-negative", requestId >= 0);
+        return requestId;
+    }
+
     @Override
     protected void setUp() throws Exception {
         super.setUp();
 
+        /**
+         * Workaround for mockito and JB-MR2 incompatibility
+         *
+         * Avoid java.lang.IllegalArgumentException: dexcache == null
+         * https://code.google.com/p/dexmaker/issues/detail?id=2
+         */
+        System.setProperty("dexmaker.dexcache", getContext().getCacheDir().toString());
         mUtils = new CameraBinderTestUtils(getContext());
 
         // This cannot be set in the constructor, since the onCreate isn't
         // called yet
         mCameraId = MediaFrameworkIntegrationTestRunner.mCameraId;
 
-        ICameraDeviceCallbacks dummyCallbacks = new DummyCameraDeviceCallbacks();
+        ICameraDeviceCallbacks.Stub dummyCallbacks = new DummyCameraDeviceCallbacks();
 
         String clientPackageName = getContext().getPackageName();
 
-        mCameraUser = mUtils.getCameraService().connectDevice(dummyCallbacks, mCameraId,
+        mMockCb = spy(dummyCallbacks);
+
+        mCameraUser = mUtils.getCameraService().connectDevice(mMockCb, mCameraId,
                 clientPackageName, CameraBinderTestUtils.USE_CALLING_UID);
         assertNotNull(String.format("Camera %s was null", mCameraId), mCameraUser);
+        createDefaultSurface();
 
         Log.v(TAG, String.format("Camera %s connected", mCameraId));
     }
@@ -79,6 +141,8 @@ protected void setUp() throws Exception {
     protected void tearDown() throws Exception {
         mCameraUser.disconnect();
         mCameraUser = null;
+        mSurface.release();
+        mSurfaceTexture.release();
     }
 
     @SmallTest
@@ -95,17 +159,12 @@ public void testCreateDefaultRequest() throws Exception {
 
     @SmallTest
     public void testCreateStream() throws Exception {
-        SurfaceTexture surfaceTexture = new SurfaceTexture(/* ignored */0);
-        surfaceTexture.setDefaultBufferSize(640, 480);
-        Surface surface = new Surface(surfaceTexture);
-
         int streamId = mCameraUser.createStream(/* ignored */10, /* ignored */20, /* ignored */30,
-                surface);
-
+                mSurface);
         assertEquals(0, streamId);
 
         assertEquals(CameraBinderTestUtils.ALREADY_EXISTS,
-                mCameraUser.createStream(/* ignored */0, /* ignored */0, /* ignored */0, surface));
+                mCameraUser.createStream(/* ignored */0, /* ignored */0, /* ignored */0, mSurface));
 
         assertEquals(CameraBinderTestUtils.NO_ERROR, mCameraUser.deleteStream(streamId));
     }
@@ -122,164 +181,71 @@ public void testDeleteInvalidStream() throws Exception {
     public void testCreateStreamTwo() throws Exception {
 
         // Create first stream
-
-        SurfaceTexture surfaceTexture = new SurfaceTexture(/* ignored */0);
-        surfaceTexture.setDefaultBufferSize(640, 480);
-        Surface surface = new Surface(surfaceTexture);
-
         int streamId = mCameraUser.createStream(/* ignored */0, /* ignored */0, /* ignored */0,
-                surface);
-
+                mSurface);
         assertEquals(0, streamId);
 
         assertEquals(CameraBinderTestUtils.ALREADY_EXISTS,
-                mCameraUser.createStream(/* ignored */0, /* ignored */0, /* ignored */0, surface));
+                mCameraUser.createStream(/* ignored */0, /* ignored */0, /* ignored */0, mSurface));
 
-        // Create second stream.
-
-        SurfaceTexture surfaceTexture2 = new SurfaceTexture(/* ignored */0);
-        surfaceTexture2.setDefaultBufferSize(640, 480);
-        Surface surface2 = new Surface(surfaceTexture2);
+        // Create second stream with a different surface.
+        SurfaceTexture surfaceTexture = new SurfaceTexture(/* ignored */0);
+        surfaceTexture.setDefaultBufferSize(640, 480);
+        Surface surface2 = new Surface(surfaceTexture);
 
         int streamId2 = mCameraUser.createStream(/* ignored */0, /* ignored */0, /* ignored */0,
                 surface2);
-
         assertEquals(1, streamId2);
 
         // Clean up streams
-
         assertEquals(CameraBinderTestUtils.NO_ERROR, mCameraUser.deleteStream(streamId));
         assertEquals(CameraBinderTestUtils.NO_ERROR, mCameraUser.deleteStream(streamId2));
     }
 
     @SmallTest
     public void testSubmitBadRequest() throws Exception {
 
-        CameraMetadata metadata = new CameraMetadata();
-        assertTrue(metadata.isEmpty());
-
-        CaptureRequest request = new CaptureRequest();
-        assertTrue(request.isEmpty());
-
-        int status = mCameraUser.createDefaultRequest(TEMPLATE_PREVIEW, /* out */metadata);
-        assertEquals(CameraBinderTestUtils.NO_ERROR, status);
-        assertFalse(metadata.isEmpty());
-
-        request.swap(metadata);
-        assertFalse(request.isEmpty());
-        assertTrue(metadata.isEmpty());
-
-        status = mCameraUser.submitRequest(request, /* streaming */false);
+        CaptureRequest request = createDefaultRequest(/* needStream */false);
+        int status = mCameraUser.submitRequest(request, /* streaming */false);
         assertEquals("Expected submitRequest to return BAD_VALUE " +
                 "since we had 0 surface targets set.", CameraBinderTestUtils.BAD_VALUE, status);
 
-        SurfaceTexture surfaceTexture = new SurfaceTexture(/* ignored */0);
-        surfaceTexture.setDefaultBufferSize(640, 480);
-        Surface surface = new Surface(surfaceTexture);
-        request.addTarget(surface);
-
+        request.addTarget(mSurface);
         status = mCameraUser.submitRequest(request, /* streaming */false);
         assertEquals("Expected submitRequest to return BAD_VALUE since " +
                 "the target surface wasn't registered with createStream.",
                 CameraBinderTestUtils.BAD_VALUE, status);
 
         request.close();
-        metadata.close();
-        surface.release();
     }
 
     @SmallTest
     public void testSubmitGoodRequest() throws Exception {
 
-        CameraMetadata metadata = new CameraMetadata();
-        assertTrue(metadata.isEmpty());
-
-        CaptureRequest request = new CaptureRequest();
-        assertTrue(request.isEmpty());
-
-        // Create default request from template.
-
-        int status = mCameraUser.createDefaultRequest(TEMPLATE_PREVIEW, /* out */metadata);
-        assertEquals(CameraBinderTestUtils.NO_ERROR, status);
-        assertFalse(metadata.isEmpty());
-
-        request.swap(metadata);
-        assertFalse(request.isEmpty());
-        assertTrue(metadata.isEmpty());
-
-        SurfaceTexture surfaceTexture = new SurfaceTexture(/* ignored */0);
-        surfaceTexture.setDefaultBufferSize(640, 480);
-        Surface surface = new Surface(surfaceTexture);
-
-        // Create stream first. Pre-requisite to submitting a request using that
-        // stream.
-
-        int streamId = mCameraUser.createStream(/* ignored */10, /* ignored */20, /* ignored */30,
-                surface);
-        assertEquals(0, streamId);
-
-        request.addTarget(surface);
+        CaptureRequest request = createDefaultRequest(/* needStream */true);
 
         // Submit valid request twice.
-
-        int requestId1;
-        requestId1 = mCameraUser.submitRequest(request, /* streaming */false);
-        assertTrue("Request IDs should be non-negative", requestId1 >= 0);
-
-        int requestId2 = mCameraUser.submitRequest(request, /* streaming */false);
-        assertTrue("Request IDs should be non-negative", requestId2 >= 0);
+        int requestId1 = submitCameraRequest(request, /* streaming */false);
+        int requestId2 = submitCameraRequest(request, /* streaming */false);
         assertNotSame("Request IDs should be unique for multiple requests", requestId1, requestId2);
 
-        surface.release();
         request.close();
-        metadata.close();
     }
 
     @SmallTest
     public void testSubmitStreamingRequest() throws Exception {
 
-        CameraMetadata metadata = new CameraMetadata();
-        assertTrue(metadata.isEmpty());
-
-        CaptureRequest request = new CaptureRequest();
-        assertTrue(request.isEmpty());
-
-        // Create default request from template.
-
-        int status = mCameraUser.createDefaultRequest(TEMPLATE_PREVIEW, /* out */metadata);
-        assertEquals(CameraBinderTestUtils.NO_ERROR, status);
-        assertFalse(metadata.isEmpty());
-
-        request.swap(metadata);
-        assertFalse(request.isEmpty());
-        assertTrue(metadata.isEmpty());
-
-        SurfaceTexture surfaceTexture = new SurfaceTexture(/* ignored */0);
-        surfaceTexture.setDefaultBufferSize(640, 480);
-        Surface surface = new Surface(surfaceTexture);
-
-        // Create stream first. Pre-requisite to submitting a request using that
-        // stream.
-
-        int streamId = mCameraUser.createStream(/* ignored */10, /* ignored */20, /* ignored */30,
-                surface);
-        assertEquals(0, streamId);
-
-        request.addTarget(surface);
+        CaptureRequest request = createDefaultRequest(/* needStream */true);
 
         // Submit valid request once (non-streaming), and another time
         // (streaming)
+        int requestId1 = submitCameraRequest(request, /* streaming */false);
 
-        int requestId1;
-        requestId1 = mCameraUser.submitRequest(request, /* streaming */false);
-        assertTrue("Request IDs should be non-negative", requestId1 >= 0);
-
-        int requestIdStreaming = mCameraUser.submitRequest(request, /* streaming */true);
-        assertTrue("Request IDs should be non-negative", requestIdStreaming >= 0);
+        int requestIdStreaming = submitCameraRequest(request, /* streaming */true);
         assertNotSame("Request IDs should be unique for multiple requests", requestId1,
                 requestIdStreaming);
 
-        status = mCameraUser.cancelRequest(-1);
+        int status = mCameraUser.cancelRequest(-1);
         assertEquals("Invalid request IDs should not be cancellable",
                 CameraBinderTestUtils.BAD_VALUE, status);
 
@@ -291,9 +257,7 @@ public void testSubmitStreamingRequest() throws Exception {
         assertEquals("Streaming request IDs should be cancellable", CameraBinderTestUtils.NO_ERROR,
                 status);
 
-        surface.release();
         request.close();
-        metadata.close();
     }
 
     @SmallTest
@@ -309,39 +273,11 @@ public void testCameraInfo() throws RemoteException {
 
     @SmallTest
     public void testWaitUntilIdle() throws Exception {
-        CameraMetadata metadata = new CameraMetadata();
-        assertTrue(metadata.isEmpty());
-
-        CaptureRequest request = new CaptureRequest();
-        assertTrue(request.isEmpty());
-
-        // Create default request from template.
-        int status = mCameraUser.createDefaultRequest(TEMPLATE_PREVIEW, /* out */metadata);
-        assertEquals(CameraBinderTestUtils.NO_ERROR, status);
-        assertFalse(metadata.isEmpty());
-
-        request.swap(metadata);
-        assertFalse(request.isEmpty());
-        assertTrue(metadata.isEmpty());
-
-        SurfaceTexture surfaceTexture = new SurfaceTexture(/* ignored */0);
-        surfaceTexture.setDefaultBufferSize(640, 480);
-        Surface surface = new Surface(surfaceTexture);
-
-        // Create stream first. Pre-requisite to submitting a request using that
-        // stream.
-
-        int streamId = mCameraUser.createStream(/* ignored */10, /* ignored */20, /* ignored */30,
-                surface);
-        assertEquals(0, streamId);
-
-        request.addTarget(surface);
-
-        int requestIdStreaming = mCameraUser.submitRequest(request, /* streaming */true);
-        assertTrue("Request IDs should be non-negative", requestIdStreaming >= 0);
+        CaptureRequest request = createDefaultRequest(/* needStream */true);
+        int requestIdStreaming = submitCameraRequest(request, /* streaming */true);
 
         // Test Bad case first: waitUntilIdle when there is active repeating request
-        status = mCameraUser.waitUntilIdle();
+        int status = mCameraUser.waitUntilIdle();
         assertEquals("waitUntilIdle is invalid operation when there is active repeating request",
             CameraBinderTestUtils.INVALID_OPERATION, status);
 
@@ -352,4 +288,22 @@ public void testWaitUntilIdle() throws Exception {
         assertEquals(CameraBinderTestUtils.NO_ERROR, status);
     }
 
+    @SmallTest
+    public void testCaptureResultCallbacks() throws Exception {
+        IsMetadataNotEmpty matcher = new IsMetadataNotEmpty();
+        CaptureRequest request = createDefaultRequest(/* needStream */true);
+
+        // Test both single request and streaming request.
+        int requestId1 = submitCameraRequest(request, /* streaming */false);
+        verify(mMockCb, timeout(WAIT_FOR_COMPLETE_TIMEOUT_MS).times(1)).onResultReceived(
+                eq(requestId1),
+                argThat(matcher));
+
+        int streamingId = submitCameraRequest(request, /* streaming */true);
+        verify(mMockCb, timeout(WAIT_FOR_COMPLETE_TIMEOUT_MS).atLeast(NUM_CALLBACKS_CHECKED))
+                .onResultReceived(
+                        eq(streamingId),
+                        argThat(matcher));
+        request.close();
+    }
 }
```

## Row 48
commit_url: https://github.com/fabric8io/fabric8-maven-plugin/commit/89abcae3019d2bcbd05142f83353165e581a49b2
rm_type: Modify Method Annotation
rm_description: Modify Method Annotation @Test to @Test(expected = IllegalArgumentException.class) in method public replicationControllerHandlerWithoutControllerTest() : void from class io.fabric8.maven.core.handler.ReplicationControllerHandlerTest
file_path: core/src/test/java/io/fabric8/maven/core/handler/ReplicationControllerHandlerTest.java
left_side: [{"filePath": "core/src/test/java/io/fabric8/maven/core/handler/ReplicationControllerHandlerTest.java", "startLine": 149, "endLine": 149, "startColumn": 5, "endColumn": 10, "codeElementType": "ANNOTATION", "description": "original annotation", "codeElement": "@Test"}, {"filePath": "core/src/test/java/io/fabric8/maven/core/handler/ReplicationControllerHandlerTest.java", "startLine": 149, "endLine": 176, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "original method declaration", "codeElement": "public replicationControllerHandlerThirdTest() : void"}]
right_side: [{"filePath": "core/src/test/java/io/fabric8/maven/core/handler/ReplicationControllerHandlerTest.java", "startLine": 140, "endLine": 140, "startColumn": 5, "endColumn": 53, "codeElementType": "ANNOTATION", "description": "modified annotation", "codeElement": "@Test(expected = IllegalArgumentException.class)"}, {"filePath": "core/src/test/java/io/fabric8/maven/core/handler/ReplicationControllerHandlerTest.java", "startLine": 140, "endLine": 159, "startColumn": 5, "endColumn": 6, "codeElementType": "METHOD_DECLARATION", "description": "method declaration with modified annotation", "codeElement": "public replicationControllerHandlerWithoutControllerTest() : void"}]

### Patch: core/src/test/java/io/fabric8/maven/core/handler/ReplicationControllerHandlerTest.java
```diff
@@ -115,63 +115,46 @@ public void replicationControllerHandlerTest() {
 
     }
 
-    @Test
-    //invalid controller name
-    public void replicationControllerHandlerSecondTest() {
-        try {
-
-            ContainerHandler containerHandler =
-                    new ContainerHandler(project, envVarHandler, probeHandler);
-
-            PodTemplateHandler podTemplateHandler = new PodTemplateHandler(containerHandler);
-
-            ReplicationControllerHandler replicationControllerHandler = new ReplicationControllerHandler(podTemplateHandler);
-
-            //with invalid controller name
-            ResourceConfig config = new ResourceConfig.Builder()
-                    .imagePullPolicy("IfNotPresent")
-                    .controllerName("TesTing")
-                    .withServiceAccount("test-account")
-                    .withReplicas(5)
-                    .volumes(volumes1)
-                    .build();
-
-            replicationControllerHandler.getReplicationController(config, images);
-        }
-        //asserting the exact message because
-        // it throws the same exception in case controller name is null
-        catch(IllegalArgumentException exception) {
-            assertEquals("Invalid upper case letter 'T' at index 0 for " +
-                    "replication controller name value: TesTing", exception.getMessage());
-        }
+    @Test(expected = IllegalArgumentException.class)
+    public void replicationControllerHandlerWithInvalidNameTest() {
+        //invalid controller name
+        ContainerHandler containerHandler =
+                new ContainerHandler(project, envVarHandler, probeHandler);
+
+        PodTemplateHandler podTemplateHandler = new PodTemplateHandler(containerHandler);
+
+        ReplicationControllerHandler replicationControllerHandler = new ReplicationControllerHandler(podTemplateHandler);
+
+        //with invalid controller name
+        ResourceConfig config = new ResourceConfig.Builder()
+                .imagePullPolicy("IfNotPresent")
+                .controllerName("TesTing")
+                .withServiceAccount("test-account")
+                .withReplicas(5)
+                .volumes(volumes1)
+                .build();
+
+        replicationControllerHandler.getReplicationController(config, images);
     }
 
-    @Test
-    //without controller name
-    public void replicationControllerHandlerThirdTest() {
-        try {
-
-            ContainerHandler containerHandler = new
-                    ContainerHandler(project, envVarHandler, probeHandler);
-
-            PodTemplateHandler podTemplateHandler = new PodTemplateHandler(containerHandler);
-
-            ReplicationControllerHandler replicationControllerHandler = new ReplicationControllerHandler(podTemplateHandler);
-
-            //without controller name
-            ResourceConfig config = new ResourceConfig.Builder()
-                    .imagePullPolicy("IfNotPresent")
-                    .withServiceAccount("test-account")
-                    .withReplicas(5)
-                    .volumes(volumes1)
-                    .build();
-
-            replicationControllerHandler.getReplicationController(config, images);
-        }
-        //asserting the exact message because
-        //it throws the same exception in case controller name is invalid
-        catch(IllegalArgumentException exception) {
-            assertEquals("No replication controller name is specified!", exception.getMessage());
-        }
+    @Test(expected = IllegalArgumentException.class)
+    public void replicationControllerHandlerWithoutControllerTest() {
+        //without controller name
+        ContainerHandler containerHandler = new
+                ContainerHandler(project, envVarHandler, probeHandler);
+
+        PodTemplateHandler podTemplateHandler = new PodTemplateHandler(containerHandler);
+
+        ReplicationControllerHandler replicationControllerHandler = new ReplicationControllerHandler(podTemplateHandler);
+
+        //without controller name
+        ResourceConfig config = new ResourceConfig.Builder()
+                .imagePullPolicy("IfNotPresent")
+                .withServiceAccount("test-account")
+                .withReplicas(5)
+                .volumes(volumes1)
+                .build();
+
+        replicationControllerHandler.getReplicationController(config, images);
     }
 }
\ No newline at end of file
```

## Row 49
commit_url: https://github.com/jitsi/jitsi-meet-torture/commit/30cefac130c36abbaf6e80fee210a3f803304d3b
rm_type: Rename Variable
rm_description: Rename Variable testsToRun : String to testsToRunString : String in method public suite() : TestSuite from class org.jitsi.meet.test.TestsRunner
file_path: src/org/jitsi/meet/test/TestsRunner.java
left_side: [{"filePath": "src/org/jitsi/meet/test/TestsRunner.java", "startLine": 42, "endLine": 42, "startColumn": 16, "endColumn": 73, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "original variable declaration", "codeElement": "testsToRun : String"}, {"filePath": "src/org/jitsi/meet/test/TestsRunner.java", "startLine": 42, "endLine": 42, "startColumn": 9, "endColumn": 74, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}, {"filePath": "src/org/jitsi/meet/test/TestsRunner.java", "startLine": 73, "endLine": 73, "startColumn": 13, "endColumn": 75, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the original variable", "codeElement": null}]
right_side: [{"filePath": "src/org/jitsi/meet/test/TestsRunner.java", "startLine": 99, "endLine": 99, "startColumn": 16, "endColumn": 73, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "renamed variable declaration", "codeElement": "testsToRunString : String"}, {"filePath": "src/org/jitsi/meet/test/TestsRunner.java", "startLine": 99, "endLine": 99, "startColumn": 9, "endColumn": 74, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}, {"filePath": "src/org/jitsi/meet/test/TestsRunner.java", "startLine": 107, "endLine": 107, "startColumn": 13, "endColumn": 81, "codeElementType": "VARIABLE_DECLARATION_STATEMENT", "description": "statement referencing the renamed variable", "codeElement": null}]

### Patch: src/org/jitsi/meet/test/TestsRunner.java
```diff
@@ -29,6 +29,61 @@
  */
 public class TestsRunner
 {
+    /**
+     * The name of the property which controls the list of tests to be run.
+     */
+    private static final String TESTS_TO_RUN_PNAME = "jitsi-meet.tests.toRun";
+
+    /**
+     * The name of the property which controls the set of tests to be excluded
+     * (i.e. not run).
+     */
+    private static final String TESTS_TO_EXCLUDE_PNAME
+            = "jitsi-meet.tests.toExclude";
+
+    /**
+     * The name of the SetupConference class.
+     */
+    private static final String SETUP_CONFERENCE_NAME = "SetupConference";
+
+    /**
+     * The name of the DisposeConference class.
+     */
+    private static final String DISPOSE_CONFERENCE_NAME = "DisposeConference";
+
+    /**
+     * The default list of tests to run. This does not include SetupConference
+     * and DisposeConference; they will be added separately.
+     *
+     * The list contains class names relative to this class' package.
+     */
+    private static final List<String> DEFAULT_TESTS_TO_RUN
+            = new LinkedList<String>();
+
+    static
+    {
+        DEFAULT_TESTS_TO_RUN.add("AvatarTest");
+        DEFAULT_TESTS_TO_RUN.add("MuteTest");
+        DEFAULT_TESTS_TO_RUN.add("StopVideoTest");
+        DEFAULT_TESTS_TO_RUN.add("SwitchVideoTests");
+        DEFAULT_TESTS_TO_RUN.add("EtherpadTests");
+        DEFAULT_TESTS_TO_RUN.add("LockRoomTest");
+        // doing the same test two more times to be sure it is
+        // not a problem, as there was reported an issue about that
+        // https://github.com/jitsi/jitsi-meet/issues/83
+        DEFAULT_TESTS_TO_RUN.add("LockRoomTest");
+        DEFAULT_TESTS_TO_RUN.add("LockRoomTest");
+
+        DEFAULT_TESTS_TO_RUN.add("UDPTest");
+        DEFAULT_TESTS_TO_RUN.add("TCPTest");
+
+        DEFAULT_TESTS_TO_RUN.add("ActiveSpeakerTest");
+
+        DEFAULT_TESTS_TO_RUN.add("StartMutedTest");
+
+        DEFAULT_TESTS_TO_RUN.add("DisplayNameTest");
+    }
+
     /**
      * The tests that are currently started.
      * If the property jitsi-meet.tests.toRun exists we use its values to
@@ -39,76 +94,84 @@ public static TestSuite suite()
     {
         TestSuite suite = new TestSuite();
 
-        String testsToRun = System.getProperty("jitsi-meet.tests.toRun");
+        List<String> testsToRun = new LinkedList<String>();
 
-        if(testsToRun == null || testsToRun.equalsIgnoreCase("all"))
+        String testsToRunString = System.getProperty(TESTS_TO_RUN_PNAME);
+        if (testsToRunString == null
+                || testsToRunString.equalsIgnoreCase("all"))
         {
-            suite.addTest(SetupConference.suite());
-
-            suite.addTest(AvatarTest.suite());
-            suite.addTest(MuteTest.suite());
-            suite.addTest(StopVideoTest.suite());
-            suite.addTest(SwitchVideoTests.suite());
-            suite.addTest(EtherpadTests.suite());
-            suite.addTest(LockRoomTest.suite());
-            // doing the same test two more times to be sure it is
-            // not a problem, as there was reported an issue about that
-            // https://github.com/jitsi/jitsi-meet/issues/83
-            suite.addTest(LockRoomTest.suite());
-            suite.addTest(LockRoomTest.suite());
-
-            suite.addTest(TCPTest.suite());
+            testsToRun.addAll(DEFAULT_TESTS_TO_RUN);
+        }
+        else
+        {
+            StringTokenizer tokens = new StringTokenizer(testsToRunString, ",");
+            while (tokens.hasMoreTokens())
+            {
+                testsToRun.add(tokens.nextToken());
+            }
+        }
 
-            suite.addTest(ActiveSpeakerTest.suite());
+        String testsToExclude = System.getProperty(TESTS_TO_EXCLUDE_PNAME);
+        if (testsToExclude != null)
+        {
+            StringTokenizer tokens = new StringTokenizer(testsToExclude, ",");
+            while (tokens.hasMoreTokens())
+            {
+                String token = tokens.nextToken();
+                while (testsToRun.remove(token))
+                    ;
+            }
+        }
 
-            suite.addTest(StartMutedTest.suite());
+        // SetupConference and DisposeConference must always be run exactly
+        // once in the beginning and end of the tests.
+        // They could potentially be moved to setUp() and tearDown().
+        while(testsToRun.remove(SETUP_CONFERENCE_NAME))
+            ;
+        while(testsToRun.remove(DISPOSE_CONFERENCE_NAME))
+            ;
+        testsToRun.add(0, SETUP_CONFERENCE_NAME);
+        testsToRun.add(DISPOSE_CONFERENCE_NAME);
 
-            suite.addTestSuite(DisplayNameTest.class);
 
-            suite.addTestSuite(DisposeConference.class);
-        }
-        else
+        for (String testName : testsToRun)
         {
-            // it is a comma separated list of class names
-            StringTokenizer tokens = new StringTokenizer(testsToRun, ",");
-            while(tokens.hasMoreTokens())
+            // class names are relative to this package
+            String className = TestsRunner.class.getPackage().getName()
+                + "." + testName;
+
+            try
             {
-                String testName = tokens.nextToken();
-                // class names are relative to this package
-                String className = "org.jitsi.meet.test." + testName;
+                Class<? extends TestCase> cl
+                    = Class.forName(className).asSubclass(TestCase.class);
 
-                try
+                Method suiteMethod = null;
+                for(Method m : cl.getDeclaredMethods())
                 {
-                    Class<? extends TestCase> cl
-                        = Class.forName(className).asSubclass(TestCase.class);
-
-                    Method suiteMethod = null;
-                    for(Method m : cl.getDeclaredMethods())
+                    if(m.getName().equals("suite"))
                     {
-                        if(m.getName().equals("suite"))
-                        {
-                            suiteMethod = m;
-                            break;
-                        }
+                        suiteMethod = m;
+                        break;
                     }
+                }
 
-                    // if suite method exists use it
-                    if(suiteMethod != null)
-                    {
-                        Object test = suiteMethod.invoke(null);
-                        suite.addTest((Test)test);
-                    }
-                    else
-                    {
-                        // otherwise just use the class
-                        suite.addTestSuite(cl);
-                    }
+                // if suite method exists use it
+                if(suiteMethod != null)
+                {
+                    Object test = suiteMethod.invoke(null);
+                    suite.addTest((Test)test);
                 }
-                catch(Throwable t)
+                else
                 {
-                    t.printStackTrace();
+                    // otherwise just use the class
+                    suite.addTestSuite(cl);
                 }
             }
+            catch(Throwable t)
+            {
+                System.err.println("Not running " + testName);
+                t.printStackTrace();
+            }
         }
 
         String fakeStreamAudioFile
```

## Row 50
commit_url: https://github.com/Yubico/yubikit-android/commit/df6326d29147b485207f305621d1afaf29935f0e
rm_type: Remove Attribute Modifier
rm_description: Remove Attribute Modifier final in attribute private value : Object from class com.yubico.yubikit.fido.CborTest.TestData
file_path: fido/src/test/java/com/yubico/yubikit/fido/CborTest.java
left_side: [{"filePath": "fido/src/test/java/com/yubico/yubikit/fido/CborTest.java", "startLine": 91, "endLine": 91, "startColumn": 30, "endColumn": 35, "codeElementType": "FIELD_DECLARATION", "description": "original attribute declaration", "codeElement": "private value : Object"}]
right_side: [{"filePath": "fido/src/test/java/com/yubico/yubikit/fido/CborTest.java", "startLine": 56, "endLine": 56, "startColumn": 23, "endColumn": 28, "codeElementType": "FIELD_DECLARATION", "description": "attribute declaration with removed modifier", "codeElement": "public value : Object"}]

### Patch: fido/src/test/java/com/yubico/yubikit/fido/CborTest.java
```diff
@@ -16,20 +16,233 @@
 
 package com.yubico.yubikit.fido;
 
+import static com.yubico.yubikit.fido.TestUtils.decodeHex;
+import static com.yubico.yubikit.fido.TestUtils.encodeHex;
+
 import org.junit.Assert;
 import org.junit.Test;
+import org.junit.experimental.runners.Enclosed;
+import org.junit.runner.RunWith;
+import org.junit.runners.Parameterized;
+import org.junit.runners.Parameterized.Parameter;
+import org.junit.runners.Parameterized.Parameters;
 
 import java.util.ArrayList;
 import java.util.Arrays;
+import java.util.Collection;
 import java.util.HashMap;
 import java.util.List;
 import java.util.Map;
 
-import static com.yubico.yubikit.fido.TestUtils.decodeHex;
-import static com.yubico.yubikit.fido.TestUtils.encodeHex;
-
+/**
+ * Unit tests for cbor functionality implemented in {@code Cbor} class.
+ */
+@RunWith(Enclosed.class)
 public class CborTest {
+    /**
+     * Superclass for cbor parametrized tests.
+     * <p>
+     * Subclasses need to be annotated with {@code @RunWith(Parameterized.class)} and implement one
+     * or more {@code @Test} methods and return test data through {@code @Parameters data()}
+     */
+    private static class ParametrizedCborTest {
+
+        @SuppressWarnings("NotNullFieldNotInitialized")
+        @Parameter
+        public String cborHex;
 
+        @SuppressWarnings("NotNullFieldNotInitialized")
+        @Parameter(1)
+        public Object value;
+    }
+
+    /**
+     * Tests encoding and decoding of integer types
+     */
+    @RunWith(Parameterized.class)
+    public static class IntegerTest extends ParametrizedCborTest {
+        @Parameters
+        public static Collection<Object[]> data() {
+            return Arrays.asList(new Object[][]{
+                    {"00", 0},
+                    {"01", 1},
+                    {"0a", 10},
+                    {"17", 23},
+                    {"1818", 24},
+                    {"1819", 25},
+                    {"1864", 100},
+                    {"1903e8", 1000},
+                    {"1a000f4240", 1000000},
+                    {"19ffff", 65535},
+                    {"1a00010000", 65536},
+                    {"1a7fffffff", Integer.MAX_VALUE},
+                    {"20", -1},
+                    {"29", -10},
+                    {"37", -24},
+                    {"3818", -25},
+                    {"3863", -100},
+                    {"3903e7", -1000},
+                    {"3a7fffffff", Integer.MIN_VALUE},
+            });
+        }
+
+        @Test
+        public void testInteger() {
+            assertCborEncodeAndDecode(cborHex, value);
+        }
+    }
+
+    /**
+     * Tests encoding and decoding of simple boolean values
+     */
+    @RunWith(Parameterized.class)
+    public static class SimpleBooleanTest extends ParametrizedCborTest {
+        @Parameters
+        public static Collection<Object[]> data() {
+            return Arrays.asList(new Object[][]{
+                    {"f4", false},
+                    {"f5", true},
+            });
+        }
+
+        @Test
+        public void testSimpleBoolean() {
+            assertCborEncodeAndDecode(cborHex, value);
+        }
+    }
+
+    /**
+     * Tests encoding and decoding of byte array values
+     */
+    @RunWith(Parameterized.class)
+    public static class ByteArrayTest extends ParametrizedCborTest {
+        @Parameters
+        public static Collection<Object[]> data() {
+            return Arrays.asList(new Object[][]{
+                    {"40", new byte[0]},
+                    {"4401020304", new byte[]{1, 2, 3, 4}},
+            });
+        }
+
+        @Test
+        public void testByteArray() {
+            assertCborEncodeAndDecode(cborHex, value);
+        }
+    }
+
+    /**
+     * Tests encoding and decoding of String values
+     */
+    @RunWith(Parameterized.class)
+    public static class StringTest extends ParametrizedCborTest {
+        @Parameters
+        public static Collection<Object[]> data() {
+            return Arrays.asList(new Object[][]{
+                    {"40", new byte[0]},
+                    {"4401020304", new byte[]{1, 2, 3, 4}},
+                    {"60", ""},
+                    {"6161", "a"},
+                    {"6449455446", "IETF"},
+                    {"62225c", "\"\\"},
+                    {"62c3bc", "ü"},
+                    {"63e6b0b4", "水"},
+                    {"64f0908591", "\ud800\udd51"},
+            });
+        }
+
+        @Test
+        public void testString() {
+            assertCborEncodeAndDecode(cborHex, value);
+        }
+    }
+
+    /**
+     * Tests encoding and decoding of Lists
+     */
+    @RunWith(Parameterized.class)
+    public static class ListTest extends ParametrizedCborTest {
+        @Parameters
+        public static Collection<Object[]> data() {
+            return Arrays.asList(new Object[][]{
+                    {"80", listOf()},
+                    {"83010203", listOf(1, 2, 3)},
+                    {"8301820203820405", listOf(1, listOf(2, 3), listOf(4, 5))},
+                    {"98190102030405060708090a0b0c0d0e0f101112131415161718181819", listOf(
+                            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
+                            15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25)
+                    },
+            });
+        }
+
+        @Test
+        public void testList() {
+            assertCborEncodeAndDecode(cborHex, value);
+        }
+    }
+
+    /**
+     * Tests encoding and decoding of Maps
+     */
+    @RunWith(Parameterized.class)
+    public static class MapTest extends ParametrizedCborTest {
+        @Parameters
+        public static Collection<Object[]> data() {
+            return Arrays.asList(new Object[][]{
+                    {"a0", mapOf()},
+                    {"a201020304", mapOf(1, 2, 3, 4)},
+                    {"a26161016162820203", mapOf("a", 1, "b", listOf(2, 3))},
+                    {"826161a161626163", listOf("a", mapOf("b", "c"))},
+                    {"a56161614161626142616361436164614461656145",
+                            mapOf("c", "C", "d", "D", "a", "A", "b", "B", "e", "E")
+                    },
+            });
+        }
+
+        @Test
+        public void testMap() {
+            assertCborEncodeAndDecode(cborHex, value);
+        }
+    }
+
+    /**
+     * Tests order of keys
+     */
+    @RunWith(Parameterized.class)
+    public static class KeyOrderTest extends ParametrizedCborTest {
+        @Parameters
+        public static Collection<Object[]> data() {
+            return Arrays.asList(new Object[][]{
+                    {"a30100413200613300",
+                            mapOf("3", 0, "2".getBytes(), 0, 1, 0)},
+                    {"a3190100004000613300",
+                            mapOf("3", 0, "".getBytes(), 0, 256, 0)},
+                    {"a4000018ff00190100001a7fffffff00",
+                            mapOf(Integer.MAX_VALUE, 0, 255, 0, 256, 0, 0, 0)},
+                    {"a3413300423232004331313100",
+                            mapOf("22".getBytes(), 0, "3".getBytes(), 0, "111".getBytes(), 0)},
+                    {"a3433030310043303032004330303300",
+                            mapOf("001".getBytes(), 0, "003".getBytes(), 0, "002".getBytes(), 0)},
+                    {"a2f400f500",
+                            mapOf(true, 0, false, 0)},
+                    {"a3613100623130006331303000",
+                            mapOf("1", 0, "100", 0, "10", 0)}
+            });
+        }
+
+        @Test
+        public void testKeyOrder() {
+            assertCborEncode(cborHex, value);
+        }
+    }
+
+    public static class OtherTests {
+        @Test(expected = IllegalArgumentException.class)
+        public void testDecodeIntOutOfRange() {
+            Cbor.decode(decodeHex("1a80000000"));
+        }
+    }
+
+    // helper methods
     private static Object wrapInt(Object value) {
         if (value instanceof Number) {
             return ((Number) value).intValue();
@@ -56,7 +269,9 @@ private static List<Object> listOf(Object... items) {
     private static void assertCborEncode(String expectedHex, Object value) {
         byte[] encoded = Cbor.encode(value);
         Assert.assertArrayEquals(
-                String.format("Expected to encode to %s, but got %s", expectedHex, encodeHex(encoded)),
+                String.format("Expected to encode to %s, but got %s",
+                        expectedHex,
+                        encodeHex(encoded)),
                 decodeHex(expectedHex),
                 encoded
         );
@@ -67,8 +282,12 @@ private static void assertCborDecode(Object expected, String cborHex) {
         if (expected instanceof byte[]) {
             byte[] expectBytes = (byte[]) expected;
             byte[] actualBytes = (byte[]) actual;
+            Assert.assertNotNull(actualBytes);
             Assert.assertArrayEquals(
-                    String.format("Expected to decode into %s, but got %s", encodeHex(expectBytes), encodeHex(actualBytes)),
+                    String.format("Expected to decode into %s, but got %s",
+                            encodeHex(expectBytes),
+                            encodeHex(actualBytes)
+                    ),
                     expectBytes,
                     actualBytes
             );
@@ -85,150 +304,4 @@ private static void assertCborEncodeAndDecode(String expectedHex, Object value)
         assertCborEncode(expectedHex, value);
         assertCborDecode(value, expectedHex);
     }
-
-    private static final class TestData {
-        private final String cborHex;
-        private final Object value;
-
-        private TestData(String cborHex, Object value) {
-            this.cborHex = cborHex;
-            this.value = value;
-        }
-    }
-
-    private static final List<TestData> TEST_VECTORS = Arrays.asList(
-            new TestData("00", 0),
-            new TestData("01", 1),
-            new TestData("0a", 10),
-            new TestData("17", 23),
-            new TestData("1818", 24),
-            new TestData("1819", 25),
-            new TestData("1864", 100),
-            new TestData("1903e8", 1000),
-            new TestData("1a000f4240", 1000000),
-            // new TestData("1b000000e8d4a51000", 1000000000000L),
-            // new TestData("1bffffffffffffffff", 18446744073709551615),
-            // ('c249010000000000000000', 18446744073709551616),
-            // new TestData("3bffffffffffffffff", -18446744073709551616),
-            // ('c349010000000000000000', -18446744073709551617),
-            new TestData("20", -1),
-            new TestData("29", -10),
-            new TestData("3863", -100),
-            new TestData("3903e7", -1000),
-            // ('f90000', 0.0),
-            // ('f98000', -0.0),
-            // ('f93c00', 1.0),
-            // ('fb3ff199999999999a', 1.1),
-            // ('f93e00', 1.5),
-            // ('f97bff', 65504.0),
-            // ('fa47c35000', 100000.0),
-            // ('fa7f7fffff', 3.4028234663852886e+38),
-            // ('fb7e37e43c8800759c', 1e+300),
-            // ('f90001', 5.960464477539063e-08),
-            // ('f90400', 6.103515625e-05),
-            // ('f9c400', -4.0),
-            // ('fbc010666666666666', -4.1),
-            // ('f97c00', None),
-            // ('f97e00', None),
-            // ('f9fc00', None),
-            // ('fa7f800000', None),
-            // ('fa7fc00000', None),
-            // ('faff800000', None),
-            // ('fb7ff0000000000000', None),
-            // ('fb7ff8000000000000', None),
-            // ('fbfff0000000000000', None),
-            new TestData("f4", false),
-            new TestData("f5", true),
-            // ('f6', None),
-            // ('f7', None),
-            // ('f0', None),
-            // ('f818', None),
-            // ('f8ff', None),
-            // ('c074323031332d30332d32315432303a30343a30305a', None),
-            // ('c11a514b67b0', None),
-            // ('c1fb41d452d9ec200000', None),
-            // ('d74401020304', None),
-            // ('d818456449455446', None),
-            // ('d82076687474703a2f2f7777772e6578616d706c652e636f6d', None),
-            new TestData("40", new byte[0]),
-            new TestData("4401020304", new byte[]{1, 2, 3, 4}),
-            new TestData("60", ""),
-            new TestData("6161", "a"),
-            new TestData("6449455446", "IETF"),
-            new TestData("62225c", "\"\\"),
-            new TestData("62c3bc", "ü"),
-            new TestData("63e6b0b4", "水"),
-            new TestData("64f0908591", "\ud800\udd51"),
-            new TestData("80", listOf()),
-            new TestData("83010203", listOf(1, 2, 3)),
-            new TestData("8301820203820405", listOf(1, listOf(2, 3), listOf(4, 5))),
-            new TestData(
-                    "98190102030405060708090a0b0c0d0e0f101112131415161718181819",
-                    listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25)
-            ),
-            new TestData("a0", mapOf()),
-            new TestData("a201020304", mapOf(1, 2, 3, 4)),
-            new TestData("a26161016162820203", mapOf("a", 1, "b", listOf(2, 3))),
-            new TestData("826161a161626163", listOf("a", mapOf("b", "c"))),
-            new TestData(
-                    "a56161614161626142616361436164614461656145",
-                    mapOf("c", "C", "d", "D", "a", "A", "b", "B", "e", "E")
-            )
-            // ('5f42010243030405ff', None),
-            // ('7f657374726561646d696e67ff', 'streaming'),
-            // ('9fff', []),
-            // ('9f018202039f0405ffff', [1, [2, 3], [4, 5]]),
-            // ('9f01820203820405ff', [1, [2, 3], [4, 5]]),
-            // ('83018202039f0405ff', [1, [2, 3], [4, 5]]),
-            // ('83019f0203ff820405', [1, [2, 3], [4, 5]]),
-            // ('9f0102030405060708090a0b0c0d0e0f101112131415161718181819ff', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]),  // noqa E501
-            // ('bf61610161629f0203ffff', {'a': 1, 'b': [2, 3]}),
-            // ('826161bf61626163ff', ['a', {'b': 'c'}]),
-            // ('bf6346756ef563416d7421ff', {'Amt': -2, 'Fun': True}),
-    );
-
-
-    @Test
-    public void testVectors() {
-        for (TestData pair : TEST_VECTORS) {
-            assertCborEncodeAndDecode(pair.cborHex, pair.value);
-        }
-    }
-
-    @Test
-    public void testIntegers() {
-        assertCborEncodeAndDecode("00", 0);
-        assertCborEncodeAndDecode("17", 23);
-        assertCborEncodeAndDecode("1818", 24);
-        assertCborEncodeAndDecode("18ff", 255);
-        assertCborEncodeAndDecode("190100", 256);
-        assertCborEncodeAndDecode("19ffff", 65535);
-        assertCborEncodeAndDecode("1a00010000", 65536);
-        assertCborEncodeAndDecode("1a7fffffff", Integer.MAX_VALUE);
-        //assertCborEncodeAndDecode("1affffffff", 4294967295L);
-        //assertCborEncodeAndDecode("1b7fffffffffffffff", Long.MAX_VALUE);
-
-        assertCborEncodeAndDecode("20", -1);
-        assertCborEncodeAndDecode("37", -24);
-        assertCborEncodeAndDecode("3818", -25);
-        assertCborEncodeAndDecode("3a7fffffff", Integer.MIN_VALUE);
-        //assertCborEncodeAndDecode("3affffffff", -4294967296L);
-        //assertCborEncodeAndDecode("3b7fffffffffffffff", Long.MIN_VALUE);
-    }
-
-    @Test(expected = IllegalArgumentException.class)
-    public void testDecodeIntOutOfRange() {
-        Cbor.decode(decodeHex("1a80000000"));
-    }
-
-    @Test
-    public void testKeyOrder() {
-        assertCborEncode("a30100413200613300", mapOf("3", 0, "2".getBytes(), 0, 1, 0));
-        assertCborEncode("a3190100004000613300", mapOf("3", 0, "".getBytes(), 0, 256, 0));
-        assertCborEncode("a4000018ff00190100001a7fffffff00", mapOf(Integer.MAX_VALUE, 0, 255, 0, 256, 0, 0, 0));
-        assertCborEncode("a3413300423232004331313100", mapOf("22".getBytes(), 0, "3".getBytes(), 0, "111".getBytes(), 0));
-        assertCborEncode("a3433030310043303032004330303300", mapOf("001".getBytes(), 0, "003".getBytes(), 0, "002".getBytes(), 0));
-        assertCborEncode("a2f400f500", mapOf(true, 0, false, 0));
-        assertCborEncode("a3613100623130006331303000", mapOf("1", 0, "100", 0, "10", 0));
-    }
-}
+}
\ No newline at end of file
```