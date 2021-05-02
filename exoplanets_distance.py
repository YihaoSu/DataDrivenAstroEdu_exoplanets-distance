import pandas as pd
import streamlit as st
import astropy.units as u
import plotly.express as px
from astroquery.nasa_exoplanet_archive import NasaExoplanetArchive


distance_unit_dict = {
    '秒差距': 'distance_pc',
    '光年': 'distance_lyr',
    '天文單位': 'distance_au',
    '公里': 'distance_km'
}


@st.cache(allow_output_mutation=True)
def get_user_list():
    return []


# @st.cache(allow_output_mutation=True, show_spinner=False)
# def get_exoplanet_data():
#     parameters = 'fpl_hostname,fpl_name,fst_dist,fpl_bmasse,'
#     parameters += 'fpl_orbper,fpl_rade,fpl_disc,fpl_discmethod'
#     data = NasaExoplanetArchive.query_criteria(
#         table='compositepars', select=parameters)

#     data['distance_lyr'] = data['fst_dist'].to(u.lyr)
#     data['distance_au'] = data['fst_dist'].to(u.au)
#     data['distance_km'] = data['fst_dist'].to(u.km)
#     data = data.to_pandas()
#     data = data[data.fst_dist > 0]
#     data = data[data.fpl_bmasse > 0]
#     data = data[data.fpl_orbper > 0]
#     data = data[data.fpl_rade > 0]
#     renamed_columns_dict = {
#         'fpl_hostname': 'host_name',
#         'fpl_name': 'pl_name',
#         'fst_dist': 'distance_pc',
#         'fpl_bmasse': 'mass',
#         'fpl_orbper': 'orbital_period',
#         'fpl_rade': 'radius',
#         'fpl_disc': 'discovery_year',
#         'fpl_discmethod': 'discovery_method'
#     }
#     data = data.rename(columns=renamed_columns_dict)
#     data = data.sort_values(
#         by=['distance_pc'], ascending=False, ignore_index=True)

#     return data


@st.cache(allow_output_mutation=True, show_spinner=False)
def get_exoplanet_data():
    parameters = 'hostname,pl_name,sy_dist,pl_bmasse,'
    parameters += 'pl_orbper,pl_rade,disc_year,discoverymethod'
    api_url = 'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?'
    api_url += f'query=select+{parameters}+from+pscomppars&format=csv'
    data = pd.read_csv(api_url)

    pc = 1 * u.parsec
    pc_to_lyr = pc.to(u.lyr)
    pc_to_au = pc.to(u.au)
    pc_to_km = pc.to(u.km)
    data['distance_lyr'] = data['sy_dist'] * pc_to_lyr.value
    data['distance_au'] = data['sy_dist'] * pc_to_au.value
    data['distance_km'] = data['sy_dist'] * pc_to_km.value
    data = data[data.sy_dist > 0]
    data = data[data.pl_bmasse > 0]
    data = data[data.pl_orbper > 0]
    data = data[data.pl_rade > 0]
    renamed_columns_dict = {
        'hostname': 'host_name',
        'sy_dist': 'distance_pc',
        'pl_bmasse': 'mass',
        'pl_orbper': 'orbital_period',
        'pl_rade': 'radius',
        'disc_year': 'discovery_year',
        'discoverymethod': 'discovery_method'
    }
    data = data.rename(columns=renamed_columns_dict)
    data = data.sort_values(
        by=['distance_pc'], ascending=False, ignore_index=True)

    return data


@st.cache(allow_output_mutation=True)
def generate_my_exoplanets(selected_exoplanet=None, start_exoplanet=None):
    if selected_exoplanet.equals(start_exoplanet):
        return [start_exoplanet]
    else:
        my_exoplanets.append(selected_exoplanet)
        return pd.DataFrame(my_exoplanets).reset_index(drop=True)


def get_exoplanet_short_info(exoplanet):
    pl_name = exoplanet['pl_name']
    distance_au = int(exoplanet['distance_au'])
    distance_lyr = int(exoplanet['distance_lyr'])
    selected_exoplanet_short_info = f'你目前位於{pl_name}，'
    selected_exoplanet_short_info += f'與星的距離約為地球和太陽距離的{distance_au}倍，'
    selected_exoplanet_short_info += f'你看到的星光來自{distance_lyr}年前'

    return selected_exoplanet_short_info


def get_exoplanet_detailed_info(exoplanet, distance_unit):
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
    nasa_url = 'https://exoplanets.nasa.gov/eyes-on-exoplanets/#/planet/'
    info += f'([到NASA網站瞧瞧它在藝術家的眼中長得如何]({nasa_url}{pl_name.replace(" ", "_")}))'

    return info


