import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv
from datetime import date
import os

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="JuanSalud Dashboard", layout="wide")

# ─── LOGIN ───────────────────────────────────────────────
def login():
    st.title("🏥 JuanSalud - Login")
    st.markdown("Ingresa tus credenciales para acceder al sistema.")

    access_key = st.text_input("Access Key", type="password")
    permission_key = st.text_input("Permission Key", type="password")

    if st.button("Ingresar"):
        if not access_key or not permission_key:
            st.error("Debes ingresar ambas llaves.")
            return

        headers = {
            "X-Access-Key": access_key,
            "X-Permission-Key": permission_key
        }

        try:
            res = requests.get(f"{API_URL}/JuanSalud/Patient/", headers=headers)
            if res.status_code == 200:
                st.session_state["access_key"] = access_key
                st.session_state["permission_key"] = permission_key
                st.session_state["logged_in"] = True
                st.rerun()
            elif res.status_code == 401:
                st.error("❌ Access Key inválida.")
            elif res.status_code == 403:
                st.error("❌ Permission Key inválida.")
            else:
                st.error(f"Error: {res.status_code}")
        except Exception as e:
            st.error(f"No se pudo conectar al servidor: {e}")

# ─── HEADERS ─────────────────────────────────────────────
def get_headers():
    return {
        "X-Access-Key": st.session_state["access_key"],
        "X-Permission-Key": st.session_state["permission_key"]
    }

# ─── DASHBOARD ───────────────────────────────────────────
def dashboard():
    st.title("🏥 JuanSalud - Dashboard Médico")

    # Sidebar
    st.sidebar.title("Navegación")
    seccion = st.sidebar.radio("Ir a:", [
        "📋 Pacientes",
        "🔬 Observaciones",
        "➕ Nuevo Paciente",
        "➕ Nueva Observación"
    ])

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    if seccion == "📋 Pacientes":
        mostrar_pacientes()
    elif seccion == "🔬 Observaciones":
        mostrar_observaciones()
    elif seccion == "➕ Nuevo Paciente":
        crear_paciente()
    elif seccion == "➕ Nueva Observación":
        crear_observacion()

# ─── PACIENTES ────────────────────────────────────────────
def mostrar_pacientes():
    st.header("📋 Lista de Pacientes")

    col1, col2 = st.columns(2)
    limit = col1.number_input("Resultados por página", min_value=1, max_value=50, value=10)
    offset = col2.number_input("Desde el registro", min_value=0, value=0)

    res = requests.get(
        f"{API_URL}/JuanSalud/Patient/",
        headers=get_headers(),
        params={"limit": limit, "offset": offset}
    )

    if res.status_code == 200:
        pacientes = res.json()
        if not pacientes:
            st.info("No hay pacientes registrados.")
            return

        df = pd.DataFrame(pacientes)
        st.dataframe(df, use_container_width=True)
        ids = [p["id"] for p in pacientes]

 # ─── EDITAR PACIENTE ───────────────────────────
        st.subheader("✏️ Editar paciente")
        st.caption("Disponible para admin y médico.")
        patient_id_editar = st.selectbox("Selecciona el paciente a editar", ids, key="editar")
        paciente_sel = next((p for p in pacientes if p["id"] == patient_id_editar), None)

        if paciente_sel:
            with st.form("form_editar"):
                col1, col2 = st.columns(2)
                family_name = col1.text_input("Apellido", value=paciente_sel["family_name"])
                given_name = col2.text_input("Nombre", value=paciente_sel["given_name"])
                gender = st.selectbox("Género", ["male", "female", "other"],
                    index=["male", "female", "other"].index(paciente_sel["gender"]))
                birthDate = st.date_input("Fecha de nacimiento",
                    value=date.fromisoformat(paciente_sel["birthDate"]),
                    min_value=date(1900, 1, 1),
                    max_value=date.today())
                identification_doc = st.text_input("Documento de identidad",
                    value=paciente_sel["identification_doc"])
                col3, col4 = st.columns(2)
                weight = col3.text_input("Peso (kg)", value=paciente_sel["weight"])
                height = col4.text_input("Altura (cm)", value=paciente_sel["height"])
                medical_summary = st.text_area("Resumen médico",
                    value=paciente_sel["medical_summary"])
                submitted = st.form_submit_button("Guardar cambios")

            if submitted:
                payload = {
                    "id": patient_id_editar,
                    "family_name": family_name,
                    "given_name": given_name,
                    "gender": gender,
                    "birthDate": str(birthDate),
                    "identification_doc": identification_doc,
                    "weight": weight,
                    "height": height,
                    "medical_summary": medical_summary
                }
                res_put = requests.put(
                    f"{API_URL}/JuanSalud/Patient/{patient_id_editar}",
                    headers={**get_headers(), "Content-Type": "application/json"},
                    json=payload
                )
                if res_put.status_code == 200:
                    st.success("✅ Paciente actualizado correctamente.")
                    st.rerun()
                elif res_put.status_code == 403:
                    st.error("❌ No tienes permisos para editar pacientes.")
                elif res_put.status_code == 404:
                    st.error("❌ Paciente no encontrado.")
                else:
                    st.error(f"Error: {res_put.status_code}")

        # ─── ELIMINAR PACIENTE ─────────────────────────
        st.subheader("🗑️ Eliminar paciente")
        
        patient_id_eliminar = st.selectbox("Selecciona el paciente a eliminar", ids, key="eliminar")
        if st.button("Eliminar paciente", type="primary"):
            res_del = requests.delete(
                f"{API_URL}/JuanSalud/Patient/{patient_id_eliminar}",
                headers=get_headers()
            )
            if res_del.status_code == 200:
                st.success(f"✅ Paciente {patient_id_eliminar} eliminado correctamente.")
                st.rerun()
            elif res_del.status_code == 403:
                st.error("❌ No tienes permisos para eliminar pacientes. Solo el admin puede hacerlo.")
            elif res_del.status_code == 404:
                st.error("❌ Paciente no encontrado.")
            else:
                st.error(f"Error: {res_del.status_code}")

    elif res.status_code == 403:
        st.error("❌ No tienes permisos para ver pacientes.")
    else:
        st.error(f"Error: {res.status_code}")

