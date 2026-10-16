# LLM Cross-Check Comparison

This file compares transparent automated labels only. These are not human-rater labels and should not be reported as the two-author Cohen's kappa requested in the response letter.

## Summary

- Sample size: 50
- Codex labels: 43/50 correct, precision 0.86
- Claude labels: 42/50 correct, precision 0.84
- Claude-Codex agreement: 49/50 (98.00%)
- Claude-Codex Cohen's kappa: 0.922

## Disagreements

| row | rm_type | Codex | Claude | Codex rationale | Claude rationale |
|---:|---|---:|---:|---|---|
| 28 | Move Method | 1 | 0 | endTracks keeps the same role/body but its declaring class changes from TestOutput to TestExtractorOutput during the split. | Diff: `public static class TestOutput implements ExtractorOutput, TrackOutput` becomes `public class TestExtractorOutput implements ExtractorOutput` (+ new TestTrackOutput). endTracks() is unchanged context (not in patch); its enclosing class was renamed/split |

## Codex Negative Labels

| row | rm_type | suggested type | rationale |
|---:|---|---|---|
| 7 | Move And Inline Method | Inline Method | The read helper is inlined locally within the same LocalDateDeserTest class; no move from LocalDateTimeDeserTest is evident. |
| 12 | Merge Attribute | Extract Class / Replace Fields with Object | runsProcessed is not merged into nativeTest; the change mainly introduces TestIntegers objects that encapsulate timing/value behavior. |
| 13 | Move And Inline Method | Inline Method | LocalDateDeserTest inlines its own read helper; the diff does not show moving LocalDateTimeDeserTest.read into this class. |
| 16 | Rename Variable | Split Method / Extract Test Method | The old monolithic statement-builder test is split into separate tests; str is not a continuous variable renamed to n. |
| 30 | Inline Method | Extract Class / Replace Method with Generator | generateRandomTreeWithReferences is not simply inlined into testSaveAndLoad; the logic is reorganized through StudyGenerator and generate(). |
| 38 | Move And Inline Method | Inline Method | The read helper is inlined inside LocalDateDeserTest itself; no move-and-inline from LocalDateTimeDeserTest is supported. |
| 50 | Remove Attribute Modifier | Replace data holder with parameterized test | The old TestData class is deleted and a new parameterized test hierarchy introduces a different public @Parameter value field. |