def plot_my_exoplanets(my_exoplanets, distance_unit):
    distance = distance_unit_dict.get(distance_unit)
    fig = px.scatter_3d(
        my_exoplanets, x='orbital_period', y='mass', z=distance,
        log_x=True, log_y=True, log_z=True, hover_name='pl_name',
        size='radius', size_max=100, color='radius',
        color_continuous_scale=px.colors.sequential.Jet,
        labels={
            'orbital_period': '繞行母恆星一圈需多少天',
            'mass': '質量是地球的幾倍',
            distance: f'與星的距離 ({distance_unit})',
            'radius': '半徑是地球的幾倍'
        }
    )
    fig.update_layout(
        width=800, height=800,
        scene=dict(
            xaxis=dict(nticks=2),
            yaxis=dict(nticks=2),
            zaxis=dict(nticks=2),
        )
    )

    return st.plotly_chart(fig, use_container_width=True)


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

if not exoplanet_data.empty:
    st.header('*縮短與星的距離 繪製專屬於你的歸途*')
    st.markdown('---')

    nearest_exoplanet = exoplanet_data[
        exoplanet_data.distance_pc == exoplanet_data.distance_pc.min()
        ].iloc[0]
    farthest_exoplanet = exoplanet_data[
        exoplanet_data.distance_pc == exoplanet_data.distance_pc.max()
        ].iloc[0]
    selected_exoplanet = farthest_exoplanet
    my_exoplanets = generate_my_exoplanets(
        selected_exoplanet, farthest_exoplanet)
    intro_text = '[太陽系外行星](https://zh.wikipedia.org/zh-tw/%E5%A4%AA%E9%99%BD%E7%B3%BB%E5%A4%96%E8%A1%8C%E6%98%9F)(簡稱系外行星)是指位於太陽系之外，不繞行太陽公轉的行星。'
    intro_text += f'你從離地球最遠的系外行星{farthest_exoplanet["pl_name"]}出發，'
    intro_text += '你將會漫步到哪個星球呢？'
    intro_text += '縮短與星的距離，繪製專屬於你的歸途吧!'
    st.info(f':scroll: {intro_text}')

    st.sidebar.header('控制室')
    st.sidebar.subheader(':straight_ruler: 選擇描述你與星距離的長度單位')
    distance_unit = st.sidebar.selectbox('', ['秒差距', '光年', '天文單位', '公里'])
    st.sidebar.markdown('[秒差距](https://zh.wikipedia.org/zh-tw/%E7%A7%92%E5%B7%AE%E8%B7%9D)、[光年](https://zh.wikipedia.org/zh-tw/%E5%85%89%E5%B9%B4)和[天文單位](https://zh.wikipedia.org/zh-tw/%E5%A4%A9%E6%96%87%E5%96%AE%E4%BD%8D)都是常用來描述星體距離的長度單位')
    st.sidebar.markdown('1秒差距約為 $3.09*10^{13}$ 公里')
    st.sidebar.markdown('1光年約為 $9.46*10^{12}$ 公里')
    st.sidebar.markdown('1天文單位是地球和太陽的平均距離，約為 $1.5*10^{8}$ 公里')
    st.sidebar.subheader('調整步伐')
    step = st.sidebar.slider(distance_unit, 0, 8000, 8000)

    st.sidebar.subheader(':game_die: 隨機漫步系外行星')
    if st.sidebar.button('前進'):
        if len(my_exoplanets) == 3:
            ad_text = '歸途中你遇到一位[神祕的宇宙社團](https://www.facebook.com/groups/1022708484514663)成員，'
            ad_text += '他歡迎你加入社團，也希望你能[支持他](https://liker.land/astrobackhacker/civic)，'
            ad_text += '一同讓天文更開放，拉近群眾與星空的距離。'
            st.warning(ad_text)
        distance_col = distance_unit_dict.get(distance_unit)
        last_exoplanet_distance = pd.Series(my_exoplanets[-1])[distance_col]
        exoplanet_data = exoplanet_data[
            (exoplanet_data[distance_col] > last_exoplanet_distance - step) &
            (exoplanet_data[distance_col] < last_exoplanet_distance)
        ]
        if len(exoplanet_data) > 0:
            selected_exoplanet = exoplanet_data.sample().iloc[0]
            my_exoplanets = generate_my_exoplanets(selected_exoplanet)
        else:
            st.error('你的步伐太小，無法抵達下一個系外行星，請調整步伐!')

    if isinstance(my_exoplanets, list):
        selected_exoplanet = my_exoplanets[-1]
    elif isinstance(my_exoplanets, pd.DataFrame):
        selected_exoplanet = my_exoplanets.iloc[-1]

    st.subheader(get_exoplanet_short_info(selected_exoplanet))
    selected_exoplanet_detailed_info = get_exoplanet_detailed_info(
        selected_exoplanet, distance_unit)
    st.info(selected_exoplanet_detailed_info)

    if selected_exoplanet['pl_name'] == nearest_exoplanet['pl_name']:
        st.balloons()
        st.success('恭喜你已經抵達離地球最近的系外行星了！ 若要再玩一次請重新載入頁面。')
        st.caching.clear_cache()

    plot_my_exoplanets(my_exoplanets, distance_unit)
