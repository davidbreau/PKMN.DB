from litestar import get, MediaType
from litestar.response import Response

@get("/", media_type=MediaType.HTML)
async def homepage() -> str:
    """Page d'accueil de l'API"""
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PKMN.DB API</title>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Poppins', sans-serif;
                background: #f5f7fa;
                color: #333;
                line-height: 1.6;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            header {
                background: linear-gradient(135deg, #3f51b5 0%, #5e35b1 100%);
                color: white;
                padding: 3rem 0;
                text-align: center;
                border-radius: 10px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            h1 {
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
            }
            .subtitle {
                font-size: 1.2rem;
                opacity: 0.8;
                max-width: 700px;
                margin: 0 auto;
            }
            .version {
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                padding: 0.2rem 0.6rem;
                border-radius: 50px;
                font-size: 0.9rem;
                margin-top: 1rem;
            }
            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 1.5rem;
                margin-top: 2rem;
            }
            .endpoint {
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .endpoint:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            }
            .endpoint h2 {
                font-size: 1.2rem;
                color: #3f51b5;
                margin-bottom: 0.5rem;
                display: flex;
                align-items: center;
            }
            .endpoint h2 span {
                background: #e8eaf6;
                color: #3f51b5;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                font-size: 0.9rem;
                margin-right: 0.5rem;
                font-weight: 500;
            }
            .endpoint p {
                font-size: 0.95rem;
                color: #666;
                margin-bottom: 1rem;
            }
            .params {
                font-size: 0.85rem;
                color: #888;
            }
            .params strong {
                color: #555;
            }
            .docs-link {
                display: inline-block;
                margin-top: 2rem;
                background: #3f51b5;
                color: white;
                padding: 0.8rem 1.5rem;
                border-radius: 50px;
                text-decoration: none;
                font-weight: 500;
                transition: background 0.2s ease;
            }
            .docs-link:hover {
                background: #303f9f;
            }
            footer {
                text-align: center;
                margin-top: 3rem;
                padding-top: 2rem;
                border-top: 1px solid #eee;
                color: #888;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>PKMN.DB API</h1>
                <p class="subtitle">Une API moderne pour accéder aux données Pokémon</p>
                <div class="version">v1.0.0</div>
            </header>
            
            <div class="endpoints">
                <div class="endpoint">
                    <h2><span>GET</span> /</h2>
                    <p>Page d'accueil de l'API</p>
                </div>
                
                <div class="endpoint">
                    <h2><span>GET</span> /pokemons</h2>
                    <p>Liste des pokémons avec pagination</p>
                    <div class="params">
                        <strong>Paramètres:</strong> page, limit
                    </div>
                </div>
                
                <div class="endpoint">
                    <h2><span>GET</span> /pokemons/{pokemon_id}</h2>
                    <p>Détails d'un pokémon spécifique</p>
                </div>
                
                <div class="endpoint">
                    <h2><span>GET</span> /pokemons/{pokemon_id}/moves</h2>
                    <p>Attaques d'un pokémon</p>
                    <div class="params">
                        <strong>Paramètres:</strong> game_version
                    </div>
                </div>
                
                <div class="endpoint">
                    <h2><span>GET</span> /pokemons/{pokemon_id}/full</h2>
                    <p>Informations complètes d'un pokémon avec ses attaques</p>
                    <div class="params">
                        <strong>Paramètres:</strong> game_version
                    </div>
                </div>
                
                <div class="endpoint">
                    <h2><span>GET</span> /games</h2>
                    <p>Liste des jeux disponibles</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 2rem;">
                <a href="/schema/swagger" class="docs-link">Documentation OpenAPI</a>
            </div>
            
            <footer>
                &copy; 2025 PKMN.DB - Projet de certification en IA
            </footer>
        </div>
    </body>
    </html>
    """ 