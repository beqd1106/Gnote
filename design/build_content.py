# -*- coding: utf-8 -*-
"""
Gnote（G検定）学習コンテンツ生成スクリプト。
JDLA公式シラバス2024（design/syllabus_gkentei_2024.txt）に紐づけて
問題(questions)・用語(terms)・レッスン(lessons)・頻出モデル一覧(services)・用語集(glossary)を生成する。

方針：
- 合格に必要な各分野の主要キーワードを取りこぼさず問題化する（量も質も）。
- 問題・解説はすべてオリジナル。公式問題・市販教材の転載はしない。
- domain rawValue は ExamDomain と一致：hist / ml / dlBasic / dlTech / dlApp / impl / law
- 問題は design/batch_*.json、用語は terms_extra*.json、用語集は glossary_source*.json、
  反復ドリルは drill_*.json から取り込む。レッスンの quizIds/drillQuizIds は分野で自動割当。
"""
import json, os, glob, random
from collections import Counter

BASE = os.path.join(os.path.dirname(__file__), "..", "Resources")
DESIGN = os.path.dirname(__file__)
random.seed(42)

VALID = {"hist", "ml", "dlBasic", "dlTech", "dlApp", "impl", "law"}

def balance_positions(questions):
    """正解位置が①に偏らないよう選択肢をシャッフルして均等化。誤答解説キーも付け替える。"""
    counter = 0
    for q in questions:
        n = len(q["choices"]); correct = list(q["correctAnswers"])
        if len(correct) == 1:
            target = counter % n; counter += 1; src = correct[0]
            others = [i for i in range(n) if i != src]; random.shuffle(others)
            new_order, oi = [], 0
            for pos in range(n):
                if pos == target: new_order.append(src)
                else: new_order.append(others[oi]); oi += 1
        else:
            new_order = list(range(n)); random.shuffle(new_order)
        o2n = {old: pos for pos, old in enumerate(new_order)}
        q["choices"] = [q["choices"][old] for old in new_order]
        q["correctAnswers"] = sorted(o2n[c] for c in correct)
        q["wrongChoiceExplanations"] = {str(o2n[int(k)]): v for k, v in q["wrongChoiceExplanations"].items()}
    return questions

# ============================================================
# レッスン（各分野1本・確認問題とドリルは分野で自動割当）
# ============================================================
def L(id, title, domain, minutes, summary, sections):
    return {"id": id, "title": title, "domain": domain, "estimatedMinutes": minutes,
            "summary": summary, "sections": sections, "quizIds": [],
            "challengeQuizIds": None, "drillQuizIds": None}

