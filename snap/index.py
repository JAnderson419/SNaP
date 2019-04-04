# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 14:57:14 2019

@author: ander906
"""
from os.path import join, dirname
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import app_viewer


changes = ''
with open(join(dirname(dirname(__file__)), 'CHANGELOG.md')) as f:
    changes = changes+f.read()

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return html.Div([
            html.H1('SNaP SnP Utilities'),
            html.H3(children='by Jackson Anderson, ander906@purdue.edu'),
            html.Hr(),
            html.H5('Release Notes'),
            dcc.Markdown(children=changes),
            html.Hr(),
            dcc.Link('Go to SnP Viewer.', href='/apps/app_viewer'),
            html.Footer('Powered by scikit-rf and Dash.')
        ])
    elif pathname == '/apps/app_viewer':
        return app_viewer.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)
    # hubzero requres these port and host settings
    # app.run_server(port=8000, host='0.0.0.0')