import SwiftUI

/// G検定（JDLA ジェネラリスト検定）のシラバス2024に対応する出題分野。
/// シラバス：design/syllabus_gkentei_2024.txt（出典 jdla.org）。
/// 技術8項目＋法律倫理2項目を、アプリでは7分野に集約している。
/// ※各分野の配点比率は公式に非公表のため、出題範囲の分量からの近似値。
///   最新情報・出題範囲は必ず公式サイト（jdla.org）で確認すること。
enum ExamDomain: String, CaseIterable, Codable, Identifiable {
    case hist       // 人工知能とは＋動向＋AI分野の問題
    case ml         // 機械学習の概要
    case dlBasic    // ディープラーニングの概要
    case dlTech     // ディープラーニングの要素技術
    case dlApp      // ディープラーニングの応用例
    case impl       // AIの社会実装＋数理・統計
    case law        // AIの法律と倫理

    var id: String { rawValue }

    /// 出題比率の近似値（模試の出題配分・合格可能性スコアに使用）。合計1.0。
    var weight: Double {
        switch self {
        case .hist:    return 0.13
        case .ml:      return 0.15
        case .dlBasic: return 0.15
        case .dlTech:  return 0.15
        case .dlApp:   return 0.17
        case .impl:    return 0.10
        case .law:     return 0.15
        }
    }

    var title: String {
        switch self {
        case .hist:    return "人工知能とは・動向"
        case .ml:      return "機械学習の手法"
        case .dlBasic: return "ディープラーニングの概要"
        case .dlTech:  return "ディープラーニングの要素技術"
        case .dlApp:   return "ディープラーニングの応用"
        case .impl:    return "社会実装・数理統計"
        case .law:     return "AIの法律と倫理"
        }
    }

    var shortTitle: String {
        switch self {
        case .hist:    return "AI史・動向"
        case .ml:      return "機械学習"
        case .dlBasic: return "DL概要"
        case .dlTech:  return "DL要素技術"
        case .dlApp:   return "DL応用"
        case .impl:    return "実装・数理"
        case .law:     return "法律・倫理"
        }
    }

    /// 章番号（並び順）
    var chapterNumber: Int {
        switch self {
        case .hist:    return 1
        case .ml:      return 2
        case .dlBasic: return 3
        case .dlTech:  return 4
        case .dlApp:   return 5
        case .impl:    return 6
        case .law:     return 7
        }
    }

    /// 配点を百分率の整数で（UI表示用）
    var weightPercent: Int { Int((weight * 100).rounded()) }

    var color: Color {
        switch self {
        case .hist:    return Theme.navy
        case .ml:      return Theme.blue
        case .dlBasic: return Theme.teal
        case .dlTech:  return Theme.purple
        case .dlApp:   return Theme.orange
        case .impl:    return Theme.indigo
        case .law:     return Theme.rose
        }
    }

    var systemIcon: String {
        switch self {
        case .hist:    return "brain.head.profile"
        case .ml:      return "chart.dots.scatter"
        case .dlBasic: return "point.3.connected.trianglepath.dotted"
        case .dlTech:  return "square.stack.3d.up.fill"
        case .dlApp:   return "eye.fill"
        case .impl:    return "gearshape.2.fill"
        case .law:     return "checkmark.shield.fill"
        }
    }
}
