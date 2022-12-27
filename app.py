import streamlit as st
import pandas as pd
from glom import glom
import requests
import json
from pandas import json_normalize 
import io

###################################
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode

###################################

from functionforDownloadButtons import download_button

###################################


def _max_width_():
    max_width_str = f"max-width: 1800px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_icon="✂️", page_title="Remodule")

# st.image("https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/balloon_1f388.png", width=100)

st.title("JSON to CSV Converter")

# st.caption(
#     "PRD : TBC | Streamlit Ag-Grid from Pablo Fonseca: https://pypi.org/project/streamlit-aggrid/"
# )


# ModelType = st.radio(
#     "Choose your model",
#     ["Flair", "DistilBERT (Default)"],
#     help="At present, you can choose between 2 models (Flair or DistilBERT) to embed your text. More to come!",
# )

# with st.expander("ToDo's", expanded=False):
#     st.markdown(
#         """
# -   Add pandas.json_normalize() - https://streamlit.slack.com/archives/D02CQ5Z5GHG/p1633102204005500
# -   **Remove 200 MB limit and test with larger CSVs**. Currently, the content is embedded in base64 format, so we may end up with a large HTML file for the browser to render
# -   **Add an encoding selector** (to cater for a wider array of encoding types)
# -   **Expand accepted file types** (currently only .csv can be imported. Could expand to .xlsx, .txt & more)
# -   Add the ability to convert to pivot → filter → export wrangled output (Pablo is due to change AgGrid to allow export of pivoted/grouped data)
# 	    """
#     )
# 
#     st.text("")


c29, c30, c31 = st.columns([1, 6, 1])

with c30:

    uploaded_file = st.file_uploader(
        "",
        key="1",
        help="To activate 'wide mode', go to the hamburger menu > Settings > turn on 'wide mode'",
    )

    if uploaded_file is not None:
        file_container = st.expander("Check your uploaded .json or .txt file")
        file_contents = uploaded_file.read()
        file_contents_str = file_contents.decode("utf-8")
        # shows = pd.read_json(uploaded_file)    
        # uploaded_file.seek(0)
        # file_container.write(shows)
        if isinstance(file_contents_str, bytes):
        # data is in bytes format, so it needs to be decoded
            json_data = json.loads(file_contents_str.decode())
        else:
        # data is already in a string format, so it does not need to be decoded
            json_data = json.loads(file_contents_str)
        if isinstance(json_data, dict):
        # data is in bytes format, so it needs to be decoded
            df = pd.json_normalize(json_data)
        else:
        # data is already in a string format, so it does not need to be decoded
            df = pd.read_json(file_contents_str)
    # Initialize an empty list to store the exploded and normalized dataframes
        df_list = []
    # Iterate over the columns of the dataframe
        for col in df.columns:
    # Check if the column contains lists
            if df[col].apply(type).eq(list).any():
        # Explode the column
                df1 = df.explode(col, ignore_index=True)
        # Normalize the dataframe
                df2 = pd.json_normalize(json.loads(df1.to_json(orient="records")))
                df_list.append(df2)   
                result = pd.concat(df_list) 
            else:
                result = df_list.append(df) 
                result = pd.concat(df_list)
    # Check if the dataframe contains any columns with dicts
        if result.applymap(type).eq(list).any().any():
    # Get the labels of the columns with dicts
            list_columns = result.applymap(type).eq(list).any().index[result.applymap(type).eq(list).any()].tolist()
            result = result.drop(list_columns, axis=1)   
        else:
            result
        shows = result 
        uploaded_file.seek(0)
        file_container.write(shows)

    else:
        st.info(
            f"""
                👆 Upload a .json or .txt file first. Sample to try: [alipayobjects.json](https://gw.alipayobjects.com/os/bmw-prod/1d565782-dde4-4bb6-8946-ea6a38ccf184.json)
                """
        )

        st.stop()

from st_aggrid import GridUpdateMode, DataReturnMode

gb = GridOptionsBuilder.from_dataframe(shows)
# enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
gb.configure_column(shows.columns[0], headerCheckboxSelection=True)
gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=10)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
gb.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
gridOptions = gb.build()

st.success(
    f"""
        💡 Tip! Hold the shift key when selecting rows to select multiple rows at once!
        """
)

response = AgGrid(
    shows,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=False,
)

df = pd.DataFrame(response["selected_rows"])
df = df.iloc[: , 1:]
df1 = df
df = df.head(10)

st.subheader("Snapshot of filtered data will appear below 👇 ")
st.text("")

st.table(df)

st.text("")

c29, c30, c31 = st.columns([1, 1, 2])

with c29:

    CSVButton = download_button(
        df1,
        "File.csv",
        "Download to CSV",
    )
