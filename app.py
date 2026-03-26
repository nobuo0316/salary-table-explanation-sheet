import streamlit as st
import pandas as pd
from io import BytesIO
from typing import Dict, List, Optional

# Optional Excel engines
try:
    import openpyxl  # noqa: F401
    OPENPYXL_AVAILABLE = True
except Exception:
    OPENPYXL_AVAILABLE = False

try:
    import xlsxwriter  # noqa: F401
    XLSXWRITER_AVAILABLE = True
except Exception:
    XLSXWRITER_AVAILABLE = False

st.set_page_config(
    page_title="Wage Table Guide / 賃金テーブル説明ページ",
    page_icon="📘",
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
        "subtitle": "初心者向けの図解、説明、テーブル編集、昇格シミュレーションを1つにまとめた完成版です。",
        "tab_overview": "制度説明",
        "tab_diagram": "図で理解",
        "tab_table": "賃金テーブル",
        "tab_sim": "昇格シミュレーション",
        "tab_admin": "管理設定",
        "sidebar_lang": "表示言語",
        "sidebar_currency": "通貨記号",
        "sidebar_decimals": "小数表示",
        "sidebar_example": "GS例",
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
        "diagram_heading1": "① Grade と Step の関係",
        "diagram_heading2": "② AP と PP の考え方",
        "diagram_heading3": "③ 昇格時の移動イメージ",
        "diagram_help1": "下の図では、横方向が Grade、縦方向が Step です。社員は必ずどこか1つの GS に所属します。",
        "diagram_help2": "AP は同じグレード内での毎年の昇給、PP は次グレードへ上がるときの追加昇給です。",
        "diagram_help3": "昇格時は、最低必要額を満たす次グレードの最も近い Step に移動します。",
        "simple_example": "初心者向けの例",
        "simple_example_text": "例：G5A-S4 の社員が昇格する場合、まず『現在給与 + AP + PP』で最低必要額を出し、その金額以上になる G4 の最初の Step を探します。",
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
        "excel_unavailable": "この環境ではExcel出力が使えません。CSVを使うか、requirements.txt に openpyxl または xlsxwriter を追加してください。",
        "table_view_mode": "表示モード",
        "table_mode_raw": "数値のみ",
        "table_mode_with_label": "GSラベル付き",
        "promotion_flow": "昇格の流れ",
        "step_search_result": "該当Stepの探索結果",
        "legend": "凡例",
        "csv_import_heading": "設定CSVインポート",
        "csv_import_text": "この画面の設定値（Step1基準額、AP、PP）をCSVで一括更新できます。反映後、賃金テーブルも自動で再生成されます。",
        "csv_upload": "設定CSVファイルをアップロード",
        "csv_apply": "CSVを設定に反映",
        "csv_template_download": "設定CSVテンプレートをダウンロード",
        "csv_import_success": "CSVから設定値を更新し、賃金テーブルを再生成しました。",
        "csv_import_error": "CSVの形式が正しくありません。Grade, Base, AP, PP 列が必要で、G6, G5B, G5A, G4, G3, G2 の6行が必要です。",
        "csv_import_empty": "CSVファイルを選択してください。",
        "csv_preview_heading": "CSVプレビュー",
    },
    "English": {
        "title": "Wage Table Management & Explanation Page",
        "subtitle": "A complete beginner-friendly Streamlit app with visual explanation, table editing, and promotion simulation.",
        "tab_overview": "Overview",
        "tab_diagram": "Visual Guide",
        "tab_table": "Wage Table",
        "tab_sim": "Promotion Simulation",
        "tab_admin": "Admin Settings",
        "sidebar_lang": "Language",
        "sidebar_currency": "Currency symbol",
        "sidebar_decimals": "Decimal places",
        "sidebar_example": "GS Example",
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
        "diagram_heading1": "1) Relationship between Grade and Step",
        "diagram_heading2": "2) How AP and PP work",
        "diagram_heading3": "3) Promotion movement image",
        "diagram_help1": "In the chart below, Grade runs horizontally and Step runs vertically. Every employee always belongs to one GS position.",
        "diagram_help2": "AP means annual raise within the same grade. PP means the additional raise given at promotion to the next grade.",
        "diagram_help3": "At promotion, the employee moves to the closest step in the next grade that meets the minimum required amount.",
        "simple_example": "Simple Example",
        "simple_example_text": "Example: when an employee at G5A-S4 is promoted, first calculate Current Salary + AP + PP, then find the first Step in G4 that is equal to or higher than that threshold.",
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
        "excel_unavailable": "Excel export is unavailable in this environment. Please use CSV export or add openpyxl / xlsxwriter to requirements.txt.",
        "table_view_mode": "View Mode",
        "table_mode_raw": "Raw Numbers",
        "table_mode_with_label": "With GS Labels",
        "promotion_flow": "Promotion Flow",
        "step_search_result": "Step Search Result",
        "legend": "Legend",
        "csv_import_heading": "Settings CSV Import",
        "csv_import_text": "You can bulk update the settings shown on this screen (Base at Step 1, AP, and PP) by CSV. After import, the wage table will be regenerated automatically.",
        "csv_upload": "Upload settings CSV file",
        "csv_apply": "Apply CSV to settings",
        "csv_template_download": "Download settings CSV template",
        "csv_import_success": "The settings were updated from CSV and the wage table was regenerated.",
        "csv_import_error": "The CSV format is invalid. The file must contain Grade, Base, AP, and PP columns, with 6 rows for G6, G5B, G5A, G4, G3, and G2.",
        "csv_import_empty": "Please choose a CSV file first.",
        "csv_preview_heading": "CSV Preview",
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


def make_excel_file(df: pd.DataFrame) -> Optional[bytes]:
    output = BytesIO()
    try:
        if OPENPYXL_AVAILABLE:
            engine = "openpyxl"
        elif XLSXWRITER_AVAILABLE:
            engine = "xlsxwriter"
        else:
            return None
        with pd.ExcelWriter(output, engine=engine) as writer:
            df.to_excel(writer, index=False, sheet_name="WageTable")
        output.seek(0)
        return output.getvalue()
    except Exception:
        return None


def build_settings_csv_template() -> pd.DataFrame:
    rows = []
    for g in GRADES:
        rows.append({
            "Grade": g,
            "Base": float(DEFAULT_PARAMS[g]["base"]),
            "AP": float(DEFAULT_PARAMS[g]["ap"]),
            "PP": float(DEFAULT_PARAMS[g]["pp"]),
        })
    return pd.DataFrame(rows)


def validate_imported_settings_csv(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    required_cols = ["Grade", "Base", "AP", "PP"]

    # Check columns
    if list(df.columns) != required_cols:
        raise ValueError(f"Columns must be exactly: {required_cols}")

    validated = df.copy()

    # Check row count
    if len(validated) != len(GRADES):
        raise ValueError(f"Row count must be {len(GRADES)} (G6→G2)")

    # Check grade order
    grade_list = validated["Grade"].tolist()
    if grade_list != GRADES:
        raise ValueError(f"Grade order must be: {GRADES}")

    new_params: Dict[str, Dict[str, float]] = {}

    for i, row in validated.iterrows():
        try:
            grade = row["Grade"]
            base = float(row["Base"])
            ap = float(row["AP"])
            pp = float(row["PP"])
        except Exception:
            raise ValueError(f"Row {i+1}: Base/AP/PP must be numeric")

        new_params[grade] = {"base": base, "ap": ap, "pp": pp}

    return new_params


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
        out[g] = out[g].apply(format_money)
    return out


def display_table_with_gs(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        step = int(row["Step"])
        record = {"Step": step}
        for g in GRADES:
            record[g] = f"{g}-S{step} / {format_money(float(row[g]))}"
        rows.append(record)
    return pd.DataFrame(rows)


def grade_step_grid(selected_grade: str = "G5A", selected_step: int = 4) -> str:
    lines = []
    lines.append("digraph G {")
    lines.append('rankdir=LR;')
    lines.append('node [shape=box, style="rounded,filled", fillcolor="white"];')
    for g in GRADES:
        lines.append(f'subgraph cluster_{g} {{ label="{g}"; style="rounded";')
        for s in [1, 2, 3, 4, 5]:
            node_name = f"{g}_{s}"
            label = f"{g}-S{s}"
            if g == selected_grade and s == selected_step:
                lines.append(f'{node_name} [label="{label}", fillcolor="lightblue"];')
            else:
                lines.append(f'{node_name} [label="{label}"];')
        lines.append("}")
    lines.append("}")
    return "\n".join(lines)


def raise_diagram() -> str:
    return """
    digraph G {
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="white"];
      A [label="Current Salary\n現在給与"];
      B [label="+ AP\n毎年昇給"];
      C [label="+ PP\n昇格昇給"];
      D [label="Minimum Required\n最低必要額"];
      E [label="Find first Step in next Grade\n次グレードで該当Stepを探す", fillcolor="lightyellow"];
      A -> B -> C -> D -> E;
    }
    """


def promotion_diagram(current_grade: str, current_step: int, next_grade: str, target_step: int) -> str:
    return f"""
    digraph G {{
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="white"];
      A [label="{current_grade}-S{current_step}\nCurrent GS", fillcolor="lightblue"];
      B [label="AP + PP\nadded"];
      C [label="Search next grade\n{next_grade}"];
      D [label="{next_grade}-S{target_step}\nNew GS", fillcolor="lightgreen"];
      A -> B -> C -> D;
    }}
    """


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
    "Language / 言語",
    ["日本語", "English"],
    index=0 if st.session_state.lang == "日本語" else 1,
)

st.session_state.currency_symbol = st.sidebar.text_input(
    t("sidebar_currency"),
    value=st.session_state.currency_symbol,
)
st.session_state.decimals = st.sidebar.selectbox(
    t("sidebar_decimals"),
    [0, 1, 2],
    index=[0, 1, 2].index(st.session_state.decimals),
)

st.sidebar.caption(f"{t('currency_preview')}: {format_money(12345.67)}")
st.sidebar.markdown("---")
st.sidebar.write(t("sidebar_example"))
example_grade = st.sidebar.selectbox("Grade", GRADES, index=2, key="example_grade")
example_step = st.sidebar.selectbox("Step", STEPS, index=3, key="example_step")
st.sidebar.info(f"GS = {example_grade}-S{example_step}")

# =========================================================
# Main header
# =========================================================
st.title(t("title"))
st.caption(t("subtitle"))

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Grades", len(GRADES))
with m2:
    st.metric("Steps", len(STEPS))
with m3:
    st.metric("GS Patterns", len(GRADES) * len(STEPS))

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    t("tab_overview"),
    t("tab_diagram"),
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
# Tab 2: Diagram
# =========================================================
with tab2:
    st.subheader(t("diagram_heading1"))
    st.write(t("diagram_help1"))
    st.graphviz_chart(grade_step_grid(example_grade, min(example_step, 5)))

    st.subheader(t("diagram_heading2"))
    st.write(t("diagram_help2"))
    st.graphviz_chart(raise_diagram())

    st.subheader(t("diagram_heading3"))
    st.write(t("diagram_help3"))

    sample_result = find_promotion_result(
        st.session_state.wage_df,
        st.session_state.params,
        "G5A",
        4,
    )
    if sample_result:
        st.graphviz_chart(
            promotion_diagram(
                "G5A",
                4,
                sample_result["target_grade"],
                int(sample_result["target_step"]),
            )
        )

    st.info(t("simple_example_text"))

# =========================================================
# Tab 3: Wage Table
# =========================================================
with tab3:
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

    view_mode = st.radio(
        t("table_view_mode"),
        [t("table_mode_raw"), t("table_mode_with_label")],
        horizontal=True,
    )

    if view_mode == t("table_mode_raw"):
        st.dataframe(display_table_with_formats(st.session_state.wage_df), use_container_width=True, hide_index=True)
    else:
        st.dataframe(display_table_with_gs(st.session_state.wage_df), use_container_width=True, hide_index=True)

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
        if excel_bytes is not None:
            st.download_button(
                t("download_excel"),
                data=excel_bytes,
                file_name="wage_table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.info(t("excel_unavailable"))

    st.caption(t("download_note"))

# =========================================================
# Tab 4: Simulation
# =========================================================
with tab4:
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

            r1, r2, r3 = st.columns(3)
            with r1:
                st.metric(t("gs_before"), f"{current_grade}-S{current_step}")
            with r2:
                st.metric(t("gs_after"), f"{result['target_grade']}-S{result['target_step']}")
            with r3:
                st.metric(t("final_salary"), format_money(final_salary))

            st.subheader(t("promotion_flow"))
            st.graphviz_chart(
                promotion_diagram(
                    current_grade,
                    int(current_step),
                    result["target_grade"],
                    int(result["target_step"]),
                )
            )

            search_df = st.session_state.wage_df[["Step", result["target_grade"]]].copy()
            search_df["Eligible"] = search_df[result["target_grade"]] >= result["minimum_required"]
            st.subheader(t("step_search_result"))
            st.dataframe(search_df, use_container_width=True, hide_index=True)

            sim_df = pd.DataFrame([
                {
                    t("gs_before"): f"{current_grade}-S{current_step}",
                    t("current_salary"): format_money(result["current_salary"]),
                    t("min_required"): format_money(result["minimum_required"]),
                    t("promoted_grade"): result["target_grade"],
                    t("promoted_step"): int(result["target_step"]),
                    t("promoted_salary"): format_money(result["target_salary"]),
                    t("adjust_allowance"): format_money(adjustment_allowance),
                    t("univ_allowance"): format_money(university_allowance if is_univ else 0.0),
                    t("other_allowance"): format_money(other_allowance),
                    t("final_salary"): format_money(final_salary),
                }
            ])
            st.dataframe(sim_df, use_container_width=True, hide_index=True)

# =========================================================
# Tab 5: Admin
# =========================================================
with tab5:
    st.subheader(t("admin_heading"))
    st.write(t("admin_text"))
    st.warning(t("warning_rebuild"))

    input_cols = st.columns(len(GRADES))
    tmp_params = {}

    for idx, g in enumerate(GRADES):
        with input_cols[idx]:
            st.markdown(f"**{g}**")
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
    st.subheader(t("csv_import_heading"))
    st.write(t("csv_import_text"))

    template_df = build_settings_csv_template()
    template_csv = template_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        t("csv_template_download"),
        data=template_csv,
        file_name="wage_table_settings_template.csv",
        mime="text/csv",
        use_container_width=False,
    )

    uploaded_csv = st.file_uploader(
        t("csv_upload"),
        type=["csv"],
        key="settings_csv_upload",
    )

    if uploaded_csv is not None:
        try:
            uploaded_csv.seek(0)
            preview_df = pd.read_csv(uploaded_csv)
            st.markdown(f"**{t('csv_preview_heading')}**")
            st.dataframe(preview_df, use_container_width=True, hide_index=True)
        except Exception:
            st.error(t("csv_import_error"))

    if st.button(t("csv_apply"), use_container_width=True):
        if uploaded_csv is None:
            st.warning(t("csv_import_empty"))
        else:
            try:
                uploaded_csv.seek(0)
                imported_df = pd.read_csv(uploaded_csv)

                new_params = validate_imported_settings_csv(imported_df)

                # Apply
                st.session_state.params = new_params
                st.session_state.wage_df = build_wage_table(new_params)

                st.success(t("csv_import_success"))

                # Force UI refresh (important)
                st.rerun()

            except Exception as e:
st.error(f"{t('csv_import_error')}\n\nDetail: {str(e)}")

st.markdown("---")
st.caption("Created for bilingual wage table explanation, visual guidance, editing, promotion simulation, and CSV import in Streamlit.")
