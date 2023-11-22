import dash
from layout import create_layout
from callbacks import register_callbacks
import dash_bootstrap_components as dbc

# Agrega Font Awesome a las hojas de estilo externas
# external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']

app = dash.Dash(__name__, suppress_callback_exceptions= True, external_stylesheets=[dbc.themes.JOURNAL])
app.layout = create_layout()

register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)