import streamlit as st
import pandas as pd
import math
from typing import Dict, List

st.set_page_config(page_title="Wage Table / 賃金テーブル", layout="wide")

# -----------------------------
# Language
# -----------------------------
lang = st.sidebar.radio("Language / 言語", ["English", "日本語"], index=1)

TEXT = {
    "English": {
        "title": "Wage Table Explanation & Editor",
        "subtitle": "Bilingual Streamlit page for explaining and maintaining the wage table.",
        "overview": "Overview",
        "rules": "Rules",
        "table_editor": "Wage Table Editor",
        "settings": "Settings",
        "simulation": "Promotion / Raise Simulation",
        "download": "Download",
        "grade": "Grade",
        "step": "Step",
        "salary": "Salary",
        "employee_level": "Employee Level",
        "grades_help": "Grades are shown on the horizontal axis (G6 to G2). Steps are shown on the vertical axis (1 to 49).",
        "gs_help": "Each employee has a Grade and a Step, abbreviated as GS. Example: G5A Step 4 = G5A-S4.",
        "ap_help": "AP (Annual Pay Raise): yearly salary increase within the same grade.",
        "pp_help": "PP (Pay by Promotion): additional increase when promoted to the next grade.",
        "allowance_help": "Main allowances for now: Adjustment Allowance and University Graduate Allowance. More can be added later.",
        "promotion_rule_title": "Promotion rule",
        "promotion_rule_body": "When promotion happens, the target salary must not be lower than current salary + current grade AP + current grade PP. The employee moves to the closest higher step in the next grade that meets or exceeds that amount.",
        "base_salary": "Base salary for Step 1",
        "annual_raise": "AP per step",
        "promotion_pay": "PP on promotion",
        "next_grade": "Next grade",
        "generate_default": "Generate / Refresh default table",
        "editable_table": "Editable wage table",
        "editable_help": "You can directly edit salary cells below. Changes are kept during the session.",
        "current_grade": "Current grade",
        "current_step": "Current step",
        "promotion_sim": "Simulate promotion",
        "promotion_result": "Result",
        "target_grade": "Promoted grade",
        "target_step": "Promoted step",
        "target_salary": "Target salary",
        "threshold_salary": "Minimum required salary",
        "allowances": "Allowances",
        "adjustment_allowance": "Adjustment allowance",
        "university_allowance": "University graduate allowance",
        "is_university_grad": "University graduate",
        "download_csv": "Download CSV",
        "download_excel_note": "You can also export this table to Excel later if needed.",
        "description_page": "Explanation",
        "grade_labels": {
            "G6": "Staff",
            "G5B": "Senior Staff",
            "G5A": "Upper Senior Staff",
            "G4": "Supervisor",
            "G3": "Manager",
            "G2": "Deputy General Manager",
        },
    },
    "日本語": {
        "title": "賃金テーブル説明・編集ページ",
        "subtitle": "賃金テーブルの説明と編集を行うための二言語対応Streamlitページです。",
        "overview": "概要",
        "rules": "ルール",
        "table_editor": "賃金テーブル編集",
        "settings": "設定",
        "simulation": "昇格・昇給シミュレーション",
        "download": "ダウンロード",
        "grade": "グレード",
        "step": "ステップ",
        "salary": "給与",
        "employee_level": "役職",
        "grades_help": "グレードは横軸（G6からG2）、ステップは縦軸（1から49）です。",
        "gs_help": "各社員には必ずGradeとStepがあり、これをGSと略します。例：G5AのStep 4 = G5A-S4。",
        "ap_help": "AP（Annual Pay Raise）：同一グレード内で毎年行う昇給額。",
        "pp_help": "PP（Pay by Promotion）：昇格時に加算される昇給額。",
        "allowance_help": "現時点の主な手当は、調整手当と大卒手当です。今後追加可能です。",
        "promotion_rule_title": "昇格ルール",
        "promotion_rule_body": "昇格時、次の給与は『現在給与 + 現グレードのAP + 現グレードのPP』を下回りません。その金額以上となる次グレード内で最も近いステップへ移動します。",
        "base_salary": "Step 1の基準給与",
        "annual_raise": "AP（1ステップ当たり）",
        "promotion_pay": "PP（昇格時）",
        "next_grade": "次グレード",
        "generate_default": "初期テーブルを作成 / 更新",
        "editable_table": "編集可能な賃金テーブル",
        "editable_help": "下のセルを直接編集できます。変更内容はこのセッション中保持されます。",
        "current_grade": "現在グレード",
        "current_step": "現在ステップ",
        "promotion_sim": "昇格シミュレーション",
        "promotion_result": "結果",
        "target_grade": "昇格後グレード",
        "target_step": "昇格後ステップ",
        "target_salary": "昇格後給与",
        "threshold_salary": "必要最低給与",
        "allowances": "手当",
        "adjustment_allowance": "調整手当",
        "university_allowance": "大卒手当",
        "is_university_grad": "大卒対象",
        "download_csv": "CSVダウンロード",
        "download_excel_note": "必要であれば後でExcel出力にも拡張できます。",
        "description_page": "説明",
        "grade_labels": {
            "G6": "平社員",
            "G5B": "シニアスタッフ",
            "G5A": "上位シニアスタッフ",
            "G4": "スーパーバイザー",
            "G3": "課長",
            "G2": "次長",
        },
    },
}

