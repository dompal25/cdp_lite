import streamlit as st
import duckdb, pandas as pd

from src.cdp.db import get_con
con = get_con()

st.title("CDP Sandbox")
st.caption("Segments, features, and quick insights")

tab1, tab2, tab3 = st.tabs(["Overview", "Segments", "User lookup"])

with tab1:
    events = con.execute("SELECT COUNT(*) FROM events").fetchone()[0] if con.execute("SELECT * FROM information_schema.tables WHERE table_name='events'").fetchall() else 0
    feats = con.execute("SELECT COUNT(*) FROM features_daily").fetchone()[0] if con.execute("SELECT * FROM information_schema.tables WHERE table_name='features_daily'").fetchall() else 0
    st.metric("Events", f"{events:,}")
    st.metric("Users with features", f"{feats:,}")

with tab2:
    seg = st.selectbox("Segment", ["active_high_value","likely_to_buy_30d"])
    limit = st.slider("Limit", 10, 500, 50)
    if st.button("Preview"):
        if seg == "active_high_value":
            df = con.execute("""
                SELECT user_id FROM features_daily
                WHERE L30D_purchases >= 2 AND clv_simple >= 150
                LIMIT ?
            """, [limit]).fetchdf()
            st.dataframe(df)
        else:
            st.write("Use API endpoint /v1/segments/likely_to_buy_30d or train model first.")
            try:
                import joblib
                model = joblib.load("data/artifacts/propensity_30d.joblib")
                feats = con.execute("""
                    SELECT user_id, L30D_events, L30D_sessions, L30D_add_to_cart, L30D_purchases, coalesce(clv_simple,0) as clv_simple
                    FROM features_daily LIMIT ?
                """, [limit]).fetchdf()
                probs = model.predict_proba(feats.drop(columns=["user_id"]))[:,1]
                feats["score"] = probs
                st.dataframe(feats.sort_values("score", ascending=False))
            except Exception as e:
                st.warning(f"Model not ready: {e}")

with tab3:
    uid = st.text_input("User ID", "user_00010")
    if st.button("Lookup"):
        df1 = con.execute("SELECT * FROM profiles WHERE user_id = ?", [uid]).fetchdf()
        df2 = con.execute("SELECT * FROM features_daily WHERE user_id = ?", [uid]).fetchdf()
        st.subheader("Profile")
        st.dataframe(df1 if len(df1) else pd.DataFrame())
        st.subheader("Features")
        st.dataframe(df2 if len(df2) else pd.DataFrame())