lessons = [
 L("l-hist", "人工知能とは・動向", "hist", 13,
   "AIの定義と古典的な問題、探索・推論、知識表現、AIの3度のブームまでを押さえます。",
   [{"heading":"AIとは何か","body":"人工知能に唯一の定義はなく、研究者ごとに立場が異なります。人間のように思考・学習・推論する機能をコンピュータで実現する技術の総称です。チューリングテストや『中国語の部屋』は知能をめぐる有名な議論です。"},
    {"heading":"AI分野の古典的問題","body":"フレーム問題（今しようとしていることに関係する事柄だけを選び出すのが難しい）、シンボルグラウンディング問題（記号と意味を結びつけられない）、身体性、シンギュラリティ（技術的特異点）など、AIが抱える本質的課題を理解します。"},
    {"heading":"探索・推論と知識表現","body":"第1次AIブームは探索・推論（幅優先/深さ優先探索、ハノイの塔、Mini-Max法）が中心。第2次は知識表現とエキスパートシステム（マイシン、意味ネットワーク、オントロジー）。ただし知識獲得のボトルネックが壁になりました。"},
    {"heading":"3度のAIブーム","body":"第1次（探索・推論）→冬の時代→第2次（知識表現）→冬の時代→第3次（機械学習・ディープラーニング）。2012年のILSVRCでディープラーニングが圧勝し、第3次ブームを決定づけました。"}]),
 L("l-ml", "機械学習の手法", "ml", 14,
   "教師あり・教師なし・強化学習の代表的アルゴリズムと、モデルの評価指標を押さえます。",
   [{"heading":"教師あり学習","body":"正解ラベル付きデータで学習。回帰（線形回帰・ロジスティック回帰）と分類（SVM、決定木、ランダムフォレスト、ブースティング、k近傍法）。過学習を避ける正則化や汎化性能が重要です。"},
    {"heading":"教師なし学習","body":"ラベルなしデータから構造を見つける。クラスタリング（k-means、階層クラスタリング）、次元削減（主成分分析PCA、t-SNE）、協調フィルタリング（レコメンド）などがあります。"},
    {"heading":"強化学習","body":"報酬を最大化するよう試行錯誤で方策を学ぶ。マルコフ決定過程、Q学習、方策勾配法、多腕バンディット（探索と活用のトレードオフ、UCB）が基礎概念です。"},
    {"heading":"モデルの選択・評価","body":"過学習/未学習、交差検証、ホールドアウト。分類の評価は混同行列から正解率・適合率・再現率・F値・ROC/AUC。バイアスとバリアンスのトレードオフも頻出です。"}]),
 L("l-dlbasic", "ディープラーニングの概要", "dlBasic", 13,
   "ニューラルネットワークの基本、活性化関数・誤差関数・誤差逆伝播・最適化を押さえます。",
   [{"heading":"ニューラルネットワーク","body":"単純パーセプトロンは線形分離しかできず、多層化（多層パーセプトロン）で非線形も扱えます。層を深くしたものがディープラーニング。かつては勾配消失問題が学習を妨げました。"},
    {"heading":"活性化関数","body":"ニューロンの出力を決める関数。シグモイド・tanhは勾配消失しやすく、ReLU（およびLeaky ReLU）が主流。出力層の多クラス分類にはソフトマックスを使います。"},
    {"heading":"誤差関数と誤差逆伝播","body":"予測と正解のズレを測るのが誤差（損失）関数（回帰は二乗誤差、分類は交差エントロピー）。その誤差を出力から入力側へ伝えて重みを更新するのが誤差逆伝播法です。"},
    {"heading":"最適化と正則化","body":"勾配降下法をベースに、SGD・モーメンタム・AdaGrad・RMSprop・Adamなどで学習を効率化。過学習対策にL1/L2正則化、ドロップアウト、早期終了、バッチ正規化を使います。"}]),
 L("l-dltech", "ディープラーニングの要素技術", "dlTech", 14,
   "CNN・RNN/LSTM・Attention/Transformer・オートエンコーダなど中核技術を押さえます。",
   [{"heading":"CNN（畳み込みニューラルネットワーク）","body":"画像処理の定番。畳み込み層（フィルタ・ストライド・パディング）で特徴を抽出し、プーリング層で位置ずれに強くします。ResNetのスキップ結合は深い層の学習を可能にしました。"},
    {"heading":"RNN・LSTM","body":"時系列・系列データを扱う回帰結合層。長い系列では勾配消失・爆発が起きるため、ゲート機構を持つLSTMやGRUが考案されました。学習にはBPTTを用います。"},
    {"heading":"Attention・Transformer","body":"入力のどこに注目するかを学ぶ仕組みがAttention。自己注意（Self-Attention）だけで構成したTransformerがBERT・GPTなど現在の主流モデルの基盤です。"},
    {"heading":"オートエンコーダ・データ拡張","body":"入力を圧縮・復元して特徴を学ぶオートエンコーダ（VAEは生成にも使える）。学習データを回転・反転などで水増しするデータ拡張は過学習対策に有効です。"}]),
 L("l-dlapp", "ディープラーニングの応用", "dlApp", 15,
   "画像認識・自然言語処理・音声・深層強化学習・生成モデル・XAIなど応用例を押さえます。",
   [{"heading":"画像認識","body":"AlexNet(2012)以降、VGG・GoogLeNet・ResNet・EfficientNetと発展。物体検出（R-CNN、YOLO、SSD）やセマンティックセグメンテーションも重要な応用です。"},
    {"heading":"自然言語処理","body":"単語をベクトル化するword2vec、系列変換のseq2seq、そしてTransformerベースのBERT・GPT。大規模言語モデル（LLM）や生成AIが急速に発展。ハルシネーションやRAG、プロンプトも押さえます。"},
    {"heading":"深層強化学習・生成モデル","body":"DQNはAtariで人間超え、AlphaGoは囲碁でトップ棋士を破りました。データ生成はGAN（生成器と識別器の敵対学習）や拡散モデル（Diffusion Model）が主流です。"},
    {"heading":"転移学習・マルチモーダル・XAI","body":"学習済みモデルを別タスクに使う転移学習・ファインチューニング。画像と言語を結ぶCLIPなどマルチモーダル。判断根拠を示す説明可能AI（Grad-CAM、LIME、SHAP）やモデル軽量化（蒸留・量子化）も重要です。"}]),
 L("l-impl", "社会実装・数理統計", "impl", 12,
   "AIプロジェクトの進め方、データの扱い、AIに必要な数理・統計の基礎を押さえます。",
   [{"heading":"AIプロジェクトの進め方","body":"目的設定→データ収集→モデル構築→評価→運用のサイクル。CRISP-DMやMLOps、PoC（概念実証）といった進め方の枠組みを理解します。"},
    {"heading":"データの収集・加工","body":"学習の成否はデータの質と量で決まります。アノテーション（教師データ付け）、前処理、匿名加工情報の活用、オープンデータセット、データの偏り（バイアス）に注意します。"},
    {"heading":"確率・統計の基礎","body":"正規分布などの確率分布、期待値・分散、相関と因果の違い、統計的仮説検定、ベイズの定理。データを正しく読むための基礎です。"},
    {"heading":"数理の基礎","body":"微分（勾配＝学習の要）と線形代数（ベクトル・行列＝データとパラメータの表現）の基礎が、ディープラーニングの仕組み理解の土台になります。"}]),
 L("l-law", "AIの法律と倫理", "law", 14,
   "AIに関わる法律（個人情報・著作権・特許等）とAI倫理・AIガバナンスを押さえます。",
   [{"heading":"AIと個人情報・データの法律","body":"個人情報保護法（要配慮個人情報、匿名加工情報、仮名加工情報）。学習データや生成物と著作権法、特許法、営業秘密や限定提供データを守る不正競争防止法、独占禁止法、海外はGDPRも押さえます。"},
    {"heading":"AI開発・利用の契約","body":"AI開発委託契約やAIサービス提供契約では、データやモデル・生成物の権利の所在、責任分担が論点になります。"},
    {"heading":"AI倫理とガイドライン","body":"『人間中心のAI社会原則』やAI事業者ガイドライン、OECD原則、EU AI Actなど国内外の指針。公平性（バイアス）、透明性、プライバシー、安全性・セキュリティが重視されます。"},
    {"heading":"AIガバナンスと社会課題","body":"敵対的サンプルやディープフェイクの悪用、説明可能性、民主主義や労働への影響、環境負荷。ルールを固定せず状況に応じて見直す『アジャイル・ガバナンス』が提唱されています。"}]),
]

