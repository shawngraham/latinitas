#!/usr/bin/env python3
"""
Fix spacing errors in Latin epigraphic transcriptions AND adjust annotation positions.
This ensures annotations remain valid after text changes.
"""

import json
import re
from typing import List, Tuple, Dict


def fix_spacing_with_annotations(text: str, annotations: List[List]) -> Tuple[str, List[List], List[str]]:
    """
    Fix spacing errors and adjust annotation positions accordingly.
    Returns (fixed_text, adjusted_annotations, list_of_changes)
    """
    changes = []

    # Define specific known patterns (same as before)
    fixes = [
        # Name fragments
        (r'\bAnto\s+nini\b', 'Antonini'),
        (r'\bAure\s+li\b', 'Aureli'),
        (r'\bAure\s+lius\b', 'Aurelius'),
        (r'\bAure\s+lio\b', 'Aurelio'),
        (r'\bLucretiu\s+s\b', 'Lucretius'),
        (r'\bCaturoni\s+s\b', 'Caturonis'),
        (r'\bCorn\s+elius\b', 'Cornelius'),
        (r'\bCorn\s+elia\b', 'Cornelia'),

        # Funerary formulas
        (r'\bhic\s+sita\s+e\s+st\b', 'hic sita est'),
        (r'\bsita\s+e\s+st\b', 'sita est'),
        (r'\bsitus\s+e\s+st\b', 'situs est'),

        # Age-related words
        (r'\ban\s+norum\b', 'annorum'),
        (r'\ban\s+nos\b', 'annos'),
        (r'\ban\s+nis\b', 'annis'),
        (r'\ban\s+num\b', 'annum'),
        (r'\ban\s+no\b', 'anno'),
        (r'\bmen\s+sis\b', 'mensis'),
        (r'\bmen\s+ses\b', 'menses'),
        (r'\bmen\s+sibus\b', 'mensibus'),
        (r'\bdie\s+bus\b', 'diebus'),
        (r'\bdie\s+rum\b', 'dierum'),

        # Verb forms
        (r'\bvix\s+it\b', 'vixit'),
        (r'\bvix\s+sit\b', 'vixit'),
        (r'\bvi\s+xit\b', 'vixit'),
        (r'\bvi\s+vus\b', 'vivus'),
        (r'\bfe\s+cit\b', 'fecit'),
        (r'\bfe\s+cerunt\b', 'fecerunt'),
        (r'\bpo\s+suit\b', 'posuit'),
        (r'\bmilita\s+vit\b', 'militavit'),

        # Family/relationship terms
        (r'\bfili\s+o\b', 'filio'),
        (r'\bfili\s+us\b', 'filius'),
        (r'\bfili\s+a\b', 'filia'),
        (r'\bfili\s+ae\b', 'filiae'),
        (r'\bfili\s+i\b', 'filii'),
        (r'\buxo\s+ri\b', 'uxori'),
        (r'\bconiu\s+gi\b', 'coniugi'),
        (r'\bconiu\s+x\b', 'coniux'),
        (r'\bpat\s+ri\b', 'patri'),
        (r'\bmat\s+ri\b', 'matri'),

        # Superlatives
        (r'\bcari\s+ssimo\b', 'carissimo'),
        (r'\bcari\s+ssimae\b', 'carissimae'),
        (r'\bcari\s+ssimi\b', 'carissimi'),
        (r'\bdulcis\s+simo\b', 'dulcissimo'),
        (r'\bdulcis\s+simae\b', 'dulcissimae'),
        (r'\bdulcis\s+simi\b', 'dulcissimi'),
        (r'\bpientis\s+simo\b', 'pientissimo'),
        (r'\bpientis\s+simae\b', 'pientissimae'),
        (r'\bpientis\s+simi\b', 'pientissimi'),
        (r'\bsanctis\s+simae\b', 'sanctissimae'),
        (r'\boptim\s+o\b', 'optimo'),
        (r'\boptim\s+ae\b', 'optimae'),

        # Other common words
        (r'\bpatri\s+bus\b', 'patribus'),
        (r'\bliberto\s+rum\b', 'libertorum'),
        (r'\bliberto\s+o\b', 'libertoo'),
        (r'\bmer\s+enti\b', 'merenti'),
        (r'\bmer\s+ito\b', 'merito'),
        (r'\bmessibus\b', 'mensibus'),
    ]

    # Track position adjustments: {position: cumulative_shift}
    # Positive shift = text got longer, negative = text got shorter
    adjustments = []  # List of (position, length_change)

    current_text = text
    for pattern, replacement in fixes:
        # Find all matches in current text
        for match in re.finditer(pattern, current_text):
            start_pos = match.start()
            end_pos = match.end()
            original_text = match.group()
            length_change = len(replacement) - len(original_text)

            # Replace this occurrence
            current_text = current_text[:start_pos] + replacement + current_text[end_pos:]

            # Record the adjustment
            adjustments.append((start_pos, end_pos, length_change))
            changes.append(f"'{original_text}' → '{replacement}' at pos {start_pos}")

            # Only replace first occurrence per pattern to avoid position confusion
            break

    # Now adjust all annotation positions based on the text changes
    adjusted_annotations = []

    for ann in annotations:
        if len(ann) != 3:
            # Malformed annotation, keep as-is
            adjusted_annotations.append(ann)
            continue

        start, end, label = ann
        new_start = start
        new_end = end

        # Apply all adjustments that occur before or within this annotation
        for adj_start, adj_end, length_change in adjustments:
            # If adjustment is completely before this annotation, shift both positions
            if adj_end <= start:
                new_start += length_change
                new_end += length_change
            # If adjustment overlaps annotation start
            elif adj_start <= start < adj_end:
                # Annotation starts in the middle of changed text - problematic
                # Best effort: move to start of replacement
                new_start = adj_start
                new_end += length_change
            # If adjustment is within the annotation
            elif start < adj_start < end:
                # Annotation contains the change - adjust end only
                new_end += length_change

        # Only keep annotations with valid positions
        if 0 <= new_start < new_end <= len(current_text):
            adjusted_annotations.append([new_start, new_end, label])

    return current_text, adjusted_annotations, changes


