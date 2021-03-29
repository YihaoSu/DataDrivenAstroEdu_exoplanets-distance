import pandas as pd
import streamlit as st
import plotly.express as px
from astropy import units as u


@st.cache(allow_output_mutation=True)
def get_data_from_nasa_api():
    parameters = 'pl_name,disc_year,discoverymethod,disc_facility,pl_orbper,pl_bmasse,pl_rade,sy_dist'
    api_url = f'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+{parameters}+from+pscomppars&format=csv'
    data = pd.read_csv(api_url)
    return data

def plot_census(data, y_value, color_by, disc_year):
    data = data[data.disc_year <= disc_year]
    dict_y_value = {
        '質量': 'pl_bmasse',
        '半徑': 'pl_rade'
    }
    dict_color_by = {
        '發現系外行星的方法': 'discoverymethod',
        '發現系外行星的觀測計劃/天文台': 'disc_facility'
    }
    fig = px.scatter(
        data, x='pl_orbper', y=dict_y_value.get(y_value),
        log_x=True, log_y=True,
        color=dict_color_by.get(color_by),
        title=f'系外行星的{y_value}及軌道週期普查 (截至{disc_year}年共發現{len(data)}個系外行星)',
        hover_data=['pl_name', 'disc_year']
        )
    fig.update_layout(
        xaxis_title=f'行星繞行母恆星的軌道週期 (天)',
        yaxis_title=f'行星{y_value} (以地球{y_value}為單位)',
        legend_title=color_by
    ) 
    return st.plotly_chart(fig, use_container_width=True)

def plot_discoverymethod_piechart(data):
    fig = px.pie(data, names='discoverymethod')
    return st.plotly_chart(fig, use_container_width=True)

def plot_distance_histogram(data, dist_unit):
    pc = 1 * u.parsec
    pc_to_lyr = pc.to(u.lyr)
    pc_to_km = pc.to(u.km)

    if dist_unit == '光年':
        data['sy_dist_lyr'] = (data['sy_dist'] * pc_to_lyr.value).round(2)
        fig = px.histogram(data, x='sy_dist_lyr', nbins=50)
    elif dist_unit == '公里':
        data['sy_dist_km'] = data['sy_dist'] * pc_to_km.value
        fig = px.histogram(data, x='sy_dist_km', nbins=50)
    else:
        fig = px.histogram(data, x='sy_dist', nbins=50)

    fig.update_layout(
        xaxis_title=f'系外行星與地球的距離 ({dist_unit})',
        yaxis_title='系外行星的數量',
    ) 
    return st.plotly_chart(fig, use_container_width=True)

def arrange_extreme_exoplanet_data(extreme_exoplanet):
    extreme_exoplanet.rename(
        {
            'pl_name': '名稱',
            'disc_year': '發現年份',
            'discoverymethod': '發現方法',
            'disc_facility': '觀測計劃/天文台',
            'pl_orbper': '軌道週期 (天)',
            'pl_bmasse': '質量 (以地球質量為單位)',
            'pl_rade': '半徑 (以地球半徑為單位)',
            'sy_dist': '距離 (秒差距)',
            'sy_dist_lyr': '距離 (光年)',
            'sy_dist_km': '距離 (公里)'
        }, inplace=True)
    return extreme_exoplanet

st.set_page_config(
    page_title='太陽系外行星儀表板',
    layout='wide'
)
st.title('太陽系外行星儀表板')
data_load_state = st.markdown('正在連線[NASA太陽系外行星資料庫](https://exoplanetarchive.ipac.caltech.edu/)讀取資料，請稍候...')
data = get_data_from_nasa_api()

