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


@st.cache(allow_output_mutation=True)
def generate_my_exoplanets(selected_exoplanet=None):
    if selected_exoplanet is None:
        return []
    elif len(my_exoplanets) == 0:
        my_exoplanets.append(selected_exoplanet)
        return pd.DataFrame(my_exoplanets).reset_index(drop=True)
    else:
        distance_my_exoplanets = pd.DataFrame(my_exoplanets)['distance_pc']
        distance_selected_exoplanet = selected_exoplanet['distance_pc']
        if distance_my_exoplanets.gt(distance_selected_exoplanet).all():
            my_exoplanets.append(selected_exoplanet)
            return pd.DataFrame(my_exoplanets).reset_index(drop=True)
        else:
            return None


st.set_page_config(page_title='歸途 - 太陽系外行星篇', layout='wide')
st.title('歸途 - 太陽系外行星篇')

with st.spinner('載入中，請稍候...'):
    exoplanet_data = get_exoplanet_data()
    my_exoplanets = generate_my_exoplanets()

if not exoplanet_data.empty:
    st.header('*縮短與星的距離 繪製專屬於你的歸途*')
    st.markdown('---')
    st.subheader(':scroll: 說明:')

    if st.sidebar.button('清掉紀錄重新開始'):
        st.caching.clear_cache()

    if st.sidebar.button('隨機產生'):
        selected_exoplanet = exoplanet_data.sample().iloc[0]
        name = selected_exoplanet['name']
        distance_au = int(selected_exoplanet['distance_au'])
        st.text(f'你與{name}的距離: 約為地球和太陽距離的{distance_au}倍')
        my_exoplanets = generate_my_exoplanets(selected_exoplanet)

        if my_exoplanets is not None:
            st.dataframe(my_exoplanets)
        else:
            st.error('哎呀，你並沒有縮短與星的距離，請再試一次')
