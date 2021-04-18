import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import talib

app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN], title='Stock Market View', update_title='Loading...')
server = app.server

options = []
optdf = pd.read_csv('ticksymbols.csv', encoding='latin-1')
optdf.set_index('Ticker', inplace=True)

for index, row in optdf.iterrows():
    optdict = {'label': str(row['Name']), 'value': index}
    options.append(optdict)

app.layout = html.Div([dbc.Row(dbc.Col(html.H1("Stock Market View"),
                                       width={'size': 5, 'offset': 4}
                                       ),
                               ),
                       dbc.Row(dbc.Col(dcc.Dropdown(id='tickinput',
                                                    options=options,
                                                    placeholder='Stock',
                                                    value='^NSEI',
                                                    multi=False,
                                                    searchable=True,
                                                    clearable=False,
                                                    optionHeight=45,
                                                    persistence=True,
                                                    persistence_type='session',
                                                    ),
                                       width={'size': 4, 'offset': 0}
                                       )
                               ),
                       dbc.Row([dbc.Col(html.Div("Period"),
                                        width={'size': 2, 'offset': 0},
                                        style={'marginBottom': 0, 'marginTop': 10}
                                        ),
                                dbc.Col(html.Div("Interval"),
                                        width={'size': 2, 'offset': 0},
                                        style={'marginBottom': 0, 'marginTop': 10}
                                        )

                                ]),
                       dbc.Row([dbc.Col(dcc.Dropdown(id='periodinput',
                                                     options=[
                                                         {'label': '15 minutes', 'value': '15m'},
                                                         {'label': '1 day', 'value': '1d'},
                                                         {'label': '5 days', 'value': '5d'},
                                                         {'label': '1 month', 'value': '1mo'},
                                                         {'label': '3 months', 'value': '3mo'},
                                                         {'label': '6 months', 'value': '6mo'},
                                                         {'label': 'YTD', 'value': 'ytd'},
                                                         {'label': '1 year', 'value': '1y'},
                                                         {'label': '5 years', 'value': '5y'},
                                                         # {'label': '10 years', 'value': '10y'},
                                                         {'label': 'MAX', 'value': 'max'}
                                                     ],
                                                     placeholder='Period',
                                                     value='1y',
                                                     optionHeight=30,
                                                     searchable=True,
                                                     clearable=False,
                                                     # style={'width': "90%"},
                                                     persistence=True,
                                                     persistence_type='session'
                                                     ),
                                        width={'size': 2, 'offset': 0}
                                        ),
                                dbc.Col(dcc.Dropdown(id='intervalinput',
                                                     options=[
                                                         {'label': '1 minute', 'value': '1m'},
                                                         {'label': '2 minutes', 'value': '2m'},
                                                         {'label': '5 minutes', 'value': '5m'},
                                                         {'label': '15 minutes', 'value': '15m'},
                                                         # {'label': '30 minutes', 'value': '30m'},
                                                         {'label': '1h', 'value': '60m'},
                                                         # {'label': '90 minutes', 'value': '90m'},
                                                         {'label': '1 day', 'value': '1d'},
                                                         # {'label': '5 days', 'value': '5d'},
                                                         # {'label': '1 week', 'value': '1wk'},
                                                         # {'label': '1 month', 'value': '1mo'},
                                                         # {'label': '3 months', 'value': '3mo'}
                                                     ],
                                                     placeholder='Interval',
                                                     value='1d',
                                                     optionHeight=30,
                                                     searchable=True,
                                                     clearable=False,
                                                     persistence=True,
                                                     persistence_type='session'
                                                     ),
                                        width={'size': 2, 'offset': 0}
                                        ),
                                dbc.Col(dcc.Dropdown(id='compare',
                                                     options=options,
                                                     placeholder='Compare',
                                                     multi=True,
                                                     searchable=True,
                                                     clearable=True,
                                                     optionHeight=45,
                                                     persistence=True,
                                                     persistence_type='session'
                                                     ),
                                        width={'size': 3, 'offset': 0}
                                        ),
                                dbc.Col(dcc.Dropdown(id='indicator_sel',
                                                     options=[
                                                         {'label': 'Bollinger Bands', 'value': 'bbands'},
                                                         {'label': 'Exponential Moving Average', 'value': 'ema'},
                                                         {'label': 'Ichimoku Cloud', 'value': 'ichi'},
                                                         {'label': 'MovAvg50', 'value': 'mov50'},
                                                         {'label': 'MovAvg200', 'value': 'mov200'},
                                                         {'label': 'Parabolic SAR', 'value': 'sar'},
                                                         {'label': 'Bullish Engulfing', 'value': 'bulleng'},
                                                         {'label': 'Bearish Engulfing', 'value': 'beareng'}
                                                     ],
                                                     placeholder='Indicators',
                                                     optionHeight=30,
                                                     multi=True,
                                                     searchable=True,
                                                     clearable=True,
                                                     persistence=True,
                                                     persistence_type='session'
                                                     ),
                                        width={'size': 3, 'offset': 0}
                                        )
                                ]
                               ),

                       dbc.Row(dbc.Col(dcc.Graph(id='graph',
                                                 config={'modeBarButtonsToAdd': ['drawline',
                                                                                 'drawopenpath',
                                                                                 'drawclosedpath',
                                                                                 'drawcircle',
                                                                                 'drawrect',
                                                                                 'eraseshape'
                                                                                 ],
                                                         'scrollZoom': True,
                                                         'displayModeBar': True,
                                                         'editable': False
                                                         }
                                                 )
                                       )
                               ),
                       dcc.Interval(
                           id='interval-component',
                           interval=30 * 1000,
                           n_intervals=0
                       ),
                       dbc.Modal([
                           dbc.ModalHeader(html.H3("Welcome to Stock Market View!!")),
                           dbc.ModalBody("This application can be used to visualize NSE and BSE stocks with indicators and "
                                         "to compare different stocks.")
                       ],
                           is_open=True)
                       ])


