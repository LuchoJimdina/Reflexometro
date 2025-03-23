import streamlit as st
import sqlite3
import pandas as pd
from typing import Optional, Tuple

# CONFIGURACIÓN DE LA PÁGINA Y CSS PERSONALIZADO
st.set_page_config(page_title="Registro de Reflexiones", layout="centered")

st.markdown(
    """
    <style>
    /* Fondo con gradiente suave */
    .stApp {
        background: linear-gradient(to right, #f2f2f2, #ececec);
    }
    /* Encabezados con mayor tamaño y centrados */
    h1 {
        font-size: 2.8em;
        color: #2c3e50;
        text-align: center;
    }
    h2 {
        font-size: 2em;
        color: #34495e;
        text-align: center;
    }
    /* Mejorar la legibilidad de los textos de los formularios */
    .stRadio label, .stTextInput > div > input, .stTextArea textarea, .stSlider > div > div {
        font-size: 1.3em;
    }
    /* Estilos de botones */
    .stButton>button {
        font-size: 1.3em;
        padding: 0.5em 1em;
        background-color: #2c3e50;
        color: white;
        border-radius: 5px;
    }
    /* Estilo para la imagen del encabezado */
    .header-img {
        width: 80%;
        margin: 0 auto 20px;
        display: block;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# IMAGEN DE ENCABEZADO (puedes reemplazar la URL o usar un archivo local)
st.image("https://via.placeholder.com/600x150.png?text=Tu+Logo+o+Encabezado", use_container_width=True)

# BASE DE DATOS
DB_NAME = "reflections.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    # Tabla de reflexiones
    c.execute('''
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            dificultad INTEGER NOT NULL,
            sentimiento INTEGER NOT NULL,
            seleccion TEXT NOT NULL,
            comentarios TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

def init_users():
    """
    Inserta usuarios iniciales (alumnos y profesor) solo si la tabla está vacía.
    Ajusta los nombres, contraseñas y roles según tus necesidades.
    """
    initial_users = [
        ("alarcon", "pass123", "student"),
        ("alvarez", "pass123", "student"),
        ("garcia1", "pass123", "student"),
        ("garcia2", "pass123", "student"),
        ("gonzalez", "pass123", "student"),
        ("igual", "pass123", "student"),
        ("juarez", "pass123", "student"),
        ("lopez", "pass123", "student"),
        ("robles", "pass123", "student"),
        ("rodriguez", "pass123", "student"),
        ("segura", "pass123", "student"),
        # Profesor (superusuario)
        ("profesor", "admin123", "admin")
    ]
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        for (username, password, role) in initial_users:
            try:
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          (username, password, role))
            except sqlite3.IntegrityError:
                pass
        conn.commit()
    conn.close()

# AUTENTICACIÓN Y GESTIÓN DE USUARIOS
def authenticate_user(username: str, password: str) -> Optional[Tuple[int, str]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, password, role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        user_id, stored_password, role = row
        if password == stored_password:  # Nota: en producción usa hash
            return (user_id, role)
    return None

# FUNCIONES DE REFLEXIONES
def insert_reflection(user_id: int, dificultad: int, sentimiento: int, seleccion: str, comentarios: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO reflections (user_id, dificultad, sentimiento, seleccion, comentarios) VALUES (?, ?, ?, ?, ?)",
              (user_id, dificultad, sentimiento, seleccion, comentarios))
    conn.commit()
    conn.close()

def get_reflections_for_user(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT r.id, u.username, r.dificultad, r.sentimiento, r.seleccion, r.comentarios
        FROM reflections r
        JOIN users u ON r.user_id = u.id
        WHERE r.user_id = ?
        ORDER BY r.id DESC
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_reflections():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT r.id, u.username, r.dificultad, r.sentimiento, r.seleccion, r.comentarios
        FROM reflections r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.id DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

# INTERFAZ DE STREAMLIT CON FUNCIONALIDADES SEGREGADAS POR ROL
def main():
    st.title("Registro de Reflexiones - Múltiples Usuarios")
    create_tables()
    init_users()

    # Manejo de sesión en st.session_state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.role = None

    if not st.session_state.logged_in:
        st.subheader("Inicia sesión")
        username = st.text_input("Usuario:")
        password = st.text_input("Contraseña:", type="password")
        if st.button("Ingresar"):
            result = authenticate_user(username, password)
            if result:
                user_id, role = result
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.role = role
                st.success("Sesión iniciada correctamente.")
            else:
                st.error("Usuario o contraseña inválidos.")
    else:
        # Vista para alumnos
        if st.session_state.role == "student":
            st.subheader("Bienvenido (Alumno)")
            with st.form("reflection_form", clear_on_submit=True):
                dificultad = st.radio(
                    "Selecciona el nivel de dificultad de la lección:",
                    [1, 2, 3, 4, 5],
                    format_func=lambda x: {
                        1: "😃 Muy fácil",
                        2: "🙂 Fácil",
                        3: "😐 Normal",
                        4: "😟 Difícil",
                        5: "😢 Muy difícil"
                    }[x]
                )
                sentimiento = st.slider("¿Cómo te has sentido? (1-5)", 1, 5, 3)
                seleccion = st.radio(
                    "¿Qué te ha resultado más fácil o difícil?",
                    ["Contenido", "Ejercicios", "Tiempo", "Otro"]
                )
                comentarios = st.text_area("Comentarios:")
                submitted = st.form_submit_button("Enviar Reflexión")
                if submitted:
                    insert_reflection(st.session_state.user_id, dificultad, sentimiento, seleccion, comentarios)
                    st.success("Reflexión enviada con éxito.")
            st.subheader("Mis Reflexiones")
            rows = get_reflections_for_user(st.session_state.user_id)
            if rows:
                df = pd.DataFrame(rows, columns=["ID", "Usuario", "Dificultad", "Sentimiento", "Opción", "Comentarios"])
                # Filtros para el alumno
                difficulties = [1, 2, 3, 4, 5]
                selected_difficulties = st.multiselect("Filtrar por Dificultad", difficulties, default=difficulties)
                df = df[df["Dificultad"].isin(selected_difficulties)]
                sentiments = [1, 2, 3, 4, 5]
                selected_sentiments = st.multiselect("Filtrar por Sentimiento", sentiments, default=sentiments)
                df = df[df["Sentimiento"].isin(selected_sentiments)]
                st.dataframe(df)
            else:
                st.info("Aún no tienes reflexiones registradas.")

        # Vista para profesor (admin)
        elif st.session_state.role == "admin":
            st.subheader("Bienvenido (Profesor / Admin)")
            st.write("Esta sección te permite ver **todas** las reflexiones de los alumnos.")
            rows = get_all_reflections()
            if rows:
                df = pd.DataFrame(rows, columns=["ID", "Usuario", "Dificultad", "Sentimiento", "Opción", "Comentarios"])
                # Filtros para el admin
                usuarios = sorted(df["Usuario"].unique())
                selected_usuarios = st.multiselect("Filtrar por Usuario", usuarios, default=usuarios)
                df = df[df["Usuario"].isin(selected_usuarios)]
                difficulties = [1, 2, 3, 4, 5]
                selected_difficulties = st.multiselect("Filtrar por Dificultad", difficulties, default=difficulties)
                df = df[df["Dificultad"].isin(selected_difficulties)]
                sentiments = [1, 2, 3, 4, 5]
                selected_sentiments = st.multiselect("Filtrar por Sentimiento", sentiments, default=sentiments)
                df = df[df["Sentimiento"].isin(selected_sentiments)]
                st.dataframe(df)
            else:
                st.info("No hay reflexiones registradas todavía.")

        # Botón de cierre de sesión
        if st.button("Cerrar Sesión"):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.role = None
                st.stop()


if __name__ == "__main__":
    main()
