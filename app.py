import streamlit as st
import pandas as pd
import json
import io

st.set_page_config(page_title="URL Discovery Tool", layout="wide")

st.image("logo.png", width=80)
st.title("🔷 URL Discovery Tool")


# ✅ Session states
if "index" not in st.session_state:
    st.session_state.index = 0

if "df" not in st.session_state:
    st.session_state.df = None

if "started" not in st.session_state:
    st.session_state.started = False

if "stop" not in st.session_state:
    st.session_state.stop = False


uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file)

    df = st.session_state.df

    # ✅ START & STOP BUTTONS
    col1, col2 = st.columns(2)

    if col1.button("▶ Start Processing", disabled=st.session_state.started):
        st.session_state.started = True

    if col2.button("🛑 Stop Processing"):
        st.session_state.stop = True
        st.session_state.started = False

    # ✅ STOP + DOWNLOAD
    if st.session_state.get("stop", False):

        st.warning("⚠️ Processing stopped. Download your progress below.")

        buffer = io.BytesIO()
        st.session_state.df.to_excel(buffer, index=False, engine="openpyxl")

        st.download_button(
            "⬇ Download Progress File",
            buffer.getvalue(),
            "partial_output.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.stop()

    # ✅ WAIT BEFORE START
    if not st.session_state.started:
        st.info("👉 Click 'Start Processing' to begin")
        st.stop()

    entity_list = df["Entity ID"].tolist()

    # ✅ All completed
    if st.session_state.index >= len(entity_list):
        st.success("✅ All entities completed!")

        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")

        st.download_button(
            "⬇ Download Output File",
            buffer.getvalue(),
            "processed_output.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.stop()

    # ✅ Current entity
    entity_id = entity_list[st.session_state.index]
    row = df[df["Entity ID"] == entity_id].iloc[0]

    # ✅ Clickable Entity ID
    st.markdown(
        f'<h3>📌 <a href="https://crawler-admin.consumerism.pressganey.com/#/verify-sources/{entity_id}" target="_blank">Entity ID: {entity_id}</a></h3>',
        unsafe_allow_html=True
    )

    # ✅ Extract Entity Name
    entity_name = ""
    try:
        payload = json.loads(row["Payload"])
        entity_name = payload.get("name", "")
    except:
        entity_name = "N/A"

    # ✅ DASHBOARD
    st.markdown("### 🧾 Entity Details")

    c1, c2, c3 = st.columns(3)

    c1.write(f"**Entity Name:** {entity_name}")
    c1.write(f"**Client Name:** {row['Client Name']}")

    c2.write(f"**Industry:** {row['Industry ID']}")
    c2.write(f"**Sync Partner:** {row['Sync Partner']}")

    c3.write(f"**Client Products:** {row['Client Products']}")
    c3.write(f"**Entity Type:** {row['Entity Type']}")

    # ✅ TRANSPOSE
    st.markdown("---")
    st.markdown("### 🔍 Error Details")

    cols = df.columns.tolist()

    start = cols.index("Healthgrades")
    end = cols.index("AppleMaps") + 1

    sources = cols[start:end]

    output_data = []

    for col in sources:
        val = str(row[col]).strip()

        if val != "" and val.lower() != "nan":

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

    # ✅ ACTION BUTTONS (Completed + Pending)
    c1, c2 = st.columns(2)

    # ✅ Completed
    if c1.button("✅ Completed & Next"):

        st.session_state.df.loc[
            st.session_state.df["Entity ID"] == entity_id,
            "Status"
        ] = "Completed"

        st.session_state.index += 1
        st.rerun()

    # ✅ 🔥 NEW Pending Button
    if c2.button("⏳ Mark as Pending & Next"):

        st.session_state.df.loc[
            st.session_state.df["Entity ID"] == entity_id,
            "Status"
        ] = "Pending"

        st.session_state.index += 1
        st.rerun()
