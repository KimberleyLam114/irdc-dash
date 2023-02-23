'''
 # @ Create Time: 2022-11-05 16:58:58.526050
 # @ Create by：Zhidian Lin
'''

import pathlib
from dash import Dash
import dash_auth
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# config = {'displaylogo': False}
# JupyterDash.infer_jupyter_proxy_config()
updatedDate = "2023/1/12"
理论工时 = 23
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("assets/data").resolve()
# 员工所属部门汇总 = pd.read_csv(DATA_PATH.joinpath("8月工时自动化分析test.csv"))
# 业务线汇总 = pd.read_csv(DATA_PATH.joinpath("8月工时自动化分析业务线.csv"))
# WBS业务线汇总 = pd.read_csv(DATA_PATH.joinpath("8月工时自动化分析wbs.csv"))
all_actual_days = pd.read_csv(DATA_PATH.joinpath('历史部门实际人均人天.csv'))
cur_bus_line_summary = pd.read_csv(DATA_PATH.joinpath('11月业务线维度.csv'))
last_bus_line_summary = pd.read_csv(DATA_PATH.joinpath('10月业务线维度.csv'))
last_mon_staff = pd.read_csv(DATA_PATH.joinpath("10月人员维度.csv"))
cur_mon_staff = pd.read_csv(DATA_PATH.joinpath("11月人员维度.csv"))
cur_mon_staff['预估填报率'] = pd.to_numeric(cur_mon_staff['预估填报率'], errors='coerce')
cur_mon_staff = cur_mon_staff.replace(np.nan, 0, regex=True)
cur_mon_staff['理论填报率'] = pd.to_numeric(cur_mon_staff['理论填报率'], errors='coerce')
cur_mon_staff = cur_mon_staff.replace(np.nan, 0, regex=True)

# cur_mon_staff['预估填报率'] = cur_mon_staff['预估填报率'].astype(int)
# cur_mon_staff['理论填报率'] = cur_mon_staff['理论填报率'].astype(int)

last_mon_wbs = pd.read_csv(DATA_PATH.joinpath("10月WBS维度.csv"))
cur_mon_wbs = pd.read_csv(DATA_PATH.joinpath("11月WBS维度.csv"))
staff_apartment_tb = pd.read_csv(DATA_PATH.joinpath("新月员工所属部门.csv"))
business_line_tb = pd.read_csv(DATA_PATH.joinpath("新月业务线.csv"))
business_line_staff_type = pd.read_csv(DATA_PATH.joinpath("新月业务线合并员工组.csv"))

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/sandstone/bootstrap.min.css']

app = Dash(__name__, title="IRDC-Dashboard | 海外研发中心工时看板", external_stylesheets=[dbc.themes.SANDSTONE],
           meta_tags=[{'name': 'viewport',
                       'content': 'width=device-width, initial-scale=1.0'}])
server = app.server
VALID_USERNAME_PASSWORD_PAIRS = {
    'IRDC': 'IRDC666'
}
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

员工所属部门汇总1 = staff_apartment_tb.iloc[0:-1, :]

业务线汇总 = business_line_tb.iloc[0:-1, :]
业务线汇总 = 业务线汇总.replace('inf%', None)
实际业务线pie = 业务线汇总[["业务线", "员工数", "实际人天"]]
实际业务线pie = 实际业务线pie.groupby('业务线').agg({'员工数': 'sum', '实际人天': 'sum'})
预估业务线pie = 业务线汇总[["业务线", "员工数", "预估人天"]]
预估业务线pie = 预估业务线pie.groupby('业务线').agg({'员工数': 'sum', '预估人天': 'sum'})
理论业务线pie = 业务线汇总[["业务线", "员工数", "理论人天"]]
理论业务线pie = 理论业务线pie.groupby('业务线').agg({'员工数': 'sum', '理论人天': 'sum'})


预估业务线汇总 = cur_mon_staff[["业务线", "员工组", "预估人天"]].rename(columns={"预估人天": "总工时"})
预估业务线汇总['工时类别'] = 预估业务线汇总['业务线'].apply(lambda row: '预估')
实际业务线汇总 = cur_mon_staff[["业务线", "员工组", "实际人天"]].rename(columns={"实际人天": "总工时"})
实际业务线汇总['工时类别'] = 实际业务线汇总['业务线'].apply(lambda row: '实际')
理论业务线汇总 = cur_mon_staff[["业务线", "员工组", "理论人天"]].rename(columns={"理论人天": "总工时"})
理论业务线汇总['工时类别'] = 理论业务线汇总['业务线'].apply(lambda row: '理论')
预计实际业务线汇总 = 预估业务线汇总.append(实际业务线汇总).append(理论业务线汇总).reset_index(drop=True)
预计实际业务线汇总 = 预计实际业务线汇总.groupby(["业务线", "员工组","工时类别"]).agg({"总工时":'sum'}).reset_index()



layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=10, r=10, b=10, t=5),
    hovermode="closest",
    #plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=15), orientation="h"),
    title="IRDC 工时 Dashboard",
)

tabs_styles = {
    'height': '44px',
    'borderBottom': '1px solid #d6d6d6',
    'borderTop':'None'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

# indicator summary for irdc
staff_number_indicator = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff.员工姓名),
    delta = {"reference": len(last_mon_staff.员工姓名), "valueformat": ".0f"},
    title = {"text": "员工数"},
    align="center",
    ))
staff_number_indicator.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator.update_layout(
    height=150,width=165,
)

# indicator summary for sx
cur_mon_staff_sx = cur_mon_staff[cur_mon_staff.业务线.str.contains('SX')]
last_mon_staff_sx = last_mon_staff[last_mon_staff.业务线.str.contains('SX')]
cur_mon_staff_sx_ibg = cur_mon_staff[cur_mon_staff.业务线.str.contains('SX-IBG')]
last_mon_staff_sx_ibg = last_mon_staff[last_mon_staff.业务线.str.contains('SX-IBG')]
cur_mon_staff_sx_abg = cur_mon_staff[cur_mon_staff.业务线.str.contains('SX-ABG')]
last_mon_staff_sx_abg = last_mon_staff[last_mon_staff.业务线.str.contains('SX-ABG')]

# indicator summary for ir
cur_mon_staff_ir = cur_mon_staff[cur_mon_staff.业务线.str.contains('IR')]
last_mon_staff_ir = last_mon_staff[last_mon_staff.业务线.str.contains('IR')]

# indicator summary for aiot
cur_mon_staff_aiot = cur_mon_staff[cur_mon_staff.业务线.str.contains('AIOT')]
last_mon_staff_aiot = last_mon_staff[last_mon_staff.业务线.str.contains('AIOT')]

# indicator summary for dx
cur_mon_staff_dx = cur_mon_staff[cur_mon_staff.业务线.str.contains('DX')]
last_mon_staff_dx = last_mon_staff[last_mon_staff.业务线.str.contains('DX')]
cur_mon_staff_dx_ty = cur_mon_staff[cur_mon_staff.业务线.str.contains('DX-TY')]
last_mon_staff_dx_ty = last_mon_staff[last_mon_staff.业务线.str.contains('DX-TY')]
cur_mon_staff_dx_sku = cur_mon_staff[cur_mon_staff.业务线.str.contains('DX-SKU')]
last_mon_staff_dx_sku = last_mon_staff[last_mon_staff.业务线.str.contains('DX-SKU')]

# indicator summary for si
cur_mon_staff_si = cur_mon_staff[cur_mon_staff.业务线.str.contains('SI')]
last_mon_staff_si = last_mon_staff[last_mon_staff.业务线.str.contains('SI')]


staff_number_indicator_sx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff_sx.员工姓名),
    delta = {"reference": len(last_mon_staff_sx.员工姓名), "valueformat": ".0f"},
    title = {"text": "SX员工数"},
    align="center",
    ))
staff_number_indicator_sx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator_sx.update_layout(
    height=150,width=165,
)

staff_number_indicator_sx_ibg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff_sx_ibg.员工姓名),
    delta = {"reference": len(last_mon_staff_sx_ibg.员工姓名), "valueformat": ".0f"},
    title = {"text": "IBG员工数"},
    align="center",
    ))