# ============================================================
# 頻出モデル・キーワード一覧（旧services＝GenAIToolItem を流用）
# ============================================================
def S(id, name, category, oneLiner, domain):
    return {"id": id, "name": name, "category": category, "oneLiner": oneLiner, "domain": domain}

services = [
 S("s-perceptron","パーセプトロン","基礎","ニューラルネットの最小単位。単純では線形分離のみ。","dlBasic"),
 S("s-relu","ReLU","活性化関数","負を0、正はそのまま。勾配消失を抑える主流の活性化関数。","dlBasic"),
 S("s-adam","Adam","最適化","モーメンタムとRMSpropを組み合わせた定番の最適化手法。","dlBasic"),
 S("s-svm","SVM（サポートベクターマシン）","機械学習","マージン最大化で分類する教師あり学習の手法。","ml"),
 S("s-kmeans","k-means","機械学習","データをk個のクラスタに分ける教師なし学習の代表。","ml"),
 S("s-pca","主成分分析(PCA)","機械学習","データの次元を情報を保ちつつ圧縮する手法。","ml"),
 S("s-cnn","CNN","DL要素技術","畳み込みとプーリングで画像特徴を抽出するネットワーク。","dlTech"),
 S("s-resnet","ResNet","画像認識","スキップ結合で超深層の学習を可能にした画像認識モデル。","dlTech"),
 S("s-lstm","LSTM","DL要素技術","ゲート機構で長期依存を扱えるRNNの改良版。","dlTech"),
 S("s-transformer","Transformer","DL要素技術","自己注意機構だけで系列を扱う。BERT・GPTの基盤。","dlTech"),
 S("s-alexnet","AlexNet","画像認識","2012年ILSVRC優勝。ディープラーニング躍進の契機。","dlApp"),
 S("s-yolo","YOLO","物体検出","画像を一度見て物体位置と種類を高速に検出。","dlApp"),
 S("s-bert","BERT","自然言語処理","双方向Transformerで文脈を理解する言語モデル。","dlApp"),
 S("s-gpt","GPT","自然言語処理","生成寄りの大規模言語モデル。ChatGPTの基盤。","dlApp"),
 S("s-word2vec","word2vec","自然言語処理","単語を意味を反映したベクトルに変換する手法。","dlApp"),
 S("s-gan","GAN","生成モデル","生成器と識別器を競わせて本物らしいデータを生成。","dlApp"),
 S("s-diffusion","拡散モデル","生成モデル","ノイズ除去を学習して画像などを生成する主流手法。","dlApp"),
 S("s-dqn","DQN","深層強化学習","強化学習に深層学習を用い、Atariで人間超えを達成。","dlApp"),
 S("s-alphago","AlphaGo","深層強化学習","深層強化学習と探索で囲碁のトップ棋士を破ったAI。","dlApp"),
 S("s-gradcam","Grad-CAM","XAI","CNNが画像のどこに注目したかを可視化する説明手法。","dlApp"),
]

