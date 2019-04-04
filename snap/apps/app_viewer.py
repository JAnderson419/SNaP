# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 14:59:14 2019

@author: ander906
"""
import base64
import io
import json
import dash_table
import copy as cp
import numpy as np
import skrf as rf
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app

layout = html.Div([
    html.H3('S Parameter Viewer'),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a Touchstone File.')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    dcc.Loading(id="loading-upload", children=[html.Div(id='output-data-upload')], type="default"),
    html.Div(id='output-data-upload'),
    html.Hr(),
    html.Div([
        html.Div([
            html.Label('Parameter Type'),
            dcc.RadioItems(
                id='parm-select',
                options=[
                    {'label': 'S Parameters', 'value': 'S'},
                    {'label': 'Y Parameters', 'value': 'Y'},
                    {'label': 'Z Parameters', 'value': 'Z'},
                    {'label': 'ABCD Parameters', 'value': 'A'}
                ],
                value='S'),
            html.Label('Plot Axes'),
            dcc.RadioItems(
                id='axes-select',
                options=[
                    {'label': 'Magnitude/Phase', 'value': 'MAG'},
                    {'label': 'Real/Imaginary', 'value': 'RI'},
                    {'label': 'Bode', 'value': 'Bode'}
                ],
                value='MAG'),
            dash_table.DataTable(
                id='port-table',
                css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                }],
                columns=[{"name": "Parameters",
                          "id": "Parameters"}],
                data=[],
                filtering=False,
                editable=False,
                sorting=False,
                row_selectable="multi",
                selected_rows=[],
            ),
            html.Button('Plot', id='button'),
            html.Hr(),
            html.H4("Loading Status"),
            html.H5("S:"),
            dcc.Loading(id="loading-S",
                        children=[html.Div(id='loaded-S-data')],
                        type="default"),
            html.H5("Y:"),
            dcc.Loading(id="loading-Y",
                        children=[html.Div(id='loaded-Y-data')],
                        type="default"),
            html.H5("Z:"),
            dcc.Loading(id="loading-Z",
                        children=[html.Div(id='loaded-Z-data')],
                        type="default"),
            html.H5("ABCD:"),
            dcc.Loading(id="loading-A",
                        children=[html.Div(id='loaded-A-data')],
                        type="default"),
        ], className="three columns"),
        html.Div([
            html.Div(id='output-plot'),
            dcc.Loading(id="loading-plot",
                        children=[html.Div(id='output-plot')],
                        type="default")
        ], className="nine columns")
    ], className="row"),
    html.Div(id='loaded-S-data', style={'display': 'none'}),
    html.Div(id='loaded-Y-data', style={'display': 'none'}),
    html.Div(id='loaded-Z-data', style={'display': 'none'}),
    html.Div(id='loaded-A-data', style={'display': 'none'}),
])


def load_touchstone(content_string, filename):
    # Define subclass of BytesIO to define a name property, which skrf expects
    class dataIO(io.BytesIO):
        _filename: str

        def __init__(self, data, filename):
            super(dataIO, self).__init__(data)
            self.name = filename

        @property
        def name(self):
            """Filename of SnP data."""
            return self._name

        @name.setter
        def name(self, value):
            assert isinstance(value, str)
            self._name = value

    data = dataIO(content_string, filename)
    d = rf.Network()
    d.read_touchstone(data)
    return d


@app.callback([Output('output-data-upload', 'children'),
               Output('loaded-S-data', 'children'),
               Output('port-table', 'data')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_s_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        ch = []
        ports = []
        d = {}
        content_type = []
        content_string = []
        for i, c in enumerate(list_of_contents):
            ct, cs = c.split(',')
            content_type.append(ct)
            content_string.append(cs)
        for c, n in zip(content_string, list_of_names       ):
            decoded = base64.b64decode(c)
            try:
                data = load_touchstone(decoded, n)
            except Exception as e:
                print(e)
                return (html.Div([
                    'There was an error processing this file.'
                ]),
                        html.Div([]))
            ch.append((html.Div([
                html.Div(data.__str__()),
            ])))
            d[n] = data.write_touchstone(return_string=True)
            if ports == []:
                for i in range(len(data.s[0, :, 0])):
                    for j in range(len(data.s[0, 0, :])):
                        ports.append({"Parameters": '{}{}'.format(i + 1, j + 1)})
        return ch, html.Div(json.dumps(d)), ports


@app.callback(Output('loaded-Y-data', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_y_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        d = {}
        content_type = []
        content_string = []
        for i, c in enumerate(list_of_contents):
            ct, cs = c.split(',')
            content_type.append(ct)
            content_string.append(cs)
        for c, n in zip(content_string, list_of_names):
            decoded = base64.b64decode(c)
            try:
                data = load_touchstone(decoded, n)
            except Exception as e:
                print(e)
                return html.Div([])
            data.s = data.y
            sd = data.write_touchstone(return_string=True)
            d[n] = sd
        return html.Div(json.dumps(d))


@app.callback(Output('loaded-Z-data', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_z_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        d = {}
        content_type = []
        content_string = []
        for i, c in enumerate(list_of_contents):
            ct, cs = c.split(',')
            content_type.append(ct)
            content_string.append(cs)
        for c, n in zip(content_string, list_of_names):
            decoded = base64.b64decode(c)
            try:
                data = load_touchstone(decoded, n)
            except Exception as e:
                print(e)
                return html.Div([])
            data.s = data.z
            sd = data.write_touchstone(return_string=True)
            d[n] = sd
        return html.Div(json.dumps(d))


@app.callback(Output('loaded-A-data', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_a_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        d = {}
        content_type = []
        content_string = []
        for i, c in enumerate(list_of_contents):
            ct, cs = c.split(',')
            content_type.append(ct)
            content_string.append(cs)
        for c, n in zip(content_string, list_of_names):
            decoded = base64.b64decode(c)
            try:
                data = load_touchstone(decoded, n)
            except Exception as e:
                print(e)
                return html.Div([])
            data.s = data.a
            sd = data.write_touchstone(return_string=True)
            d[n] = sd
        return html.Div(json.dumps(d))


@app.callback(
    Output('output-plot', "children"),
    [Input('button', 'n_clicks')],
    #    Input('nsmooth_input', 'n_submit'), Input('nsmooth_input', 'n_blur')],
    [State('parm-select', 'value'),
     State('axes-select', 'value'),
     State('port-table', "derived_virtual_selected_rows"),
     State('port-table', "derived_virtual_data"),
     State('loaded-S-data', 'children'),
     State('loaded-Y-data', 'children'),
     State('loaded-Z-data', 'children'),
     State('loaded-A-data', 'children')])
def update_graph(n_clicks, parm, axes_format, selected_rows, selected_data, s_data, y_data, z_data, a_data):
    json_data = None
    if parm == 'S':
        json_data = s_data
    elif parm == 'Y':
        json_data = y_data
    elif parm == 'Z':
        json_data = z_data
    elif parm == 'A':
        json_data = a_data
    else:
        return html.Div("Unrecognized Parameter.")

    if json_data is None or json_data == []:
        return html.Div(children='Please Upload Data to Plot.')
    else:
        traces1 = []
        traces2 = []
        layout1 = []
        layout2 = []
        data = json.loads(json_data['props']['children'])
        #        print(data)
        for key, val in data.items():
            ntwk = load_touchstone(val.encode(), key)
            for i in range(len(ntwk.s[0, :, 0])):
                for j in range(len(ntwk.s[0, 0, :])):
                    for k in selected_rows:
                        if selected_data[k]['Parameters'] == f'{i+1}{j+1}':
                            yvals1 = []
                            yvals2 = []
                            if axes_format == "MAG":
                                yvals1.append(np.abs(ntwk.s[:, i, j]))
                                yvals2.append(np.angle(ntwk.s[:, i, j]))
                            elif axes_format == "RI":
                                yvals1.append(np.real(ntwk.s[:, i, j]))
                                yvals2.append(np.imag(ntwk.s[:, i, j]))
                            elif axes_format == "Bode":
                                return html.Div("Option Under Development.")

                            traces1.append(
                                go.Scatter(x=ntwk.f, y=yvals1[0],
                                           name='{}{}{} {}'.format(parm, i + 1, j + 1, key)
                                           )
                            )
                            traces2.append(
                                go.Scatter(x=ntwk.f, y=yvals2[0],
                                           name='{}{}{} {}'.format(parm, i + 1, j + 1, key)
                                           )
                            )
                        else:
                            continue

# Define Layouts
        if axes_format == "MAG":
            layout1.append(go.Layout(
                xaxis={'title': 'Frequency [Hz]',
                       'exponentformat': 'SI'},
                yaxis={'type': 'log',
                       'title': '{} Parameter Magnitude'.format(parm)},
                margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            ))
            layout2.append(go.Layout(
                xaxis={'title': 'Frequency [Hz]',
                       'exponentformat': 'SI'},
                yaxis={'type': 'linear',
                       'title': '{} Parameter Phase'.format(parm)},
                margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            ))
        elif axes_format == "RI":
            layout1.append(go.Layout(
                xaxis={'title': 'Frequency [Hz]',
                       'exponentformat': 'SI'},
                yaxis={'type': 'linear',
                       'title': '{} Parameter Real'.format(parm)},
                margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            ))
            layout2.append(go.Layout(
                xaxis={'title': 'Frequency [Hz]',
                       'exponentformat': 'SI'},
                yaxis={'type': 'linear',
                       'title': '{} Parameter Imaginary'.format(parm)},
                margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            ))
        elif axes_format == "Bode":
            return html.Div("Option Under Development.")
        #        ax1.set_title('Gmdd')
        #        ax1.set_ylabel('|gm$_{dd}$| [S]')
        #        ax12.set_ylabel('Phase gm$_{dd}$, [deg]')
        #        ax1.yaxis.set_major_formatter(EngFormatter())
        #        ax1.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
        #        ax12.xaxis.set_major_formatter(EngFormatter(unit='Hz'))
        #        ax12.set_xlabel('Frequency')
        #        fig.autofmt_xdate(rotation=20, ha='right')
        #        ax1.legend())

        #        print(mpl_to_plotly(fig))
        #        print (traces)
        return html.Div(
            [
                dcc.Graph(figure={'data': traces1, 'layout': layout1[0]}),
                dcc.Graph(figure={'data': traces2, 'layout': layout2[0]})
            ]
        )