staff_number_indicator_sx_ibg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator_sx_ibg.update_layout(
    height=150,width=165,
)


staff_number_indicator_sx_abg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff_sx_abg.员工姓名),
    delta = {"reference": len(last_mon_staff_sx_abg.员工姓名), "valueformat": ".0f"},
    title = {"text": "ABG员工数"},
    align="center",
    ))
staff_number_indicator_sx_abg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator_sx_abg.update_layout(
    height=150,width=165,
)

staff_number_indicator_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff_ir.员工姓名),
    delta = {"reference": len(cur_mon_staff_ir.员工姓名), "valueformat": ".0f"},
    title = {"text": "IR员工数"},
    align="center",
    ))
staff_number_indicator_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator_ir.update_layout(
    height=150,width=165,
)


staff_number_indicator_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff_aiot.员工姓名),
    delta = {"reference": len(last_mon_staff_aiot.员工姓名), "valueformat": ".0f"},
    title = {"text": "AIOT员工数"},
    align="center",
    ))
staff_number_indicator_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator_aiot.update_layout(
    height=150,width=165,
)


staff_number_indicator_dx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff_dx.员工姓名),
    delta = {"reference": len(last_mon_staff_dx.员工姓名), "valueformat": ".0f"},
    title = {"text": "DX员工数"},
    align="center",
    ))
staff_number_indicator_dx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator_dx.update_layout(
    height=150,width=165,
)


staff_number_indicator_dx_ty = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff_dx_ty.员工姓名),
    delta = {"reference": len(cur_mon_staff_dx_ty.员工姓名), "valueformat": ".0f"},
    title = {"text": "体育员工数"},
    align="center",
    ))
staff_number_indicator_dx_ty.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator_dx_ty.update_layout(
    height=150,width=165,
)

staff_number_indicator_dx_sku = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff_dx_sku.员工姓名),
    delta = {"reference": len(last_mon_staff_dx_sku.员工姓名), "valueformat": ".0f"},
    title = {"text": "冰箱员工数"},
    align="center",
    ))
staff_number_indicator_dx_sku.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator_dx_sku.update_layout(
    height=150,width=165,
)


staff_number_indicator_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff_si.员工姓名),
    delta = {"reference": len(last_mon_staff_si.员工姓名), "valueformat": ".0f"},
    title = {"text": "SI员工数"},
    align="center",
    ))
staff_number_indicator_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator_si.update_layout(
    height=150,width=165,
)


staff_number_indicator_sx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = len(cur_mon_staff_sx.员工姓名),
    delta = {"reference": len(last_mon_staff_sx.员工姓名), "valueformat": ".0f"},
    title = {"text": "SX员工数"},
    align="center",
    ))
staff_number_indicator_sx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
staff_number_indicator_sx.update_layout(
    height=150,width=165,
)

cur_actual_indicator_sx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SX')]['实际人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SX')]['实际人天'].sum(), "valueformat": ".0f"},
    title = {"text": "实际人天"},
    align="center",
    ))
cur_actual_indicator_sx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_indicator_sx.update_layout(
    height=150,width=165,
)


cur_actual_indicator_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('IR')]['实际人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('IR')]['实际人天'].sum(), "valueformat": ".0f"},
    title = {"text": "实际人天"},
    align="center",
    ))
cur_actual_indicator_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_indicator_ir.update_layout(
    height=150,width=165,
)

cur_actual_indicator_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('AIOT')]['实际人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('AIOT')]['实际人天'].sum(), "valueformat": ".0f"},
    title = {"text": "实际人天"},
    align="center",
    ))
cur_actual_indicator_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_indicator_aiot.update_layout(
    height=150,width=165,
)

cur_actual_indicator_dx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX')]['实际人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX')]['实际人天'].sum(), "valueformat": ".0f"},
    title = {"text": "实际人天"},
    align="center",
    ))
cur_actual_indicator_dx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_indicator_dx.update_layout(
    height=150,width=165,
)


cur_actual_indicator_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SI')]['实际人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SI')]['实际人天'].sum(), "valueformat": ".0f"},
    title = {"text": "实际人天"},
    align="center",
    ))
cur_actual_indicator_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_indicator_si.update_layout(
    height=150,width=165,
)



cur_actual_avg_indicator_sx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SX')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SX')]['员工数'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SX')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SX')]['员工数'].sum(), "valueformat": ".0f"},
    title = {"text": "实际人均"},
    align="center",
    ))
cur_actual_avg_indicator_sx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_avg_indicator_sx.update_layout(
    height=150,width=165,
)


cur_actual_avg_indicator_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('IR')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('IR')]['员工数'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('IR')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('IR')]['员工数'].sum(), "valueformat": ".0f"},
    title = {"text": "实际人均"},
    align="center",
    ))
cur_actual_avg_indicator_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_avg_indicator_ir.update_layout(
    height=150,width=165,
)


cur_actual_avg_indicator_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('AIOT')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('AIOT')]['员工数'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('AIOT')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('AIOT')]['员工数'].sum(), "valueformat": ".0f"},
    title = {"text": "实际人均"},
    align="center",
    ))
cur_actual_avg_indicator_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_avg_indicator_aiot.update_layout(
    height=150,width=165,
)

cur_actual_avg_indicator_dx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX')]['员工数'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX')]['员工数'].sum(), "valueformat": ".0f"},
    title = {"text": "实际人均"},
    align="center",
    ))
cur_actual_avg_indicator_dx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_avg_indicator_dx.update_layout(
    height=150,width=165,
)

cur_actual_avg_indicator_dx_ty = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX-TY')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX-TY')]['员工数'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX-TY')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX-TY')]['员工数'].sum(), "valueformat": ".0f"},
    title = {"text": "体育实际人均"},
    align="center",
    ))
cur_actual_avg_indicator_dx_ty.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_avg_indicator_dx_ty.update_layout(
    height=150,width=165,
)

cur_actual_avg_indicator_dx_sku = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX-SKU')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX-SKU')]['员工数'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX-SKU')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX-SKU')]['员工数'].sum(), "valueformat": ".0f"},
    title = {"text": "冰箱实际人均"},
    align="center",
    ))
cur_actual_avg_indicator_dx_sku.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_avg_indicator_dx_sku.update_layout(
    height=150,width=165,
)

cur_actual_avg_indicator_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SI')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SI')]['员工数'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SI')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SI')]['员工数'].sum(), "valueformat": ".0f"},
    title = {"text": "实际人均"},
    align="center",
    ))
cur_actual_avg_indicator_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_avg_indicator_si.update_layout(
    height=150,width=165,
)


cur_est_indicator_sx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SX')]['预估人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SX')]['预估人天'].sum(), "valueformat": ".0f"},
    title = {"text": "预估人天"},
    align="center",
    ))
cur_est_indicator_sx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_indicator_sx.update_layout(
    height=150,width=165,
)


cur_est_indicator_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('IR')]['预估人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('IR')]['预估人天'].sum(), "valueformat": ".0f"},
    title = {"text": "预估人天"},
    align="center",
    ))
cur_est_indicator_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_indicator_ir.update_layout(
    height=150,width=165,
)

cur_est_indicator_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('AIOT')]['预估人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('AIOT')]['预估人天'].sum(), "valueformat": ".0f"},
    title = {"text": "预估人天"},
    align="center",
    ))
cur_est_indicator_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_indicator_aiot.update_layout(
    height=150,width=165,
)

cur_est_indicator_dx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX')]['预估人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX')]['预估人天'].sum(), "valueformat": ".0f"},
    title = {"text": "预估人天"},
    align="center",
    ))
cur_est_indicator_dx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_indicator_dx.update_layout(
    height=150,width=165,
)


cur_est_indicator_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SI')]['预估人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SI')]['预估人天'].sum(), "valueformat": ".0f"},
    title = {"text": "预估人天"},
    align="center",
    ))
cur_est_indicator_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_indicator_si.update_layout(
    height=150,width=165,
)


