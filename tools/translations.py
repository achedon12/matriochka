"""Languages beyond English and French.

English and French live in content.py and ui_lang.py, side by side. Every other language is a plain table in
tools/i18n/<code>.json mapping a lang key to its translation, maintained by hand (or by a translator) as a source
file. gen.py calls write() once the English table is complete:

- only keys that still exist in English are written, so a renamed or removed key never ships;
- a translation whose %s placeholders do not match the English string is dropped (and reported), so a broken
  format can never crash a tooltip;
- a missing key is simply left out: Minecraft loads en_us under every language, so it falls back to English.

    python3 tools/translations.py            coverage of every language
    python3 tools/translations.py es_es      the missing or stale keys of one language, as JSON (EN and FR shown)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "i18n")
# Minecraft language codes, in the order they are listed in the docs
LANGS = ["es_es", "de_de", "pt_br", "it_it", "ru_ru", "pl_pl", "zh_cn"]
_PH = re.compile(r"%(?:(\d+)\$)?([sd])")


def placeholders(text):
    """(count, highest positional index) of the %s / %d / %1$s placeholders of a string; %% is not one."""
    text = text.replace("%%", "")
    found = _PH.findall(text)
    return len(found), max((int(i) for i, _ in found if i), default=0)


def compatible(en, tr):
    n_en, _ = placeholders(en)
    n_tr, pos = placeholders(tr)
    return n_tr == n_en and pos <= n_en


def load(code):
    path = os.path.join(SRC, f"{code}.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build(code, en):
    """The lang table to ship for one language, and what was left out: (table, missing, stale, broken)."""
    src = load(code)
    table, broken = {}, []
    for k, v in src.items():
        if k not in en:
            continue
        if not isinstance(v, str) or not v.strip() or not compatible(en[k], v):
            broken.append(k)
            continue
        table[k] = v
    missing = sorted(k for k in en if k not in src)
    stale = sorted(k for k in src if k not in en)
    return table, missing, stale, sorted(broken)


def write(en, assets, w):
    """Writes assets/lang/<code>.json for every extra language; returns a short report."""
    report = []
    for code in LANGS:
        table, missing, stale, broken = build(code, en)
        w(os.path.join(assets, f"lang/{code}.json"), dict(sorted(table.items())))
        line = f"{code}={len(table)}/{len(en)}"
        if broken:
            line += f" broken={len(broken)}"
            print(f"  {code}: placeholders differ from English, falling back for: {', '.join(broken[:8])}{' ...' if len(broken) > 8 else ''}")
        if stale:
            line += f" stale={len(stale)}"
        report.append(line)
    return " ".join(report)


def _main():
    lang_dir = os.path.join(HERE, "..", "src/main/resources/assets/matriochka/lang")
    with open(os.path.join(lang_dir, "en_us.json"), encoding="utf-8") as f:
        en = json.load(f)
    with open(os.path.join(lang_dir, "fr_fr.json"), encoding="utf-8") as f:
        fr = json.load(f)
    if len(sys.argv) > 1:
        code = sys.argv[1]
        _, missing, stale, broken = build(code, en)
        todo = {k: {"en": en[k], "fr": fr.get(k, "")} for k in missing + broken}
        json.dump({"missing": todo, "stale": stale}, sys.stdout, indent=1, ensure_ascii=False)
        print()
        return
    for code in LANGS:
        table, missing, stale, broken = build(code, en)
        print(f"{code}: {len(table)}/{len(en)} keys, {len(missing)} missing, {len(broken)} broken, {len(stale)} stale")


if __name__ == "__main__":
    _main()
