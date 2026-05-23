import streamlit as st
import pandas as pd

st.set_page_config(page_title="Harvester QA Tool", layout="wide")

st.title("🔷 Harvester QA Tool")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    st.success("✅ File uploaded successfully")

    # ✅ Step 1: Get Assignee
    assignee = st.text_input("👤 Enter Your Name")

    if assignee:

        my_data = df[df['Assignee'] == assignee]

        if my_data.empty:
            st.warning("⚠️ No data found for this assignee")
            st.stop()

        st.info(f"✅ {len(my_data)} entities assigned to you")

        # ✅ Step 2: Select Entity
        entity_list = my_data['Entity ID'].unique()
        entity_id = st.selectbox("📌 Select Entity ID", entity_list)

        if st.button("⚙ Process"):

            row = my_data[my_data['Entity ID'] == entity_id].iloc[0]

            # ✅ Identify source columns dynamically
            cols = df.columns.tolist()

            start = cols.index("Healthgrades")
            end = cols.index("Healthline") + 1

            source_cols = cols[start:end]

            output = []

            for col in source_cols:
                val = str(row[col])

                if val and val.lower() != "nan":

                    if "404" in val or "No URLs" in val:
                        action = "Add URL"
                    elif "500" in val:
                        action = "Retry"
                    elif "Different URL already exists" in val:
                        action = "Verify Duplicate"
                    else:
                        action = ""

                    output.append({
                        "Entity ID": entity_id,
                        "Source": col,
                        "Value": val,
                        "Action Required": action
                    })

            result_df = pd.DataFrame(output)

            st.subheader("📊 Output")

            st.dataframe(result_df, use_container_width=True)

            # ✅ Download button
            csv = result_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇ Download Report",
                csv,
                f"{entity_id}_report.csv",
                "text/csv"
            )