cur_est_rate_indicator_sx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SX')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SX')]['预估人天'].sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SX')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SX')]['预估人天'].sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "预估填报率"},
    align="center",
    ))
cur_est_rate_indicator_sx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_rate_indicator_sx.update_layout(
    height=150,width=165,
)


cur_est_rate_indicator_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('IR')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('IR')]['预估人天'].sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('IR')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('IR')]['预估人天'].sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "预估填报率"},
    align="center",
    ))
cur_est_rate_indicator_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_rate_indicator_ir.update_layout(
    height=150,width=165,
)

cur_est_rate_indicator_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('AIOT')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('AIOT')]['预估人天'].sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('AIOT')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('AIOT')]['预估人天'].sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "预估填报率"},
    align="center",
    ))
cur_est_rate_indicator_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_rate_indicator_aiot.update_layout(
    height=150,width=165,
)

cur_est_rate_indicator_dx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX')]['预估人天'].sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX')]['预估人天'].sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "预估填报率"},
    align="center",
    ))
cur_est_rate_indicator_dx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_rate_indicator_dx.update_layout(
    height=150,width=165,
)


cur_est_rate_indicator_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SI')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SI')]['预估人天'].sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SI')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SI')]['预估人天'].sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "预估填报率"},
    align="center",
    ))
cur_est_rate_indicator_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_rate_indicator_si.update_layout(
    height=150,width=165,
)


cur_logic_indicator_sx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SX')]['理论人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SX')]['理论人天'].sum(), "valueformat": ".0f"},
    title = {"text": "理论人天"},
    align="center",
    ))
cur_logic_indicator_sx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_indicator_sx.update_layout(
    height=150,width=165,
)


cur_logic_indicator_dx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX')]['理论人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX')]['理论人天'].sum(), "valueformat": ".0f"},
    title = {"text": "理论人天"},
    align="center",
    ))
cur_logic_indicator_dx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_indicator_dx.update_layout(
    height=150,width=165,
)

cur_logic_indicator_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('AIOT')]['理论人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('AIOT')]['理论人天'].sum(), "valueformat": ".0f"},
    title = {"text": "理论人天"},
    align="center",
    ))
cur_logic_indicator_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_indicator_aiot.update_layout(
    height=150,width=165,
)

cur_logic_indicator_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('IR')]['理论人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('IR')]['理论人天'].sum(), "valueformat": ".0f"},
    title = {"text": "理论人天"},
    align="center",
    ))
cur_logic_indicator_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_indicator_ir.update_layout(
    height=150,width=165,
)


cur_logic_indicator_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SI')]['理论人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SI')]['理论人天'].sum(), "valueformat": ".0f"},
    title = {"text": "理论人天"},
    align="center",
    ))
cur_logic_indicator_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_indicator_si.update_layout(
    height=150,width=165,
)


cur_logic_avg_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('AIOT')]['理论人均人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('AIOT')]['理论人均人天'].sum(), "valueformat": ".0f"},
    title = {"text": "理论人均"},
    align="center",
    ))
cur_logic_avg_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_avg_aiot.update_layout(
    height=150,width=165,
)


cur_logic_avg_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('IR')]['理论人均人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('IR')]['理论人均人天'].sum(), "valueformat": ".0f"},
    title = {"text": "理论人均"},
    align="center",
    ))
cur_logic_avg_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_avg_ir.update_layout(
    height=150,width=165,
)


cur_logic_avg_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SI')]['理论人均人天'].sum(),
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SI')]['理论人均人天'].sum(), "valueformat": ".0f"},
    title = {"text": "理论人均"},
    align="center",
    ))
cur_logic_avg_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_avg_si.update_layout(
    height=150,width=165,
)


cur_logic_rate_indicator_sx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SX')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SX')]['理论人天'].sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SX')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SX')]['理论人天'].sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "理论填报率"},
    align="center",
    ))
cur_logic_rate_indicator_sx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_rate_indicator_sx.update_layout(
    height=150,width=165,
)

cur_logic_rate_indicator_dx = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('DX')]['理论人天'].sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('DX')]['理论人天'].sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "理论填报率"},
    align="center",
    ))
cur_logic_rate_indicator_dx.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_rate_indicator_dx.update_layout(
    height=150,width=165,
)

cur_logic_rate_indicator_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('IR')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('IR')]['理论人天'].sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('IR')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('IR')]['理论人天'].sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "理论填报率"},
    align="center",
    ))
cur_logic_rate_indicator_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_rate_indicator_ir.update_layout(
    height=150,width=165,
)

cur_logic_rate_indicator_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('AIOT')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('AIOT')]['理论人天'].sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('AIOT')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('AIOT')]['理论人天'].sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "理论填报率"},
    align="center",
    ))
cur_logic_rate_indicator_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_rate_indicator_aiot.update_layout(
    height=150,width=165,
)

cur_logic_rate_indicator_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SI')]['实际人天'].sum()/cur_bus_line_summary[cur_bus_line_summary['业务线'].str.contains('SI')]['理论人天'].sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SI')]['实际人天'].sum()/last_bus_line_summary[last_bus_line_summary['业务线'].str.contains('SI')]['理论人天'].sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "理论填报率"},
    align="center",
    ))
cur_logic_rate_indicator_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_logic_rate_indicator_si.update_layout(
    height=150,width=165,
)


cur_est_avg_sx_ibg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'SX-IBG']['预估人均人天'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'SX-IBG']['预估人均人天'].values[0], "valueformat": ".0f"},
    title = {"text": "IBG预估人均"},
    align="center",
    ))
cur_est_avg_sx_ibg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_avg_sx_ibg.update_layout(
    height=150,width=165,
)


cur_est_avg_sx_abg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'SX-ABG']['预估人均人天'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'SX-ABG']['预估人均人天'].values[0], "valueformat": ".0f"},
    title = {"text": "ABG预估人均"},
    align="center",
    ))
cur_est_avg_sx_abg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_avg_sx_abg.update_layout(
    height=150,width=165,
)


cur_est_avg_dx_ty = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'DX-TY']['预估人均人天'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'DX-TY']['预估人均人天'].values[0], "valueformat": ".0f"},
    title = {"text": "体育预估人均"},
    align="center",
    ))
cur_est_avg_dx_ty.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_avg_dx_ty.update_layout(
    height=150,width=165,
)

cur_est_avg_dx_sku = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'DX-SKU']['预估人均人天'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'DX-SKU']['预估人均人天'].values[0], "valueformat": ".0f"},
    title = {"text": "冰箱预估人均"},
    align="center",
    ))
cur_est_avg_dx_sku.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_avg_dx_sku.update_layout(
    height=150,width=165,
)


cur_est_avg_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'IR']['预估人均人天'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'IR']['预估人均人天'].values[0], "valueformat": ".0f"},
    title = {"text": "预估人均"},
    align="center",
    ))
cur_est_avg_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_avg_ir.update_layout(
    height=150,width=165,
)

cur_est_avg_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'AIOT']['预估人均人天'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'AIOT']['预估人均人天'].values[0], "valueformat": ".0f"},
    title = {"text": "预估人均"},
    align="center",
    ))
cur_est_avg_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_avg_aiot.update_layout(
    height=150,width=165,
)

cur_est_avg_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'SI']['预估人均人天'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'SI']['预估人均人天'].values[0], "valueformat": ".0f"},
    title = {"text": "预估人均"},
    align="center",
    ))
cur_est_avg_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_est_avg_si.update_layout(
    height=150,width=165,
)



cur_actual_avg_sx_ibg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'SX-IBG']['实际人均人天'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'SX-IBG']['实际人均人天'].values[0], "valueformat": ".0f"},
    title = {"text": "IBG实际人均"},
    align="center",
    ))
cur_actual_avg_sx_ibg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_avg_sx_ibg.update_layout(
    height=150,width=165,
)

cur_actual_avg_sx_abg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'SX-ABG']['实际人均人天'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'SX-ABG']['实际人均人天'].values[0], "valueformat": ".0f"},
    title = {"text": "ABG实际人均"},
    align="center",
    ))
