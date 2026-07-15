import SwiftUI

/// 試験直前モード：頻出ポイントの総復習＋直前チェックリスト
struct FinalCheckView: View {
    @EnvironmentObject var store: StudyStore
    @State private var checked: Set<String> = []
    @State private var showQuiz = false

    /// 直前チェックリスト項目（G検定 頻出ポイント）
    private let checklist: [String] = [
        "教師あり・教師なし・強化学習と代表的アルゴリズムを整理した",
        "フレーム問題・シンボルグラウンディング問題など古典的課題を説明できる",
        "活性化関数（ReLU等）・誤差逆伝播・最適化（Adam等）の役割を言える",
        "CNN（畳み込み・プーリング）とRNN・LSTMの違いを説明できる",
        "Attention・Transformer・BERT・GPTの関係を整理した",
        "混同行列・適合率・再現率・F値・ROC/AUCを区別できる",
        "画像認識（ResNet・YOLO）や生成モデル（GAN・拡散モデル）の代表例を言える",
        "深層強化学習（DQN・AlphaGo）の概要を説明できる",
        "個人情報保護法・著作権・不正競争防止法のAI関連ポイントを整理した",
        "AI社会原則・AI事業者ガイドライン・XAI（説明可能性）を思い出せる",
        "受験環境（オンライン・カメラ・本人確認）を事前に確認した",
    ]

    /// 頻出の重要用語（直前に見直すカード）
    private var keyTerms: [TermCard] {
        let ids = ["t-transformer", "t-cnn", "t-backprop", "t-overfitting", "t-copyright", "t-ai-principles"]
        return ids.compactMap { id in ContentRepository.shared.terms.first { $0.id == id } }
    }

    var body: some View {
        ZStack {
            AppBackground()
            ScrollView {
                VStack(alignment: .leading, spacing: Theme.Space.l) {
                    header
                    quickReviewCard
                    keyTermsCard
                    checklistCard
                }
                .padding(Theme.Space.l)
            }
        }
        .navigationTitle("試験直前モード")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(isPresented: $showQuiz) {
            QuizPlayerView(title: "直前総まとめ", questions: finalQuestions)
        }
    }

    private var header: some View {
        Card {
            HStack(spacing: Theme.Space.m) {
                Image(systemName: "bolt.fill").font(.system(size: 24)).foregroundStyle(.white)
                    .frame(width: 48, height: 48).background(Theme.orange).clipShape(Circle())
                VStack(alignment: .leading, spacing: 3) {
                    if let days = store.profile?.daysUntilExam, days >= 0 {
                        Text("試験まで残り\(days)日").font(.system(size: 17, weight: .bold)).foregroundStyle(Theme.navy)
                    } else {
                        Text("ラストスパート").font(.system(size: 17, weight: .bold)).foregroundStyle(Theme.navy)
                    }
                    Text("頻出ポイントを一気に総復習しましょう").captionStyle()
                }
            }
        }
    }

    private var quickReviewCard: some View {
        Card {
            VStack(alignment: .leading, spacing: Theme.Space.m) {
                Text("総まとめ問題").font(.system(size: 16, weight: .bold)).foregroundStyle(Theme.navy)
                Text("苦手分野と間違えた問題を中心に出題します。").captionStyle()
                PrimaryButton(title: "総まとめ問題を解く（\(finalQuestions.count)問）", icon: "checklist") {
                    showQuiz = true
                }
            }
        }
    }

    private var keyTermsCard: some View {
        Card {
            VStack(alignment: .leading, spacing: Theme.Space.m) {
                Text("頻出の重要用語").font(.system(size: 16, weight: .bold)).foregroundStyle(Theme.navy)
                ForEach(keyTerms) { term in
                    VStack(alignment: .leading, spacing: 3) {
                        Text(term.term).font(.system(size: 14, weight: .bold)).foregroundStyle(Theme.blue)
                        Text(term.examPoint).font(.system(size: 13)).foregroundStyle(Theme.ink)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    if term.id != keyTerms.last?.id { Divider() }
                }
            }
        }
    }

    private var checklistCard: some View {
        Card {
            VStack(alignment: .leading, spacing: Theme.Space.m) {
                Text("直前チェックリスト").font(.system(size: 16, weight: .bold)).foregroundStyle(Theme.navy)
                ForEach(checklist, id: \.self) { item in
                    Button {
                        if checked.contains(item) { checked.remove(item) } else { checked.insert(item) }
                    } label: {
                        HStack(alignment: .top, spacing: Theme.Space.s) {
                            Image(systemName: checked.contains(item) ? "checkmark.square.fill" : "square")
                                .foregroundStyle(checked.contains(item) ? Theme.green : Theme.inkSoft)
                            Text(item).font(.system(size: 14))
                                .foregroundStyle(checked.contains(item) ? Theme.inkSoft : Theme.ink)
                                .strikethrough(checked.contains(item))
                                .fixedSize(horizontal: false, vertical: true)
                            Spacer(minLength: 0)
                        }
                    }.buttonStyle(.plain)
                }
                Text("※受験要件・当日ルールは必ずJDLA公式・受験サイトでご確認ください。")
                    .font(.system(size: 11)).foregroundStyle(Theme.inkSoft)
            }
        }
    }

    /// 苦手分野＋復習＋足りなければ全体から補充
    private var finalQuestions: [QuizQuestion] {
        var qs: [QuizQuestion] = store.dueReviewQuestions()
        if let weak = store.weakestDomain() {
            qs += ContentRepository.shared.questions(in: weak)
        }
        var seen = Set<String>()
        var unique = qs.filter { seen.insert($0.id).inserted }
        if unique.count < 10 {
            let extra = ContentRepository.shared.questions.shuffled()
                .filter { seen.insert($0.id).inserted }
            unique += extra.prefix(10 - unique.count)
        }
        return Array(unique.prefix(15))
    }
}