def fix_file_with_annotation_adjustment(input_path: str, output_path: str):
    """
    Fix spacing in all transcriptions and adjust annotations.
    """
    print(f"Reading from: {input_path}")

    fixed_count = 0
    total_count = 0
    ann_removed = 0
    all_changes = []

    with open(input_path, 'r', encoding='utf-8') as f_in:
        with open(output_path, 'w', encoding='utf-8') as f_out:
            for line_num, line in enumerate(f_in, 1):
                try:
                    record = json.loads(line)
                    total_count += 1

                    original_text = record.get('transcription', '')
                    original_annotations = record.get('annotations', [])

                    if original_text:
                        fixed_text, adjusted_annotations, changes = fix_spacing_with_annotations(
                            original_text,
                            original_annotations
                        )

                        if changes:
                            fixed_count += 1
                            all_changes.extend([f"Line {line_num} ({record.get('id', '?')}): {c}"
                                              for c in changes])
                            record['transcription'] = fixed_text
                            record['annotations'] = adjusted_annotations

                            removed = len(original_annotations) - len(adjusted_annotations)
                            if removed > 0:
                                ann_removed += removed

                    f_out.write(json.dumps(record, ensure_ascii=False) + '\n')

                    if line_num % 100 == 0:
                        print(f"Processed {line_num} records...")

                except Exception as e:
                    print(f"Error on line {line_num}: {e}")
                    f_out.write(line)

    print(f"\n✅ Spacing and annotation adjustment complete!")
    print(f"   Total records: {total_count}")
    print(f"   Records with spacing fixes: {fixed_count}")
    print(f"   Total text changes: {len(all_changes)}")
    print(f"   Annotations removed (invalid after adjustment): {ann_removed}")

    if all_changes and len(all_changes) <= 50:
        print(f"\n📝 All changes:")
        for change in all_changes:
            print(f"   {change}")
    elif all_changes:
        print(f"\n📝 First 30 changes:")
        for change in all_changes[:30]:
            print(f"   {change}")

    print(f"\n   Output: {output_path}")


if __name__ == '__main__':
    input_file = 'real_data_w_generated_annotations_to_fix.jsonl'
    output_file = 'real_data_w_spacing_and_annotations_fixed.jsonl'

    fix_file_with_annotation_adjustment(input_file, output_file)