cur_actual_avg_sx_abg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_actual_avg_sx_abg.update_layout(
    height=150,width=165,
)


cur_act_logic_gap_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'AIOT']['实际-理论差'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'AIOT']['实际-理论差'].values[0], "valueformat": ".0f"},
    title = {"text": "实际理论Gap"},
    align="center",
    ))
cur_act_logic_gap_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_act_logic_gap_aiot.update_layout(
    height=150,width=165,
)

cur_act_logic_gap_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'IR']['实际-理论差'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'IR']['实际-理论差'].values[0], "valueformat": ".0f"},
    title = {"text": "实际理论Gap"},
    align="center",
    ))
cur_act_logic_gap_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_act_logic_gap_ir.update_layout(
    height=150,width=165,
)

cur_act_logic_gap_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = cur_bus_line_summary[cur_bus_line_summary['业务线'] == 'SI']['实际-理论差'].values[0],
    delta = {"reference": last_bus_line_summary[last_bus_line_summary['业务线'] == 'SI']['实际-理论差'].values[0], "valueformat": ".0f"},
    title = {"text": "实际理论Gap"},
    align="center",
    ))
cur_act_logic_gap_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_act_logic_gap_si.update_layout(
    height=150,width=165,
)

def try_except(value, default):
    try:
        return value
    except KeyError:
        return default


cur_mon_staff_under_est_ibg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SX-IBG']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SX-IBG']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "IBG预估不满数"},
    align="center",
    ))
cur_mon_staff_under_est_ibg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_est_ibg.update_layout(
    height=150,width=165,
)

cur_mon_staff_under_est_abg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SX-ABG']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SX-ABG']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "ABG预估不满数"},
    align="center",
    ))
cur_mon_staff_under_est_abg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_est_abg.update_layout(
    height=150,width=165,
)


cur_mon_staff_under_est_dx_ty = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'DX-TY']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'DX-TY']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "体育预估不满数"},
    align="center",
    ))
cur_mon_staff_under_est_dx_ty.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_est_dx_ty.update_layout(
    height=150,width=165,
)


cur_mon_staff_under_est_dx_sku = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'DX-SKU']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'DX-SKU']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "冰箱预估不满数"},
    align="center",
    ))
cur_mon_staff_under_est_dx_sku.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_est_dx_sku.update_layout(
    height=150,width=165,
)


cur_mon_staff_under_est_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'AIOT']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'AIOT']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "预估不满数"},
    align="center",
    ))
cur_mon_staff_under_est_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_est_aiot.update_layout(
    height=150,width=165,
)


cur_mon_staff_under_est_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'IR']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'IR']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "预估不满数"},
    align="center",
    ))
cur_mon_staff_under_est_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_est_ir.update_layout(
    height=150,width=165,
)

cur_mon_staff_under_est_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SI']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SI']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "预估不满数"},
    align="center",
    ))
cur_mon_staff_under_est_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_est_si.update_layout(
    height=150,width=165,
)


cur_mon_staff_over_est_ibg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SX-IBG']['预估填报'].value_counts()['超载'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SX-IBG']['预估填报'].value_counts()['超载'], 0), "valueformat": ".0f"},
    title = {"text": "IBG预估超载数"},
    align="center",
    ))
cur_mon_staff_over_est_ibg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_est_ibg.update_layout(
    height=150,width=165,
)

cur_mon_staff_over_est_abg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SX-ABG']['预估填报'].value_counts()['超载'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SX-ABG']['预估填报'].value_counts()['超载'], 0), "valueformat": ".0f"},
    title = {"text": "ABG预估超载数"},
    align="center",
    ))
cur_mon_staff_over_est_abg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_est_abg.update_layout(
    height=150,width=165,
)


#######to over

cur_mon_staff_over_est_dx_ty = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'DX-TY']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'DX-TY']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "体育预估超载数"},
    align="center",
    ))
cur_mon_staff_over_est_dx_ty.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_est_dx_ty.update_layout(
    height=150,width=165,
)

########to over est
cur_mon_staff_over_est_dx_sku = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'DX-SKU']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'DX-SKU']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "冰箱预估超载数"},
    align="center",
    ))
cur_mon_staff_over_est_dx_sku.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_est_dx_sku.update_layout(
    height=150,width=165,
)


cur_mon_staff_over_est_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'IR']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'IR']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "预估超载数"},
    align="center",
    ))
cur_mon_staff_over_est_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_est_ir.update_layout(
    height=150,width=165,
)


cur_mon_staff_over_est_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'AIOT']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'AIOT']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "预估超载数"},
    align="center",
    ))
cur_mon_staff_over_est_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_est_aiot.update_layout(
    height=150,width=165,
)


cur_mon_staff_over_est_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SI']['预估填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SI']['预估填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "预估超载数"},
    align="center",
    ))
cur_mon_staff_over_est_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_est_si.update_layout(
    height=150,width=165,
)


cur_mon_staff_under_logic_ibg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SX-IBG']['理论填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SX-IBG']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "IBG理论不满数"},
    align="center",
    ))
cur_mon_staff_under_logic_ibg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_logic_ibg.update_layout(
    height=150,width=165,
)


cur_mon_staff_under_logic_abg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SX-ABG']['理论填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SX-ABG']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "ABG理论不满数"},
    align="center",
    ))
cur_mon_staff_under_logic_abg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_logic_abg.update_layout(
    height=150,width=165,
)


cur_mon_staff_under_logic_dx_ty = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'DX-TY']['理论填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'DX-TY']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "体育理论不满数"},
    align="center",
    ))
cur_mon_staff_under_logic_dx_ty.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_logic_dx_ty.update_layout(
    height=150,width=165,
)

cur_mon_staff_under_logic_dx_sku = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'DX-SKU']['理论填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'DX-SKU']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "冰箱理论不满数"},
    align="center",
    ))
cur_mon_staff_under_logic_dx_sku.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_logic_dx_sku.update_layout(
    height=150,width=165,
)

cur_mon_staff_under_logic_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'IR']['理论填报'].value_counts()['合理'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'IR']['理论填报'].value_counts()['合理'], 0), "valueformat": ".0f"},
    title = {"text": "理论不满数"},
    align="center",
    ))
cur_mon_staff_under_logic_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_logic_ir.update_layout(
    height=150,width=165,
)

cur_mon_staff_under_logic_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'AIOT']['理论填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'AIOT']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "理论不满数"},
    align="center",
    ))
cur_mon_staff_under_logic_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_logic_aiot.update_layout(
    height=150,width=165,
)


cur_mon_staff_under_logic_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SI']['理论填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SI']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "理论不满数"},
    align="center",
    ))
cur_mon_staff_under_logic_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_under_logic_si.update_layout(
    height=150,width=165,
)

cur_mon_staff_over_logic_ibg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SX-IBG']['理论填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SX-IBG']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "IBG理论超载数"},
    align="center",
    ))
cur_mon_staff_over_logic_ibg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_logic_ibg.update_layout(
    height=150,width=165,
)


cur_mon_staff_over_logic_abg = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SX-ABG']['理论填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SX-ABG']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "ABG理论超载数"},
    align="center",
    ))
cur_mon_staff_over_logic_abg.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_logic_abg.update_layout(
    height=150,width=165,
)


cur_mon_staff_over_logic_dx_ty = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'DX-TY']['理论填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'DX-TY']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "体育理论超载数"},
    align="center",
    ))
cur_mon_staff_over_logic_dx_ty.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_logic_dx_ty.update_layout(
    height=150,width=165,
)


cur_mon_staff_over_logic_dx_sku = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'DX-SKU']['理论填报'].value_counts()['不满'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'DX-SKU']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "冰箱理论超载数"},
    align="center",
    ))
cur_mon_staff_over_logic_dx_sku.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_logic_dx_sku.update_layout(
    height=150,width=165,
)

###########over
cur_mon_staff_over_logic_ir = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'IR']['理论填报'].value_counts()['合理'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'IR']['理论填报'].value_counts()['合理'], 0), "valueformat": ".0f"},
    title = {"text": "理论超载数"},
    align="center",
    ))
