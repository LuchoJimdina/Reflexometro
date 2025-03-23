import streamlit as st
import sqlite3

# Configurar la página lo antes posible
st.set_page_config(page_title="Registro de Reflexiones", layout="centered")

# Inyectamos CSS personalizado para mejorar la apariencia
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

# Mostrar un encabezado con imagen (coloca la URL de tu imagen o logo)
st.image("https://img.freepik.com/foto-gratis/pequeno-genio-resolviendo-algebra-clase_53876-96969.jpg?ga=GA1.1.811801369.1705990291&semt=ais_hybrid", use_container_width=True)

# Función para inicializar la base de datos
def init_db():
    conn = sqlite3.connect('reflections.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dificultad INTEGER NOT NULL,
            sentimiento INTEGER NOT NULL,
            seleccion TEXT NOT NULL,
            comentarios TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Función para insertar una reflexión en la base de datos
def insert_reflection(dificultad, sentimiento, seleccion, comentarios):
    conn = sqlite3.connect('reflections.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO reflections (dificultad, sentimiento, seleccion, comentarios)
        VALUES (?, ?, ?, ?)
    ''', (dificultad, sentimiento, seleccion, comentarios))
    conn.commit()
    conn.close()

# Función para obtener todas las reflexiones (opcional)
def get_reflections():
    conn = sqlite3.connect('reflections.db')
    c = conn.cursor()
    c.execute('SELECT * FROM reflections')
    rows = c.fetchall()
    conn.close()
    return rows

def main():
    st.title("Registro de Reflexiones de la Lección")
    st.markdown("<h2 style='color: #2c3e50;'>¡Bienvenidos estudiantes!</h2>", unsafe_allow_html=True)
    st.markdown("Inicia sesión para registrar tu reflexión de la lección de hoy.", unsafe_allow_html=True)
    
    # Simulación de inicio de sesión
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("Inicia sesión")
        password = st.text_input("Ingresa tu clave:", type="password")
        if st.button("Ingresar"):
            if password == "12345":  # La clave correcta
                st.session_state.logged_in = True
                st.success("Inicio de sesión correcto!")
            else:
                st.error("Clave incorrecta. Intenta nuevamente.")
    else:
        st.write("¡Bienvenido!")
        st.subheader("Ingresa tu reflexión")

        # Formulario para recoger los datos
        with st.form("reflection_form", clear_on_submit=True):
            dificultad = st.radio(
                "Selecciona el nivel de dificultad de la lección:",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: {
                    1: "😃 Muy fácil",
                    2: "🙂 Fácil",
                    3: "😐 Normal",
                    4: "😟 Difícil",
                    5: "😢 Muy difícil"
                }[x]
            )
            sentimiento = st.slider("¿Cómo te has sentido durante la lección? (1-5)", min_value=1, max_value=5, step=1)
            seleccion = st.radio(
                "¿Qué te ha resultado más fácil o difícil?",
                ("Contenido", "Ejercicios", "Tiempo", "Otro")
            )
            comentarios = st.text_area("Comentarios adicionales:")
            submitted = st.form_submit_button("Enviar Reflexión")
            if submitted:
                insert_reflection(dificultad, sentimiento, seleccion, comentarios)
                st.success("Reflexión enviada. ¡Gracias!")

        # Mostrar reflexiones registradas (opcional)
        st.subheader("Reflexiones Registradas")
        reflections = get_reflections()
        if reflections:
            for row in reflections:
                st.markdown(
                    f"**ID:** {row[0]} | **Dificultad:** {row[1]} | **Sentimiento:** {row[2]} | **Opción:** {row[3]}<br>"
                    f"**Comentarios:** {row[4]}",
                    unsafe_allow_html=True
                )
        else:
            st.info("Aún no hay reflexiones registradas.")

if __name__ == "__main__":
    init_db()
    main()
