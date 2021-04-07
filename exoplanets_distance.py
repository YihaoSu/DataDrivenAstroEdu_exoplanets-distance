import pandas as pd
import streamlit as st
from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive


@st.cache(allow_output_mutation=True, show_spinner=False)
def get_exoplanet_data():
    parameters = 'fpl_name,fst_dist,fpl_bmasse,fpl_orbper,fpl_rade,'
    parameters += 'fpl_disc,fpl_discmethod'
    exoplanet_data = NasaExoplanetArchive.query_criteria(
        table='compositepars', select=parameters).to_pandas()

    return exoplanet_data


st.set_page_config(page_title='歸途 - 太陽系外行星篇', layout='wide')
st.title('歸途 - 太陽系外行星篇')
st.header('*縮短與星的距離 拼出專屬於你的歸途*')
st.markdown('<hr>', unsafe_allow_html=True)
main_subheader = st.subheader('載入遊戲中，請稍候...')
exoplanet_data = get_exoplanet_data()

if not exoplanet_data.empty:
    main_subheader.subheader(':scroll: 遊戲說明:')

    if st.sidebar.button('隨機產生'):
        st.dataframe(exoplanet_data.sample())