cur_mon_staff_over_logic_ir.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_logic_ir.update_layout(
    height=150,width=165,
)

###########
cur_mon_staff_over_logic_aiot = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'AIOT']['理论填报'].value_counts()['合理'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'AIOT']['理论填报'].value_counts()['合理'], 0), "valueformat": ".0f"},
    title = {"text": "理论超载数"},
    align="center",
    ))
cur_mon_staff_over_logic_aiot.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_logic_aiot.update_layout(
    height=150,width=165,
)

#########3
cur_mon_staff_over_logic_si = go.Figure(go.Indicator(
    mode = "number+delta",
    value = try_except(cur_mon_staff[cur_mon_staff['业务线'] == 'SI']['理论填报'].value_counts()['合理'], 0),
    delta = {"reference": try_except(last_mon_staff[last_mon_staff['业务线'] == 'SI']['理论填报'].value_counts()['不满'], 0), "valueformat": ".0f"},
    title = {"text": "理论超载数"},
    align="center",
    ))
cur_mon_staff_over_logic_si.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
cur_mon_staff_over_logic_si.update_layout(
    height=150,width=165,
)




# actual all day
act_allday = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_mon_staff.实际人天.sum(),1),
    delta = {"reference": round(last_mon_staff.实际人天.sum(),1), "valueformat": ".0f"},
    title = {"text": "实际人天"},
    align="center",
    ))
act_allday.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
act_allday.update_layout(
    height=150,width=165
)

# actural per day
act_perday = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_mon_staff.实际人天.sum()/len(cur_mon_staff.员工姓名),1),
    delta = {"reference": round(last_mon_staff.实际人天.sum()/len(last_mon_staff.员工姓名),1), "valueformat": ".0f"},
    title = {"text": "实际人均"},
    align="center",
    ))
act_perday.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
act_perday.update_layout(
    height=150,width=165
)

# est all day
est_allday = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_mon_staff.预估人天.sum(),1),
    delta = {"reference": round(last_mon_staff.预估人天.sum(),1), "valueformat": ".0f"},
    title = {"text": "预估人天"},
    align="center",
    ))
est_allday.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
est_allday.update_layout(
    height=150,width=165
)

# est fill rate
est_percentage = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_mon_staff.实际人天.sum()/cur_mon_staff.预估人天.sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_mon_staff.实际人天.sum()/last_mon_staff.预估人天.sum()*100,1), "valueformat": ".0f", "suffix": "%"},
    title = {"text": "预估填报率"},
    align="center",
    ))
est_percentage.update_traces(
    delta_font_size=15,number_font_size=30,title_font_size=15
)
est_percentage.update_layout(
    height=150,width=165
)


# logic all day
logic_allday = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_mon_staff.理论人天.sum(),1),
    delta = {"reference": round(last_mon_staff.理论人天.sum(),1), "valueformat": ".0f"},
    title = {"text": "理论人天"},
    align="center",
    ))
logic_allday.update_traces(
    domain_column=1, domain_row=3,delta_font_size=15,number_font_size=30,title_font_size=15
)
logic_allday.update_layout(
    height=150,width=165
)

# logic  fill rate
logic_percentage = go.Figure(go.Indicator(
    mode = "number+delta",
    value = round(cur_mon_staff.实际人天.sum()/cur_mon_staff.理论人天.sum()*100,1),
    number={"suffix": "%"},
    delta = {"reference": round(last_mon_staff.实际人天.sum()/last_mon_staff.理论人天.sum()*100,1), "valueformat": ".0f","suffix": "%"},
    title = {"text": "理论填报率"},
    align="center",
    ))
logic_percentage.update_traces(
    delta_font_size=15,number_font_size=30,title_font_size=15
)
logic_percentage.update_layout(
    height=150,width=165
)


# graph staff apartment
fig员工所属部门汇总 = go.Figure()
fig员工所属部门汇总.add_bar(x=list(员工所属部门汇总1.员工所属部门)
                            , y=list(员工所属部门汇总1.预估人天)
                            , name="预估人天")
fig员工所属部门汇总.add_bar(x=list(员工所属部门汇总1.员工所属部门)
                            , y=list(员工所属部门汇总1.理论人天)
                            , name="理论人天")
fig员工所属部门汇总.add_trace(
    go.Scatter(x=list(员工所属部门汇总1.员工所属部门), y=list(员工所属部门汇总1.实际人天), mode='markers',
               name='实际人天', marker=dict(
            color='LightSkyBlue', size=10,
            line=dict(
                color='MediumPurple',
                width=2))))
fig员工所属部门汇总.update_layout(title='员工所属部门总工时', template='plotly_white', yaxis_title='总工时/小时')

fig员工所属部门人均人天 = go.Figure()
fig员工所属部门人均人天.add_bar(x=list(员工所属部门汇总1.员工所属部门)
                                , y=list(员工所属部门汇总1.预估人均人天)
                                , name="预估人均人天")
fig员工所属部门人均人天.add_bar(x=list(员工所属部门汇总1.员工所属部门)
                                , y=list(员工所属部门汇总1.实际人均人天)
                                , name="实际人均人天")
fig员工所属部门人均人天.add_bar(x=list(员工所属部门汇总1.员工所属部门)
                                , y=list(员工所属部门汇总1.理论人均人天)
                                , name="理论人均人天")
fig员工所属部门人均人天.add_trace(go.Scatter(
    x=list(员工所属部门汇总1.员工所属部门),
    y=list(员工所属部门汇总1.部门实际人均人天),
    mode="markers+lines",
    name="部门实际人均人天",
    line=dict(
        color="black")))
fig员工所属部门人均人天.update_layout(title='员工所属部门人均人天', template='plotly_white', yaxis_title='人均人天')

fig员工所属部门实际填报率 = go.Figure()
fig员工所属部门实际填报率.add_trace(
    go.Scatter(x=list(员工所属部门汇总1.员工所属部门), y=list(员工所属部门汇总1.预估填报率),
               mode="markers+lines", name="预估填报率", line=dict(color="blue")))
fig员工所属部门实际填报率.add_trace(
    go.Scatter(x=list(员工所属部门汇总1.员工所属部门), y=list(员工所属部门汇总1.理论填报率),
               mode="markers+lines", name="理论填报率", line=dict(color="red")))
fig员工所属部门实际填报率.update_layout(title='员工所属部门预估实际填报率', template='plotly_white',
                                        yaxis_title='工时填报率%')


# fig = px.line(df, x="月份", y="lifeExp", color='country')


fig业务线 = px.bar(预计实际业务线汇总, x="工时类别", y="总工时", facet_col="业务线", color="员工组")
fig业务线.update_layout(title='业务线员工组工时', yaxis_title='总工时/小时')
fig业务线.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))


labels = list(实际业务线pie['实际人天'].keys())
fig业务线pie = make_subplots(rows=1, cols=3, specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]])
fig业务线pie.add_trace(go.Pie(labels=labels, values=list(预估业务线pie['预估人天']), name="预估"), 1, 1)
fig业务线pie.add_trace(go.Pie(labels=labels, values=list(实际业务线pie['实际人天']), name="实际"), 1, 2)
fig业务线pie.add_trace(go.Pie(labels=labels, values=list(理论业务线pie['理论人天']), name="理论"), 1, 3)
fig业务线pie.update_traces(hole=.4, hoverinfo="label+percent+name")
fig业务线pie.update_traces(textposition='inside')
fig业务线pie.update_layout(uniformtext_minsize=12, uniformtext_mode='hide',
                           title_text="业务线总工时",
                           annotations=[dict(text='预估', x=0.125, y=0.5, font_size=20, showarrow=False),
                                        dict(text='实际', font_size=20, showarrow=False),
                                        dict(text='理论', x=0.875, y=0.5, font_size=20, showarrow=False)])



fig全量实际vs预估人天 = px.scatter(cur_mon_staff, x="实际人天", y="预估人天", color="业务线",
                 size='实际人天', hover_data=['员工姓名'])

