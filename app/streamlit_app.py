import streamlit as st
from supabase import create_client, Client
import math

# --- Connexion à Supabase ---
url = st.secrets["supabase_url"]
key = st.secrets["supabase_key"]
supabase: Client = create_client(url, key)

# --- CSS pour fond blanc et grille moderne ---
st.markdown(
    """
    <style>
        body, .stApp { background: #fff !important; }
        .pokemon-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 24px;
            margin-top: 32px;
        }
        .pokemon-card {
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.07);
            padding: 16px;
            text-align: center !important;
            transition: box-shadow 0.2s;
            cursor: pointer;
        }
        .pokemon-card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.13);
        }
        .pokemon-sprite {
            width: 72px;
            height: 72px;
            background: #fff;
            margin-bottom: 8px;
            margin-left: auto;
            margin-right: auto;
            display: block;
        }
        .search-bar input {
            background: #fff !important;
        }
        .pokemon-name, .pokemon-number {
            display: block;
            text-align: center;
            color: #111 !important;
            font-weight: 600;
            font-size: 1.1em;
        }
        .pokemon-number {
            font-weight: 700;
        }
        .stTextInput, .stTextInput > div, .stTextInput > div > div {
            background: transparent !important;
            box-shadow: none !important;
            border: none !important;
        }
        .stTextInput > div > div > input {
            background: linear-gradient(90deg, rgba(255,255,255,0.98) 0%, rgba(210,210,210,0.95) 100%) !important;
            color: #222 !important;
            border: 1.5px solid #bbb !important;
            border-radius: 2em !important;
            box-shadow: none !important;
            padding: 0.7em 1.2em !important;
            font-size: 1.1em !important;
            transition: border 0.2s;
        }
        .stTextInput > div > div > input::placeholder {
            color: #888 !important;
            opacity: 1 !important;
        }
        .stTextInput > div > div > input:focus {
            border: 1.5px solid #888 !important;
            background: rgba(255,255,255,0.95) !important;
        }
        .stTextInput label {
            display: none !important;
        }
        /* Style des boutons de pagination */
        .stButton > button {
            background: linear-gradient(90deg, rgba(255,255,255,0.98) 0%, rgba(210,210,210,0.95) 100%) !important;
            color: #222 !important;
            border: 1.5px solid #bbb !important;
            border-radius: 2em !important;
            box-shadow: none !important;
            padding: 0.5em 1.2em !important;
            font-size: 1em !important;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            border: 1.5px solid #888 !important;
            background: rgba(255,255,255,0.95) !important;
        }
        .stButton > button:disabled {
            background: rgba(240,240,240,0.5) !important;
            color: #999 !important;
            border: 1.5px solid #ddd !important;
        }
        /* Style du sélecteur de page */
        .page-nav {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.2em;
            margin: 2em auto;
            background: linear-gradient(90deg, rgba(255,255,255,0.98) 0%, rgba(210,210,210,0.95) 100%);
            border: 1.5px solid #bbb;
            border-radius: 2em;
            padding: 0.5em 1em;
            width: fit-content;
        }
        .page-nav .stButton {
            display: inline-block;
        }
        .page-nav .stButton > button:disabled {
            cursor: not-allowed;
            color: #999 !important;
            background: none !important;
        }
        .page-info {
            display: inline-flex;
            align-items: center;
            font-size: 1.1em;
            color: #222;
            font-weight: 600;
            padding: 0 0.2em;
        }
        div[data-testid="stNumberInput"] {
            max-width: 100px;
            margin: 1em auto 0 auto;
        }
        div[data-testid="stNumberInput"] input {
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Barre de recherche ---
st.markdown("""
<h1 style='text-align: center; color: #222; font-size: 2.5em; font-weight: 800; margin-bottom: 0.2em;'>Pokédex PKMN.DB</h1>
""", unsafe_allow_html=True)
search = st.text_input("", key="search", placeholder="Rechercher par nom ou ID…")

# --- Récupération des Pokémon ---
limit = 25

# Pagination : page courante dans session_state
if 'page' not in st.session_state:
    st.session_state['page'] = 1

# Calcul de l'offset
page = st.session_state['page']
offset = (page - 1) * limit

total_count = 0

if search:
    # Recherche par nom (ilike) ou ID
    query = supabase.table("pokemons").select("*", count="exact")
    if search.isdigit():
        query = query.eq("id", int(search))
    else:
        query = query.ilike("name_en", f"%{search}%")
    data = query.range(offset, offset + limit - 1).execute()
    pokemons = data.data
    total_count = data.count or 0
else:
    # 25 par page, triés par ID croissant
    data = supabase.table("pokemons").select("*", count="exact").order("id").range(offset, offset + limit - 1).execute()
    pokemons = data.data
    total_count = data.count or 0

# --- Affichage en grille ---
if pokemons:
    st.markdown('<div class="pokemon-grid">', unsafe_allow_html=True)
    for row in [pokemons[i:i+5] for i in range(0, len(pokemons), 5)]:
        cols = st.columns(5)
        for idx, p in enumerate(row):
            name = p.get("name_en", "???")
            sprite_url = p.get("sprite_url") or p.get("sprite") or ""
            with cols[idx]:
                st.markdown(f"<div style='display: flex; justify-content: center;'><img src='{sprite_url}' width='72' style='display:block;'/></div>", unsafe_allow_html=True)
                st.markdown(f"<span class='pokemon-number'>#{p.get('id', 0):03d}</span> <span class='pokemon-name'>{name.capitalize()}</span>&nbsp;&nbsp;", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Aucun Pokémon trouvé.")

# --- Pagination ---
max_page = max(1, (total_count + limit - 1) // limit)

# Boutons de pagination
col1, col2, col3 = st.columns([4,2,4])
with col2:
    col_prev, _, col_next = st.columns([1,1,1])
    with col_prev:
        if st.button("<", disabled=page <= 1):
            st.session_state['page'] = max(1, page - 1)
            st.rerun()
    with col_next:
        if st.button("&gt;", disabled=page >= max_page):
            st.session_state['page'] = min(max_page, page + 1)
            st.rerun()

# Slider de pagination sur la ligne du dessous
_, col_slider, _ = st.columns([1.5,2,1.5])
with col_slider:
    page = st.slider("", min_value=1, max_value=max_page, value=page, step=1, key="page_slider", label_visibility="collapsed") 