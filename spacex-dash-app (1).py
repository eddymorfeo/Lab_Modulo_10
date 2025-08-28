# Importar las bibliotecas necesarias
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Leer el conjunto de datos de lanzamientos de SpaceX
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Renombrar columnas para evitar errores de acceso
spacex_df.rename(columns={'Launch Site': 'Launch_Site', 'class': 'Class'}, inplace=True)

# Obtener valores mínimos y máximos de carga útil
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Definir la estructura de la aplicación con todas las tareas
app.layout = html.Div(children=[
    html.H1('Panel de Lanzamientos de SpaceX',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TAREA 1: Menú desplegable para seleccionar el sitio de lanzamiento
    html.Div([
        html.Label("Selecciona un sitio de lanzamiento:", style={'font-size': '18px', 'font-weight': 'bold'}),
        dcc.Dropdown(
            id='site-dropdown',
            options=[{'label': 'Todos los sitios', 'value': 'ALL'}] +
                    [{'label': site, 'value': site} for site in spacex_df['Launch_Site'].unique()],
            value='ALL',
            placeholder="Selecciona un sitio de lanzamiento",
            searchable=True,
            style={'width': '60%', 'margin': 'auto'}
        )
    ], style={'textAlign': 'center'}),
    
    html.Br(),

    # TAREA 2: Gráfico circular de lanzamientos exitosos
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # TAREA 3: Control deslizante de carga útil
    html.Label("Rango de carga útil (Kg):", style={'font-size': '18px', 'font-weight': 'bold'}),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload, max=max_payload, step=1000,
        marks={min_payload: f'{min_payload} kg', max_payload: f'{max_payload} kg'},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TAREA 4: Gráfico de dispersión para carga útil y éxito de lanzamiento
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TAREA 2: Función de callback para actualizar el gráfico circular según el sitio seleccionado
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(selected_site):
    if 'Class' not in spacex_df.columns or 'Launch_Site' not in spacex_df.columns:
        return px.pie(title="Error: Columnas no encontradas")

    if selected_site == 'ALL':
        site_success_counts = spacex_df.groupby('Launch_Site')['Class'].sum().reset_index()
        fig = px.pie(site_success_counts, values='Class', names='Launch_Site',
                     title='Total de lanzamientos exitosos por sitio')
    else:
        filtered_df = spacex_df[spacex_df['Launch_Site'] == selected_site]
        if filtered_df.empty:
            return px.pie(title=f"No hay datos disponibles para {selected_site}")
        
        outcome_counts = filtered_df['Class'].value_counts().reset_index()
        outcome_counts.columns = ['Resultado', 'Cantidad']
        fig = px.pie(outcome_counts, values='Cantidad', names='Resultado',
                     title=f'Resultados de lanzamientos en {selected_site}')
    
    return fig

# TAREA 4: Función de callback para actualizar el gráfico de dispersión según el sitio y el rango de carga útil
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(selected_site, payload_range):
    # Filtrar datos por carga útil
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    if filtered_df.empty:
        return px.scatter(title="No hay datos disponibles en el rango seleccionado.")

    if selected_site == 'ALL':
        # Mostrar todos los sitios con color basado en la versión del booster
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='Class', color='Booster Version Category',
                         title='Relación entre carga útil y éxito de lanzamiento en todos los sitios',
                         labels={'Payload Mass (kg)': 'Carga Útil (Kg)', 'Class': 'Éxito (0 = Falla, 1 = Éxito)'})
    else:
        # Filtrar datos por sitio específico
        filtered_df = filtered_df[filtered_df['Launch_Site'] == selected_site]
        if filtered_df.empty:
            return px.scatter(title=f"No hay datos disponibles para {selected_site} en el rango seleccionado.")

        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='Class', color='Booster Version Category',
                         title=f'Relación entre carga útil y éxito en {selected_site}',
                         labels={'Payload Mass (kg)': 'Carga Útil (Kg)', 'Class': 'Éxito (0 = Falla, 1 = Éxito)'})

    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)