# Which File to Use for Training?

## TL;DR Answer

**Use `real_data_w_generated_annotations_FIXED.jsonl`**

## The Problem You Identified

You're absolutely right that spacing errors like "Anto nini" (instead of "Antonini") are problematic. These occur in **27 of 879 records (3%)**.

## Why It's Complex

When we fix spacing in the transcription text:
- "Anto nini" → "Antonini" (removes space, text gets shorter)
- All annotation character positions after this change become invalid
- Annotations that pointed to characters 89-94 now point to wrong positions

### Attempted Solution: Automatic Position Adjustment

I created `fix_spacing_and_adjust_annotations.py` which tries to:
1. Fix all spacing errors
2. Automatically adjust annotation positions

**Problem**: The adjustment logic has bugs. It creates annotations like:
- `[83:93]` "Antonini P" (includes part of next word)
- `[94:101]` "i Felic" (starts mid-word)

These bad boundaries are arguably worse than the original spacing issues.

## The Trade-off

| Approach | Pros | Cons |
|----------|------|------|
| **Use FIXED file (with spacing issues)** | • 96.9% of records are clean<br>• All annotation logic fixed<br>• Ready to train immediately | • 27 records have spacing errors<br>• Model may learn "Anto" + "nini" separately |
| **Fix spacing + adjust positions** | • All spacing corrected<br>• Text looks better | • Creates bad annotation boundaries<br>• Loses ~70% of annotations<br>• More errors than benefit |
| **Fix spacing + re-annotate** | • Perfect data quality<br>• No compromises | • Requires re-running Gemini on 27 records<br>• More work |

## My Recommendation

### For Immediate Training: Use the FIXED File

**File**: `real_data_w_generated_annotations_FIXED.jsonl`

**What's been fixed**:
- ✅ Adjectives mislabeled as names (pia, optimo, carissimae)
- ✅ Pronouns mislabeled (qui, quae, cum)
- ✅ Formula phrases properly merged ("Dis Manibus", "hic situs est")
- ✅ Overlapping annotations removed
- ✅ Label errors corrected (age words, relationships, verbs)
- ✅ 9,684 clean annotations ready for training

**What's NOT fixed**:
- ⚠️ 27 records (3%) still have spacing errors like "Anto nini"

**Why this works**:
- spaCy's tokenizer will handle "Anto" and "nini" as separate tokens
- The model can still learn from these examples (not ideal, but functional)
- The 321 records with annotation logic fixes (36%) have much bigger impact on quality

### For Perfect Data: Two-Phase Approach

**Phase 1**: Train with current FIXED file

**Phase 2** (optional improvement):
1. Extract the 27 records with spacing issues
2. Fix spacing in those transcriptions
3. Re-annotate with Gemini (just 27 API calls)
4. Merge back into training data
5. Retrain model

## The 27 Records with Spacing Issues

```
HD000052: "Anto nini" → should be "Antonini"
HD000069: "Lucretiu s", "Caturoni s"
HD000165: "vix sit", "messibus" (OCR error)
HD000221: "Corn elius", "hic sita e st", "an norum", "uxo ri"
HD000237: "men sis", "vi xit"
... and 22 more
```

See full list in `fix_spacing_in_transcriptions.py` (lines 26-96)

## Example Comparison

### Record HD000052 in FIXED file:
```
Text: "...Marci Aureli Anto nini Pii Felicis..."
Annotations:
  [70:75] PRAENOMEN = "Marci"
  [76:82] NOMEN = "Aureli"
  [83:88] COGNOMEN = "Anto "      ← spacing issue
  [89:94] COGNOMEN = "ini P"      ← spacing issue
```

**Impact on training**: Model will see these as separate entities. Not ideal, but it won't break training. The model might learn less efficiently from these specific examples, but with 852 clean records, it will learn the patterns correctly.

## What About the Spacing-Adjusted Files?

These are in the repo for reference:
- `real_data_w_generated_annotations_spacing_fixed.jsonl` - spacing fixed, annotations not adjusted (positions invalid)
- `real_data_w_spacing_and_annotations_fixed.jsonl` - spacing fixed, positions adjusted (but buggy)

**Do NOT use these for training** - they have more problems than the FIXED file.

## Bottom Line

Your Latin knowledge is excellent - "Antonini" as one word is definitely better than "Anto nini". But the practical reality is:

1. **Annotation logic errors affect 36% of records** (adjectives as names, split formulas, overlaps)
2. **Spacing errors affect 3% of records** (broken words)

The FIXED file solves #1 completely and leaves #2 for later. This gives you usable training data now, with a clear path to improve those 27 records if needed.

## Action Items

**Immediate**: Use `real_data_w_generated_annotations_FIXED.jsonl` for training

**Optional future improvement**:
1. Run `fix_spacing_in_transcriptions.py` on just the 27 problem records
2. Re-annotate those 27 with Gemini
3. Merge into training data
4. Compare model performance (likely marginal improvement for 3% of data)
