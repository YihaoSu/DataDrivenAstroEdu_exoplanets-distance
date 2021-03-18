import pandas as pd
import streamlit as st


@st.cache(allow_output_mutation=True)
def get_data_from_nasa_api():
    parameters = 'pl_name,disc_year,discoverymethod,disc_facility,ra,dec,pl_orbper,pl_bmasse'
    api_url = f'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+{parameters}+from+pscomppars&format=csv'
    data = pd.read_csv(api_url)
    return data

st.title('太陽系外行星儀表板')
data_load_state = st.markdown('正在連線[NASA太陽系外行星資料庫](https://exoplanetarchive.ipac.caltech.edu/)讀取資料，請稍候...')
data = get_data_from_nasa_api()

if not data.empty:
    data_load_state.markdown(f'資料讀取完成，共有{len(data)}筆[太陽系外行星](https://zh.wikipedia.org/wiki/%E5%A4%AA%E9%99%BD%E7%B3%BB%E5%A4%96%E8%A1%8C%E6%98%9F)資料。')
    st.dataframe(data)
