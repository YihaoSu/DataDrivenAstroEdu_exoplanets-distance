# 天文教育網頁APP - 太陽系外行星篇
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/yihaosu/streamlit4astroedu-exoplanets/main/exoplanets_distance.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/YihaoSu/streamlit4astroedu-exoplanets/blob/main/LICENSE)

此專案是以[Streamlit](https://streamlit.io/)開發，並從[NASA太陽系外行星資料庫](https://exoplanetarchive.ipac.caltech.edu/)抓取資料。

[:coffee: 贊助一杯咖啡 支持我的創作 讓天文更開放 拉近群眾與星空的距離](https://liker.land/astrobackhacker/civic)

## 在自己的電腦上運行此專案APP
### 1. 下載此APP原始碼並安裝所需Python套件
```bash
git clone https://github.com/YihaoSu/streamlit4astroedu-exoplanets.git
cd streamlit4astroedu-exoplanets
pip install -r requirements.txt
```
### 2. 執行以下指令後即可在瀏覽器運行APP
```shell
streamlit run exoplanets_distance.py # 縮短與星的距離 繪製專屬於你的歸途
或
streamlit run exoplanets_dashboard.py # 系外行星儀表板
```