t = TEXT[lang]

GRADES: List[str] = ["G6", "G5B", "G5A", "G4", "G3", "G2"]
NEXT_GRADE: Dict[str, str] = {
    "G6": "G5B",
    "G5B": "G5A",
    "G5A": "G4",
    "G4": "G3",
    "G3": "G2",
    "G2": "",
}
STEPS = list(range(1, 50))

DEFAULT_PARAMS = {
    "G6": {"base": 18000, "ap": 500, "pp": 1500},
    "G5B": {"base": 22000, "ap": 600, "pp": 1800},
    "G5A": {"base": 26000, "ap": 700, "pp": 2200},
    "G4": {"base": 32000, "ap": 800, "pp": 2800},
    "G3": {"base": 40000, "ap": 1000, "pp": 3500},
    "G2": {"base": 52000, "ap": 1200, "pp": 0},
}


def build_wage_table(params: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    data = {}
    for grade in GRADES:
        base = params[grade]["base"]
        ap = params[grade]["ap"]
        data[grade] = [base + (s - 1) * ap for s in STEPS]
    df = pd.DataFrame(data, index=STEPS)
    df.index.name = "Step"
    return df


def find_promoted_step(
    current_grade: str,
    current_step: int,
    wage_df: pd.DataFrame,
    params: Dict[str, Dict[str, float]],
):
    next_grade = NEXT_GRADE.get(current_grade, "")
    if not next_grade:
        return None

    current_salary = float(wage_df.loc[current_step, current_grade])
    minimum_required = current_salary + params[current_grade]["ap"] + params[current_grade]["pp"]

    next_grade_series = wage_df[next_grade]
    eligible = next_grade_series[next_grade_series >= minimum_required]

    if eligible.empty:
        target_step = int(next_grade_series.index.max())
        target_salary = float(next_grade_series.iloc[-1])
    else:
        target_step = int(eligible.index[0])
        target_salary = float(eligible.iloc[0])

    return {
        "current_salary": current_salary,
        "minimum_required": minimum_required,
        "target_grade": next_grade,
        "target_step": target_step,
        "target_salary": target_salary,
    }


if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

if "wage_df" not in st.session_state:
    st.session_state.wage_df = build_wage_table(st.session_state.params)

st.title(t["title"])
st.caption(t["subtitle"])

tab1, tab2, tab3 = st.tabs([t["description_page"], t["table_editor"], t["simulation"]])

with tab1:
    st.subheader(t["overview"])
    st.write(f"- {t['grades_help']}")
    st.write(f"- {t['gs_help']}")

    overview_rows = []
    for g in GRADES:
        overview_rows.append({
            t["grade"]: g,
            t["employee_level"]: t["grade_labels"][g],
            t["next_grade"]: NEXT_GRADE[g] if NEXT_GRADE[g] else "-",
        })
    st.dataframe(pd.DataFrame(overview_rows), use_container_width=True)

    st.subheader(t["rules"])
    st.write(f"- {t['ap_help']}")
    st.write(f"- {t['pp_help']}")
    st.write(f"- {t['allowance_help']}")

    st.info(f"**{t['promotion_rule_title']}**\n\n{t['promotion_rule_body']}")

with tab2:
    st.subheader(t["settings"])

    cols = st.columns(len(GRADES))
    new_params = {}
    for i, grade in enumerate(GRADES):
        with cols[i]:
            st.markdown(f"**{grade} / {t['grade_labels'][grade]}**")
            base = st.number_input(
                f"{grade} - {t['base_salary']}",
                min_value=0.0,
                value=float(st.session_state.params[grade]["base"]),
                step=100.0,
                key=f"base_{grade}",
            )
            ap = st.number_input(
                f"{grade} - {t['annual_raise']}",
                min_value=0.0,
                value=float(st.session_state.params[grade]["ap"]),
                step=50.0,
                key=f"ap_{grade}",
            )
            pp = st.number_input(
                f"{grade} - {t['promotion_pay']}",
                min_value=0.0,
                value=float(st.session_state.params[grade]["pp"]),
                step=50.0,
                key=f"pp_{grade}",
            )
            new_params[grade] = {"base": base, "ap": ap, "pp": pp}

    if st.button(t["generate_default"]):
        st.session_state.params = new_params
        st.session_state.wage_df = build_wage_table(new_params)

    st.subheader(t["editable_table"])
    st.caption(t["editable_help"])

    edited_df = st.data_editor(
        st.session_state.wage_df,
        use_container_width=True,
        num_rows="fixed",
        key="wage_editor",
    )
    st.session_state.wage_df = edited_df

    csv_data = edited_df.to_csv().encode("utf-8-sig")
    st.download_button(
        label=t["download_csv"],
        data=csv_data,
        file_name="wage_table.csv",
        mime="text/csv",
    )
    st.caption(t["download_excel_note"])

with tab3:
    st.subheader(t["simulation"])

    c1, c2, c3 = st.columns(3)
    with c1:
        current_grade = st.selectbox(t["current_grade"], GRADES[:-1], index=0)
    with c2:
        current_step = st.selectbox(t["current_step"], STEPS, index=0)
    with c3:
        university_grad = st.checkbox(t["is_university_grad"], value=False)

    allow1, allow2 = st.columns(2)
    with allow1:
        adjustment_allowance = st.number_input(t["adjustment_allowance"], min_value=0.0, value=0.0, step=100.0)
    with allow2:
        university_allowance = st.number_input(t["university_allowance"], min_value=0.0, value=0.0, step=100.0)

    if st.button(t["promotion_sim"]):
        result = find_promoted_step(
            current_grade=current_grade,
            current_step=int(current_step),
            wage_df=st.session_state.wage_df,
            params=st.session_state.params,
        )

        if result is None:
            st.warning("No next grade available / 次グレードがありません")
        else:
            total_allowance = adjustment_allowance + (university_allowance if university_grad else 0)
            final_salary = result["target_salary"] + total_allowance

            res_df = pd.DataFrame([
                {
                    t["current_grade"]: current_grade,
                    t["current_step"]: current_step,
                    t["salary"]: result["current_salary"],
                    t["threshold_salary"]: result["minimum_required"],
                    t["target_grade"]: result["target_grade"],
                    t["target_step"]: result["target_step"],
                    t["target_salary"]: result["target_salary"],
                    t["allowances"]: total_allowance,
                    "Final Salary / 最終給与": final_salary,
                }
            ])
            st.subheader(t["promotion_result"])
            st.dataframe(res_df, use_container_width=True)

            st.success(
                f"{current_grade}-S{current_step} → {result['target_grade']}-S{result['target_step']} | "
                f"{t['target_salary']}: {result['target_salary']:,.0f} | "
                f"Final Salary / 最終給与: {final_salary:,.0f}"
            )

st.sidebar.markdown("---")
st.sidebar.markdown("### GS Example / GS例")
example_grade = st.sidebar.selectbox("Grade", GRADES, index=2)
example_step = st.sidebar.selectbox("Step", STEPS, index=3)
st.sidebar.write(f"GS = {example_grade}-S{example_step}")

st.sidebar.markdown("---")
st.sidebar.markdown("### Notes / 備考")
st.sidebar.write("- Default salary figures are placeholders. Replace them with your actual numbers.")
st.sidebar.write("- 初期給与額は仮置きです。実際の数値に置き換えてください。")