fig全量实际vs预估人天.update_layout(
    title='员工"实际人天"v."预估人天"by业务线',
    xaxis=dict(
        title='实际人天',
        gridcolor='white',
#         type='log',
        gridwidth=2,
    ),
    yaxis=dict(
        title='预估人天',
        gridcolor='white',
        gridwidth=2,
    ),
)

fig全量实际vs理论人天 = px.scatter(cur_mon_staff, x="实际人天", y="理论人天", color="业务线",
                 size='实际人天', hover_data=['员工姓名'])

fig全量实际vs理论人天.update_layout(
    title='员工"实际人天"v."理论人天"by业务线',
    xaxis=dict(
        title='实际人天',
        gridcolor='white',
#         type='log',
        gridwidth=2,
    ),
    yaxis=dict(
        title='理论人天',
        gridcolor='white',
        gridwidth=2,
    ),
)

fig历史实际人均人天 = px.line(all_actual_days, x="月份", y=all_actual_days.columns,
              hover_data={"月份": "|%B, %Y"},
              title='员工所属部门实际人均人天趋势')

app.layout = dbc.Container([
    # dbc.Row([
    #     html.Div([
    #         className="alert alert-dismissible alert-info",
    #         html.Button([
    #             className="btn-close",
    #             data-bs-dismiss="alert",
    #         ])
    #     ])
    # ]),
    dbc.Row([
        dbc.Col(
            dbc.Row([
                html.Img(src=app.get_asset_url("dash-logo.png"), id="plotly-image",
                         style={"height": "60px", "width": "auto"}),
                html.P(" Updated at "+ updatedDate)
            ]), width=3
        ),

        dbc.Col([
            dcc.Tabs(id="tabs-title", value='IRDC', children=[
                dcc.Tab(label='IRDC', value='IRDC', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='SX', value='SX', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='IR', value='IR', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='AIOT', value='AIOT', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='DX', value='DX', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='SI', value='SI', style=tab_style, selected_style=tab_selected_style),
            ])
        ], width=9)
    ]),
    dbc.Row([
        dbc.Col(
            html.Div([
                html.Br(),
                html.Div(children='''
                1、数据来源：10月26日-11月25日内OA工时填报已报送工时，中国内地全勤23人天，新加坡全勤23人天 ;'''),
                html.Div(children='''
                2、人员构成：部门正式员工、人力外包、实习生（不含外部门人员、项目外包成员、当月入离职员工）;'''),
                html.Div(children='''
                3、数据定义：理论工时，部门人数*当月工作日天数；实际工时，OA工时填报已报送工时；预计工时，PM对项目当月做出的工时预估。'''),
                html.Br(),
            ])
        )
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='tabs-content')
        ])
    ])
], fluid=True)


@app.callback(Output('tabs-content', 'children'),
              Input('tabs-title', 'value'))
