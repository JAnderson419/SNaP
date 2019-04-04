# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 14:55:47 2019

@author: ander906
"""

import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True