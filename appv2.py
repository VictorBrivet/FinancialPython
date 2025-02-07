import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import plotly.figure_factory as ff  # Pour la matrice de corrélation

# Initialisation de Dash
app = dash.Dash(__name__)

# Layout de l'application
app.layout = html.Div([
    html.H1("Analyse des Performances Boursières"),

    # 📌 Input pour entrer les tickers + bouton de mise à jour
    dcc.Input(id="input-tickers", type="text", placeholder="Entrez les tickers (ex: MC.PA, BNP.PA, SAN.PA)", style={'width': '50%'}),
    html.Button("Mettre à jour", id="update-button", n_clicks=0),
   
    # 📌 Sélecteur de dates
    dcc.DatePickerRange(
    id="date-picker",
    min_date_allowed="2000-01-01",  # Date minimale (modifiable)
    max_date_allowed=pd.to_datetime("today").strftime("%Y-%m-%d"),  # Aujourd'hui
    start_date="2019-01-01",  # Date par défaut
    end_date=pd.to_datetime("today").strftime("%Y-%m-%d"),  # Aujourd'hui
    display_format="YYYY-MM-DD",
    style={"margin-left": "20px"}),

    # 📌 Dropdown pour sélectionner les tickers après mise à jour
    dcc.Dropdown(id="dropdown-tickers", multi=True, placeholder="Sélectionnez les actions"),

    # 📌 Graphiques affichés
    dcc.Graph(id="price-chart"),
    dcc.Graph(id="price-chart-no-index"),
    dcc.Graph(id="cumulative-returns-chart"),
    dcc.Graph(id="volatility-chart"),
    dcc.Graph(id="beta-chart"),
    dcc.Graph(id="sharpe-ratio-chart"),
    dcc.Graph(id="correlation-heatmap"),
])

# Fonction pour récupérer les données des actions demandées par l'utilisateur
def fetch_data_dynamic(tickers, start_date, end_date):
    if not tickers:
        return None, None  # Si aucun ticker n'est donné

    print(f"\n🔄 Téléchargement des données pour : {tickers} de {start_date} à {end_date}")

    # Ajouter l'indice de référence **seulement s'il n'est pas déjà présent**
    indice_reference = "^FCHI"
    if indice_reference not in tickers:
        tickers.append(indice_reference)

    # Télécharger les prix des actions avec la période sélectionnée
    data = yf.download(tickers, start=start_date, end=end_date)["Close"]

    # Vérifier que des données ont bien été récupérées
    if data.empty:
        print("❌ Aucune donnée téléchargée ! Vérifiez les tickers et la période.")
        return None, None

    # Calcul des rendements journaliers
    returns = data.pct_change()

    # Calcul des métriques financières
    volatility = returns.std() * (252**0.5)
    cov_matrix = returns.cov()
    betas = cov_matrix[indice_reference] / cov_matrix.loc[indice_reference, indice_reference]
    risk_free_rate = 0.025
    annual_returns = returns.mean() * 252
    sharpe_ratios = (annual_returns - risk_free_rate) / volatility

    # Création du DataFrame des métriques
    metrics_data = pd.DataFrame({
        "Volatilité": volatility,
        "Beta": betas,
        "Sharpe Ratio": sharpe_ratios
    })

    print("Données téléchargées et calculées !")
    return data, metrics_data