if not data.empty:
    data_load_state.markdown(f'資料讀取完成，共取得{len(data)}筆[太陽系外行星](https://zh.wikipedia.org/wiki/%E5%A4%AA%E9%99%BD%E7%B3%BB%E5%A4%96%E8%A1%8C%E6%98%9F)資料。')
    want_to_know = st.sidebar.selectbox('你想要知道系外行星...', ['有多大？', '有多遠？'])

    if want_to_know == '有多大？':
        disc_year_min = int(data.disc_year.min())
        disc_year_max = int(data.disc_year.max())
        y_value = st.sidebar.selectbox('請選擇y軸：', ['質量', '半徑'])
        color_by = st.sidebar.selectbox('請選擇資料點的顏色要依據什麼區分：', ['發現系外行星的方法','發現系外行星的觀測計劃/天文台'])
        disc_year = st.sidebar.slider('篩選截至某年所發現的系外行星：', disc_year_min, disc_year_max, disc_year_max, 1)
        plot_census(data, y_value, color_by, disc_year)
        discoverymethod_col1, discoverymethod_col2 = st.beta_columns(2)

        with discoverymethod_col1:
            st.header('發現方法的佔比')
            plot_discoverymethod_piechart(data)

        with discoverymethod_col2:
            st.header('前4大發現方法的簡述')
            st.write('')
            with st.beta_expander('凌日法 (Transit)'):
                st.markdown('「如果一顆行星從母恆星盤面的前方橫越時，將可以觀察到恆星的視覺亮度會略為下降一些，而這顆恆星變暗的數量取決於行星相對於恆星的大小。...」([了解更多](https://zh.wikipedia.org/wiki/%E7%B3%BB%E5%A4%96%E8%A1%8C%E6%98%9F%E5%81%B5%E6%B8%AC%E6%B3%95#%E5%87%8C%E6%97%A5%E6%B3%95))')
            with st.beta_expander('徑向速度法 (Radial Velocity)'):
                st.write('「當一顆行星繞著恆星公轉，恆星也會繞著質量中心在自己小小的軌道上移動。恆星徑向速度的變化 －就是它遠離或接近地球的速度－ 可以從因為都卜勒效應造成在譜線上的變化檢測出來。...」([了解更多](https://zh.wikipedia.org/zh-tw/%E5%A4%AA%E9%99%BD%E7%B3%BB%E5%A4%96%E8%A1%8C%E6%98%9F#%E6%AA%A2%E6%B8%AC%E7%9A%84%E6%96%B9%E6%B3%95))')
            with st.beta_expander('重力微透鏡法 (Microlensing)'):
                st.write('「當恆星的重力場產生像透鏡一樣的微透鏡，會放大遙遠背景恆星的光。環繞著恆星的行星會導致探測到的恆星光度會隨著時間的推移產生異常的放大。...」([了解更多](https://zh.wikipedia.org/zh-tw/%E5%A4%AA%E9%99%BD%E7%B3%BB%E5%A4%96%E8%A1%8C%E6%98%9F#%E6%AA%A2%E6%B8%AC%E7%9A%84%E6%96%B9%E6%B3%95))')
            with st.beta_expander('直接影像法 (Imaging)'):
                st.write('「在一些特殊情況，現代的望遠鏡亦可以直接得到系外行星的影象，例如行星體積特別大...」([了解更多](https://zh.wikipedia.org/zh-tw/%E5%A4%AA%E9%99%BD%E7%B3%BB%E5%A4%96%E8%A1%8C%E6%98%9F#%E7%9B%B4%E6%8E%A5%E6%94%9D%E5%BD%B1))')

    if want_to_know == '有多遠？':
        dist_unit = st.sidebar.selectbox('請選擇要以哪個距離單位顯示資料：', ['秒差距', '光年', '公里'])
        st.sidebar.markdown('1[秒差距](https://zh.wikipedia.org/zh-tw/%E7%A7%92%E5%B7%AE%E8%B7%9D)約為3.26光年')
        st.sidebar.markdown('1[光年](https://zh.wikipedia.org/zh-tw/%E5%85%89%E5%B9%B4)約為$9.46*10^{13}$公里')
        plot_distance_histogram(data, dist_unit)
        nearest = data[data.sy_dist == data.sy_dist.min()].iloc[0]
        farthest = data[data.sy_dist == data.sy_dist.max()].iloc[0]
        nearest_info_col, farthest_info_col = st.beta_columns(2)

        with nearest_info_col:
            nearest = arrange_extreme_exoplanet_data(nearest)
            st.table(nearest.rename('目前發現離地球最近的系外行星'))
            
        with farthest_info_col:
            farthest = arrange_extreme_exoplanet_data(farthest)
            st.table(farthest.rename('目前發現離地球最遠的系外行星'))