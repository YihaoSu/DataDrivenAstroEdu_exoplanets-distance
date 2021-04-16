import pandas as pd
import streamlit as st
import astropy.units as u
from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive


@st.cache(allow_output_mutation=True)
def get_user_list():
    return []


@st.cache(allow_output_mutation=True, show_spinner=False)
def get_exoplanet_data():
    parameters = 'fpl_hostname,fpl_name,fst_dist,fpl_bmasse,'
    parameters += 'fpl_orbper,fpl_rade,fpl_disc,fpl_discmethod'
    data = NasaExoplanetArchive.query_criteria(
        table='compositepars', select=parameters)

    data['distance_lyr'] = data['fst_dist'].to(u.lyr)
    data['distance_au'] = data['fst_dist'].to(u.au)
    data['distance_km'] = data['fst_dist'].to(u.km)
    data = data.to_pandas()
    data = data[data.fst_dist > 0]
    data = data[data.fpl_bmasse > 0]
    data = data[data.fpl_orbper > 0]
    data = data[data.fpl_rade > 0]
    renamed_columns_dict = {
        'fpl_hostname': 'host_name',
        'fpl_name': 'pl_name',
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


def get_exoplanet_info(exoplanet, distance_unit):
    distance_unit_dict = {
        '秒差距': 'distance_pc',
        '光年': 'distance_lyr',
        '天文單位': 'distance_au',
        '公里': 'distance_km'
    }
    pl_name = exoplanet['pl_name']
    distance = exoplanet[distance_unit_dict.get(distance_unit)]
    discovery_year = exoplanet['discovery_year']
    mass = exoplanet['mass']
    radius = exoplanet['radius']
    host_name = exoplanet['host_name']
    orbital_period = exoplanet['orbital_period']
    info = f'{pl_name}於{discovery_year}年被發現，'
    info += f'距離地球{round(distance, 1)}{distance_unit}。'
    info += f'它的質量約為地球的{round(mass, 1)}倍、半徑約為地球的{round(radius, 1)}倍。'
    info += f'它繞行母恆星{host_name}一圈約需{round(orbital_period, 1)}天。'

    return info


st.set_page_config(page_title='歸途 - 太陽系外行星篇', layout='wide')
st.title('歸途 - 太陽系外行星篇')

session_id = st.report_thread.get_report_ctx().session_id
user_list = get_user_list()

if session_id not in user_list:
    get_user_list().append(session_id)

if len(user_list) > 1:
    st.caching.clear_cache()

with st.spinner('從[NASA太陽系外行星資料庫](https://exoplanetarchive.ipac.caltech.edu/)載入資料中，請稍候...'):
    exoplanet_data = get_exoplanet_data()
    my_exoplanets = generate_my_exoplanets()

if not exoplanet_data.empty:
    st.header('*縮短與星的距離 繪製專屬於你的歸途*')
    st.markdown('---')
    st.subheader(':scroll: 說明:')

    if st.sidebar.button('清掉紀錄重新開始'):
        st.caching.clear_cache()

    distance_unit = st.sidebar.selectbox(
        '請先選擇要以哪個長度單位來描述距離：', ['秒差距', '光年', '天文單位', '公里'])
    st.sidebar.markdown('[秒差距](https://zh.wikipedia.org/zh-tw/%E7%A7%92%E5%B7%AE%E8%B7%9D)、[光年](https://zh.wikipedia.org/zh-tw/%E5%85%89%E5%B9%B4)和[天文單位](https://zh.wikipedia.org/zh-tw/%E5%A4%A9%E6%96%87%E5%96%AE%E4%BD%8D)都是常用來描述星體距離的長度單位')
    st.sidebar.markdown('1秒差距約為 $3.09*10^{13}$ 公里')
    st.sidebar.markdown('1光年約為 $9.46*10^{12}$ 公里')
    st.sidebar.markdown('1天文單位是地球和太陽的平均距離，約為 $1.5*10^{8}$ 公里')

    if st.sidebar.button('隨機產生'):
        nearest_exoplanet = exoplanet_data[
            exoplanet_data.distance_pc == exoplanet_data.distance_pc.min()
            ].iloc[0]
        selected_exoplanet = exoplanet_data.sample().iloc[0]
        pl_name = selected_exoplanet['pl_name']
        distance_au = int(selected_exoplanet['distance_au'])
        st.subheader(f'你目前位於{pl_name}，與星的距離約為地球和太陽距離的{distance_au}倍')
        my_exoplanets = generate_my_exoplanets(selected_exoplanet)
        selected_exoplanet_info = get_exoplanet_info(
            selected_exoplanet, distance_unit)

        if pl_name == nearest_exoplanet['pl_name']:
            st.balloons()
            st.success('恭喜你已經抵達離地球最近的系外行星了！ 若要再玩一次請按「清掉紀錄重新開始」。')
            st.info(selected_exoplanet_info)
        elif my_exoplanets is not None:
            st.success('恭喜你又離家更近了！')
            st.info(selected_exoplanet_info)
        else:
            st.error('哎呀，你並沒有縮短與星的距離，請再試一次！')
            st.info(selected_exoplanet_info)
