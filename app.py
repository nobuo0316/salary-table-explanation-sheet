import streamlit as st
import pandas as pd
from io import BytesIO
from typing import Dict, List, Optional

st.set_page_config(
    page_title="Wage Table / 賃金テーブル",
    page_icon="📊",
    layout="wide",
)

# =========================================================
# Master data
# =========================================================
GRADES: List[str] = ["G6", "G5B", "G5A", "G4", "G3", "G2"]
STEPS: List[int] = list(range(1, 50))
NEXT_GRADE: Dict[str, str] = {
    "G6": "G5B",
    "G5B": "G5A",
    "G5A": "G4",
    "G4": "G3",
    "G3": "G2",
    "G2": "",
}

DEFAULT_PARAMS = {
    "G6": {"base": 18000.0, "ap": 500.0, "pp": 1500.0},
    "G5B": {"base": 22000.0, "ap": 600.0, "pp": 1800.0},
    "G5A": {"base": 26000.0, "ap": 700.0, "pp": 2200.0},
    "G4": {"base": 32000.0, "ap": 800.0, "pp": 2800.0},
    "G3": {"base": 40000.0, "ap": 1000.0, "pp": 3500.0},
    "G2": {"base": 52000.0, "ap": 1200.0, "pp": 0.0},
}

LANGUAGE_PACK = {
    "日本語": {
        "title": "賃金テーブル管理・説明ページ",
        "subtitle": "説明、設定、テーブル編集、昇格シミュレーションを1つにまとめた完成版です。",
        "tab_overview": "説明",
        "tab_table": "賃金テーブル",
        "tab_sim": "昇格シミュレーション",
        "tab_admin": "管理設定",
        "sidebar_lang": "表示言語",
        "sidebar_currency": "通貨記号",
        "sidebar_decimals": "小数表示",
        "overview_heading": "制度概要",
        "overview_text1": "このページでは、Grade（グレード）と Step（ステップ）に基づく賃金テーブルを、英語・日本語の両方で説明・管理できます。",
        "overview_text2": "各社員には必ず Grade と Step があり、略して GS と表記します。例：G5A の Step 4 は G5A-S4 です。",
        "grade_axis": "横軸は Grade（G6～G2）、縦軸は Step（1～49）です。",
        "rule_heading": "基本ルール",
        "rule_ap": "AP（Annual Pay Raise）：毎年、同一グレード内で昇給する額。",
        "rule_pp": "PP（Pay by Promotion）：昇格時に加算される昇給額。",
        "rule_allow": "主な手当は、調整手当と大卒手当です。将来的に追加可能です。",
        "rule_promo": "昇格時は、『現在給与 + 現在グレードの AP + 現在グレードの PP』を下回らないことを条件に、次グレードでその金額以上となる最も近い Step に移動します。",
        "grade_table": "グレード一覧",
        "grade": "グレード",
        "position": "役職イメージ",
        "next_grade": "次グレード",
        "glabel_G6": "平社員",
        "glabel_G5B": "シニアスタッフ",
        "glabel_G5A": "上位シニアスタッフ",
        "glabel_G4": "スーパーバイザー",
        "glabel_G3": "課長",
        "glabel_G2": "次長",
        "wage_heading": "賃金テーブル",
        "wage_caption": "値は直接編集できます。説明会で見せる用にも、そのまま管理用にも使えます。",
        "show_formatted": "表示用フォーマット列も見る",
        "download_csv": "CSVをダウンロード",
        "download_excel": "Excelをダウンロード",
        "sim_heading": "昇格シミュレーション",
        "current_grade": "現在グレード",
        "current_step": "現在ステップ",
        "current_salary": "現在給与",
        "min_required": "昇格時の最低必要額",
        "promoted_grade": "昇格後グレード",
        "promoted_step": "昇格後ステップ",
        "promoted_salary": "昇格後基本給",
        "adjust_allowance": "調整手当",
        "univ_allowance": "大卒手当",
        "is_univ": "大卒対象",
        "other_allowance": "その他手当",
        "final_salary": "最終支給額",
        "simulate": "シミュレーション実行",
        "no_next_grade": "これ以上の次グレードはありません。",
        "gs_before": "昇格前GS",
        "gs_after": "昇格後GS",
        "admin_heading": "管理設定",
        "admin_text": "ここで初期テーブルの自動生成ルールを変更できます。実際の賃金額が決まっている場合は、下のテーブルを直接編集してください。",
        "base_salary": "Step1基準額",
        "ap": "AP（毎年昇給額）",
        "pp": "PP（昇格昇給額）",
        "rebuild": "設定値でテーブル再生成",
        "reset": "初期値に戻す",
        "warning_rebuild": "再生成すると、現在の手動編集内容は上書きされます。",
        "success_rebuild": "テーブルを再生成しました。",
        "success_reset": "初期値に戻しました。",
        "download_note": "必要に応じてこのままCSV / Excelで配布できます。",
        "currency_preview": "表示例",
    },
    "English": {
        "title": "Wage Table Management & Explanation Page",
        "subtitle": "A complete Streamlit app for explanation, setup, table editing, and promotion simulation.",
        "tab_overview": "Overview",
        "tab_table": "Wage Table",
        "tab_sim": "Promotion Simulation",
        "tab_admin": "Admin Settings",
        "sidebar_lang": "Language",
        "sidebar_currency": "Currency symbol",
        "sidebar_decimals": "Decimal places",
        "overview_heading": "System Overview",
        "overview_text1": "This page explains and manages the wage table based on Grade and Step in both English and Japanese.",
        "overview_text2": "Each employee always has a Grade and a Step, abbreviated as GS. Example: G5A Step 4 is written as G5A-S4.",
        "grade_axis": "The horizontal axis is Grade (G6 to G2), and the vertical axis is Step (1 to 49).",
        "rule_heading": "Basic Rules",
        "rule_ap": "AP (Annual Pay Raise): the amount of annual raise within the same grade.",
        "rule_pp": "PP (Pay by Promotion): the additional increase applied upon promotion.",
        "rule_allow": "Main allowances for now are Adjustment Allowance and University Graduate Allowance. More can be added later.",
        "rule_promo": "Upon promotion, the new salary must not be lower than Current Salary + current grade AP + current grade PP. The employee moves to the closest step in the next grade that meets or exceeds that amount.",
        "grade_table": "Grade Reference",
        "grade": "Grade",
        "position": "Position Image",
        "next_grade": "Next Grade",
        "glabel_G6": "Staff",
        "glabel_G5B": "Senior Staff",
        "glabel_G5A": "Upper Senior Staff",
        "glabel_G4": "Supervisor",
        "glabel_G3": "Manager",
        "glabel_G2": "Deputy General Manager",
        "wage_heading": "Wage Table",
        "wage_caption": "You can edit the values directly. It can be used both for presentation and management.",
        "show_formatted": "Show formatted display columns",
        "download_csv": "Download CSV",
        "download_excel": "Download Excel",
        "sim_heading": "Promotion Simulation",
        "current_grade": "Current Grade",
        "current_step": "Current Step",
        "current_salary": "Current Salary",
        "min_required": "Minimum Required for Promotion",
        "promoted_grade": "Promoted Grade",
        "promoted_step": "Promoted Step",
        "promoted_salary": "Promoted Base Salary",
        "adjust_allowance": "Adjustment Allowance",
        "univ_allowance": "University Allowance",
        "is_univ": "University Graduate",
        "other_allowance": "Other Allowance",
        "final_salary": "Final Pay",
        "simulate": "Run Simulation",
        "no_next_grade": "No higher grade is available.",
        "gs_before": "Current GS",
        "gs_after": "New GS",
        "admin_heading": "Admin Settings",
        "admin_text": "Here you can change the auto-generation rule for the initial table. If actual salary values are fixed, you can edit the wage table directly below.",
        "base_salary": "Base Salary at Step 1",
        "ap": "AP (Annual Raise)",
        "pp": "PP (Promotion Raise)",
        "rebuild": "Rebuild table from settings",
        "reset": "Reset to defaults",
        "warning_rebuild": "Rebuilding will overwrite current manual edits.",
        "success_rebuild": "The wage table has been rebuilt.",
        "success_reset": "The defaults have been restored.",
        "download_note": "You can distribute this as CSV or Excel as needed.",
        "currency_preview": "Preview",
    },
}

