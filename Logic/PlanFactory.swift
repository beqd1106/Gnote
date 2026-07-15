import Foundation

/// 8週間標準カリキュラムをベースに、選択プランの週数へスケールして
/// 週ごとの学習テーマ（ロードマップ）を生成する。
struct WeekGoal: Identifiable, Hashable {
    let id = UUID()
    let week: Int
    let title: String
    let detail: String
    let domains: [ExamDomain]
}

enum PlanFactory {

    /// 完全初心者向け 8週間の標準ロードマップ（G検定 公式シラバス2024の分野に沿う）
    private static let baseEightWeeks: [WeekGoal] = [
        .init(week: 1, title: "人工知能とは・動向", detail: "AIの定義／探索・推論／知識表現・エキスパートシステム／AIの3度のブーム／フレーム問題・シンギュラリティ", domains: [.hist]),
        .init(week: 2, title: "機械学習の手法", detail: "教師あり（回帰・SVM・決定木）／教師なし（k-means・PCA）／強化学習／モデルの評価（適合率・再現率・ROC）", domains: [.ml]),
        .init(week: 3, title: "ディープラーニングの概要", detail: "ニューラルネット／活性化関数／誤差関数／誤差逆伝播／最適化（SGD・Adam）／勾配消失", domains: [.dlBasic]),
        .init(week: 4, title: "ディープラーニングの要素技術", detail: "CNN（畳み込み・プーリング）／RNN・LSTM／Attention・Transformer／オートエンコーダ／バッチ正規化", domains: [.dlTech]),
        .init(week: 5, title: "ディープラーニングの応用", detail: "画像認識（ResNet・YOLO）／NLP（BERT・GPT・LLM）／深層強化学習（DQN・AlphaGo）／生成（GAN・拡散モデル）／XAI", domains: [.dlApp]),
        .init(week: 6, title: "社会実装・数理統計", detail: "AIプロジェクト（CRISP-DM・MLOps）／データ加工／確率統計・仮説検定・ベイズの定理", domains: [.impl]),
        .init(week: 7, title: "AIの法律と倫理", detail: "個人情報保護法／著作権・特許／AI事業者ガイドライン／公平性・透明性・AIガバナンス", domains: [.law]),
        .init(week: 8, title: "模擬試験と直前対策", detail: "5章横断の模試→間違い集中復習→頻出用語の総仕上げ", domains: ExamDomain.allCases),
    ]

    /// プラン週数に合わせてロードマップを生成する。
    /// 8週以外は週数に応じて圧縮/伸長する（テーマの順序は保つ）。
    static func roadmap(for plan: StudyPlanType) -> [WeekGoal] {
        let weeks = plan.durationWeeks
        if weeks == 8 { return baseEightWeeks }

        var result: [WeekGoal] = []
        for w in 1...weeks {
            // 8週カリキュラム上の対応位置を比例で求める
            let srcIndex = min(baseEightWeeks.count - 1,
                               Int((Double(w - 1) / Double(weeks - 1)) * Double(baseEightWeeks.count - 1)))
            let base = baseEightWeeks[srcIndex]
            result.append(.init(week: w, title: base.title, detail: base.detail, domains: base.domains))
        }
        return result
    }

    /// 現在の経過日数から「今が何週目か」を返す（1始まり）。
    static func currentWeek(startedAt: Date, plan: StudyPlanType, now: Date = .now) -> Int {
        let days = Calendar.current.dateComponents([.day],
            from: Calendar.current.startOfDay(for: startedAt),
            to: Calendar.current.startOfDay(for: now)).day ?? 0
        let week = days / 7 + 1
        return min(max(week, 1), plan.durationWeeks)
    }
}
