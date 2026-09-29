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

注意（v1.1.0〜）：このスクリプトは Resources を作り直すので、実行後に必ず次の順で再反映する。
  python design/apply_polish.py design/polish --apply     # 選択肢の長さ・解説の手直し
  python design/apply_polish.py design/balance --apply    # 正解が最長にならない逆の癖の是正
  python design/add_basic_questions.py design/basic --apply  # 各レッスンの基礎問題10問
  python design/validate_resources.py
ただし正解位置の並べ替え（balance_positions）で choices の順が変わると手直しと食い違うため、
再実行する場合は手直し前後で各問の choices 順が一致しているかを先に確かめること。
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
# レッスン（各分野3小テーマ＝計21本）
# 確認問題とドリルは lessonTheme（新規問題）または service（既存問題）で自動割当。
# ============================================================
def SL(id, domain, theme, title, minutes, summary, services, sections):
    return {"id": id, "domain": domain, "theme": theme, "title": title, "minutes": minutes,
            "summary": summary, "services": services, "sections": sections}

SUBLESSONS = [
 # ------- 人工知能とは・動向 -------
 SL("l-hist1", "hist", "AIの定義と議論", "AIの定義と議論", 11,
    "AIに唯一の定義がないこと、知能をめぐる古典的な議論、AIが抱える本質的な課題を押さえます。",
    ["AIの定義","チューリングテスト","中国語の部屋","強いAI/弱いAI","フレーム問題",
     "シンボルグラウンディング問題","身体性","シンギュラリティ","知能爆発","AI効果",
     "AIをめぐる議論","AIの古典的問題"],
    [{"heading":"AIとは何か","body":"人工知能に唯一の定義はなく、研究者ごとに立場が異なります。人間のように思考・学習・推論する機能をコンピュータで実現する技術の総称と理解しておけば十分です。原理が解明されると『それは知能ではない』と見なされてしまう現象はAI効果と呼ばれます。"},
     {"heading":"知能をめぐる議論","body":"アラン・チューリングが考案したチューリングテストは、対話相手が人間か機械か判別できなければ知能があるとみなす、という判定法です。これに対しジョン・サールの『中国語の部屋』は、記号操作だけで受け答えできても意味を理解しているとは言えないと反論しました。サールは心を持つAIを強いAI、道具として振る舞うだけのAIを弱いAIと分類しています。"},
     {"heading":"AIの古典的な問題","body":"フレーム問題は、今しようとしていることに関係のある事柄だけを有限の処理能力で切り出すのが難しいという問題。シンボルグラウンディング問題は、記号がそれが指す実世界の意味と結びついていないという問題です。知能には身体を通じた環境との相互作用が必要だとする身体性の立場や、AIが人間の知能を超えるとされるシンギュラリティ（技術的特異点）の議論も押さえます。"}]),
 SL("l-hist2", "hist", "探索・推論と知識表現", "探索・推論と知識表現", 11,
    "第1次ブームの探索・推論と、第2次ブームの知識表現・エキスパートシステムを押さえます。",
    ["Mini-Max法","αβ枝刈り","ハノイの塔","モンテカルロ法","幅優先探索","深さ優先探索",
     "トイプロブレム","マイシン(MYCIN)","意味ネットワーク","オントロジー","Cycプロジェクト",
     "知識獲得のボトルネック","探索と推論","知識表現"],
    [{"heading":"探索・推論（第1次AIブーム）","body":"迷路やハノイの塔のような問題を、場合分けを尽くして解く探索・推論が中心でした。手前から順に探す幅優先探索と、行けるところまで進む深さ優先探索、ゲームの手を読むMini-Max法と無駄な枝を刈るαβ法、ランダムな試行を重ねるモンテカルロ法が代表格です。"},
     {"heading":"トイプロブレムの壁","body":"当時扱えたのは、現実の複雑さを削ぎ落とした簡略な問題（トイプロブレム）に限られました。現実世界の問題は解けないと分かり、第1次ブームは冬の時代を迎えます。"},
     {"heading":"知識表現（第2次AIブーム）","body":"専門家の知識をルールとして詰め込むエキスパートシステムが登場し、感染症診断のMYCINが有名です。知識の表し方として意味ネットワークやオントロジー、一般常識を大量に記述するCycプロジェクトも進みました。しかし知識を人手で書き出す作業が膨大で、知識獲得のボトルネックが壁となり再び冬の時代に入ります。"}]),
 SL("l-hist3", "hist", "AIブームの変遷と現在", "AIブームの変遷と現在", 10,
    "3度のブームとAIの冬の流れ、第3次ブームの契機、話題になったAIを押さえます。",
    ["AIの3度のブーム","ダートマス会議","ELIZA","統計的自然言語処理","第3次AIブーム・ILSVRC",
     "東ロボくん","ワトソン","AIの歴史","AIの動向"],
    [{"heading":"AIの誕生と3度のブーム","body":"1956年のダートマス会議で『人工知能（Artificial Intelligence）』という言葉が初めて使われました。以降、第1次（探索・推論）→冬の時代→第2次（知識表現）→冬の時代→第3次（機械学習・ディープラーニング）という波を繰り返しています。"},
     {"heading":"第3次ブームの契機","body":"Webの普及で大量のデータが集まり、統計的自然言語処理のようにデータから学ぶ手法が力を持ちました。決定打は2012年の画像認識コンペILSVRCで、ディープラーニングを用いたAlexNetが圧勝したことです。"},
     {"heading":"話題になったAIたち","body":"初期の対話プログラムELIZAは、発言を言い換えて返すだけの単純な仕組みで人間らしさを演出しました。IBMのワトソンは米国のクイズ番組で人間のチャンピオンに勝利し、東ロボくんは大学入試に挑戦して、AIの得手不得手（読解の難しさ）を浮き彫りにしました。"}]),
 # ------- 機械学習の手法 -------
 SL("l-ml1", "ml", "教師あり学習", "教師あり学習", 12,
    "正解ラベル付きデータから学ぶ回帰・分類の代表的アルゴリズムとアンサンブル学習を押さえます。",
    ["教師あり学習","線形回帰","ロジスティック回帰","サポートベクターマシン",
     "サポートベクターマシン（カーネル法）","決定木","決定木（不純度指標）","ランダムフォレスト",
     "勾配ブースティング","AdaBoost","k近傍法","ナイーブベイズ","アンサンブル学習"],
    [{"heading":"回帰と分類","body":"教師あり学習は入力と正解ラベルのペアから規則を学びます。連続値を予測するのが回帰（線形回帰）、カテゴリを当てるのが分類です。ロジスティック回帰は線形結合をシグモイド関数に通して0〜1の確率を出すため、名前は回帰ですが分類に使います。"},
     {"heading":"代表的なアルゴリズム","body":"SVMは決定境界と最も近いデータ点との距離（マージン）を最大化する手法で、カーネルトリックにより非線形な分離もできます。決定木は不純度（ジニ係数・情報利得）が最も減る特徴量で分岐を繰り返します。ほかに近くのk個の多数決で決めるk近傍法、特徴量の条件付き独立を仮定するナイーブベイズがあります。"},
     {"heading":"アンサンブル学習","body":"複数のモデルを組み合わせて精度と安定性を高める考え方です。ブートストラップ標本で並列に学習し多数決するバギング（その代表がランダムフォレスト）と、前のモデルの誤りを次が補うよう直列に学習するブースティング（AdaBoost、勾配ブースティング）を対比して覚えます。"}]),
 SL("l-ml2", "ml", "教師なし学習と強化学習", "教師なし学習と強化学習", 12,
    "ラベルなしデータから構造を見つける手法と、報酬から方策を学ぶ強化学習を押さえます。",
    ["教師なし学習","k-means法","k-means法（クラスタ数の決定）","階層型クラスタリング",
     "主成分分析（PCA）","主成分分析（寄与率）","t-SNE","協調フィルタリング","半教師あり学習",
     "強化学習","マルコフ決定過程","Q学習","方策勾配法","多腕バンディット問題","UCBアルゴリズム",
     "探索と活用のトレードオフ"],
    [{"heading":"クラスタリング","body":"データをk個のグループに分けるk-means法と、近いものから順に併合し樹形図（デンドログラム）で表す階層型クラスタリングが代表です。デンドログラムを任意の高さで切ればクラスタ数を決められます。"},
     {"heading":"次元削減とレコメンド","body":"情報をなるべく保ったまま次元を減らすのが主成分分析（PCA）で、各主成分がどれだけ情報を説明するかは寄与率で測ります。高次元データの可視化にはt-SNEを使います。似たユーザーの行動から推薦する協調フィルタリングは、履歴のない新規ユーザーに弱いコールドスタート問題を抱えます。少量のラベル付きと大量のラベルなしを併用するのが半教師あり学習です。"},
     {"heading":"強化学習","body":"エージェントが行動し、環境から報酬を受け取りながら、累積報酬を最大化する方策を試行錯誤で学びます。定式化にはマルコフ決定過程を使い、行動価値を学ぶQ学習と、方策を直接改善する方策勾配法が基本です。どの腕を引くか選ぶ多腕バンディット問題では、未知を試す探索と、良いと分かっているものを選ぶ活用のトレードオフが核心で、UCBやε-greedyが方策として使われます。"}]),
 SL("l-ml3", "ml", "モデルの評価と汎化", "モデルの評価と汎化", 12,
    "過学習と汎化性能、混同行列から導く評価指標、正則化までを押さえます。",
    ["モデルの評価","混同行列","適合率・再現率","F値（F1スコア）","ROC曲線・AUC",
     "交差検証（k分割交差検証）","過学習（オーバーフィッティング）","未学習（アンダーフィッティング）",
     "バイアスとバリアンスのトレードオフ","正則化（L1/L2）","汎化性能・検証"],
    [{"heading":"過学習と汎化","body":"訓練データに合わせすぎて未知データで精度が落ちるのが過学習、そもそも学習不足なのが未学習です。汎化性能を測るためデータを訓練・検証・テストに分け、1回だけ分割するホールドアウト法や、分割を変えて繰り返すk分割交差検証を使います。"},
     {"heading":"分類の評価指標","body":"予測と正解の組み合わせを整理した混同行列から各指標を計算します。適合率＝TP/(TP+FP)は『陽性と予測したうちの正解率』、再現率＝TP/(TP+FN)は『実際の陽性を取りこぼさない率』で、両者は трейドオフの関係にあり調和平均のF値で総合評価します。閾値を動かして描くROC曲線の下面積がAUCです。"},
     {"heading":"バイアス・バリアンスと正則化","body":"モデルが単純すぎる誤差（バイアス）と、データの揺らぎに敏感すぎる誤差（バリアンス）はトレードオフの関係にあります。過学習を抑えるには、重みの大きさに罰則を課す正則化（不要な特徴量の係数を0にしやすいL1＝ラッソ、全体を滑らかに抑えるL2＝リッジ）が有効です。"}]),
 # ------- ディープラーニングの概要 -------
 SL("l-dlb1", "dlBasic", "ニューラルネットワークの基礎", "ニューラルネットワークの基礎", 11,
    "パーセプトロンから多層化・ディープラーニングへの発展と、重みの初期化を押さえます。",
    ["ニューラルネットワーク","パーセプトロン","ディープラーニング概要","事前学習",
     "オートエンコーダ","重みの初期化","学習理論"],
    [{"heading":"パーセプトロンから多層へ","body":"単純パーセプトロンは直線でしか分けられず、XOR問題が解けないことが指摘されました。中間の隠れ層を挟んだ多層パーセプトロンにすることで非線形な分離ができるようになります。"},
     {"heading":"ディープラーニングとは","body":"隠れ層を何層も重ねたニューラルネットワークを用い、特徴量の設計まで含めてデータから自動的に学習する手法です。層を深くするほど表現力は上がりますが、勾配消失などで学習が難しくなるという課題も生まれました。"},
     {"heading":"重みの初期化と事前学習","body":"重みを全て同じ値にすると各ニューロンが同じ更新をしてしまい多様な特徴を学べません。活性化関数に応じてXavier初期化（シグモイド系）やHe初期化（ReLU系）を使い分けます。深い学習が難しかった時代には、オートエンコーダで層ごとに学習してから積み上げる事前学習が用いられました。なお、あらゆる問題で万能な唯一のアルゴリズムは存在しないことを示すノーフリーランチ定理も押さえます。"}]),
 SL("l-dlb2", "dlBasic", "活性化関数と誤差逆伝播", "活性化関数と誤差逆伝播", 12,
    "活性化関数の使い分け、誤差関数、誤差逆伝播と勾配消失を押さえます。",
    ["活性化関数","誤差関数","誤差逆伝播","勾配消失"],
    [{"heading":"活性化関数","body":"ニューロンの出力を決める関数です。シグモイドやtanhは微分の最大値が小さく勾配消失を起こしやすいため、負を0・正はそのまま通すReLUが主流になりました。ReLUは負の領域で勾配が0になるため、わずかな傾きを残すLeaky ReLUも使われます。tanhの出力は-1〜1、シグモイドは0〜1である点は混同しやすいので注意します。"},
     {"heading":"出力層と誤差関数","body":"出力層は解きたいタスクで決まります。回帰なら恒等関数＋二乗誤差、多クラス分類なら合計が1になるソフトマックス＋交差エントロピーが基本の組み合わせです。誤差（損失）関数は予測と正解のズレを数値化し、学習の指標になります。"},
     {"heading":"誤差逆伝播と勾配消失","body":"出力側で計算した誤差を、連鎖律を使って入力側へ遡らせながら各重みの勾配を求めるのが誤差逆伝播法です。層が深いと勾配が掛け合わされて指数的に小さくなり、入力側の層が学習されなくなる勾配消失問題が起きます。"}]),
 SL("l-dlb3", "dlBasic", "最適化と過学習対策", "最適化と過学習対策", 12,
    "勾配降下法とその発展形、学習を妨げる要因、過学習を抑える手法を押さえます。",
    ["最適化","正則化"],
    [{"heading":"勾配降下法とミニバッチ","body":"誤差が小さくなる方向へ重みを少しずつ動かすのが勾配降下法で、更新幅を決めるのが学習率です。データを小分けにして更新するミニバッチ学習では、1回の更新がイテレーション、訓練データを1周するのがエポックです。"},
     {"heading":"学習を妨げる地形","body":"一部の近傍でだけ誤差最小になる局所最適解、ある方向には極小で別方向には極大となる鞍点、傾きがほぼ平らで進まないプラトーが学習を停滞させます。勢いを付けるモーメンタム、学習率を自動調整するAdaGrad・RMSprop・AdaDelta、両者を組み合わせたAdamが対策として使われます。"},
     {"heading":"過学習対策","body":"重みに罰則を課すL1/L2正則化、学習のたびにニューロンをランダムに無効化するドロップアウト、検証誤差が悪化したら止める早期終了、各層の入力の分布を整えるバッチ正規化が代表的です。なお近年は、モデルを大きくすると誤差が一度悪化した後また下がる二重降下現象も知られています。"}]),
 # ------- ディープラーニングの要素技術 -------
 SL("l-dlt1", "dlTech", "CNNと画像の要素技術", "CNNと画像の要素技術", 12,
    "畳み込み・プーリングの仕組みと、深いCNNを可能にした工夫を押さえます。",
    ["CNN","CNN(重み共有)","畳み込み層","ストライド","パディング","プーリング層","特徴マップ",
     "全結合層","スキップ結合(ResNet)","バッチ正規化","画像処理の基本技術"],
    [{"heading":"畳み込み層","body":"フィルタ（カーネル）を少しずつずらしながら重ね合わせ、特徴マップを作ります。ずらす幅がストライド、周囲を埋めて出力サイズを保つのがパディングです。出力サイズは（入力＋2×パディング−フィルタ）÷ストライド＋1で求められます。同じフィルタを画像全体で使い回す重み共有により、全結合層よりパラメータが大幅に少なくて済みます。"},
     {"heading":"プーリングと全結合層","body":"プーリング層は領域内の最大値や平均値を取って情報を圧縮し、多少の位置ずれに強くします（位置不変性）。終盤の全結合層でクラス分類を行いますが、パラメータが多く過学習しやすいため、各チャンネルを1つの平均値に集約するGlobal Average Poolingで置き換える構成も広く使われます。"},
     {"heading":"深いCNNを可能にした工夫","body":"CNNの源流は視覚野の仕組みを模したネオコグニトロン、実用的な初期例が手書き数字認識のLeNetです。層を深くすると学習が困難になりますが、入力をそのまま先の層の出力に足すResNetのスキップ結合により勾配が伝わりやすくなり、超深層でも学習できるようになりました。各層の入力分布を整えるバッチ正規化も学習を安定させます。"}]),
 SL("l-dlt2", "dlTech", "RNN・LSTMと系列処理", "RNN・LSTMと系列処理", 12,
    "時系列データを扱うRNNと、長期依存を扱うLSTM・GRUを押さえます。",
    ["RNN","LSTM","GRU","BPTT","勾配クリッピング","勾配消失・爆発"],
    [{"heading":"RNNとBPTT","body":"RNNは前の時刻の出力を次の時刻へ渡す回帰結合を持ち、並び順に意味がある時系列・系列データを扱えます。学習は時間方向に展開して誤差を遡らせるBPTTで行います。"},
     {"heading":"勾配消失・爆発とその対策","body":"長い系列では同じ重みが繰り返し掛かるため、勾配が指数的に小さくなる勾配消失や、逆に発散する勾配爆発が起きます。勾配爆発には勾配の大きさに上限を設ける勾配クリッピングが有効です。"},
     {"heading":"LSTMとGRU","body":"LSTMは誤差がほぼ減衰せず流れる経路CEC（Constant Error Carousel）と、入力・出力・忘却の3つのゲートで情報の出し入れを制御し、長期依存を学習できるようにしました。GRUはセル状態と隠れ状態を統合し、更新ゲートとリセットゲートの2つに簡略化した軽量版です。前後両方向の文脈を使う双方向RNNも押さえます。"}]),
 SL("l-dlt3", "dlTech", "Attention・Transformerと生成の基礎", "Attention・Transformerと生成の基礎", 13,
    "Attentionの仕組みとTransformer、オートエンコーダ・データ拡張・転移学習を押さえます。",
    ["Attention","Attention・Transformer","Self-Attention","Transformer","Transformer(スケーリング)",
     "マルチヘッドアテンション","位置エンコーディング","オートエンコーダ","VAE","データ拡張",
     "転移学習・ファインチューニング","モデル軽量化"],
    [{"heading":"Attentionの仕組み","body":"入力のどこに注目すべきかを重み付けして学ぶのがAttentionです。QueryとKeyの内積で関連度を測りValueを取り出す仕組みで、同一系列内の要素同士の関連を見るものをSelf-Attention（自己注意）と呼びます。離れた位置にある単語同士の関係も直接捉えられるのが強みです。"},
     {"heading":"Transformer","body":"再帰も畳み込みも使わず、Self-Attentionだけで系列を処理するのがTransformerです。並列計算しやすく大規模化に向き、BERTやGPTの基盤となりました。複数の視点で同時に注意を計算するMulti-Head Attentionと、語順の情報を与える位置エンコーディングが要素技術です。"},
     {"heading":"オートエンコーダ・データ拡張・転移学習","body":"入力を圧縮して復元するオートエンコーダは特徴表現の学習や異常検知に使え、潜在変数を確率分布として学ぶVAEは生成にも使えます。学習データを回転・反転・Cutout・Mixupなどで水増しするデータ拡張は過学習対策として有効です。学習済みモデルを別タスクに流用するのが転移学習、その重みを再調整するのがファインチューニング。蒸留・量子化・プルーニングはモデルを軽量化する手法です。"}]),
 # ------- ディープラーニングの応用 -------
 SL("l-dla1", "dlApp", "画像認識と物体検出", "画像認識と物体検出", 13,
    "画像認識モデルの系譜、物体検出、セグメンテーション・姿勢推定を押さえます。",
    ["画像認識","AlexNet","VGGNet","GoogLeNet(Inception)","ResNet","EfficientNet",
     "物体検出","R-CNN","Fast R-CNN","Faster R-CNN","YOLO","SSD","セグメンテーション",
     "FCN","U-Net","姿勢推定","画像認識モデル"],
    [{"heading":"画像認識モデルの系譜","body":"2012年のILSVRCでAlexNetが圧勝して以降、層を深くしたVGG、複数サイズのフィルタを並列に使うGoogLeNet（Inception）、スキップ結合で超深層を可能にしたResNet、深さ・幅・解像度をバランスよく拡大したEfficientNetへと発展しました。近年は画像をパッチに分割しTransformerで扱うVision Transformerも主流です。"},
     {"heading":"物体検出","body":"画像中の物体の位置（バウンディングボックス）と種類を求めるタスクです。候補領域の提案と分類を分ける2段階検出（R-CNN→Fast R-CNN→Faster R-CNNと高速化）と、1回の処理でまとめて行う1段階検出（YOLO、SSD）に大別され、後者は高速です。"},
     {"heading":"セグメンテーションと姿勢推定","body":"ピクセル単位で領域を塗り分けるのがセマンティックセグメンテーション（FCN、U-Net、SegNet）で、同じクラスでも個体を区別するのがインスタンスセグメンテーション（Mask R-CNN）です。人物の関節点を検出して姿勢を推定するOpenPoseも代表的な応用です。"}]),
 SL("l-dla2", "dlApp", "自然言語処理と音声", "自然言語処理と音声", 13,
    "単語のベクトル化からBERT・GPT・LLM、そして音声処理までを押さえます。",
    ["自然言語処理","word2vec","seq2seq","Attention","BERT","GPT","LLM","RAG",
     "ハルシネーション","プロンプトエンジニアリング","音声処理","WaveNet","メル尺度","音素",
     "隠れマルコフモデル"],
    [{"heading":"単語のベクトル化","body":"日本語は単語の区切りが明確でないため、まず形態素解析で分割します。単語の出現回数だけを見るBoWや重要度を測るTF-IDFに対し、word2vecは単語を意味を反映したベクトルに変換します。サブワードに分解して未知語に対応するfastTextもあります。系列を別の系列に変換するseq2seqは翻訳などに使われます。"},
     {"heading":"BERT・GPTとLLM","body":"Transformerを基盤に、文中の単語を隠して前後双方向の文脈から当てるMLMで学習するBERTと、次の単語を予測する生成寄りのGPTが登場しました。モデルとデータを大きくするほど性能が上がるスケーリング則のもと大規模言語モデル（LLM）が発展。事実でない内容をもっともらしく生成するハルシネーションが課題で、外部知識を検索して回答に使うRAGや、指示の工夫であるプロンプトエンジニアリングが対策・活用法として重要です。"},
     {"heading":"音声処理","body":"音声は波形のままでは扱いにくいため、周波数成分に変換し、人間の聴覚特性に合わせたメル尺度やMFCCで特徴量にします。言語の最小音単位が音素で、古くは隠れマルコフモデルが使われました。音声からテキストへ変換するのが音声認識、テキストから波形を生成するのが音声合成で、WaveNetは深層学習による音声合成の代表例です。"}]),
 SL("l-dla3", "dlApp", "強化学習・生成モデル・XAI", "強化学習・生成モデル・XAI", 13,
    "深層強化学習、GAN・拡散モデル、マルチモーダルとXAI・軽量化を押さえます。",
    ["深層強化学習","DQN","経験再生","A3C","AlphaGo","生成モデル","GAN","DCGAN","拡散モデル",
     "マルチモーダル","CLIP","XAI","XAI(Grad-CAM・LIME・SHAP)","モデルの軽量化",
     "転移学習・ファインチューニング","敵対的サンプル"],
    [{"heading":"深層強化学習","body":"強化学習に深層学習を組み合わせたのがDQNで、Atariのゲームで人間を超えました。過去の経験を貯めてランダムに再利用する経験再生により学習を安定させています。囲碁のAlphaGoは深層強化学習と探索でトップ棋士を破り、AlphaGo Zeroは人間の棋譜を一切使わず自己対戦のみで前身を上回りました。複数エージェントを並列に動かすA3Cや、シミュレーションで学んだ方策を実機へ移すsim2realも押さえます。"},
     {"heading":"生成モデル","body":"GANは偽データを作る生成器と真贋を見抜く識別器を競わせて学習します（DCGANはCNNを用いた発展形、対になっていない画像同士を変換するCycleGANも有名）。近年はノイズを段階的に除去することを学ぶ拡散モデルが主流で、Stable Diffusionなどの画像生成を支えています。潜在変数を確率分布として学ぶVAEも生成に使えます。"},
     {"heading":"マルチモーダル・XAI・軽量化","body":"画像とテキストを対照学習で結ぶCLIPや、文章から画像を作るDALL-Eなど、複数種類のデータを扱うマルチモーダルが広がっています。判断根拠を示す説明可能AI（XAI）には、CNNの注目領域を可視化するGrad-CAM、局所的に近似して説明するLIME、協力ゲーム理論のシャープレイ値に基づくSHAPがあります。実運用では蒸留・量子化・プルーニングによる軽量化や、微小なノイズで誤分類を誘発する敵対的サンプルへの備えも重要です。"}]),
 # ------- 社会実装・数理統計 -------
 SL("l-imp1", "impl", "AIプロジェクトの進め方", "AIプロジェクトの進め方", 11,
    "企画から運用までの流れ、体制の考え方、運用後の劣化への対応を押さえます。",
    ["AIプロジェクトの進め方","CRISP-DM","MLOps","PoC","内製・外注","開発と運用",
     "プロジェクト計画"],
    [{"heading":"進め方の全体像","body":"目的設定→データ収集→モデル構築→評価→運用のサイクルで進めます。データ分析の標準的な進め方の枠組みがCRISP-DM、小さく作って実現性を確かめる工程がPoC（概念実証）です。AIは事前に性能を確約できないため、段階を踏んで進めることが重要になります。業務のやり方そのものを見直すBPRや、企画を1枚に整理するAIキャンバスも活用されます。"},
     {"heading":"体制と内製・外注","body":"自社で人材を育てて内製するか、外部に委託するかは、データやモデルの権利の所在、ノウハウの蓄積、スピードを踏まえて判断します。委託する場合は契約で権利と責任の分担を明確にします。"},
     {"heading":"運用とモデルの劣化","body":"開発環境と本番環境の差を吸収するにはコンテナ（Docker）が使われます。運用を継続的に回す仕組みがMLOpsです。時間の経過とともに現実のデータ傾向が学習時から変化し精度が落ちる概念ドリフトが起きるため、監視と再学習の計画が欠かせません。"}]),
 SL("l-imp2", "impl", "データの収集と加工", "データの収集と加工", 11,
    "データの質と量、前処理、データの偏りと関連法令を押さえます。",
    ["データの扱い","アノテーション","オープンデータセット","データバイアス","データリーケージ",
     "匿名加工情報"],
    [{"heading":"データの質と量","body":"学習の成否はデータの質と量で決まります。正解ラベルを付ける作業がアノテーションで、コストと品質のバランスが課題です。自前で集められない場合は公開されているオープンデータセットの活用も検討します。"},
     {"heading":"前処理","body":"未入力の欠損値は除去や補完で扱い、極端な値である外れ値は原因を確認したうえで除去するか意味あるデータとして残すか判断します。特徴量ごとに単位や範囲が違うと学習が偏るため、正規化・標準化でスケールを揃えます。本来使えない情報が訓練データに混入するデータリーケージにも注意が必要です。"},
     {"heading":"データの偏りと法令","body":"学習データが偏っていると、モデルの予測も偏り差別的な結果を生みます（データバイアス）。個人情報を含むデータは、特定の個人を識別できないよう加工した匿名加工情報として活用する道があります。また日本の著作権法30条の4により、思想・感情の享受を目的としない情報解析の用途では、一定の要件のもとで著作物を許諾なく利用できます。"}]),
 SL("l-imp3", "impl", "確率・統計と数理基礎", "確率・統計と数理基礎", 12,
    "確率分布と統計量、相関と因果・仮説検定、微分と線形代数の基礎を押さえます。",
    ["確率・統計","正規分布","期待値","分散・標準偏差","条件付き確率","ベイズの定理",
     "相関と因果","統計的仮説検定","数理基礎","微分・勾配","線形代数"],
    [{"heading":"確率分布と統計量","body":"左右対称の釣鐘型で自然界に広く現れるのが正規分布です。平均的な値を表す期待値、ばらつきを表す分散・標準偏差が基本の統計量。母集団の分布によらず標本平均の分布が正規分布に近づくのが中心極限定理です。"},
     {"heading":"相関と因果・ベイズ・検定","body":"2つの量が一緒に動くこと（相関）は、一方が他方を引き起こすこと（因果）を意味しません。第3の要因による擬似相関に注意します。条件付き確率から原因側の確率を求め直すのがベイズの定理で、迷惑メール判定などに応用されます。統計的仮説検定では、帰無仮説のもとで観測結果以上に極端な値が出る確率であるp値を用いて判断します。"},
     {"heading":"微分と線形代数","body":"誤差を小さくする方向＝勾配は微分で求めるため、微分・偏微分・連鎖律がディープラーニングの学習の土台です。データとパラメータはベクトル・行列で表現されるため、内積や行列積といった線形代数の基礎も欠かせません。情報の不確実性を測るエントロピーなど情報理論の考え方も押さえます。"}]),
 # ------- AIの法律と倫理 -------
 SL("l-law1", "law", "データと知的財産の法律", "データと知的財産の法律", 13,
    "個人情報保護法、著作権法とAI、産業財産権・営業秘密などを押さえます。",
    ["個人情報保護法","個人情報保護委員会","著作権法","特許法","不正競争防止法","独占禁止法",
     "データに関する法律","第三者提供","オプトアウト","オプトイン","クリエイティブ・コモンズ"],
    [{"heading":"個人情報保護法","body":"生存する個人を識別できる情報が個人情報で、人種・信条・病歴など特に配慮を要するものが要配慮個人情報です。特定の個人を識別できないよう加工した匿名加工情報、他の情報と照合しない限り識別できない仮名加工情報という区分もあります。第三者提供には原則として本人の同意が必要で、個人情報保護委員会への届出等により同意なく提供できるオプトアウト制度もあります（要配慮個人情報などには使えません）。"},
     {"heading":"著作権法とAI","body":"著作権は創作した時点で自動的に発生し、登録は不要です。日本では著作権法30条の4により、思想・感情の享受を目的としない情報解析（AIの学習など）は一定の要件のもとで許諾なく行えます。著作権侵害の判断には、既存の著作物に依拠したか（依拠性）と、表現が似ているか（類似性）が問われます。二次利用の条件をあらかじめ示す仕組みとしてクリエイティブ・コモンズ・ライセンスがあります。"},
     {"heading":"産業財産権・営業秘密など","body":"発明を保護する特許法をはじめ、産業財産権は出願・登録が必要な点が著作権と対照的です。不正競争防止法は、秘密管理性・有用性・非公知性の3要件を満たす営業秘密や、限定提供データを保護します。市場の公正な競争を守る独占禁止法も、データの囲い込みなどの文脈で関わります。"}]),
 SL("l-law2", "law", "契約と海外の規制", "契約と海外の規制", 12,
    "AI開発契約、民法・PL法による責任、GDPRとEU AI Actを押さえます。",
    ["AI関連契約","民法","製造物責任法","GDPR","EU AI Act","AI開発契約","海外の規制",
     "契約自由の原則","不法行為責任"],
    [{"heading":"AI開発契約","body":"AIは事前に性能を確約できないという特性があるため、経済産業省「AI・データの利用に関する契約ガイドライン」は、アセスメント→PoC→開発→追加学習と段階を分けて都度契約を結ぶ探索的段階型開発方式を提案しています。学習データ・学習済みモデル・生成物の権利の所在と、責任の分担が主な論点です。"},
     {"heading":"民法とPL法","body":"誰とどんな内容の契約を結ぶかは当事者が自由に決められる（契約自由の原則）のが民法の基本です。故意・過失で他人に損害を与えた場合は不法行為責任（民法709条）を負います。製造物の欠陥で生命・身体・財産に損害が生じた場合は、製造物責任法（PL法）により製造業者等の過失を立証しなくても賠償を求められます。"},
     {"heading":"GDPRとEU AI Act","body":"EUのGDPRは、忘れられる権利（消去権）、データポータビリティの権利、プロファイリングを含む自動化された意思決定のみに服さない権利など、日本の個人情報保護法にはない権利を認めています。EU域外への移転には十分性認定などの手当てが必要です。EU AI Actは、AIの用途をリスクの高さで区分して規制の強さを変えるリスクベースアプローチを採っています。"}]),
 SL("l-law3", "law", "AI倫理・ガバナンスと社会課題", "AI倫理・ガバナンスと社会課題", 13,
    "AI倫理の原則、AIガバナンスの考え方、AIがもたらす社会課題を押さえます。",
    ["AI倫理","AI倫理・ガイドライン","AIガバナンス","社会課題","AI倫理原則",
     "アジャイル・ガバナンス","AIの軍事利用","フィルターバブル","シンギュラリティ"],
    [{"heading":"AI倫理の原則","body":"日本の『人間中心のAI社会原則』やAI事業者ガイドライン、OECDのAI原則など、国内外で指針が示されています。共通して重視されるのは、公平性（バイアスを避ける）、透明性（判断根拠の可視化）、説明責任（アカウンタビリティ）、追跡可能性（トレーサビリティ）、プライバシー、安全性・セキュリティです。"},
     {"heading":"AIガバナンス","body":"技術と社会の変化が速いため、一度決めたルールを固定するのではなく、策定・実行・評価・改善を継続的に回して統治の仕組み自体を見直していくアジャイル・ガバナンスが提唱されています。"},
     {"heading":"AIがもたらす社会課題","body":"精巧な偽動画・偽音声を作るディープフェイクやフェイクニュースの拡散、パーソナライズにより自分の興味に近い情報ばかりに囲まれるフィルターバブル、同じ意見が閉じた集団内で増幅されるエコーチェンバーが問題になっています。人間の関与なく攻撃対象を選ぶ自律型致死兵器システム（LAWS）の規制、雇用への影響、学習にかかる環境負荷、シンギュラリティの議論も押さえます。"}]),
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
for df in sorted(glob.glob(os.path.join(DESIGN, "drill_*.json"))):
    ds = json.load(open(df, encoding="utf-8"))
    for q in ds:
        if "ドリル" not in q.get("tags", []): q.setdefault("tags", []).append("ドリル")
    questions.extend(ds); print(f"merged {os.path.basename(df)}: +{len(ds)} (ドリル)")

# ------------------------------------------------------------
# レッスン割当：新規問題は lessonTheme、既存問題は service で小レッスンへ。
# 本問が1問でも割当漏れするとエラー（ドリルは同分野内でラウンドロビン）。
# ------------------------------------------------------------
def build_lessons(all_qs):
    from collections import defaultdict
    main = [q for q in all_qs if "ドリル" not in q.get("tags", [])]
    drills = [q for q in all_qs if "ドリル" in q.get("tags", [])]
    dom_subs = defaultdict(list)
    for sl in SUBLESSONS:
        sl["_quiz"], sl["_drill"] = [], []
        dom_subs[sl["domain"]].append(sl)

    def find(q):
        subs = dom_subs.get(q["domain"], [])
        theme = q.get("lessonTheme")
        if theme:
            hit = next((sl for sl in subs if sl["theme"] == theme), None)
            if hit is None:
                raise SystemExit(f'{q["id"]} の lessonTheme「{theme}」が {q["domain"]} に存在しない')
            return hit
        return next((sl for sl in subs if q.get("service") in sl["services"]), None)

    unmapped = []
    for q in main:
        sl = find(q)
        if sl is None:
            unmapped.append((q["id"], q["domain"], q.get("service")))
        else:
            sl["_quiz"].append(q["id"])
    if unmapped:
        print("=== レッスン未割当の本問 ===")
        for u in unmapped[:30]: print("  -", u)
        raise SystemExit(f"未割当 {len(unmapped)}件（SUBLESSONSのservicesに追加が必要）")

    rr = defaultdict(int)
    for dq in drills:
        subs = dom_subs.get(dq["domain"], [])
        if not subs: continue
        target = find(dq)
        if target is None:
            target = subs[rr[dq["domain"]] % len(subs)]; rr[dq["domain"]] += 1
        target["_drill"].append(dq["id"])

    out = []
    for sl in SUBLESSONS:
        out.append({"id": sl["id"], "title": sl["title"], "domain": sl["domain"],
                    "estimatedMinutes": sl["minutes"], "summary": sl["summary"],
                    "sections": sl["sections"], "quizIds": sl["_quiz"],
                    "challengeQuizIds": None,
                    "drillQuizIds": sl["_drill"] if sl["_drill"] else None})
    return out

lessons = build_lessons(questions)
print("レッスン:", len(lessons), "本／quiz計", sum(len(l["quizIds"]) for l in lessons),
      "／drill計", sum(len(l["drillQuizIds"] or []) for l in lessons))
for l in lessons:
    print(f'  {l["id"]:9s} {l["title"]:28s} quiz{len(l["quizIds"]):3d} drill{len(l["drillQuizIds"] or []):3d}')

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

# --- 選択肢の書き換えパッチ（design/fix_choices*.json）---
# 「正解だけ文章が長い＝中身を知らなくても最長を選べば当たる」癖を是正するため、
# 選択肢の文言だけを差し替える。形式：[{"id": "q-xx-001", "choices": [4つ]}]。
# 順序は元データのまま＝correctAnswers・wrongChoiceExplanationsのindexは不変。
# この後の balance_positions で正解位置は均等化される。
_fixed = 0
for ff in sorted(glob.glob(os.path.join(DESIGN, "fix_choices*.json"))):
    fixes = {f["id"]: f["choices"] for f in json.load(open(ff, encoding="utf-8"))}
    for q in questions:
        new = fixes.pop(q["id"], None)
        if new is None: continue
        if len(new) != len(q["choices"]):
            raise SystemExit(f"fix適用エラー {q['id']}: 選択肢数が {len(q['choices'])} → {len(new)}")
        q["choices"] = new; _fixed += 1
    if fixes:
        raise SystemExit(f"fix適用エラー: 存在しないid {sorted(fixes)[:5]}")
if _fixed: print(f"選択肢パッチ適用: {_fixed}問")

# 作業用：シャッフル前（元データ順）の問題を書き出す。fix_choices を作る際の参照元。
with open(os.path.join(DESIGN, "_source_questions.json"), "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=1)

# 「正解だけ明らかに長い」癖の残数を報告（差6字以上かつ1.3倍以上）
def count_long_tell(qs):
    n = []
    for q in qs:
        ch = q["choices"]; ci = q["correctAnswers"][0]; c = ch[ci]
        mx = max(len(x) for i, x in enumerate(ch) if i != ci)
        if len(c) > mx and len(c) - mx >= 6 and len(c) >= mx * 1.3: n.append(q["id"])
    return n

_errs = validate(questions)
if _errs:
    print("=== 検証エラー ===")
    for e in _errs[:60]: print("  -", e)
    raise SystemExit(f"検証エラー {len(_errs)}件")

_tell = count_long_tell(questions)
print(f"正解だけ明らかに長い問題: {len(_tell)}問 / {len(questions)}")

questions = balance_positions(questions)

# lessonTheme はレッスン割当専用のメタ情報＝アプリ側へは出さない
for q in questions:
    q.pop("lessonTheme", None)

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
