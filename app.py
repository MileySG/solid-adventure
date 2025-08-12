# app.py
# Roles de Contribución Consciente — Test anti-sesgo con WhatsApp share
# Ejecuta: streamlit run app.py

import streamlit as st
import random
import pandas as pd
import json
from io import StringIO
from urllib.parse import quote

st.set_page_config(page_title="Roles de Contribución Consciente", page_icon="🌟", layout="centered")

# ------------------ Definición de roles (desc, fortalezas, mejoras, preguntas Access) ------------------
ROLES = [
    {
        "key": "Coordinador",
        "desc": "Conecta personas, recursos e información. Facilita acuerdos, claridad y flujo.",
        "fortalezas": [
            "Hace visibles los objetivos y responsables.",
            "Genera alineación y reduce fricción.",
            "Traduce necesidades entre equipos."
        ],
        "mejoras": [
            "Evitar sobre-facilitar: deja espacio a otros.",
            "Pedir evidencia cuando haya ambigüedad.",
            "Decidir a tiempo (no quedar en mediación eterna)."
        ],
        "access": [
            "¿Qué energía, espacio y conciencia puedo ser para que la colaboración sea ligera?",
            "¿Esto crea más para todos, incluído yo?",
            "¿Qué claridad falta aquí que si aparece lo facilita todo?"
        ]
    },
    {
        "key": "Creativo",
        "desc": "Genera alternativas y posibilidades. Encuentra caminos no obvios e innovación.",
        "fortalezas": [
            "Abre el campo de opciones y disrumpe bloqueos.",
            "Propone enfoques originales y frescos.",
            "Tolera la ambigüedad inicial."
        ],
        "mejoras": [
            "Aterrizar ideas con criterios de priorización.",
            "Evitar saltar de idea en idea sin cerrar ciclos.",
            "Co-diseñar con quien implementa desde el inicio."
        ],
        "access": [
            "¿Qué más es posible que no he considerado?",
            "Si nada estuviera mal, ¿qué elegiría crear ahora?",
            "¿Qué idea hace que todo sea más simple?"
        ]
    },
    {
        "key": "Implementador",
        "desc": "Convierte ideas en acción. Estructura pasos, tiempos y seguimiento.",
        "fortalezas": [
            "Define entregables claros y medibles.",
            "Mantiene foco y convierte intención en resultado.",
            "Cuida el ritmo del proyecto."
        ],
        "mejoras": [
            "Permitir ajustes sin apego al plan original.",
            "Pedir contexto para evitar ejecutar en vacío.",
            "Delegar cuando el volumen crece."
        ],
        "access": [
            "¿Cuál es el próximo paso más ligero?",
            "¿Qué parte no es necesaria y puedo eliminar?",
            "¿Qué elegiría si el plazo fuera fácil?"
        ]
    },
    {
        "key": "Finalizador",
        "desc": "Cuida calidad, detalle y cumplimiento de plazos. Cierra bien los ciclos.",
        "fortalezas": [
            "Sube estándares y reduce errores.",
            "Asegura entregas a tiempo.",
            "Sostiene la excelencia del producto."
        ],
        "mejoras": [
            "Evitar perfeccionismo paralizante.",
            "Diferenciar lo crítico de lo accesorio.",
            "Comunicar criterios de calidad temprano."
        ],
        "access": [
            "¿Qué nivel de calidad crea más valor aquí?",
            "¿Qué es suficientemente bueno para avanzar hoy?",
            "Si el perfeccionismo no fuera real, ¿qué elegiría?"
        ]
    },
    {
        "key": "Investigador",
        "desc": "Busca datos y patrones. Valida supuestos y soporta decisiones.",
        "fortalezas": [
            "Encuentra información clave y reduce riesgos.",
            "Conecta datos con insights accionables.",
            "Aporta criterio y profundidad."
        ],
        "mejoras": [
            "Evitar la parálisis por análisis.",
            "Definir ventanas de tiempo para investigar.",
            "Compartir hallazgos en lenguaje simple."
        ],
        "access": [
            "¿Qué dato falta que haría esto obvio?",
            "¿Qué suposición puedo destruir y descrear ahora?",
            "¿Qué fuente hará esto más ligero y veloz?"
        ]
    },
    {
        "key": "Especialista",
        "desc": "Aporta profundidad técnica/experta en un área específica.",
        "fortalezas": [
            "Alta precisión y dominio especializado.",
            "Resuelve problemas complejos con criterio experto.",
            "Estandariza buenas prácticas."
        ],
        "mejoras": [
            "Evitar el silo: compartir conocimiento.",
            "Practicar comunicación no técnica para negocio.",
            "Confiar en otros para tareas no críticas."
        ],
        "access": [
            "¿Qué facilidad puedo ser para traducir lo técnico?",
            "¿Dónde compartir mi experiencia crea más?",
            "¿Qué actualización haría mi expertise exponencial?"
        ]
    },
]

