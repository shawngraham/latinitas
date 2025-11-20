# Findings: Spacing Issues and Annotation Fixes

## Problem Identified

You correctly identified that spacing errors in the EDH transcriptions affect annotation quality. For example:
- **Original**: "Anto nini" (broken across space)
- **Correct**: "Antonini" (Roman cognomen)

When Gemini annotates the broken version, it creates poor annotations:
- `[83:88]` COGNOMEN = "Anto "
- `[89:94]` COGNOMEN = "nini P" (includes part of next word!)

## Extent of the Problem

**Spacing issues affect 27 of 879 records (3%)**

Common patterns found:
- Name fragments: "Anto nini", "Lucretiu s", "Caturoni s", "Corn elius"
- Age words: "an norum", "vi xit", "men sibus", "die bus"
- Superlatives: "cari ssimo", "dulcis simo", "pientis simo"
- Funerary formulas: "hic sita e st", "sit tibi terra levis"
- Relationships: "coniu gi", "uxo ri", "fili us"

Total: 37 specific spacing errors identified

## Solutions Created

### 1. Simple Spacing Fix (NOT RECOMMENDED)
**File**: `fix_spacing_in_transcriptions.py`

- Fixes 37 known spacing patterns using regex
- **Problem**: Breaks all annotation character positions
- **Result**: Clean text, but invalid annotations

### 2. Spacing Fix + Annotation Adjustment (EXPERIMENTAL)
**File**: `fix_spacing_and_adjust_annotations.py`

- Fixes spacing AND attempts to adjust annotation positions
- **Problem**: Complex logic, has bugs in position calculation
- **Example bug**: After fixing "Anto nini" → "Antonini", annotations at [89:94] got incorrectly adjusted to [83:93]
- **Result**: Partially works, but not reliable

### 3. Annotation Logic Fixes Only (RECOMMENDED)
**File**: `fix_annotations_v3.py`

**Approach**: Fix annotation errors without touching spacing

**What it fixes**:
1. **Removes adjectives mislabeled as names**: pia, optimo, carissimae, dulcissimo
2. **Removes pronouns mislabeled**: qui, quae, cum
3. **Merges formulaic phrases**:
   - "Dis Manibus" → single DEDICATION_TO_THE_GODS
   - "hic situs est" → single FUNERARY_FORMULA
   - "bene merenti" → single BENE_MERENTI
4. **Fixes label errors**:
   - vixit, annos → AGE_PREFIX
   - coniugi, libertus → RELATIONSHIP
   - fecit, posuit → FUNERARY_FORMULA
5. **Removes overlapping annotations** (keeps longer spans)
6. **Trims spaces/punctuation** from annotation edges

**Results**:
- Modified: 321 of 879 records (36%)
- Removed: 631 problematic entities
- Added: 3 merged formulas
- Net improvement: -628 entities (cleaner training data)
- Final total: 9,684 annotations (was 10,312)

**Quality improvement**:
- Removed word fragments like "Gratu", " sit", "r fec", "s mat"
- Removed overlapping spans
- Proper multi-word formulas instead of fragments

## Recommendation

**Use `fix_annotations_v3.py` on the original data**

**Rationale**:
1. Spacing issues only affect 3% of records
2. Annotation logic errors affect 36% of records (much more widespread)
3. Adjusting annotations after text changes is complex and error-prone
4. The spacing errors don't prevent the model from learning (it can learn "Anto" and "nini" as separate tokens, even if not ideal)
5. The annotation logic errors actively harm training (adjectives labeled as names, split formulas, etc.)

## Future Improvements

If you want to fix spacing properly:

**Option A**: Re-annotate the 27 affected records
1. Fix spacing with `fix_spacing_in_transcriptions.py`
2. Re-run Gemini annotation on just those 27 records
3. Merge with the other 852 records

**Option B**: Manual correction
- The 27 records with spacing issues could be manually corrected since it's a small set

**Option C**: Smarter annotation adjustment
- Develop a more robust position adjustment algorithm
- Track character shifts more carefully
- Handle edge cases (overlaps, mid-word splits, etc.)

## Files in This Repository

| File | Purpose | Status |
|------|---------|--------|
| `real_data_w_generated_annotations_to_fix.jsonl` | Original Gemini annotations | Original |
| `real_data_w_generated_annotations_FIXED.jsonl` | After annotation logic fixes | **USE THIS** |
| `fix_annotations_v3.py` | Recommended fixing script | ✅ Working |
| `fix_spacing_in_transcriptions.py` | Spacing-only fix | ⚠️ Breaks annotations |
| `fix_spacing_and_adjust_annotations.py` | Combined approach | ⚠️ Has bugs |

## Your Insight

Your question about regex preprocessing was spot-on! The spacing issues do affect annotation quality. The scripts I created demonstrate:
1. The problem is real but affects only 3% of records
2. Simple regex fixes work for text, but cascade into annotation position problems
3. For training data, fixing annotation logic errors has bigger impact than fixing spacing
4. The best approach depends on your priorities: perfect text vs. practical workflow

You have excellent intuition about Latin epigraphy - "Antonini" as a single cognomen is much better for the model to learn than "Anto" + "nini" as separate entities!