# =========================================================
# Helpers
# =========================================================
def t(key: str) -> str:
    return LANGUAGE_PACK[st.session_state.lang][key]


def grade_label(grade: str) -> str:
    return LANGUAGE_PACK[st.session_state.lang][f"glabel_{grade}"]


def format_money(value: float) -> str:
    decimals = st.session_state.decimals
    symbol = st.session_state.currency_symbol
    return f"{symbol}{value:,.{decimals}f}"


def build_wage_table(params: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    data = {"Step": STEPS}
    for g in GRADES:
        base = params[g]["base"]
        ap = params[g]["ap"]
        data[g] = [base + (step - 1) * ap for step in STEPS]
    return pd.DataFrame(data)


def make_excel_file(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="WageTable")
    output.seek(0)
    return output.getvalue()


def get_current_salary(df: pd.DataFrame, grade: str, step: int) -> float:
    row = df.loc[df["Step"] == step]
    return float(row.iloc[0][grade])


def find_promotion_result(
    df: pd.DataFrame,
    params: Dict[str, Dict[str, float]],
    current_grade: str,
    current_step: int,
) -> Optional[Dict[str, float]]:
    next_grade = NEXT_GRADE[current_grade]
    if not next_grade:
        return None

    current_salary = get_current_salary(df, current_grade, current_step)
    minimum_required = current_salary + params[current_grade]["ap"] + params[current_grade]["pp"]

    next_rows = df[["Step", next_grade]].copy()
    eligible = next_rows[next_rows[next_grade] >= minimum_required]

    if eligible.empty:
        target_step = int(next_rows.iloc[-1]["Step"])
        target_salary = float(next_rows.iloc[-1][next_grade])
    else:
        target_step = int(eligible.iloc[0]["Step"])
        target_salary = float(eligible.iloc[0][next_grade])

    return {
        "current_salary": current_salary,
        "minimum_required": minimum_required,
        "target_step": target_step,
        "target_salary": target_salary,
        "target_grade": next_grade,
    }


def display_table_with_formats(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for g in GRADES:
        out[f"{g}_Display"] = out[g].apply(format_money)
    return out


# =========================================================
# State
# =========================================================
if "lang" not in st.session_state:
    st.session_state.lang = "日本語"
if "currency_symbol" not in st.session_state:
    st.session_state.currency_symbol = "₱"
if "decimals" not in st.session_state:
    st.session_state.decimals = 0
if "params" not in st.session_state:
    st.session_state.params = {k: v.copy() for k, v in DEFAULT_PARAMS.items()}
if "wage_df" not in st.session_state:
    st.session_state.wage_df = build_wage_table(st.session_state.params)

# =========================================================
# Sidebar
# =========================================================
st.sidebar.title("Wage Table")
st.session_state.lang = st.sidebar.radio(
    t("sidebar_lang") if "lang" in st.session_state else "表示言語",
    ["日本語", "English"],
    index=0 if st.session_state.lang == "日本語" else 1,
)

currency_symbol = st.sidebar.text_input(t("sidebar_currency"), value=st.session_state.currency_symbol)
st.session_state.currency_symbol = currency_symbol
st.session_state.decimals = st.sidebar.selectbox(t("sidebar_decimals"), [0, 1, 2], index=[0, 1, 2].index(st.session_state.decimals))

st.sidebar.caption(f"{t('currency_preview')}: {format_money(12345.67)}")
st.sidebar.markdown("---")
st.sidebar.write("GS Example / GS例")
example_grade = st.sidebar.selectbox("Grade", GRADES, index=2, key="example_grade")
example_step = st.sidebar.selectbox("Step", STEPS, index=3, key="example_step")
st.sidebar.info(f"GS = {example_grade}-S{example_step}")

# =========================================================
# Main
# =========================================================
st.title(t("title"))
st.caption(t("subtitle"))

col_top1, col_top2, col_top3 = st.columns(3)
with col_top1:
    st.metric("Grades", len(GRADES))
with col_top2:
    st.metric("Steps", len(STEPS))
with col_top3:
    st.metric("GS Patterns", len(GRADES) * len(STEPS))

tab1, tab2, tab3, tab4 = st.tabs([
    t("tab_overview"),
    t("tab_table"),
    t("tab_sim"),
    t("tab_admin"),
])

# =========================================================
# Tab 1: Overview
# =========================================================
with tab1:
    st.subheader(t("overview_heading"))
    st.write(t("overview_text1"))
    st.write(t("overview_text2"))
    st.write(t("grade_axis"))

    st.subheader(t("rule_heading"))
    st.markdown(f"- {t('rule_ap')}")
    st.markdown(f"- {t('rule_pp')}")
    st.markdown(f"- {t('rule_allow')}")
    st.info(t("rule_promo"))

    ref_df = pd.DataFrame({
        t("grade"): GRADES,
        t("position"): [grade_label(g) for g in GRADES],
        t("next_grade"): [NEXT_GRADE[g] if NEXT_GRADE[g] else "-" for g in GRADES],
    })
    st.subheader(t("grade_table"))
    st.dataframe(ref_df, use_container_width=True, hide_index=True)

# =========================================================
# Tab 2: Wage Table
# =========================================================
with tab2:
    st.subheader(t("wage_heading"))
    st.caption(t("wage_caption"))

    edited_df = st.data_editor(
        st.session_state.wage_df,
        use_container_width=True,
        num_rows="fixed",
        hide_index=True,
        column_config={
            "Step": st.column_config.NumberColumn("Step", disabled=True),
            "G6": st.column_config.NumberColumn("G6", format="%.2f"),
            "G5B": st.column_config.NumberColumn("G5B", format="%.2f"),
            "G5A": st.column_config.NumberColumn("G5A", format="%.2f"),
            "G4": st.column_config.NumberColumn("G4", format="%.2f"),
            "G3": st.column_config.NumberColumn("G3", format="%.2f"),
            "G2": st.column_config.NumberColumn("G2", format="%.2f"),
        },
        key="wage_table_editor",
    )
    st.session_state.wage_df = edited_df

    show_formatted = st.checkbox(t("show_formatted"), value=False)
    if show_formatted:
        st.dataframe(display_table_with_formats(st.session_state.wage_df), use_container_width=True, hide_index=True)

    csv_bytes = st.session_state.wage_df.to_csv(index=False).encode("utf-8-sig")
    excel_bytes = make_excel_file(st.session_state.wage_df)

    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            t("download_csv"),
            data=csv_bytes,
            file_name="wage_table.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            t("download_excel"),
            data=excel_bytes,
            file_name="wage_table.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.caption(t("download_note"))

# =========================================================
# Tab 3: Simulation
# =========================================================
with tab3:
    st.subheader(t("sim_heading"))

    c1, c2, c3 = st.columns(3)
    with c1:
        current_grade = st.selectbox(t("current_grade"), GRADES[:-1], index=0)
    with c2:
        current_step = st.selectbox(t("current_step"), STEPS, index=0)
    with c3:
        is_univ = st.checkbox(t("is_univ"), value=False)

    a1, a2, a3 = st.columns(3)
    with a1:
        adjustment_allowance = st.number_input(t("adjust_allowance"), min_value=0.0, value=0.0, step=100.0)
    with a2:
        university_allowance = st.number_input(t("univ_allowance"), min_value=0.0, value=0.0, step=100.0)
    with a3:
        other_allowance = st.number_input(t("other_allowance"), min_value=0.0, value=0.0, step=100.0)

    if st.button(t("simulate"), use_container_width=True):
        result = find_promotion_result(
            st.session_state.wage_df,
            st.session_state.params,
            current_grade,
            int(current_step),
        )

        if result is None:
            st.warning(t("no_next_grade"))
        else:
            total_allowance = adjustment_allowance + other_allowance
            if is_univ:
                total_allowance += university_allowance

            final_salary = result["target_salary"] + total_allowance

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(t("gs_before"), f"{current_grade}-S{current_step}")
            with m2:
                st.metric(t("gs_after"), f"{result['target_grade']}-S{result['target_step']}")
            with m3:
                st.metric(t("final_salary"), format_money(final_salary))

            sim_df = pd.DataFrame([
                {
                    t("gs_before"): f"{current_grade}-S{current_step}",
                    t("current_salary"): result["current_salary"],
                    t("min_required"): result["minimum_required"],
                    t("promoted_grade"): result["target_grade"],
                    t("promoted_step"): result["target_step"],
                    t("promoted_salary"): result["target_salary"],
                    t("adjust_allowance"): adjustment_allowance,
                    t("univ_allowance"): university_allowance if is_univ else 0.0,
                    t("other_allowance"): other_allowance,
                    t("final_salary"): final_salary,
                }
            ])

            st.dataframe(sim_df, use_container_width=True, hide_index=True)

            st.success(
                f"{current_grade}-S{current_step} → {result['target_grade']}-S{result['target_step']} / "
                f"{t('final_salary')}: {format_money(final_salary)}"
            )

# =========================================================
# Tab 4: Admin
# =========================================================
with tab4:
    st.subheader(t("admin_heading"))
    st.write(t("admin_text"))
    st.warning(t("warning_rebuild"))

    input_cols = st.columns(len(GRADES))
    tmp_params = {}

    for idx, g in enumerate(GRADES):
        with input_cols[idx]:
            st.markdown(f"**{g}**  ")
            st.caption(grade_label(g))
            base = st.number_input(
                f"{g} - {t('base_salary')}",
                min_value=0.0,
                value=float(st.session_state.params[g]["base"]),
                step=100.0,
                key=f"base_{g}",
            )
            ap = st.number_input(
                f"{g} - {t('ap')}",
                min_value=0.0,
                value=float(st.session_state.params[g]["ap"]),
                step=50.0,
                key=f"ap_{g}",
            )
            pp = st.number_input(
                f"{g} - {t('pp')}",
                min_value=0.0,
                value=float(st.session_state.params[g]["pp"]),
                step=50.0,
                key=f"pp_{g}",
            )
            tmp_params[g] = {"base": base, "ap": ap, "pp": pp}

    b1, b2 = st.columns(2)
    with b1:
        if st.button(t("rebuild"), use_container_width=True):
            st.session_state.params = tmp_params
            st.session_state.wage_df = build_wage_table(st.session_state.params)
            st.success(t("success_rebuild"))
    with b2:
        if st.button(t("reset"), use_container_width=True):
            st.session_state.params = {k: v.copy() for k, v in DEFAULT_PARAMS.items()}
            st.session_state.wage_df = build_wage_table(st.session_state.params)
            st.success(t("success_reset"))

st.markdown("---")
st.caption("Created for bilingual wage table explanation, editing, and promotion simulation in Streamlit.")