# ------------------ Banco de preguntas (anti-sesgo; algunas invertidas) ------------------
# inv=True => inversión 1↔5
BANK = [
    {"id": 1,  "text": "Cuando surge un problema, visualizo varias maneras distintas de resolverlo.",               "role": "Creativo"},
    {"id": 2,  "text": "Prefiero trabajar con un plan claro antes de empezar.",                                    "role": "Implementador", "inv": True},
    {"id": 3,  "text": "Disfruto presentar personas que podrían beneficiarse de conocerse.",                       "role": "Coordinador"},
    {"id": 4,  "text": "Me motiva encontrar información que otros pasaron por alto.",                              "role": "Investigador"},
    {"id": 5,  "text": "Me enfoco en detalles para asegurar que todo quede impecable.",                            "role": "Finalizador"},
    {"id": 6,  "text": "Prefiero mantenerme en mi área de especialidad.",                                          "role": "Especialista"},
    {"id": 7,  "text": "Me incomoda decidir rápido sin datos suficientes.",                                        "role": "Coordinador",   "inv": True},
    {"id": 8,  "text": "Encuentro soluciones creativas a problemas complejos con facilidad.",                      "role": "Creativo"},
    {"id": 9,  "text": "Disfruto investigar y explorar opciones antes de decidir.",                                "role": "Investigador"},
    {"id": 10, "text": "Prefiero terminar una tarea antes de empezar otra.",                                       "role": "Finalizador"},
    {"id": 11, "text": "Me centro más en el objetivo general que en los detalles.",                                "role": "Finalizador",   "inv": True},
    {"id": 12, "text": "Me gusta mejorar procesos existentes para que funcionen mejor.",                           "role": "Implementador"},
    {"id": 13, "text": "Identifico rápido quién sería adecuado para cada tarea.",                                  "role": "Coordinador"},
    {"id": 14, "text": "Disfruto profundizar en habilidades técnicas avanzadas.",                                  "role": "Especialista"},
    {"id": 15, "text": "Rara vez cuestiono las formas establecidas de hacer las cosas.",                           "role": "Creativo",      "inv": True},
    {"id": 16, "text": "Me ocupo de que el equipo cumpla plazos y estándares.",                                    "role": "Finalizador"},
    {"id": 17, "text": "Me entusiasma diseñar estrategias no obvias a futuro.",                                    "role": "Creativo"},
    {"id": 18, "text": "Busco y analizo información para sustentar decisiones importantes.",                       "role": "Investigador"},
    {"id": 19, "text": "Transformo ideas generales en pasos concretos y medibles.",                                "role": "Implementador"},
    {"id": 20, "text": "Prefiero aplicar mi experiencia para resolver problemas técnicos.",                        "role": "Especialista"},
]

def invert_score(v: int) -> int:
    return 6 - v  # 1<->5, 2<->4, 3=3

@st.cache_data
def shuffled_bank(seed: int):
    items = BANK.copy()
    random.Random(seed).shuffle(items)
    return items

def compute_scores(answers: dict, items: list) -> pd.DataFrame:
    sums = {r["key"]: 0 for r in ROLES}
    counts = {r["key"]: 0 for r in ROLES}
    for q in items:
        v = answers.get(q["id"])
        if v is None:
            continue
        score = invert_score(v) if q.get("inv") else v
        sums[q["role"]] += score
        counts[q["role"]] += 1
    rows = []
    for r in ROLES:
        key = r["key"]
        max_role = counts[key] * 5 if counts[key] else 1
        pct = (sums[key] / max_role) * 100 if max_role else 0
        rows.append({"Rol": key, "Puntaje": sums[key], "Ítems": counts[key], "Porcentaje": round(pct, 1)})
    return pd.DataFrame(rows).sort_values("Puntaje", ascending=False).reset_index(drop=True)