# ─── OBSERVACIONES ────────────────────────────────────────
def mostrar_observaciones():
    st.header("🔬 Observaciones")

    patient_id = st.text_input("ID del paciente")

    if patient_id:
        res = requests.get(
            f"{API_URL}/JuanSalud/Observation/",
            headers=get_headers(),
            params={"patient_id": patient_id, "limit": 50, "offset": 0}
        )

        if res.status_code == 200:
            obs = res.json()
            if not obs:
                st.info("Este paciente no tiene observaciones.")
                return

            df = pd.DataFrame(obs)
            st.dataframe(df, use_container_width=True)

            # ─── GRÁFICA DE TENDENCIAS ─────────────────────
            st.subheader("📈 Tendencia de signos vitales")

            categorias = df["display"].unique().tolist()
            categoria = st.selectbox("Selecciona signo vital", categorias)

            df_filtrado = df[df["display"] == categoria].copy()
            df_filtrado["date"] = pd.to_datetime(df_filtrado["date"])
            df_filtrado = df_filtrado.sort_values("date")

            # ─── DETECCIÓN DE OUTLIERS ─────────────────────
            outliers = {
                "Blood Pressure": (60, 180),
                "Body Temperature": (35, 42),
                "Heart Rate": (40, 180),
                "Oxygen Saturation": (85, 100),
            }

            if categoria in outliers:
                min_val, max_val = outliers[categoria]
                df_filtrado["alerta"] = df_filtrado["value"].apply(
                    lambda v: "⚠️ Fuera de rango" if v < min_val or v > max_val else "✅ Normal"
                )
                alertas = df_filtrado[df_filtrado["alerta"] == "⚠️ Fuera de rango"]
                if not alertas.empty:
                    st.error(f"⚠️ Se detectaron {len(alertas)} valores fuera de rango clínico.")
                    st.dataframe(alertas[["date", "value", "unit", "alerta"]], use_container_width=True)

            fig = px.line(
                df_filtrado,
                x="date",
                y="value",
                title=f"Tendencia: {categoria}",
                markers=True,
                labels={"value": df_filtrado["unit"].iloc[0], "date": "Fecha"}
            )

            # Colorea puntos outliers en rojo
            if categoria in outliers:
                min_val, max_val = outliers[categoria]
                fig.add_hline(y=min_val, line_dash="dash", line_color="red", annotation_text="Mín. clínico")
                fig.add_hline(y=max_val, line_dash="dash", line_color="red", annotation_text="Máx. clínico")

            st.plotly_chart(fig, use_container_width=True)
            # ─── EDITAR OBSERVACIÓN ───────────────────────
            st.subheader("✏️ Editar observación")
            st.caption("Disponible para admin y médico.")
            obs_ids = [o["id"] for o in obs]
            obs_display = [f"{o['display']} - {o['date']} ({o['id'][:8]}...)" for o in obs]
            obs_index = st.selectbox("Selecciona la observación a editar", range(len(obs_ids)),
                format_func=lambda x: obs_display[x], key="editar_obs")

            obs_sel = obs[obs_index]

            with st.form("form_editar_obs"):
                category = st.selectbox("Categoría", ["vital-signs", "laboratory", "imaging"],
                    index=["vital-signs", "laboratory", "imaging"].index(obs_sel["category"]))
                col1, col2 = st.columns(2)
                code = col1.text_input("Código FHIR", value=obs_sel["code"])
                display = col2.text_input("Nombre", value=obs_sel["display"])
                col3, col4 = st.columns(2)
                value = col3.number_input("Valor", value=float(obs_sel["value"]), format="%.2f")
                unit = col4.text_input("Unidad", value=obs_sel["unit"])
                obs_date = st.date_input("Fecha",
                    value=date.fromisoformat(obs_sel["date"]),
                    min_value=date(1900, 1, 1),
                    max_value=date.today())
                submitted_obs = st.form_submit_button("Guardar cambios")

            if submitted_obs:
                payload = {
                    "patient_id": patient_id,
                    "category": category,
                    "code": code,
                    "display": display,
                    "value": value,
                    "unit": unit,
                    "date": str(obs_date)
                }
                res_put = requests.put(
                    f"{API_URL}/JuanSalud/Observation/{obs_ids[obs_index]}",
                    headers={**get_headers(), "Content-Type": "application/json"},
                    json=payload
                )
                if res_put.status_code == 200:
                    st.success("✅ Observación actualizada correctamente.")
                    st.rerun()
                elif res_put.status_code == 403:
                    st.error("❌ No tienes permisos para editar observaciones.")
                elif res_put.status_code == 404:
                    st.error("❌ Observación no encontrada.")
                else:
                    st.error(f"Error: {res_put.status_code}")

            # ─── ELIMINAR OBSERVACIÓN ─────────────────────
            st.subheader("🗑️ Eliminar observación")
            st.caption("Solo disponible para admin.")
            obs_id_eliminar = st.selectbox("Selecciona la observación a eliminar",
                range(len(obs_ids)), format_func=lambda x: obs_display[x], key="eliminar_obs")

            if st.button("Eliminar observación", type="primary"):
                res_del = requests.delete(
                    f"{API_URL}/JuanSalud/Observation/{obs_ids[obs_id_eliminar]}",
                    headers=get_headers()
                )
                if res_del.status_code == 204:
                    st.success("✅ Observación eliminada correctamente.")
                    st.rerun()
                elif res_del.status_code == 403:
                    st.error("❌ No tienes permisos para eliminar observaciones.")
                elif res_del.status_code == 404:
                    st.error("❌ Observación no encontrada.")
                else:
                    st.error(f"Error: {res_del.status_code}")

        elif res.status_code == 403:
            st.error("❌ No tienes permisos para ver observaciones.")
        else:
            st.error(f"Error: {res.status_code}")