@app.callback(
    [Output("dropdown-tickers", "options"),
     Output("dropdown-tickers", "value"),
     Output("price-chart", "figure"),
     Output("price-chart-no-index", "figure"), 
     Output("cumulative-returns-chart", "figure"),
     Output("volatility-chart", "figure"),
     Output("beta-chart", "figure"),
     Output("sharpe-ratio-chart", "figure"),
     Output("correlation-heatmap", "figure")],
    [Input("update-button", "n_clicks")],
    [State("input-tickers", "value"),
     State("date-picker", "start_date"),
     State("date-picker", "end_date")]
)
def update_graphs(n_clicks, tickers_input, start_date, end_date):
    try:
        if not tickers_input:
            return [], None, go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()

        # Séparer correctement les tickers entrés par l'utilisateur
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

        # Vérifier qu'on a bien plusieurs tickers
        if not tickers:
            print("❌ Aucun ticker valide n'a été saisi.")
            return [], None, go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()

        # Télécharger les données avec la période sélectionnée
        df_prices, df_metrics = fetch_data_dynamic(tickers, start_date, end_date)

        # Vérifier si les données ont bien été récupérées
        if df_prices is None or df_metrics is None or df_prices.empty or df_metrics.empty:
            print("❌ Problème lors du chargement des données.")
            return [], None, go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()

        # Mettre à jour les options du dropdown avec les tickers récupérés
        options = [{"label": t, "value": t} for t in tickers]

        # Graphique des prix
        price_fig = go.Figure()
        for ticker in tickers:
            price_fig.add_trace(go.Scatter(x=df_prices.index, y=df_prices[ticker], mode='lines', name=ticker))
        price_fig.update_layout(title="Évolution des Prix", xaxis_title="Date", yaxis_title="Prix (€)")

        # Graphique des rendements cumulés
        cumulative_returns = (1 + df_prices.pct_change()).cumprod()
        returns_fig = go.Figure()
        for ticker in tickers:
            returns_fig.add_trace(go.Scatter(x=cumulative_returns.index, y=cumulative_returns[ticker], mode='lines', name=ticker))
        returns_fig.update_layout(title="Rendements Cumulés", xaxis_title="Date", yaxis_title="Performance Normalisée")

        # Graphique de la Volatilité
        volatility_fig = go.Figure()
        for ticker in tickers:
            if ticker in df_metrics.index and not pd.isna(df_metrics.loc[ticker, "Volatilité"]):
                volatility_fig.add_trace(go.Bar(x=[ticker], y=[df_metrics.loc[ticker, "Volatilité"]], name=ticker))
        volatility_fig.update_layout(title="Volatilité des Actifs", yaxis_title="Volatilité annuelle (%)")

        # Graphique des Betas
        beta_fig = go.Figure()
        for ticker in tickers:
            if ticker in df_metrics.index and not pd.isna(df_metrics.loc[ticker, "Beta"]):
                beta_fig.add_trace(go.Bar(x=[ticker], y=[df_metrics.loc[ticker, "Beta"]], name=ticker))
        beta_fig.update_layout(title="Beta des Actifs par rapport à l’Indice", yaxis_title="Beta")

        # Graphique du Sharpe Ratio
        sharpe_fig = go.Figure()
        for ticker in tickers:
            if ticker in df_metrics.index and not pd.isna(df_metrics.loc[ticker, "Sharpe Ratio"]):
                sharpe_fig.add_trace(go.Bar(x=[ticker], y=[df_metrics.loc[ticker, "Sharpe Ratio"]], name=ticker))
        sharpe_fig.update_layout(title="Sharpe Ratio des Actifs", yaxis_title="Sharpe Ratio")

        # Graphique des prix sans l’indice
        price_fig_no_index = go.Figure()
        actions_only = [ticker for ticker in tickers if ticker != "^FCHI"]
        for ticker in actions_only:
            price_fig_no_index.add_trace(go.Scatter(x=df_prices.index, y=df_prices[ticker], mode='lines', name=ticker))
        price_fig_no_index.update_layout(title="Évolution des Prix (Sans l'Indice)", xaxis_title="Date", yaxis_title="Prix (€)")

        # Matrice de corrélation
        correlation_matrix = df_prices.pct_change().corr()

        # Vérifier que la matrice de corrélation n'est pas vide
        if correlation_matrix.empty:
            heatmap_fig = go.Figure()
        else:
            heatmap_fig = ff.create_annotated_heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns.tolist(),
                y=correlation_matrix.index.tolist(),
                colorscale="bluered"
            )
            heatmap_fig.update_layout(title="Matrice de Corrélation")

        tickers_selected = tickers if tickers else []

        return options, tickers_selected, price_fig, price_fig_no_index, returns_fig, volatility_fig, beta_fig, sharpe_fig, heatmap_fig

    except Exception as e:
        print(f"🚨 Erreur dans update_graphs: {str(e)}")
        return [], None, go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()

# Lancer l'application
if __name__ == "__main__":
    app.run_server(debug=True)