def render_content(tab):
    if tab == 'IRDC':
        return dbc.Container([
            html.P("人员维度Summary"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator', figure=staff_number_indicator,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color":"#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width":"165px"
                               }
                )]),
                dbc.Col([
                    dcc.Graph(id='act_allday', figure=act_allday,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='act_perday', figure=act_perday,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='est_allday', figure=est_allday,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='est_percentage', figure=est_percentage,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='logic_allday', figure=logic_allday,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='logic_percentage', figure=logic_percentage,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),

            ]),
            html.P("WBS维度Summary（数据未更新）"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator', figure=staff_number_indicator,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='act_allday', figure=act_allday, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='act_perday', figure=act_perday, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='est_allday', figure=est_allday, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='est_percentage', figure=est_percentage, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='logic_allday', figure=logic_allday, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='logic_percentage', figure=logic_percentage, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),

            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='员工所属部门汇总-summary', figure=fig员工所属部门汇总,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "15px"
                                     }
                              ),
                ], xs=12, sm=12, md=6, lg=6, xl=6),
                dbc.Col([
                    dcc.Graph(id='员工所属部门汇总-bar', figure=fig员工所属部门人均人天,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "15px"
                                     }
                              ),
                ], xs=12, sm=12, md=6, lg=6, xl=6),
                dbc.Col([
                    dcc.Graph(id="历史部门实际人均人天-line", figure=fig历史实际人均人天,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "15px"
                                     }
                              ),
                ]),
                dbc.Col([
                    dcc.Graph(id='员工所属部门汇总-line', figure=fig员工所属部门实际填报率,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "15px"
                                     }
                              ),
                html.Br(),
                ]),
            ]),
            dbc.Row([
                html.Div([
                    dbc.Button(
                        "查看数据原表",
                        id="collapse-button",
                        className="mb-3",
                        color="info",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dash_table.DataTable(
                            id="staff_apartment_tb",
                            columns=[{"name": i, "id": i,} for i in staff_apartment_tb.columns],
                            sort_action="native",
                            sort_mode="multi",
                            data=staff_apartment_tb.to_dict('records'),
                            style_header={
                                'backgroundColor': 'rgb(210, 210, 210)',
                                'color': 'black',
                                'fontWeight': 'bold',
                                'border': '1px solid white'
                            },
                            style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{预估填报} = 不满',
                                        'column_id': '预估填报'
                                    },
                                    'color': 'orange',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{理论填报} = 不满',
                                        'column_id': '理论填报'
                                    },
                                    'color': 'orange',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{预估填报} = 超载',
                                        'column_id': '预估填报'
                                    },
                                    'color': 'tomato',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{理论填报} = 超载',
                                        'column_id': '理论填报'
                                    },
                                    'color': 'tomato',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{预估填报} = 合理',
                                        'column_id': '预估填报'
                                    },
                                    'color': 'green',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{理论填报} = 合理',
                                        'column_id': '理论填报'
                                    },
                                    'color': 'green',
                                    'fontWeight': 'bold'
                                }
                            ],
                            style_cell={'border': '1px solid lightgrey'}
                        ),
                        is_open=False,
                        id="collapse"
                    ),
                ]),
                html.Br(),
            ]),
            html.Br(),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='业务线汇总-pie', figure=fig业务线pie, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "15px"
                                     }
                              ),


                    dbc.Row([
                        html.Div([
                            dbc.Button(
                                "查看数据原表",
                                id="collapse-button2",
                                className="mb-3",
                                color="info",
                                n_clicks=0,
                            ),
                            dbc.Collapse(
                                dash_table.DataTable(
                                    id="business_line_tb",
                                    columns=[{"name": i, "id": i, } for i in business_line_tb.columns],
                                    sort_action="native",
                                    sort_mode="multi",
                                    data=business_line_tb.to_dict('records'),
                                    style_header={
                                        'backgroundColor': 'rgb(210, 210, 210)',
                                        'color': 'black',
                                        'fontWeight': 'bold',
                                        'border': '1px solid white'
                                    },
                                    style_data_conditional=[
                                        {
                                            'if': {
                                                'filter_query': '{预估填报} = 不满',
                                                'column_id': '预估填报'
                                            },
                                            'color': 'orange',
                                            'fontWeight': 'bold'
                                        },
                                        {
                                            'if': {
                                                'filter_query': '{理论填报} = 不满',
                                                'column_id': '理论填报'
                                            },
                                            'color': 'orange',
                                            'fontWeight': 'bold'
                                        },
                                        {
                                            'if': {
                                                'filter_query': '{预估填报} = 超载',
                                                'column_id': '预估填报'
                                            },
                                            'color': 'tomato',
                                            'fontWeight': 'bold'
                                        },
                                        {
                                            'if': {
                                                'filter_query': '{理论填报} = 超载',
                                                'column_id': '理论填报'
                                            },
                                            'color': 'tomato',
                                            'fontWeight': 'bold'
                                        },
                                        {
                                            'if': {
                                                'filter_query': '{预估填报} = 合理',
                                                'column_id': '预估填报'
                                            },
                                            'color': 'green',
                                            'fontWeight': 'bold'
                                        },
                                        {
                                            'if': {
                                                'filter_query': '{理论填报} = 合理',
                                                'column_id': '理论填报'
                                            },
                                            'color': 'green',
                                            'fontWeight': 'bold'
                                        }
                                    ],
                                    style_cell={'border': '1px solid lightgrey'}
                                ),
                                is_open=False,
                                id="collapse2"
                            ),
                        ]),
                        html.Br(),
                    ]),
                    html.Br(),
                    dcc.Graph(id='业务线汇总-bar', figure=fig业务线,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "15px"
                                     }
                              ),


                ])
            ]),


            dbc.Row([
                html.Div([
                    dbc.Button(
                        "查看数据原表",
                        id="collapse-button4",
                        className="mb-3",
                        color="info",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dash_table.DataTable(
                            id="business_line_staff_type_detailed",
                            columns=[{"name": i, "id": i, } for i in business_line_staff_type.columns],
                            sort_action="native",
                            sort_mode="multi",
                            data=business_line_staff_type.to_dict('records'),
                            style_header={
                                'backgroundColor': 'rgb(210, 210, 210)',
                                'color': 'black',
                                'fontWeight': 'bold',
                                'border': '1px solid white'
                            },
                            style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{预估填报} = 不满',
                                        'column_id': '预估填报'
                                    },
                                    'color': 'orange',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{理论填报} = 不满',
                                        'column_id': '理论填报'
                                    },
                                    'color': 'orange',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{预估填报} = 超载',
                                        'column_id': '预估填报'
                                    },
                                    'color': 'tomato',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{理论填报} = 超载',
                                        'column_id': '理论填报'
                                    },
                                    'color': 'tomato',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{预估填报} = 合理',
                                        'column_id': '预估填报'
                                    },
                                    'color': 'green',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{理论填报} = 合理',
                                        'column_id': '理论填报'
                                    },
                                    'color': 'green',
                                    'fontWeight': 'bold'
                                }
                            ],
                            style_cell={'border': '1px solid lightgrey'}
                        ),
                        is_open=False,
                        id="collapse4"
                    ),
                ]),
                html.Br(),
            ]),
            html.Br(),

            # dbc.Row([
            #     dcc.Graph(id="staff_3d_graph",config={'displayModeBar': False},
            #               style={"border-radius": "5px",
            #                      "background-color": "#f9f9f9",
            #                      "box-shadow": "2px 2px 2px lightgrey",
            #                      "position": "relative",
            #                      "margin-bottom": "15px",
            #                      "height":'800px'
            #                      }
            # ),
            #     html.P("理论填报率:"),
            #     dcc.RangeSlider(
            #         id='range-slider',
            #         min=min(cur_mon_staff['理论填报率']), max=max(cur_mon_staff['理论填报率']), step=5,
            #         marks={min(cur_mon_staff['理论填报率']): min(cur_mon_staff['理论填报率']), max(cur_mon_staff['理论填报率']): max(cur_mon_staff['理论填报率'])},
            #         value = [0, 120]
            #     ),
            # ]),
            # html.Br(),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='fig全量实际vs预估人天-scatter', figure=fig全量实际vs预估人天,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "15px"
                                     }
                              ),
                    html.P("预估填报率:"),
                    dcc.RangeSlider(
                        id='range-slider实际vs预估',
                        min=cur_mon_staff.预估填报率.min(), max=cur_mon_staff.预估填报率.max(), step=1,
                        marks={
                            cur_mon_staff.预估填报率.min(): {'label': str(cur_mon_staff.预估填报率.min()), 'style': {'color': 'orange'}},
                            80: {'label': '80%', 'style': {'color': 'green'}},
                            120: {'label': '120%','style': {'color': 'green'}},
                            cur_mon_staff.预估填报率.max(): {'label': str(cur_mon_staff.预估填报率.max()), 'style': {'color': 'red'}}},
                        value=[cur_mon_staff.预估填报率.min(), cur_mon_staff.预估填报率.max()], allowCross=False, tooltip={"placement": "bottom", "always_visible": True}
                    ),

                ], xs=12, sm=12, md=6, lg=6, xl=6),
                dbc.Col([
                    dcc.Graph(id='fig全量实际vs理论人天-scatter', figure=fig全量实际vs理论人天,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "15px"
                                     }
                              ),
                    html.P("理论填报率:"),
                    dcc.RangeSlider(
                        id='range-slider实际vs理论',
                        min=cur_mon_staff.理论填报率.min(), max=cur_mon_staff.理论填报率.max(), step=1,
                        marks={
                            cur_mon_staff.理论填报率.min(): {'label': str(cur_mon_staff.理论填报率.min()),
                                                             'style': {'color': 'orange'}},
                            90: {'label': '90%', 'style': {'color': 'green'}},
                            120: {'label': '120%', 'style': {'color': 'green'}},
                            cur_mon_staff.理论填报率.max(): {'label': str(cur_mon_staff.理论填报率.max()),
                                                             'style': {'color': 'red'}}},
                        value=[cur_mon_staff.理论填报率.min(), cur_mon_staff.理论填报率.max()], allowCross=False,
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                ], xs=12, sm=12, md=6, lg=6, xl=6)
            ]),


            dbc.Row([
                html.Div([
                    dbc.Button(
                        "查看数据原表",
                        id="collapse-button3",
                        className="mb-3",
                        color="info",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        dash_table.DataTable(
                            id="cur_mon_staff_detailed",
                            columns=[{"name": i, "id": i, } for i in cur_mon_staff.columns],
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            page_action="native",
                            page_current=0,
                            page_size=10,

                            data=cur_mon_staff.to_dict('records'),
                            style_header={
                                'backgroundColor': 'rgb(210, 210, 210)',
                                'color': 'black',
                                'fontWeight': 'bold',
                                'border': '1px solid white'
                            },
                            style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{预估填报} = 不满',
                                        'column_id': '预估填报'
                                    },
                                    'color': 'orange',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{理论填报} = 不满',
                                        'column_id': '理论填报'
                                    },
                                    'color': 'orange',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{预估填报} = 超载',
                                        'column_id': '预估填报'
                                    },
                                    'color': 'tomato',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{理论填报} = 超载',
                                        'column_id': '理论填报'
                                    },
                                    'color': 'tomato',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{预估填报} = 合理',
                                        'column_id': '预估填报'
                                    },
                                    'color': 'green',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {
                                        'filter_query': '{理论填报} = 合理',
                                        'column_id': '理论填报'
                                    },
                                    'color': 'green',
                                    'fontWeight': 'bold'
                                }
                            ],
                            style_cell={'border': '1px solid lightgrey'}
                        ),
                        is_open=False,
                        id="collapse3"
                    ),
                ]),
                html.Br(),
            ]),
            html.Br(),

            # dbc.Row([
            #     dbc.Col([
            #         dcc.Dropdown(list(员工所属部门汇总1['员工所属部门']), list(员工所属部门汇总1['员工所属部门']),
            #                      multi=True,
            #                      placeholder="请选择员工所属部门"),
            #         html.Br(),
            #
            #         dcc.RangeSlider(0, 30, value=[10, 15], tooltip={"placement": "bottom", "always_visible": True},
            #                         allowCross=False)
            #     ])
            # ])
        ], fluid=True)

    elif tab == 'SX':
        return dbc.Container([
            html.P("人员维度Summary"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator_sx', figure=staff_number_indicator_sx,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color":"#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width":"165px"
                               }
                )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_indicator_sx', figure=cur_actual_indicator_sx,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_avg_indicator_sx', figure=cur_actual_avg_indicator_sx, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_indicator_sx', figure=cur_est_indicator_sx,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_rate_indicator_sx', figure=cur_est_rate_indicator_sx,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_indicator_sx', figure=cur_logic_indicator_sx,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_rate_indicator_sx', figure=cur_logic_rate_indicator_sx,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),


            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator_sx_ibg', figure=staff_number_indicator_sx_ibg,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_avg_sx_ibg', figure=cur_actual_avg_sx_ibg, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_avg_sx_ibg', figure=cur_est_avg_sx_ibg,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_est_ibg', figure=cur_mon_staff_under_est_ibg,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_est_ibg', figure=cur_mon_staff_over_est_ibg,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_logic_ibg', figure=cur_mon_staff_under_logic_ibg,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_logic_ibg', figure=cur_mon_staff_over_logic_ibg,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),

            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator_sx_abg', figure=staff_number_indicator_sx_abg,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_avg_sx_abg', figure=cur_actual_avg_sx_abg, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_avg_sx_abg', figure=cur_est_avg_sx_abg,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_est_abg', figure=cur_mon_staff_under_est_abg,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_est_abg', figure=cur_mon_staff_over_est_abg,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_logic_abg', figure=cur_mon_staff_under_logic_abg,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_logic_abg', figure=cur_mon_staff_over_logic_abg,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),

            ]),
        ], fluid=True)

    elif tab == 'AIOT':
        return dbc.Container([
            html.P("人员维度Summary"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator_aiot', figure=staff_number_indicator_aiot,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color":"#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width":"165px"
                               }
                )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_indicator_aiot', figure=cur_actual_indicator_aiot,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_avg_indicator_aiot', figure=cur_actual_avg_indicator_aiot, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_indicator_aiot', figure=cur_est_indicator_aiot,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_avg_aiot', figure=cur_est_avg_aiot,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_indicator_aiot', figure=cur_logic_indicator_aiot,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_avg_aiot', figure=cur_logic_avg_aiot,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),

            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='cur_act_logic_gap_aiot', figure=cur_act_logic_gap_aiot,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_rate_indicator_aiot', figure=cur_est_rate_indicator_aiot, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_rate_indicator_aiot', figure=cur_logic_rate_indicator_aiot,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_est_aiot', figure=cur_mon_staff_under_est_aiot,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_est_aiot', figure=cur_mon_staff_over_est_aiot,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_logic_aiot', figure=cur_mon_staff_under_logic_aiot,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_logic_aiot', figure=cur_mon_staff_over_logic_aiot,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),

            ]),
        ], fluid=True)

    elif tab == 'DX':
        return dbc.Container([
            html.P("人员维度Summary"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator_dx', figure=staff_number_indicator_dx,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color":"#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width":"165px"
                               }
                )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_indicator_dx', figure=cur_actual_indicator_dx,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_avg_indicator_dx', figure=cur_actual_avg_indicator_dx, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_indicator_dx', figure=cur_est_indicator_dx,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_rate_indicator_dx', figure=cur_est_rate_indicator_dx,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_indicator_dx', figure=cur_logic_indicator_dx,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_rate_indicator_dx', figure=cur_logic_rate_indicator_dx,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),


            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator_dx_ty', figure=staff_number_indicator_dx_ty,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_avg_indicator_dx_ty', figure=cur_actual_avg_indicator_dx_ty, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_avg_dx_ty', figure=cur_est_avg_dx_ty,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_est_dx_ty', figure=cur_mon_staff_under_est_dx_ty,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_est_dx_ty', figure=cur_mon_staff_over_est_dx_ty,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_logic_dx_ty', figure=cur_mon_staff_under_logic_dx_ty,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_logic_dx_ty', figure=cur_mon_staff_over_logic_dx_ty,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),

            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator_dx_sku', figure=staff_number_indicator_dx_sku,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_avg_indicator_dx_sku', figure=cur_actual_avg_indicator_dx_sku, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_avg_dx_sku', figure=cur_est_avg_dx_sku,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_est_dx_sku', figure=cur_mon_staff_under_est_dx_sku,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_est_dx_sku', figure=cur_mon_staff_over_est_dx_sku,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_logic_dx_sku', figure=cur_mon_staff_under_logic_dx_sku,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_logic_dx_sku', figure=cur_mon_staff_over_logic_dx_sku,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),

            ]),
        ], fluid=True)

    elif tab == 'IR':
        return dbc.Container([
            html.P("人员维度Summary"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator_ir', figure=staff_number_indicator_ir,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color":"#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width":"165px"
                               }
                )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_indicator_ir', figure=cur_actual_indicator_ir,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_avg_indicator_ir', figure=cur_actual_avg_indicator_ir, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_indicator_ir', figure=cur_est_indicator_ir,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_avg_ir', figure=cur_est_avg_ir,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_indicator_ir', figure=cur_logic_indicator_ir,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_avg_ir', figure=cur_logic_avg_ir,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),


            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='cur_act_logic_gap_ir', figure=cur_act_logic_gap_ir,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_rate_indicator_ir', figure=cur_est_rate_indicator_ir, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_rate_indicator_ir', figure=cur_logic_rate_indicator_ir,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_est_ir', figure=cur_mon_staff_under_est_ir,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_est_ir', figure=cur_mon_staff_over_est_ir,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_logic_ir', figure=cur_mon_staff_under_logic_ir,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_logic_ir', figure=cur_mon_staff_over_logic_ir,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),

            ]),

        ], fluid=True)

    elif tab == 'SI':
        return dbc.Container([
            html.P("人员维度Summary"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='staff_number_indicator_si', figure=staff_number_indicator_si,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color":"#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width":"165px"
                               }
                )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_indicator_si', figure=cur_actual_indicator_si,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_actual_avg_indicator_si', figure=cur_actual_avg_indicator_si, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_indicator_si', figure=cur_est_indicator_si,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_avg_si', figure=cur_est_avg_si,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_indicator_si', figure=cur_logic_indicator_si,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_avg_si', figure=cur_logic_avg_si,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),


            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='cur_act_logic_gap_si', figure=cur_act_logic_gap_si,
                              config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_est_rate_indicator_si', figure=cur_est_rate_indicator_si, config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_logic_rate_indicator_si', figure=cur_logic_rate_indicator_si,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_est_si', figure=cur_mon_staff_under_est_si,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_est_si', figure=cur_mon_staff_over_est_si,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_under_logic_si', figure=cur_mon_staff_under_logic_si,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),
                dbc.Col([
                    dcc.Graph(id='cur_mon_staff_over_logic_si', figure=cur_mon_staff_over_logic_si,config={'displayModeBar': False},
                              style={"border-radius": "5px",
                                     "background-color": "#f9f9f9",
                                     "box-shadow": "2px 2px 2px lightgrey",
                                     "position": "relative",
                                     "margin-bottom": "20px",
                                     "width": "165px"
                                     }
                              )]),

            ]),

        ], fluid=True)