# ------------------ Sidebar ------------------
st.sidebar.title("🌟 Roles de Contribución Consciente")
st.sidebar.write("Escala **1–5**: 1 = Nunca · 5 = Siempre")
seed = st.sidebar.number_input("Semilla de aleatorización", min_value=0, value=108, step=1,
                               help="Cambia la semilla para reordenar preguntas y reducir sesgos.")
st.sidebar.write("---")

# ------------------ Título ------------------
st.title("Roles de Contribución Consciente")
st.caption("Responde con sinceridad. Algunas afirmaciones están invertidas para controlar consistencia.")

# ------------------ Formulario ------------------
items = shuffled_bank(seed)
with st.form("quiz"):
    st.subheader("Responde a cada afirmación (1–5)")
    answers = {}
    for i, q in enumerate(items, start=1):
        st.markdown(f"**{i}.** {q['text']}")
        answers[q["id"]] = st.slider(" ", 1, 5, 3, key=f"q_{q['id']}")
        st.divider()
    submitted = st.form_submit_button("Ver mi perfil")

# ------------------ Resultados ------------------
if submitted:
    df = compute_scores(answers, items)
    st.success("¡Listo! Este es tu perfil de Roles de Contribución Consciente.")
    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("Rol")["Puntaje"], use_container_width=True)

    # Top roles
    max_score = df["Puntaje"].max()
    top_roles = df[df["Puntaje"] == max_score]["Rol"].tolist()
    st.subheader("Tu rol principal")
    st.write(", ".join(top_roles))

    # Descripción y recomendaciones
    st.subheader("Descripción, fortalezas y expansión")
    for meta in ROLES:
        row = df[df["Rol"] == meta["key"]].iloc[0]
        st.markdown(f"### {meta['key']} — {meta['desc']}")
        st.markdown(f"**Puntaje:** {int(row['Puntaje'])} · **Cobertura:** {int(row['Ítems'])} ítems · **{row['Porcentaje']}%** del máximo para este rol.")
        with st.expander("Fortalezas que aportas"):
            st.markdown("- " + "\n- ".join(meta["fortalezas"]))
        with st.expander("Áreas de mejora / expansión"):
            st.markdown("- " + "\n- ".join(meta["mejoras"]))
        with st.expander("Preguntas de Access para expandir este rol"):
            st.markdown("- " + "\n- ".join([f"*{q}*" for q in meta["access"]]))
        st.write("")

    # Descargas
    payload = {
        "respuestas": answers,
        "puntajes": {row["Rol"]: int(row["Puntaje"]) for _, row in df.iterrows()},
        "porcentajes": {row["Rol"]: float(row["Porcentaje"]) for _, row in df.iterrows()},
        "top_roles": top_roles,
        "nombre_app": "Roles de Contribución Consciente",
    }
    json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    csv_buf = StringIO(); df.to_csv(csv_buf, index=False)
    st.download_button("⬇️ Descargar JSON", data=json_bytes, file_name="roles_contribucion_consciente.json", mime="application/json")
    st.download_button("⬇️ Descargar CSV", data=csv_buf.getvalue(), file_name="roles_contribucion_consciente.csv", mime="text/csv")

    # ------------------ Compartir por WhatsApp ------------------
    st.subheader("Compartir por WhatsApp")
    resumen_lineas = [f"🌟 Roles de Contribución Consciente"]
    resumen_lineas.append(f"Rol(es) principal(es): {', '.join(top_roles)}")
    for _, row in df.iterrows():
        resumen_lineas.append(f"• {row['Rol']}: {int(row['Puntaje'])} pts ({row['Porcentaje']}%)")
    resumen_lineas.append("¿Qué energía puedes ser hoy para crear más?")
    resumen = "\n".join(resumen_lineas)

    texto_wa = quote(f"¡Acabo de descubrir mis Roles de Contribución Consciente! 🌟\n\n{resumen}")
    wa_link = f"https://wa.me/?text={texto_wa}"  # o usa https://wa.me/52NUMERO?text=...

    st.code(resumen, language="markdown")
    st.link_button("📲 Compartir por WhatsApp", wa_link)
    st.caption("Tip: Para enviar a un número concreto usa: https://wa.me/52NUMERO?text=...")

else:
    st.info("Ajusta las barras (1–5) y presiona **Ver mi perfil** para conocer tus roles, ver fortalezas y áreas de expansión, y compartir por WhatsApp.")
