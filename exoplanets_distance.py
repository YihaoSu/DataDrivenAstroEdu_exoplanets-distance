import pandas as pd
import streamlit as st
import astropy.units as u
from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive


@st.cache(allow_output_mutation=True, show_spinner=False)
def get_exoplanet_data():
    parameters = 'fpl_name,fst_dist,fpl_bmasse,fpl_orbper,fpl_rade,'
    parameters += 'fpl_disc,fpl_discmethod'
    data = NasaExoplanetArchive.query_criteria(
        table='compositepars', select=parameters)

    data['distance_lyr'] = data['fst_dist'].to(u.lyr)
    data['distance_au'] = data['fst_dist'].to(u.au)
    data['distance_km'] = data['fst_dist'].to(u.km)
    data = data.to_pandas()
    data = data[data.fst_dist > 0]
    renamed_columns_dict = {
        'fpl_name': 'name',
        'fst_dist': 'distance_pc',
        'fpl_bmasse': 'mass',
        'fpl_orbper': 'orbital_period',
        'fpl_rade': 'radius',
        'fpl_disc': 'discovery_year',
        'fpl_discmethod': 'discovery_method'
    }
    data.rename(columns=renamed_columns_dict, inplace=True)

    return data


st.set_page_config(page_title='歸途 - 太陽系外行星篇', layout='wide')
st.title('歸途 - 太陽系外行星篇')

with st.spinner('載入遊戲中，請稍候...'):
    exoplanet_data = get_exoplanet_data()

if not exoplanet_data.empty:
    st.header('*縮短與星的距離 拼出專屬於你的歸途*')
    st.markdown('<hr>', unsafe_allow_html=True)
    st.subheader(':scroll: 遊戲說明:')

    if st.sidebar.button('隨機產生'):
        st.dataframe(exoplanet_data.sample())