@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
@app.callback(
    Output("collapse2", "is_open"),
    [Input("collapse-button2", "n_clicks")],
    [State("collapse2", "is_open")],
)
@app.callback(
    Output("collapse3", "is_open"),
    [Input("collapse-button3", "n_clicks")],
    [State("collapse3", "is_open")],
)
@app.callback(
    Output("collapse4", "is_open"),
    [Input("collapse-button4", "n_clicks")],
    [State("collapse4", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("fig全量实际vs预估人天-scatter", "figure"),
    Input("range-slider实际vs预估", "value"))
def update_bar_chart(slider_range):
    low, high = slider_range
    mask = (cur_mon_staff.预估填报率 > low) & (cur_mon_staff.预估填报率 < high)
    fig = px.scatter(cur_mon_staff[mask],
        title='员工"实际人天"v."预估人天"by业务线',
        x="实际人天", y="预估人天",
        color="业务线", size='实际人天', hover_data=['员工姓名'])
    return fig

@app.callback(
    Output("fig全量实际vs理论人天-scatter", "figure"),
    Input("range-slider实际vs理论", "value"))
def update_bar_chart(slider_range):
    low, high = slider_range
    mask = (cur_mon_staff.理论填报率 > low) & (cur_mon_staff.理论填报率 < high)
    fig = px.scatter(cur_mon_staff[mask],
        title='员工"实际人天"v."理论人天"by业务线',
        x="实际人天", y="理论人天",
        color="业务线", size='实际人天', hover_data=['员工姓名'])
    return fig





if __name__ == "__main__":
    app.run_server(debug=True, port=8070)

# app.callback 里加上prevent_initial_callback=True,为了不要一开始就call back
# 用判断条件来看是是否要trigger，用state，然后def里的参数需要input 和state 几个
# return 记得用component_property 来放在def里return
# 用df作图，永远先copy 成新df来做！！！
# PreventUpdate 用来避免output update
# 有很多output，但有些不想update 用Dash.no_update
