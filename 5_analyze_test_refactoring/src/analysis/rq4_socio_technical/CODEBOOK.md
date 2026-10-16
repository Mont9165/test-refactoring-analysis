# Codebook: motivations for test refactorings

This codebook defines the 11 categories used to code why developers performed
each test refactoring (paper, Section 6.1). The unit of analysis is one test
refactoring type within one commit, which gives 185 cases. For each case, two
authors independently read the commit message and, if the commit belonged to a
pull request, its title, description, comments and reviews, and assigned
exactly one category. The final labels are in `motivation_coding_final.csv`
(columns `category_kosei`, `category_fujiwara` and `final label`).

The taxonomy adapts the six general-refactoring motivations of Silva et al.
(FSE 2016) to test code and adds four test-specific categories.

## Categories

| Category | Definition | Origin |
|---|---|---|
| `bug_fix` | The refactoring fixes a known test defect, such as a broken or failing test, a regression, a time-out, or an incorrect assertion. Flaky behaviour is coded as `flaky_test`. | Silva et al. 2016; Murphy-Hill et al. 2012; Kim et al. 2012 |
| `improve_comprehension` | The refactoring makes the intent of the test clearer to a reader, for example through clearer naming, more specific assertions or assertion messages. | Silva et al. 2016 |
| `improve_maintainability` | The refactoring reduces duplication, increases reuse or makes future changes easier, for example by extracting fixtures, consolidating helpers or cleaning up. | Silva et al. 2016; Murphy-Hill et al. 2012; Mens and Tourwé 2004 |
| `improve_test_performance` | The developer states that the refactoring speeds up the tests or reduces their resource use. | Silva et al. 2016 (`improve_performance`), applied to test execution |
| `support_feature` | The test change accompanies or prepares a feature addition or behaviour change in production code. | Silva et al. 2016 |
| `remove_code_smell` | The developer names a test smell, an anti-pattern or a warning of a quality tool (e.g. SonarQube) as the reason. | Bavota et al. 2015; Tufano et al. 2016; van Deursen et al. 2001; Meszaros 2007 |
| `sync_with_production` | The refactoring is required because production code was renamed, moved, extracted or redesigned. | test-specific |
| `improve_test_isolation` | The refactoring reduces the coupling of the test to external resources such as databases, the network, the file system or frameworks, often by introducing or removing mocks or other test doubles. | test-specific; Spadini et al. 2018; Meszaros 2007 |
| `modernize_test_framework` | The refactoring moves the test to newer framework idioms, for example from JUnit 4 to JUnit 5, to `assertThrows`, to parameterized tests or to AssertJ-style assertions. | test-specific; Soares et al. 2023 |
| `flaky_test` | The developer states that the refactoring makes a non-deterministic (flaky) test stable, for example by waiting for an asynchronous event or by removing a dependence on ordering or timing. | test-specific |
| `not_documented` | The commit message and the pull request contain no discernible reason for the refactoring. | Silva et al. 2016 |

## Assigning a single category

When several categories apply, the coders chose the first one in this order:

1. `flaky_test`
2. `bug_fix`
3. `remove_code_smell`
4. `improve_test_performance`
5. `sync_with_production`
6. `modernize_test_framework`
7. `improve_test_isolation`
8. `support_feature`
9. `improve_comprehension`
10. `improve_maintainability`
11. `not_documented`

## Agreement and distribution

`compute_motivation_kappa.py` reproduces the numbers in the paper: the two
coders agreed in 176 of the 185 cases (95.1%, Cohen's kappa = 0.93), and the
9 disagreements were resolved in a discussion with a third author.
`support_feature` was defined but not assigned to any case, so 10 of the 11
categories appear in the reconciled distribution (paper, Table 9).