@app.callback(
    Output(component_id='intervalinput', component_property='value'),
    Input(component_id='periodinput', component_property='value')
)
def callback2(p):
    if p == '15m' or p == '1d':
        return '1m'
    elif p == '5d':
        return '5m'
    else:
        return '1d'


@app.callback(

    Output(component_id='graph', component_property='figure'),
    [Input(component_id='tickinput', component_property='value'),
     Input(component_id='periodinput', component_property='value'),
     Input(component_id='intervalinput', component_property='value'),
     Input(component_id='interval-component', component_property='n_intervals'),
     Input(component_id='indicator_sel', component_property='value'),
     Input(component_id='compare', component_property='value')],
    prevent_initial_call=True
)
def callback1(tick, period, interval, n, indicator_sel, compare):
    ticker = yf.Ticker(tick)
    df = ticker.history(period=period, interval=interval)
    df = df.dropna()
    df['Engulfing'] = talib.CDLENGULFING(df['Open'], df['High'], df['Low'], df['Close'])
    layout = go.Layout({
        'title': {
            'text': optdf.Name[optdf.index == tick].sum(),
            'font': {
                'size': 30,
                'color': 'grey'
            },
        },
        'xaxis_title': 'Time',
        'yaxis_title': 'Price',
        'xaxis': {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1
        },
        'yaxis': {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikecolor': 'black',
            'spikethickness': 1,
            'side': 'right'
        },
        'width': 1400,
        'height': 650,
        'dragmode': 'pan',
        'hovermode': 'x',
        'xaxis_rangeslider_visible': False,
        'modebar': {
            'orientation': 'v'},
        'uirevision': (period + interval + tick + str(compare)),
        'spikedistance': -1, 'hoverdistance': 100,
        'template': 'plotly_white',
        'legend': {
            'orientation': 'h'
        },
        # 'paper_bgcolor': "#19334d",
        # 'plot_bgcolor': "#d8e6f3"
    })

    trace = {
        'type': 'candlestick',
        'open': df.Open,
        'high': df.High,
        'low': df.Low,
        'close': df.Close,
        'x': df.index,
        'name': tick.upper(),
    }
    fig = go.Figure(data=trace, layout=layout)
    if compare is not None:
        for c in compare:
            tickers = yf.Ticker(c)
            dfc = tickers.history(period=period, interval=interval)
            comptrace = {
                'x': dfc.index,
                'y': dfc.Close,
                'type': 'scatter',
                'mode': 'lines',
                'line': {
                    'width': 1,
                    'color': 'green'
                },
                'hoverinfo': 'skip'

            }
            fig.add_trace(comptrace)
    if indicator_sel is not None:
        for ind in indicator_sel:
            if ind == 'mov50':
                trace_mov50 = {
                    'x': df.index,
                    'y': talib.MA(df['Close'], timeperiod=50, matype=0),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'red'
                    },
                    'name': 'MovAvg50',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_mov50)
            elif ind == 'mov200':
                trace_mov200 = {
                    'x': df.index,
                    'y': talib.MA(df['Close'], timeperiod=200, matype=0),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'yellow'
                    },
                    'name': 'MovAvg200',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_mov200)
            elif ind == 'bbands':
                upperband, middleband, lowerband = talib.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2,
                                                                matype=0)
                trace_bbandlow = {
                    'x': df.index,
                    'y': lowerband,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'green'
                    },
                    'name': 'BBlow',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_bbandlow)
                trace_bbandup = {
                    'x': df.index,
                    'y': upperband,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'green'
                    },
                    'fill': 'tonexty',
                    'fillcolor': 'rgba(173,204,255,0.2)',
                    'name': 'BBup',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_bbandup)
                trace_bbandmid = {
                    'x': df.index,
                    'y': middleband,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'brown'
                    },
                    'name': 'BBmid',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_bbandmid)
            elif ind == 'ema':
                trace_ema = {
                    'x': df.index,
                    'y': talib.EMA(df['Close'], timeperiod=9),
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'purple'
                    },
                    'name': 'EMA',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_ema)
            elif ind == 'sar':
                trace_sar = {
                    'x': df.index,
                    'y': talib.SAR(df['High'], df['Close'], acceleration=0.02, maximum=0.2),
                    'type': 'scatter',
                    'mode': 'markers',
                    'marker': {
                        'size': 3,
                        'color': 'orange'
                    },
                    'name': 'SAR',
                    'hoverinfo': 'skip'

                }
                fig.add_trace(trace_sar)
            elif ind == 'ichi':
                tenkan_sen = (df['High'].rolling(window=9).max() + df['Low'].rolling(window=9).min()) / 2
                kijun_sen = (df['High'].rolling(window=26).max() + df['Low'].rolling(window=26).min()) / 2
                senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
                senkou_span_b = ((df['High'].rolling(window=52).max() + df['Low'].rolling(window=52).min()) / 2).shift(
                    26)
                chikou_span = df['Close'].shift(-26)
                trace_tenkan = {
                    'x': df.index,
                    'y': tenkan_sen,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'cyan'
                    },
                    'name': 'tenkan_sen',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_tenkan)
                trace_kijun = {
                    'x': df.index,
                    'y': kijun_sen,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'maroon'
                    },
                    'name': 'kijun_sen',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_kijun)
                trace_senkou_span_a = {
                    'x': df.index,
                    'y': senkou_span_a,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'green'
                    },
                    'name': 'senkou_span_a',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_senkou_span_a)
                trace_senkou_span_b = {
                    'x': df.index,
                    'y': senkou_span_b,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'red'
                    },
                    'fill': 'tonexty',
                    'fillcolor': 'rgba(173,204,255,0.2)',
                    'name': 'senkou_span_b',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_senkou_span_b)
                trace_chikou_span = {
                    'x': df.index,
                    'y': chikou_span,
                    'type': 'scatter',
                    'mode': 'lines',
                    'line': {
                        'width': 1,
                        'color': 'green'
                    },
                    'name': 'chikou_span',
                    'hoverinfo': 'skip'
                }
                fig.add_trace(trace_chikou_span)
            elif ind == 'bulleng':
                for i, j in df.iterrows():
                    if j['Engulfing'] != 100:
                        k = i
                        continue
                    else:
                        fig.add_vrect(
                            x0=k, x1=i,
                            annotation_text="BE", annotation_position="top left",
                            fillcolor="green", opacity=0.25,
                            line_width=0, line_color='green')
            elif ind == 'beareng':
                for i, j in df.iterrows():
                    if j['Engulfing'] != -100:
                        k = i
                        continue
                    else:
                        fig.add_vrect(
                            x0=k, x1=i,
                            # x0=k-datetime.timedelta(hours=6), x1=i+datetime.timedelta(hours=6),
                            annotation_text="BE", annotation_position="top left",
                            fillcolor="red", opacity=0.25,
                            line_width=0, line_color='red'
                        )
    if interval != '1d':
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]),
                dict(bounds=[15.5, 9.25], pattern='hour')
            ]

        )
    else:
        fig.update_xaxes(
            rangebreaks=[
                dict(bounds=["sat", "mon"]),
                # dict(bounds=[15.5,9.1],pattern='hour')
            ]

        )

    return fig


app.run_server(debug=True)
