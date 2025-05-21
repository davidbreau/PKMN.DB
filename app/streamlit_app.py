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
        /* Étendre la largeur de la page */
        .block-container {
            max-width: 1000px;
            padding-left: 5px;
            padding-right: 5px;
        }
        
        body, .stApp { background: #fff !important; }
        
        /* Style de la grille */
        .pokemon-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 32px;
            margin-top: 32px;
            padding: 0 24px;
            margin-bottom: 32px;
        }
        
        /* Style de la carte Pokémon */
        .pokemon-card {
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.07);
            padding: 16px;
            text-align: center !important;
            transition: all 0.3s ease;
            cursor: pointer;
            min-width: 160px;
            width: 100%;
            margin: 0 auto;
            max-width: 200px;
            position: relative;
            padding-bottom: 40px !important;
        }

        .pokemon-card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.13);
        }

        /* Style de la carte sélectionnée */
        .selected-pokemon {
            box-shadow: 0 4px 12px rgba(255,139,61,0.2) !important;
            border: 1px solid rgba(255,139,61,0.3) !important;
        }

        .selected-pokemon:hover {
            box-shadow: 0 6px 16px rgba(255,139,61,0.25) !important;
        }

        /* Style des éléments de la carte */
        .pokemon-name {
            display: block;
            text-align: center;
            color: #111 !important;
            font-weight: 600;
            font-size: 1.1em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            padding: 0 5px;
            margin-bottom: 8px;
        }

        .pokemon-number {
            display: block;
            text-align: center;
            color: #111 !important;
            font-weight: 700;
            margin-bottom: 4px;
        }

        /* Style du bouton */
        .stButton > button {
            background: #f5f5f5 !important;
            border: none !important;
            padding: 5px 10px !important;
            border-radius: 5px !important;
            color: #666 !important;
            font-size: 0.9em !important;
            transition: all 0.2s ease !important;
            margin-top: 5px !important;
        }

        .stButton > button:hover {
            background: #ebebeb !important;
            color: #333 !important;
        }

        /* Conteneur pour le bouton */
        .button-container {
            position: absolute;
            bottom: 8px;
            left: 0;
            right: 0;
            display: flex;
            justify-content: center;
        }

        /* Style de la barre de recherche */
        .search-bar input {
            background: #fff !important;
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

        /* Style des types */
        .type-badge {
            display: inline-block;
            padding: 0.3em 1em;
            border-radius: 2em;
            color: white;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            margin: 0.2em;
            min-width: 80px;
            text-align: center;
        }

        /* Style des stats */
        .stat-bar {
            background: linear-gradient(90deg, var(--stat-color) var(--stat-percent), #eee var(--stat-percent));
            height: 8px;
            border-radius: 4px;
            margin: 4px 0;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 2px;
        }
        .stat-value {
            color: #222;
            font-weight: 600;
            font-size: 0.9em;
            float: right;
        }

        /* Couleurs des types */
        .type-normal { background-color: #A8A878; }
        .type-fire { background-color: #F08030; }
        .type-water { background-color: #6890F0; }
        .type-grass { background-color: #78C850; }
        .type-electric { background-color: #F8D030; }
        .type-ice { background-color: #98D8D8; }
        .type-fighting { background-color: #C03028; }
        .type-poison { background-color: #A040A0; }
        .type-ground { background-color: #E0C068; }
        .type-flying { background-color: #A890F0; }
        .type-psychic { background-color: #F85888; }
        .type-bug { background-color: #A8B820; }
        .type-rock { background-color: #B8A038; }
        .type-ghost { background-color: #705898; }
        .type-dark { background-color: #705848; }
        .type-dragon { background-color: #7038F8; }
        .type-steel { background-color: #B8B8D0; }
        .type-fairy { background-color: #F0B6BC; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Supprimer les marges par défaut de Streamlit
st.markdown("""
    <style>
        .main > div {
            padding-top: 1rem;
        }
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

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

# Si une nouvelle recherche est lancée, revenir à la page 1
if 'previous_search' not in st.session_state:
    st.session_state['previous_search'] = ''
if search != st.session_state['previous_search']:
    st.session_state['page'] = 1
    st.session_state['previous_search'] = search

# Calcul de l'offset
page = st.session_state['page']
offset = (page - 1) * limit

total_count = 0

try:
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
except Exception as e:
    st.error("Une erreur est survenue lors de la recherche. Veuillez réessayer.")
    pokemons = []
    total_count = 0

# Initialize session state for selected Pokémon
if 'selected_pokemon_id' not in st.session_state:
    st.session_state['selected_pokemon_id'] = None

# --- Affichage en grille ---
if pokemons:
    # Organiser les Pokémon en lignes de 5
    rows = [pokemons[i:i+5] for i in range(0, len(pokemons), 5)]
    
    for row_idx, row in enumerate(rows):
        # Ouvrir une nouvelle grille pour chaque ligne
        st.markdown('<div class="pokemon-grid">', unsafe_allow_html=True)
        
        # Afficher les cartes de la ligne
        cols = st.columns(5)
        for idx, p in enumerate(row):
            name = p.get("name_en", "???")
            sprite_url = p.get("sprite_url") or p.get("sprite") or ""
            pokemon_id = p.get("id")
            with cols[idx]:
                # Ajouter la classe selected-pokemon si ce Pokémon est sélectionné
                is_selected = st.session_state.get('selected_pokemon_id') == pokemon_id
                card_class = "pokemon-card" + (" selected-pokemon" if is_selected else "")
                
                # Display the card content
                st.markdown(f"""
                    <div class="{card_class}">
                        <div style='display: flex; justify-content: center;'>
                            <img src='{sprite_url}' width='72' style='display:block;'/>
                        </div>
                        <span class='pokemon-number'>#{pokemon_id:03d}</span>
                        <span class='pokemon-name'>{name.capitalize()}</span>
                        <div class="button-container">
                """, unsafe_allow_html=True)
                
                # Bouton pour afficher/masquer les détails
                button_text = "Hide Details" if is_selected else "Show Details"
                if st.button(button_text, key=f"btn_{pokemon_id}"):
                    if st.session_state.get('selected_pokemon_id') == pokemon_id:
                        st.session_state['selected_pokemon_id'] = None
                        st.session_state['selected_row'] = None
                    else:
                        st.session_state['selected_pokemon_id'] = pokemon_id
                        st.session_state['selected_row'] = row_idx
                    st.rerun()
                
                st.markdown("</div></div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Afficher les détails si un Pokémon de cette ligne est sélectionné
        if st.session_state.get('selected_pokemon_id') and st.session_state.get('selected_row') == row_idx:
            try:
                pokemon_id = st.session_state['selected_pokemon_id']
                
                # Basic info first
                pokemon = supabase.table("pokemons").select("*").eq("id", pokemon_id).single().execute()
                if not pokemon.data:
                    st.error(f"Pokemon {pokemon_id} not found")
                    st.session_state['selected_pokemon_id'] = None
                    st.rerun()
                
                pokemon = pokemon.data
                
                # Titre et Types sur la même ligne
                type1 = supabase.table("types").select("name").eq("id", pokemon["type_1_id"]).single().execute().data
                type_html = f'<span class="type-badge type-{type1["name"].lower()}">{type1["name"]}</span>'
                
                if pokemon.get("type_2_id"):
                    type2 = supabase.table("types").select("name").eq("id", pokemon["type_2_id"]).single().execute().data
                    type_html += f' <span class="type-badge type-{type2["name"].lower()}">{type2["name"]}</span>'
                
                st.markdown(f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <h2 style="color: #333; margin-bottom: 15px;">
                            {pokemon['name_en']} / {pokemon['name_fr'] or '???'}
                        </h2>
                        <div style="margin: 10px 0;">
                            {type_html}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Stats dans une grille 2 colonnes
                col1, col2 = st.columns(2)
                
                with col1:
                    # Stats de base
                    stats = supabase.table("pokemon_stats").select("*").eq("pokemon_id", pokemon_id).single().execute()
                    if stats.data:
                        st.markdown("""
                            <h3 style="color: #444; margin: 10px 0;">Base Stats</h3>
                        """, unsafe_allow_html=True)
                        
                        stats_data = [
                            ("HP", stats.data['hp'], "#FF0000"),
                            ("Attack", stats.data['attack'], "#F08030"),
                            ("Defense", stats.data['defense'], "#F8D030"),
                            ("Sp. Attack", stats.data['special_attack'], "#6890F0"),
                            ("Sp. Defense", stats.data['special_defense'], "#78C850"),
                            ("Speed", stats.data['speed'], "#F85888")
                        ]
                        
                        for name, value, color in stats_data:
                            percentage = (value / 255) * 100
                            st.markdown(f"""
                                <div style="margin: 8px 0;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                        <span style="color: #555;">{name}</span>
                                        <span style="color: #333; font-weight: 500;">{value}</span>
                                    </div>
                                    <div style="background: #e9ecef; height: 8px; border-radius: 4px;">
                                        <div style="width: {percentage}%; background: {color}; height: 100%; border-radius: 4px;"></div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                
                with col2:
                    # GO stats
                    try:
                        go_pokemon = supabase.table("go_pokemons").select("*").eq("pokedex_number", pokemon["national_pokedex_number"]).single().execute()
                        if go_pokemon.data:
                            go_stats = supabase.table("go_pokemon_stats").select("*").eq("pokemon_id", go_pokemon.data["id"]).single().execute()
                            if go_stats.data:
                                st.markdown("""
                                    <h3 style="color: #444; margin: 10px 0;">Pokémon GO Stats</h3>
                                """, unsafe_allow_html=True)
                                
                                # Max CP séparé
                                st.markdown(f"""
                                    <div style="text-align: center; margin: 15px 0;">
                                        <span style="font-size: 1.2em; color: #333;">
                                            Max CP: <strong>{go_stats.data['max_cp']:,}</strong>
                                        </span>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Autres stats GO
                                go_stats_data = [
                                    ("Attack", go_stats.data['attack'], "#F08030"),
                                    ("Defense", go_stats.data['defense'], "#F8D030"),
                                    ("Stamina", go_stats.data['stamina'], "#78C850")
                                ]
                                
                                for name, value, color in go_stats_data:
                                    percentage = (value / 300) * 100
                                    st.markdown(f"""
                                        <div style="margin: 8px 0;">
                                            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                                <span style="color: #555;">{name}</span>
                                                <span style="color: #333; font-weight: 500;">{value}</span>
                                            </div>
                                            <div style="background: #e9ecef; height: 8px; border-radius: 4px;">
                                                <div style="width: {percentage}%; background: {color}; height: 100%; border-radius: 4px;"></div>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown("""
                            <p style="color: #666; font-style: italic; text-align: center; margin: 10px 0;">
                                Pokémon GO stats not available
                            </p>
                        """, unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"Error loading details: {str(e)}")
else:
    st.info("Aucun Pokémon trouvé.")

# --- Pagination ---
max_page = max(1, (total_count + limit - 1) // limit)

# Boutons de pagination
col1, col2, col3 = st.columns([4,2,4])
with col2:
    col_prev, col_next = st.columns([1,1])
    with col_prev:
        prev_disabled = page <= 1
        if st.button("←", disabled=prev_disabled, key="prev_page"):
            st.session_state['page'] = max(1, page - 1)
            # Ne pas réinitialiser selected_pokemon_id ici
            st.rerun()
    with col_next:
        next_disabled = page >= max_page
        if st.button("→", disabled=next_disabled, key="next_page"):
            st.session_state['page'] = min(max_page, page + 1)
            # Ne pas réinitialiser selected_pokemon_id ici
            st.rerun()

# Slider de pagination sur la ligne du dessous
_, col_slider, _ = st.columns([1.5,2,1.5])
with col_slider:
    if max_page > 1:
        new_page = st.slider("", min_value=1, max_value=max_page, value=page, step=1, key="page_slider", label_visibility="collapsed")
        if new_page != page:
            st.session_state['page'] = new_page
            # Ne pas réinitialiser selected_pokemon_id ici
            st.rerun()
    else:
        st.markdown("<div style='text-align: center; color: #666;'>Page 1/1</div>", unsafe_allow_html=True)

# Réinitialiser la sélection uniquement lors d'une nouvelle recherche
if search != st.session_state['previous_search']:
    st.session_state['page'] = 1
    st.session_state['previous_search'] = search
    st.session_state['selected_pokemon_id'] = None  # Réinitialiser uniquement lors d'une nouvelle recherche
    st.session_state['selected_row'] = None 