#!/usr/bin/env python3
"""
Fix spacing errors in Latin epigraphic transcriptions.
These errors typically come from OCR/digitization and break proper word boundaries.
"""

import json
import re
from typing import List, Tuple


def fix_spacing(text: str) -> Tuple[str, List[str]]:
    """
    Fix spacing errors in transcription.
    Returns (fixed_text, list_of_changes)

    CONSERVATIVE approach: Only fix known patterns to avoid breaking valid word boundaries.
    """
    original = text
    changes = []

    # Use ONLY specific known patterns (most conservative approach)
    # Fix specific common breaks we see in the data
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

        # Funerary formulas - critical for annotation quality
        (r'\bhic\s+sita\s+e\s+st\b', 'hic sita est'),
        (r'\bsita\s+e\s+st\b', 'sita est'),
        (r'\bsitus\s+e\s+st\b', 'situs est'),
        (r'\bh\s+s\s+e\b', 'h s e'),  # Keep abbreviated form spaced

        # Age-related words (very common in inscriptions)
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

        # Superlatives and adjectives
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
        (r'\bmessibus\b', 'mensibus'),  # Common OCR error: messibus → mensibus
    ]

    for pattern, replacement in fixes:
        if re.search(pattern, text):
            old_text = text
            text = re.sub(pattern, replacement, text)
            if text != old_text:
                changes.append(f"'{pattern}' → '{replacement}'")

    return text, changes


def fix_spacing_in_file(input_path: str, output_path: str):
    """
    Fix spacing in all transcriptions in a JSONL file.
    """
    print(f"Reading from: {input_path}")

    fixed_count = 0
    total_count = 0
    all_changes = []

    with open(input_path, 'r', encoding='utf-8') as f_in:
        with open(output_path, 'w', encoding='utf-8') as f_out:
            for line_num, line in enumerate(f_in, 1):
                try:
                    record = json.loads(line)
                    total_count += 1

                    original_text = record.get('transcription', '')
                    if original_text:
                        fixed_text, changes = fix_spacing(original_text)

                        if changes:
                            fixed_count += 1
                            all_changes.extend([f"Line {line_num} ({record.get('id', '?')}): {c}" for c in changes])
                            record['transcription'] = fixed_text

                    f_out.write(json.dumps(record, ensure_ascii=False) + '\n')

                    if line_num % 100 == 0:
                        print(f"Processed {line_num} records...")

                except Exception as e:
                    print(f"Error on line {line_num}: {e}")
                    f_out.write(line)

    print(f"\n✅ Spacing fixes complete!")
    print(f"   Total records: {total_count}")
    print(f"   Records with fixes: {fixed_count}")
    print(f"   Total changes: {len(all_changes)}")

    if all_changes and len(all_changes) <= 50:
        print(f"\n📝 All changes:")
        for change in all_changes:
            print(f"   {change}")
    elif all_changes:
        print(f"\n📝 First 50 changes:")
        for change in all_changes[:50]:
            print(f"   {change}")
        print(f"   ... and {len(all_changes) - 50} more")

    print(f"\n   Output: {output_path}")


if __name__ == '__main__':
    input_file = 'real_data_w_generated_annotations_to_fix.jsonl'
    output_file = 'real_data_w_generated_annotations_spacing_fixed.jsonl'

    fix_spacing_in_file(input_file, output_file)
