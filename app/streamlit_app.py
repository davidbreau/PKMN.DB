import streamlit as st
from supabase import create_client, Client
import math
import requests
import json

# --- Connexion à Supabase ---
url = st.secrets["supabase_url"]
key = st.secrets["supabase_key"]
supabase: Client = create_client(url, key)

# --- Configuration de l'API BentoML ---
BENTOML_API_URL = st.secrets["bento_cloud_api_end_point"]
BENTOML_API_KEY = st.secrets["bento_cloud_api_key"]

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
            gap: 8px 24px;
            margin-top: 8px;
            padding: 0 24px;
            margin-bottom: 0;
        }
        
        /* Réduire l'espace entre les lignes de la grille */
        .pokemon-grid + .pokemon-grid {
            margin-top: 8px;
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
            padding-bottom: 30px !important;
        }

        .pokemon-card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.13);
        }

        /* Style de la carte sélectionnée */
        .selected-pokemon {
            box-shadow: 0 2px 8px rgba(255,95,32,0.4) !important;
            border: 2px solid rgba(255,95,32,0.5) !important;
        }

        .selected-pokemon:hover {
            box-shadow: 0 3px 12px rgba(255,95,32,0.5) !important;
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
        
        /* Style du bouton MEGA */
        .mega-button > button {
            background: linear-gradient(135deg, #4285f4, #34a853) !important;
            color: white !important;
            font-weight: bold !important;
            border: none !important;
            padding: 8px 16px !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            margin: 10px auto !important;
            display: block !important;
        }
        
        .mega-button > button:hover {
            background: linear-gradient(135deg, #3b77db, #2d9348) !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
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
        
        /* Style pour les stats augmentées */
        .stat-increase {
            color: #4285f4 !important;
            font-weight: bold !important;
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

        /* Supprimer les marges par défaut de Streamlit */
        .stMarkdown {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        .row-widget {
            margin-bottom: 0 !important;
        }
        /* Réduire l'espace des colonnes Streamlit */
        .css-ocqkz7.e1tzin5v4,
        .css-1r6slb0.e1tzin5v2 {
            gap: 0 !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
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

# --- Fonction pour prédire l'évolution ---
def predict_evolution(pokemon_data):
    try:
        # Debug: print the pokemon_data to see what fields are available
        # st.write(f"Debug - Données disponibles: {pokemon_data.keys()}")
        
        headers = {
            "Authorization": f"Bearer {BENTOML_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Create payload, ensuring all fields are present with fallbacks
        payload = {
            "pokemon_data": {
                "base_hp": pokemon_data.get("hp", 0),
                "base_attack": pokemon_data.get("attack", 0),
                "base_defense": pokemon_data.get("defense", 0),
                "base_sp_attack": pokemon_data.get("special_attack", 0),
                "base_sp_defense": pokemon_data.get("special_defense", 0),
                "base_speed": pokemon_data.get("speed", 0),
                "base_height": pokemon_data.get("height_m", pokemon_data.get("height", 0)),
                "base_weight": pokemon_data.get("weight_kg", pokemon_data.get("weight", 0)),
                "base_experience": pokemon_data.get("base_experience", 0)
            }
        }
        
        # Debug: print the actual payload being sent
        # st.write(f"Debug - Payload envoyé: {payload}")
        
        # Make sure the URL doesn't have a trailing slash
        api_url = BENTOML_API_URL.rstrip('/')
        # st.write(f"Debug - API URL: {api_url}/predict")
        
        response = requests.post(
            f"{api_url}/predict",
            headers=headers,
            json=payload,
            timeout=10  # Add timeout
        )
        
        # Debug: print the response
        # st.write(f"Debug - Status code: {response.status_code}")
        
        # Check if response has content and is valid JSON
        response_text = response.text.strip()
        if response.status_code == 200 and response_text:
            try:
                return response.json()
            except json.JSONDecodeError as json_err:
                # st.write(f"Debug - Response body: '{response_text}'")
                st.error(f"Erreur de format JSON: {str(json_err)}")
                
                # Temporary solution: create mock data for demonstration
                attack = pokemon_data.get("attack", 0)
                defense = pokemon_data.get("defense", 0)
                sp_attack = pokemon_data.get("special_attack", 0)
                sp_defense = pokemon_data.get("special_defense", 0)
                speed = pokemon_data.get("speed", 0)
                
                # Create a dummy response with approximately 20-30% stat increases
                dummy_response = {
                    "evolved_attack": round(attack * 1.25),
                    "evolved_defense": round(defense * 1.2),
                    "evolved_sp_attack": round(sp_attack * 1.3),
                    "evolved_sp_defense": round(sp_defense * 1.25),
                    "evolved_speed": round(speed * 1.15)
                }
                
                st.warning("Utilisation de données de simulation pour la démonstration")
                return dummy_response
        else:
            st.error(f"Erreur API: {response.status_code}")
            if response_text:
                # st.write(f"Debug - Response body: '{response_text}'")
                pass
                
            # Temporary solution: create mock data for demonstration
            attack = pokemon_data.get("attack", 0)
            defense = pokemon_data.get("defense", 0)
            sp_attack = pokemon_data.get("special_attack", 0)
            sp_defense = pokemon_data.get("special_defense", 0)
            speed = pokemon_data.get("speed", 0)
            
            # Create a dummy response with approximately 20-30% stat increases
            dummy_response = {
                "evolved_attack": round(attack * 1.25),
                "evolved_defense": round(defense * 1.2),
                "evolved_sp_attack": round(sp_attack * 1.3),
                "evolved_sp_defense": round(sp_defense * 1.25),
                "evolved_speed": round(speed * 1.15)
            }
            
            st.warning("Utilisation de données de simulation pour la démonstration")
            return dummy_response
    except Exception as e:
        st.error(f"Erreur de prédiction: {str(e)}")
        
        # Temporary solution: create mock data for demonstration
        attack = pokemon_data.get("attack", 0)
        defense = pokemon_data.get("defense", 0)
        sp_attack = pokemon_data.get("special_attack", 0)
        sp_defense = pokemon_data.get("special_defense", 0)
        speed = pokemon_data.get("speed", 0)
        
        # Create a dummy response with approximately 20-30% stat increases
        dummy_response = {
            "evolved_attack": round(attack * 1.25),
            "evolved_defense": round(defense * 1.2),
            "evolved_sp_attack": round(sp_attack * 1.3),
            "evolved_sp_defense": round(sp_defense * 1.25),
            "evolved_speed": round(speed * 1.15)
        }
        
        st.warning("Utilisation de données de simulation pour la démonstration")
        return dummy_response

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

# État de la prédiction
if 'evolution_prediction' not in st.session_state:
    st.session_state['evolution_prediction'] = None

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
                        st.session_state['evolution_prediction'] = None
                    else:
                        # Always clear previous selection before setting new one
                        st.session_state['selected_pokemon_id'] = None
                        st.session_state['selected_row'] = None
                        st.session_state['evolution_prediction'] = None
                        # Then set the new selection
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
                try:
                    pokemon = supabase.table("pokemons").select("*").eq("id", pokemon_id).single().execute()
                    if not pokemon.data:
                        st.error(f"Pokemon {pokemon_id} not found")
                        st.session_state['selected_pokemon_id'] = None
                        st.rerun()
                    
                    pokemon = pokemon.data
                    
                    # Get pokemon details for height, weight, etc.
                    try:
                        pokemon_details = supabase.table("pokemon_details").select("*").eq("pokemon_id", pokemon_id).single().execute()
                        if pokemon_details.data:
                            pokemon.update(pokemon_details.data)
                    except Exception:
                        # Ignorer l'erreur si les détails du Pokémon ne sont pas disponibles
                        pass
                    
                    # Titre et Types sur la même ligne
                    try:
                        type1 = supabase.table("types").select("name").eq("id", pokemon["type_1_id"]).single().execute().data
                        type_html = f'<span class="type-badge type-{type1["name"].lower()}">{type1["name"]}</span>'
                        
                        if pokemon.get("type_2_id"):
                            try:
                                type2 = supabase.table("types").select("name").eq("id", pokemon["type_2_id"]).single().execute().data
                                type_html += f' <span class="type-badge type-{type2["name"].lower()}">{type2["name"]}</span>'
                            except Exception:
                                # Ignorer l'erreur si le second type n'est pas disponible
                                pass
                    except Exception:
                        # Si le type est introuvable, afficher une valeur par défaut
                        type_html = '<span class="type-badge type-normal">Normal</span>'
                except Exception as e:
                    st.error(f"Error loading details: {str(e)}")
                
                st.markdown("""<div style="margin-top: -8px;"></div>""", unsafe_allow_html=True)
                
                # Trois colonnes pour les détails
                col_info, col_stats, col_go = st.columns([1,1,1])
                
                # Colonne d'informations de base
                with col_info:
                    st.markdown(f"""
                        <div style="text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100%; padding: 8px;">
                            <h2 style="color: #333; margin-bottom: 2px; font-size: 1.6em;">
                                {pokemon['name_en']}
                            </h2>
                            <div style="color: #666; font-size: 1em; margin: 4px 0;">
                                {pokemon['name_fr'] or '???'}
                            </div>
                            <div style="margin: 8px 0;">
                                {type_html}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Colonne des stats de base
                with col_stats:
                    try:
                        stats = supabase.table("pokemon_stats").select("*").eq("pokemon_id", pokemon_id).single().execute()
                        if stats.data:
                            # Entête des stats de base
                            with st.container():
                                st.markdown("""
                                    <h3 style="color: #444; margin: 2px 0; font-size: 1.1em;">Base Stats</h3>
                                """, unsafe_allow_html=True)
                            
                            # Vérifier s'il y a une prédiction pour afficher les stats augmentées
                            prediction = st.session_state.get('evolution_prediction')
                            
                            stats_data = [
                                ("HP", stats.data['hp'], "#FF5F20"),
                                ("Attack", stats.data['attack'], "#FF5F20"),
                                ("Defense", stats.data['defense'], "#FF5F20"),
                                ("Sp. Attack", stats.data['special_attack'], "#FF5F20"),
                                ("Sp. Defense", stats.data['special_defense'], "#FF5F20"),
                                ("Speed", stats.data['speed'], "#FF5F20")
                            ]
                            
                            for name, value, color in stats_data:
                                percentage = (value / 255) * 100
                                
                                # Calculer l'augmentation si une prédiction existe
                                increase_html = ""
                                increase_percentage = 0
                                
                                if prediction:
                                    if name == "HP" and "evolved_hp" in prediction:
                                        new_value = prediction["evolved_hp"]
                                        increase = new_value - value
                                        increase_percentage = (increase / 255) * 100
                                        increase_html = f'<span class="stat-increase">+{increase:.0f}</span> '
                                    elif name == "Attack" and "evolved_attack" in prediction:
                                        new_value = prediction["evolved_attack"]
                                        increase = new_value - value
                                        increase_percentage = (increase / 255) * 100
                                        increase_html = f'<span class="stat-increase">+{increase:.0f}</span> '
                                    elif name == "Defense" and "evolved_defense" in prediction:
                                        new_value = prediction["evolved_defense"]
                                        increase = new_value - value
                                        increase_percentage = (increase / 255) * 100
                                        increase_html = f'<span class="stat-increase">+{increase:.0f}</span> '
                                    elif name == "Sp. Attack" and "evolved_sp_attack" in prediction:
                                        new_value = prediction["evolved_sp_attack"]
                                        increase = new_value - value
                                        increase_percentage = (increase / 255) * 100
                                        increase_html = f'<span class="stat-increase">+{increase:.0f}</span> '
                                    elif name == "Sp. Defense" and "evolved_sp_defense" in prediction:
                                        new_value = prediction["evolved_sp_defense"]
                                        increase = new_value - value
                                        increase_percentage = (increase / 255) * 100
                                        increase_html = f'<span class="stat-increase">+{increase:.0f}</span> '
                                    elif name == "Speed" and "evolved_speed" in prediction:
                                        new_value = prediction["evolved_speed"]
                                        increase = new_value - value
                                        increase_percentage = (increase / 255) * 100
                                        increase_html = f'<span class="stat-increase">+{increase:.0f}</span> '
                                
                                st.markdown(f"""
                                    <div style="margin: 2px 0;">
                                        <div style="display: flex; justify-content: space-between; margin-bottom: 1px;">
                                            <span style="color: #555; font-size: 0.9em;">{name}</span>
                                            <span style="color: #333; font-weight: 500; font-size: 0.9em;">{increase_html}{value}</span>
                                        </div>
                                        <div style="background: #e9ecef; height: 6px; border-radius: 3px; position: relative; overflow: hidden;">
                                            <div style="width: {percentage}%; height: 100%; background: {color}; border-radius: 3px;"></div>
                                            {f'<div style="position: absolute; top: 0; left: {percentage}%; width: {increase_percentage}%; background: #4285f4; height: 100%; border-radius: 0 3px 3px 0;"></div>' if increase_percentage > 0 else ''}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Bouton MEGA pour prédire l'évolution
                                with st.container():
                                    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
                                    mega_col1, mega_col2, mega_col3 = st.columns([1,2,1])
                                    with mega_col2:
                                        # Bouton PREDICT MEGA
                                        button_style = """
                                        <style>
                                        div[data-testid="stButton"] button {
                                            background-color: #4285f4 !important;
                                            color: white !important;
                                            font-weight: bold !important;
                                            border: none !important;
                                        }
                                        div[data-testid="stButton"] button:hover {
                                            background-color: #3b77db !important;
                                        }
                                        </style>
                                        """
                                        st.markdown(button_style, unsafe_allow_html=True)
                                        if st.button("PREDICT MEGA", key=f"mega_{pokemon_id}", use_container_width=True):
                                            with st.spinner("Prédiction en cours..."):
                                                # Préparer les données pour l'API
                                                stats_data = stats.data.copy()
                                                stats_data.update(pokemon)
                                                
                                                # S'assurer que toutes les données obligatoires sont présentes
                                                required_fields = ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]
                                                missing_fields = [field for field in required_fields if field not in stats_data or stats_data[field] is None]
                                                
                                                if missing_fields:
                                                    st.error(f"Données manquantes pour la prédiction: {', '.join(missing_fields)}")
                                                else:
                                                    # Pour les champs optionnels, ajouter des valeurs par défaut
                                                    stats_data["height_m"] = stats_data.get("height_m", 0)
                                                    stats_data["weight_kg"] = stats_data.get("weight_kg", 0)
                                                    stats_data["base_experience"] = stats_data.get("base_experience", 0)
                                                    
                                                    # Appel à l'API de prédiction
                                                    prediction = predict_evolution(stats_data)
                                                    st.session_state['evolution_prediction'] = prediction
                                                    st.rerun()
                                    
                                    # Afficher un message explicatif si une prédiction existe
                                    if prediction:
                                        st.markdown("""
                                            <div style="margin-top: 5px; font-size: 0.7em; color: #bbb; text-align: center;">
                                                ⚡ Valeurs en bleu = augmentations prédites lors d'une méga-évolution
                                            </div>
                                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown("""
                            <div style="text-align: center; margin: 20px 0;">
                                <p style="color: #666;">Statistiques indisponibles pour ce Pokémon</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Colonne des stats GO
                with col_go:
                    try:
                        go_stats = supabase.table("go_pokemon_stats").select("*").eq("pokemon_id", pokemon_id).execute()
                        if go_stats.data and len(go_stats.data) > 0:
                            st.markdown("""
                                <h3 style="color: #444; margin: 2px 0; font-size: 1.1em;">Pokémon GO Stats</h3>
                            """, unsafe_allow_html=True)
                            
                            # Max CP séparé
                            st.markdown(f"""
                                <div style="text-align: center; margin: 4px 0;">
                                    <span style="font-size: 1.1em; color: #333;">
                                        Max CP: <strong>{go_stats.data[0]['max_cp']:,}</strong>
                                    </span>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Autres stats GO
                            go_stats_data = [
                                ("Attack", go_stats.data[0]['attack'], "#FF5F20"),
                                ("Defense", go_stats.data[0]['defense'], "#FF5F20"),
                                ("Stamina", go_stats.data[0]['stamina'], "#FF5F20")
                            ]
                            
                            for name, value, color in go_stats_data:
                                percentage = (value / 300) * 100
                                st.markdown(f"""
                                    <div style="margin: 2px 0;">
                                        <div style="display: flex; justify-content: space-between; margin-bottom: 1px;">
                                            <span style="color: #555; font-size: 0.9em;">{name}</span>
                                            <span style="color: #333; font-weight: 500; font-size: 0.9em;">{value}</span>
                                        </div>
                                        <div style="background: #e9ecef; height: 6px; border-radius: 3px; position: relative; overflow: hidden;">
                                            <div style="width: {percentage}%; height: 100%; background: {color}; border-radius: 3px;"></div>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown("""
                            <p style="color: #666; font-style: italic; text-align: center; margin: 4px 0;">
                                Pokémon GO stats not available
                            </p>
                        """, unsafe_allow_html=True)
                
                st.markdown("""<div style="margin-bottom: -8px;"></div>""", unsafe_allow_html=True)
            
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
    st.session_state['evolution_prediction'] = None 