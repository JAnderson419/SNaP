# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 14:57:14 2019

@author: ander906
"""
import sys
from os.path import join, dirname, abspath, basename
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

hubzero=False

for arg in sys.argv:
    if arg == 'hubzero':
        hubzero=True
    else:
        continue

if hubzero:
    from hubzeroapp import app
else:
    from app import app
from apps import app_viewer

changes = ''
with open(join(dirname(dirname(abspath(__file__))), 'CHANGELOG.md')) as f:
    changes = changes+f.read()

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    try:  # Need to take basename to handle nanohub proxy
        if basename(pathname):
            pathname=basename(pathname)
    except TypeError:  # On start of app, pathname will be NoneType, throwing error unless caught
        pass
    if pathname == 'app_viewer':
        return app_viewer.layout
    else:
        return html.Div([
            html.A(
                children=html.Img(src=app.get_asset_url('github2.svg')),
                href=r'https://github.com/JAnderson419/SNaP',
                style={'fill': r'#151513', 'color': r'#fff', 'position': 'absolute', 'top': 0, 'border': 0, 'right': 0}
            ),
            html.H1('SNaP SnP Utilities'),
            html.H3(children='by Jackson Anderson, ander906@purdue.edu'),
            html.Hr(),
            html.H5('Release Notes'),
            html.Div(
                dcc.Markdown(children=changes),
                style={'border': '2px solid #a3a3c2', 'background-color': r'#f0f0f5',
                       'height': r'10em', 'overflow': 'scroll', 'resize': 'both'}
            ),
            html.Hr(),
            dcc.Link('Go to SnP Viewer.', href='app_viewer'),
            html.A(
                children=html.Img(src=app.get_asset_url('powered_by_scikit-rf.svg')),
                href=r'http://scikit-rf.org',
                style={'position': 'absolute', 'bottom': 0, 'right': 0}
            ),
        ])

if __name__ == '__main__':
    if hubzero:
        app.run_server(port=8000, host='0.0.0.0')
    else:
        app.run_server(debug=True)