# ============================================================
# 取り込み・組み立て
# ============================================================
questions = []
for bf in sorted(glob.glob(os.path.join(DESIGN, "batch_*.json"))):
    b = json.load(open(bf, encoding="utf-8")); questions.extend(b)
    print(f"merged {os.path.basename(bf)}: +{len(b)}")

# 反復ドリル（tag「ドリル」・模試除外）
drill_by_domain = {}
for df in sorted(glob.glob(os.path.join(DESIGN, "drill_*.json"))):
    ds = json.load(open(df, encoding="utf-8"))
    for q in ds:
        if "ドリル" not in q.get("tags", []): q.setdefault("tags", []).append("ドリル")
        drill_by_domain.setdefault(q["domain"], []).append(q["id"])
    questions.extend(ds); print(f"merged {os.path.basename(df)}: +{len(ds)} (ドリル)")

# レッスンへ確認問題（本問・各分野先頭8問）とドリルを自動割当
by_domain_main = {}
for q in questions:
    if "ドリル" not in q.get("tags", []):
        by_domain_main.setdefault(q["domain"], []).append(q["id"])
for l in lessons:
    l["quizIds"] = by_domain_main.get(l["domain"], [])[:8]
    ids = drill_by_domain.get(l["domain"], [])
    l["drillQuizIds"] = ids if ids else None

# 用語カード（全て terms_extra*.json から）
terms = []
for tf in sorted(glob.glob(os.path.join(DESIGN, "terms_extra*.json"))):
    ex = json.load(open(tf, encoding="utf-8")); sid = {t["id"] for t in terms}; strm = {t["term"] for t in terms}
    add = 0
    for t in ex:
        if t["id"] in sid or t["term"] in strm: continue
        terms.append(t); sid.add(t["id"]); strm.add(t["term"]); add += 1
    print(f"merged {os.path.basename(tf)}: +{add} terms")

# 検証
def validate(qs):
    errs, seen = [], set()
    for q in qs:
        i = q.get("id", "?")
        if i in seen: errs.append(f"重複id {i}")
        seen.add(i)
        if q.get("domain") not in VALID: errs.append(f"{i} 不正domain {q.get('domain')}")
        ch = q.get("choices", [])
        if len(ch) != 4: errs.append(f"{i} choices={len(ch)}")
        if len(set(ch)) != 4: errs.append(f"{i} 選択肢重複")
        ca = q.get("correctAnswers", [])
        if len(ca) != 1 or not (0 <= ca[0] < len(ch)): errs.append(f"{i} correct異常 {ca}")
        for k in q.get("wrongChoiceExplanations", {}):
            ki = int(k)
            if not (0 <= ki < len(ch)) or ki in ca: errs.append(f"{i} wrongkey異常 {k}")
        if "ドリル" not in q.get("tags", []):
            for idx in range(len(ch)):
                if idx not in ca and str(idx) not in q.get("wrongChoiceExplanations", {}):
                    errs.append(f"{i} 誤答解説欠落{idx}")
        if not q.get("explanation", "").strip(): errs.append(f"{i} 解説空")
        if q.get("difficulty") not in (1, 2, 3): errs.append(f"{i} difficulty={q.get('difficulty')}")
    return errs

_errs = validate(questions)
if _errs:
    print("=== 検証エラー ===")
    for e in _errs[:60]: print("  -", e)
    raise SystemExit(f"検証エラー {len(_errs)}件")

questions = balance_positions(questions)

def dump(name, data):
    json.dump(data, open(os.path.join(BASE, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{name}: {len(data)} items")

dump("questions.json", questions)
dump("terms.json", terms)
dump("lessons.json", lessons)
dump("services.json", services)

# 用語集（tooltip）
gsrc = []
for gf in sorted(glob.glob(os.path.join(DESIGN, "glossary_source*.json"))):
    gsrc += json.load(open(gf, encoding="utf-8"))
seen = set(); gout = []
for g in gsrc:
    if g["term"] in seen: continue
    seen.add(g["term"]); gout.append({"term": g["term"], "explanation": g["explanation"]})
gout.sort(key=lambda x: len(x["term"]), reverse=True)
json.dump(gout, open(os.path.join(BASE, "glossary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"glossary.json: {len(gout)} entries")

main = [q for q in questions if "ドリル" not in q.get("tags", [])]
print("本問:", len(main), "総問題:", len(questions),
      "分野別(本問):", dict(Counter(q["domain"] for q in main)))
