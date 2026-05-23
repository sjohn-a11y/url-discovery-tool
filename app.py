import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Harvester QA Tool", layout="wide")

st.title("🔷 Harvester QA Tool")

# ✅ Session
if "index" not in st.session_state:
    st.session_state.index = 0

if "df" not in st.session_state:
    st.session_state.df = None

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file)

    df = st.session_state.df

    entity_list = df["Entity ID"].tolist()

    # ✅ All processed
    if st.session_state.index >= len(entity_list):
        st.success("✅ All entities completed!")

        output = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download Output File",
            output,
            "processed_output.csv",
            "text/csv"
        )
        st.stop()

    # ✅ Current entity
    entity_id = entity_list[st.session_state.index]
    row = df[df["Entity ID"] == entity_id].iloc[0]

    st.subheader(f"📌 Entity ID: {entity_id}")

    # ✅ Extract Entity Name from Payload
    entity_name = ""
    try:
        payload = json.loads(row["Payload"])
        entity_name = payload.get("name", "")
    except:
        entity_name = "N/A"

    # ✅ TOP DASHBOARD
    st.markdown("### 🧾 Entity Details")

    c1, c2, c3 = st.columns(3)

    c1.write(f"**Entity Name:** {entity_name}")
    c1.write(f"**Client Name:** {row['Client Name']}")

    c2.write(f"**Industry:** {row['Industry ID']}")
    c2.write(f"**Sync Partner:** {row['Sync Partner']}")

    c3.write(f"**Client Products:** {row['Client Products']}")
    c3.write(f"**Entity Type:** {row['Entity Type']}")

    # ✅ TRANSPOSE DATA
    st.markdown("---")
    st.markdown("### 🔍 Source Details")

    cols = df.columns.tolist()

    start = cols.index("Healthgrades")
    end = cols.index("AppleMaps") + 1

    sources = cols[start:end]

    output_data = []

    for col in sources:
        val = str(row[col]).strip()

        # ✅ skip blanks
        if val != "" and val.lower() != "nan":

            # ✅ Action logic
            if "404" in val or "No URLs" in val:
                action = "Add URL"
            elif "500" in val:
                action = "Retry"
            elif "Different URL already exists" in val:
                action = "Verify Duplicate"
            else:
                action = ""

            output_data.append({
                "Source": col,
                "Value": val,
                "Action Required": action
            })

    if output_data:
        out_df = pd.DataFrame(output_data)

        def highlight(row):
            return ["background-color: #ffe6e6" if row["Action Required"] else "" for _ in row]

        st.dataframe(out_df.style.apply(highlight, axis=1), use_container_width=True)
    else:
        st.info("✅ No data available")

    # ✅ PROGRESS
    progress = (st.session_state.index + 1) / len(entity_list)
    st.progress(progress)

    st.write(f"Processing {st.session_state.index + 1} / {len(entity_list)}")

    # ✅ COMPLETED BUTTON
    if st.button("✅ Completed & Next"):

        st.session_state.df.loc[
            st.session_state.df["Entity ID"] == entity_id,
            "Status"
        ] = "Completed"

        st.session_state.index += 1

        st.rerun()
