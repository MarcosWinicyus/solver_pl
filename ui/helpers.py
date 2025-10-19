import streamlit as st

def _store_problem(c, A, b, int_vars=None):
    st.session_state["problem"] = {"c": c, "A": A, "b": b, "int_vars": int_vars or []}


def _load_problem(default_nvars=2, default_ncons=2):
    p = st.session_state.get("problem")
    if not p:
        return [], [], [], default_nvars, default_ncons
    return p["c"], p["A"], p["b"], len(p["c"]), len(p["A"])

number_emojis = {
        1: "1️⃣",
        2: "2️⃣",
        3: "3️⃣",
        4: "4️⃣",
        5: "5️⃣",
        6: "6️⃣",
        7: "7️⃣",
        8: "8️⃣",
        9: "9️⃣",
        10: "🔟"
    }