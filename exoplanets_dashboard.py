import pandas as pd
import streamlit as st
import plotly.express as px


@st.cache(allow_output_mutation=True)
def get_data_from_nasa_api():
    parameters = 'pl_name,disc_year,discoverymethod,disc_facility,ra,dec,pl_orbper,pl_bmasse,pl_rade'
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
        xaxis_title=f'行星軌道週期 (天)',
        yaxis_title=f'行星{y_value} (以地球{y_value}為單位)',
        legend_title=color_by
    ) 
    return st.plotly_chart(fig, use_container_width=True)

st.set_page_config(
    page_title='太陽系外行星儀表板',
    layout='wide'
)
st.title('太陽系外行星儀表板')
data_load_state = st.markdown('正在連線[NASA太陽系外行星資料庫](https://exoplanetarchive.ipac.caltech.edu/)讀取資料，請稍候...')
data = get_data_from_nasa_api()

if not data.empty:
    data_load_state.markdown(f'資料讀取完成，共取得{len(data)}筆[太陽系外行星](https://zh.wikipedia.org/wiki/%E5%A4%AA%E9%99%BD%E7%B3%BB%E5%A4%96%E8%A1%8C%E6%98%9F)資料。')
    disc_year_min = int(data.disc_year.min())
    disc_year_max = int(data.disc_year.max())
    y_value = st.sidebar.selectbox('請選擇y軸：', ['質量', '半徑'])
    color_by = st.sidebar.selectbox('請選擇資料點的顏色要依據什麼區分：', ['發現系外行星的方法','發現系外行星的觀測計劃/天文台'])
    disc_year = st.sidebar.slider('篩選截至某年所發現的系外行星：', disc_year_min, disc_year_max, disc_year_max, 1)
    plot_census(data, y_value, color_by, disc_year)
