# JuanSalud - Frontend Dashboard Médico

Interfaz gráfica desarrollada con Streamlit para gestión clínica.

## Tecnologías
- Python 3.11
- Streamlit
- Plotly
- Requests

## Instalación local

1. Clonar el repositorio:
git clone https://github.com/tu-usuario/JuanSalud-Frontend.git
cd JuanSalud-Frontend

2. Crear entorno virtual:
python -m venv venv
venv\Scripts\activate

3. Instalar dependencias:
pip install -r requirements.txt

4. Crear archivo .env:
API_URL=https://tu-backend.onrender.com

5. Levantar la aplicación:
streamlit run app.py

## Funcionalidades
- Login con doble API Key
- Gestión de pacientes (CRUD completo)
- Registro de observaciones clínicas
- Gráficas de tendencias de signos vitales
- Alertas de valores fuera de rango clínico
- Control de acceso por roles