# ─── CREAR PACIENTE ───────────────────────────────────────
def crear_paciente():
    st.header("➕ Nuevo Paciente")

    with st.form("form_paciente"):
        id = st.text_input("ID del paciente (ej: PAC-002)")
        col1, col2 = st.columns(2)
        family_name = col1.text_input("Apellido")
        given_name = col2.text_input("Nombre")
        gender = st.selectbox("Género", ["male", "female", "other"])
        birthDate = st.date_input(
            "Fecha de nacimiento",
            value=date(1990, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )
        identification_doc = st.text_input("Documento de identidad")
        col3, col4 = st.columns(2)
        weight = col3.text_input("Peso (kg)")
        height = col4.text_input("Altura (cm)")
        medical_summary = st.text_area("Resumen médico")

        submitted = st.form_submit_button("Crear paciente")

    if submitted:
        payload = {
            "id": id,
            "family_name": family_name,
            "given_name": given_name,
            "gender": gender,
            "birthDate": str(birthDate),
            "identification_doc": identification_doc,
            "weight": weight,
            "height": height,
            "medical_summary": medical_summary
        }
        res = requests.post(
            f"{API_URL}/JuanSalud/Patient/",
            headers={**get_headers(), "Content-Type": "application/json"},
            json=payload
        )
        if res.status_code == 200:
            st.success("✅ Paciente creado correctamente.")
        elif res.status_code == 403:
            st.error("❌ No tienes permisos para crear pacientes.")
        elif res.status_code == 400:
            st.error(f"❌ {res.json()['detail']}")
        else:
            st.error(f"Error: {res.status_code}")

# ─── CREAR OBSERVACIÓN ────────────────────────────────────
def crear_observacion():
    st.header("➕ Nueva Observación")

    with st.form("form_observacion"):
        patient_id = st.text_input("ID del paciente")
        category = st.selectbox("Categoría", ["vital-signs", "laboratory", "imaging"])
        col1, col2 = st.columns(2)
        code = col1.text_input("Código FHIR (ej: 55284-4)")
        display = col2.text_input("Nombre (ej: Blood Pressure)")
        col3, col4 = st.columns(2)
        value = col3.number_input("Valor", format="%.2f")
        unit = col4.text_input("Unidad (ej: mmHg)")
        date = st.date_input("Fecha")

        submitted = st.form_submit_button("Crear observación")

    if submitted:
        payload = {
            "patient_id": patient_id,
            "category": category,
            "code": code,
            "display": display,
            "value": value,
            "unit": unit,
            "date": str(date)
        }
        res = requests.post(
            f"{API_URL}/JuanSalud/Observation/",
            headers={**get_headers(), "Content-Type": "application/json"},
            json=payload
        )
        if res.status_code == 201:
            st.success("✅ Observación creada correctamente.")
        elif res.status_code == 403:
            st.error("❌ No tienes permisos para crear observaciones.")
        elif res.status_code == 404:
            st.error("❌ Paciente no encontrado.")
        else:
            st.error(f"Error: {res.status_code} - {res.text}")

# ─── MAIN ─────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    login()
else:
    dashboard()