import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff  # IMPORT MANQUANT !

# Charger les fichiers séparément
def load_prices():
    return pd.read_csv("prices_data.csv", index_col=0)

def load_metrics():
    return pd.read_csv("metrics_data.csv", index_col=0)

# Initialisation de Dash
app = dash.Dash(__name__)

# Layout du Dashboard
app.layout = html.Div([
    html.H1("Analyse des Performances Boursières"),
    
    # Sélection des actifs
    dcc.Dropdown(id="dropdown-tickers", multi=True, placeholder="Sélectionnez les actions"),
    
    # Graphique des prix des actions
    dcc.Graph(id="price-chart"),
    
    # Graphique des rendements cumulés
    dcc.Graph(id="cumulative-returns-chart"),

    # Graphique de la volatilité
    dcc.Graph(id="volatility-chart"),

    # Graphique des betas
    dcc.Graph(id="beta-chart"),

    # Graphique des Sharpes Ratio
    dcc.Graph(id="sharpe-ratio-chart"),

    # Matrice de corrélation
    dcc.Graph(id="correlation-heatmap"),
])

# Callback pour mettre à jour la liste des tickers
@app.callback(
    Output("dropdown-tickers", "options"),
    Input("dropdown-tickers", "value")
)
def update_dropdown(_):
    df_prices = load_prices()
    tickers = [col for col in df_prices.columns if "Return_" not in col]  # Exclure les rendements
    return [{"label": col, "value": col} for col in tickers]

# Callback pour mettre à jour les graphiques
@app.callback(
    [Output("price-chart", "figure"),
     Output("cumulative-returns-chart", "figure"),
     Output("volatility-chart", "figure"),
     Output("beta-chart", "figure"),
     Output("sharpe-ratio-chart", "figure"),  # 🆕 Ajout du Sharpe Ratio ici
     Output("correlation-heatmap", "figure")],
    [Input("dropdown-tickers", "value")]
)

def update_graphs(selected_tickers):
    if not selected_tickers:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()

    df_prices = load_prices()
    df_metrics = load_metrics()

    # Graphique des prix
    price_fig = go.Figure()
    for ticker in selected_tickers:
        price_fig.add_trace(go.Scatter(x=df_prices.index, y=df_prices[ticker], mode='lines', name=ticker))
    price_fig.update_layout(title="Évolution des Prix", xaxis_title="Date", yaxis_title="Prix (€)")

    # Graphique des rendements cumulés
    cumulative_returns = (1 + df_prices.filter(like="Return_")).cumprod()
    returns_fig = go.Figure()
    for ticker in selected_tickers:
        if f"Return_{ticker}" in cumulative_returns.columns:
            returns_fig.add_trace(go.Scatter(x=cumulative_returns.index, y=cumulative_returns[f"Return_{ticker}"], mode='lines', name=ticker))
    returns_fig.update_layout(title="Rendements Cumulés", xaxis_title="Date", yaxis_title="Performance Normalisée")

    # Graphique de la Volatilité
    volatility_fig = go.Figure()
    if not df_metrics["Volatilité"].dropna().empty:
        for ticker in selected_tickers:
            if ticker in df_metrics.index and not pd.isna(df_metrics.loc[ticker, "Volatilité"]):
                volatility_fig.add_trace(go.Bar(x=[ticker], y=[df_metrics.loc[ticker, "Volatilité"]], name=ticker))

    volatility_fig.update_layout(title="Volatilité des Actifs", yaxis_title="Volatilité annuelle (%)")

    # Graphique des Betas
    beta_fig = go.Figure()
    if not df_metrics["Beta"].dropna().empty:
        for ticker in selected_tickers:
            if ticker in df_metrics.index and not pd.isna(df_metrics.loc[ticker, "Beta"]):
                beta_fig.add_trace(go.Bar(x=[ticker], y=[df_metrics.loc[ticker, "Beta"]], name=ticker))

    beta_fig.update_layout(title="Beta des Actifs par rapport à l’Indice", yaxis_title="Beta")

    # Graphique du Sharpe Ratio
    sharpe_fig = go.Figure()
    df_metrics = load_metrics()  # Charger les métriques

    if "Sharpe Ratio" in df_metrics.columns:
        for ticker in selected_tickers:
            if ticker in df_metrics.index and not pd.isna(df_metrics.loc[ticker, "Sharpe Ratio"]):
                sharpe_fig.add_trace(go.Bar(x=[ticker], y=[df_metrics.loc[ticker, "Sharpe Ratio"]], name=ticker))

    sharpe_fig.update_layout(title="Sharpe Ratio des Actifs", yaxis_title="Sharpe Ratio")


    # Matrice de corrélation
    correlation_matrix = df_prices.filter(like="Return_").corr()

    # Vérifier que la matrice n'est pas vide avant de la passer à Plotly
    if correlation_matrix.empty:
        heatmap_fig = go.Figure()
    else:
        heatmap_fig = ff.create_annotated_heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns.tolist(),  # ✅ Conversion en liste
            y=correlation_matrix.index.tolist(),  # ✅ Conversion en liste
            colorscale="bluered"
        )

    heatmap_fig.update_layout(title="Matrice de Corrélation")


    return price_fig, returns_fig, volatility_fig, beta_fig, sharpe_fig, heatmap_fig


# Lancer l'application
if __name__ == "__main__":
    app.run_server(debug=True)
