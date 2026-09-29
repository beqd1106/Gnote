# -*- coding: utf-8 -*-
"""
Gnote：既存問題の手直し（選択肢の長さの癖・短い解説）を検算して反映する。

  python design/apply_polish.py <手直しJSONのフォルダ> [--apply]

フォルダには <レッスンID>.json（{id, choices, explanation, wrongChoiceExplanations} の配列）を置く。
並び順と正解位置は変えない前提なので、正解の選択肢が大きく変わったものは目視用に一覧で出す。
--apply なしでは検査だけ行い、Resources は書き換えない。
"""
import json, os, sys, glob, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "Resources")


def stats(qs):
    n = len(qs)
    lh = sh = 0
    for q in qs:
        L = [len(c) for c in q["choices"]]
        c = q["correctAnswers"][0]
        if L[c] == max(L):
            lh += 1 / L.count(max(L))
        if L[c] == min(L):
            sh += 1 / L.count(min(L))
    short = sum(1 for q in qs if len(q["explanation"]) < 100)
    return lh / n, sh / n, short


def main():
    folder, apply = sys.argv[1], "--apply" in sys.argv
    path = os.path.join(RES, "questions.json")
    qs = json.load(open(path, encoding="utf-8"))
    by_id = {q["id"]: q for q in qs}
    before = stats(qs)

    patches, errors, review = {}, [], []
    for f in sorted(glob.glob(os.path.join(folder, "l-*.json"))):
        for p in json.load(open(f, encoding="utf-8")):
            q = by_id.get(p.get("id"))
            if not q:
                errors.append(f"{p.get('id')}: 元の問題が無い")
                continue
            ch = p.get("choices", q["choices"])
            if len(ch) != 4 or len(set(ch)) != 4:
                errors.append(f"{q['id']}: 選択肢が4つでない／重複")
                continue
            c = q["correctAnswers"][0]
            we = p.get("wrongChoiceExplanations", q["wrongChoiceExplanations"])
            if set(we) != {str(i) for i in range(4) if i != c}:
                errors.append(f"{q['id']}: 誤答解説のキーが正解位置と合わない")
                continue
            ratio = difflib.SequenceMatcher(None, q["choices"][c], ch[c]).ratio()
            if ratio < 0.5:
                review.append(f"{q['id']}: 正解が大きく変わった\n    前: {q['choices'][c]}\n    後: {ch[c]}")
            patches[q["id"]] = {"choices": ch, "wrongChoiceExplanations": we,
                                "explanation": p.get("explanation", q["explanation"])}

    after_qs = [dict(q, **patches.get(q["id"], {})) for q in qs]
    after = stats(after_qs)
    print(f"手直し {len(patches)}問")
    print(f"一番長い選択肢を選ぶだけ: {before[0]:.1%} → {after[0]:.1%}（目標25%前後）")
    print(f"一番短い選択肢を選ぶだけ: {before[1]:.1%} → {after[1]:.1%}")
    print(f"解説100字未満: {before[2]} → {after[2]}問")
    for r in review:
        print("  要確認", r)
    for e in errors:
        print("  エラー", e)
    if errors:
        sys.exit(1)
    if apply:
        json.dump(after_qs, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("反映しました")
    else:
        print("検査のみ（--apply で反映）")


if __name__ == "__main__":
    main()
