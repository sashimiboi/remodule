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

STRIPE_CHECKOUT = 'https://buy.stripe.com/test_14k7uXbZFfgfdZS9AA'

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

st.set_page_config(page_icon="https://i.imgur.com/y2i91bJ.png", page_title="Remodule")
st.image(
    "https://i.imgur.com/P7PyXuk.png",
    width=100,
)
st.title("JSON to CSV Converter by Remodule")

c29, c30, c31 = st.columns([1, 6, 1])

with c30:

    uploaded_file = st.file_uploader(
        "",
        key="1",
        help="To activate 'wide mode', go to the hamburger menu > Settings > turn on 'wide mode'",
    )

    # uploaded_file = st.text_input('Or copy and paste file here 👇')
    # uploaded_file = st.write(uploaded_file)

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
        # Create an empty list to store the dataframes
        df_list = []
        # Iterate over each key-value pair in the data dictionary
        for key, value in json_data.items():
            # If the value is a list of lists, unnest it and create a dataframe
            if isinstance(value, list) and all(isinstance(i, list) for i in value):
                df = pd.DataFrame(value, columns=[key, f'{key}_value'])
                df_list.append(df)
            # If the value is a list of dictionaries, unnest it and create a dataframe
            elif isinstance(value, list) and all(isinstance(i, dict) for i in value):
                # Unnest the data in the 'totalDataChartBreakdown_value' column
                df = pd.json_normalize(value)
                # Merge the unnested data with the original dataframe
                df = pd.merge(df, pd.DataFrame(value, columns=[key, f'{key}_value']), on=key)
                df_list.append(df)
            # If the value is not a list, create a dataframe with a single column and a default index
            else:
                df = pd.DataFrame({key: value}, index=[0])
                df_list.append(df)

        # Concatenate the dataframes into a single dataframe
        df = pd.concat(df_list, axis=1)

        # Display the resulting dataframe
        df1 = pd.json_normalize(json.loads(df.to_json(orient="records")))
        shows = df1 
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
    enable_enterprise_modules=False,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=False,
    allow_unsafe_jscode=True,
)

df = pd.DataFrame(response["selected_rows"])
df = df.iloc[: , 1:]

st.subheader("Snapshot of filtered data will appear below 👇 ")
st.text("")

st.table(df.head(10))

st.text("")

c29, c30, c31 = st.columns([1, 1, 2])

with c29:

    CSVButton = download_button(
        df,
        "File.csv",
        "Download to CSV",
    )
