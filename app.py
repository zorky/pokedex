from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
import httpx

app = FastAPI(title="Pokédex API", description="Application Pokémon utilisant PokeAPI")

# Client HTTP pour les requêtes à PokeAPI
client = httpx.AsyncClient(timeout=30.0)

POKEAPI_BASE = "https://pokeapi.co/api/v2"
BASE_APP_URL = ""
# BASE_APP_URL = "/pokedex"  # Décommentez cette ligne si l'application est servie sous un sous-chemin

router = APIRouter(prefix=BASE_APP_URL)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil avec interface interactive"""
    return """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pokédex Interactif</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: white;
            font-size: 3em;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .search-box {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .search-input {
            width: 100%;
            padding: 15px;
            font-size: 1.1em;
            border: 2px solid #667eea;
            border-radius: 10px;
            outline: none;
        }
        .pokemon-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .pokemon-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .pokemon-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }
        .pokemon-img {
            width: 150px;
            height: 150px;
            margin: 0 auto;
            display: block;
        }
        .pokemon-name {
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
            margin-top: 10px;
            text-transform: capitalize;
        }
        .pokemon-id {
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }
        .pokemon-types {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 10px;
        }
        .type-badge {
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-size: 0.9em;
            font-weight: bold;
            text-transform: capitalize;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.7);
            overflow-y: auto;
        }
        .modal-content {
            background-color: white;
            margin: 50px auto;
            padding: 30px;
            border-radius: 20px;
            width: 90%;
            max-width: 800px;
            position: relative;
        }
        .close {
            position: absolute;
            right: 20px;
            top: 20px;
            font-size: 30px;
            font-weight: bold;
            cursor: pointer;
            color: #999;
        }
        .close:hover { color: #333; }
        .detail-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .detail-img {
            width: 200px;
            height: 200px;
        }
        .stats-container {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        .stat-bar {
            background: #f0f0f0;
            border-radius: 10px;
            padding: 10px;
        }
        .stat-name {
            font-weight: bold;
            margin-bottom: 5px;
            text-transform: capitalize;
        }
        .stat-value {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 20px;
            border-radius: 5px;
            color: white;
            text-align: right;
            padding-right: 10px;
            line-height: 20px;
            font-weight: bold;
        }
        .loading {
            text-align: center;
            color: white;
            font-size: 1.5em;
            margin: 50px 0;
        }
        .load-more {
            background: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            border-radius: 10px;
            cursor: pointer;
            display: block;
            margin: 20px auto;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            transition: all 0.3s;
        }
        .load-more:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }
        .abilities, .moves {
            margin-top: 20px;
        }
        .section-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #667eea;
        }
        .ability-tag, .move-tag {
            display: inline-block;
            background: #f0f0f0;
            padding: 5px 15px;
            border-radius: 20px;
            margin: 5px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔴 Pokédex Interactif</h1>
        
        <div class="search-box">
            <input type="text" class="search-input" id="searchInput" 
                   placeholder="Rechercher un Pokémon par nom ou numéro...">
        </div>
        
        <div id="pokemonGrid" class="pokemon-grid"></div>
        <div id="loading" class="loading" style="display:none;">Chargement...</div>
        <button class="load-more" id="loadMore">Charger plus de Pokémon</button>
    </div>

    <div id="pokemonModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modalContent"></div>
        </div>
    </div>

    <script>
        let offset = 0;
        const limit = 20;
        const typeColors = {
            normal: '#A8A878', fire: '#F08030', water: '#6890F0',
            electric: '#F8D030', grass: '#78C850', ice: '#98D8D8',
            fighting: '#C03028', poison: '#A040A0', ground: '#E0C068',
            flying: '#A890F0', psychic: '#F85888', bug: '#A8B820',
            rock: '#B8A038', ghost: '#705898', dragon: '#7038F8',
            dark: '#705848', steel: '#B8B8D0', fairy: '#EE99AC'
        };

        async function loadPokemon() {
            document.getElementById('loading').style.display = 'block';
            const response = await fetch(`/api/pokemon?offset=${offset}&limit=${limit}`);
            const data = await response.json();
            
            for (const pokemon of data.results) {
                const details = await fetch(`/api/pokemon/${pokemon.name}`).then(r => r.json());
                displayPokemonCard(details);
            }
            
            offset += limit;
            document.getElementById('loading').style.display = 'none';
        }

        function displayPokemonCard(pokemon) {
            const grid = document.getElementById('pokemonGrid');
            const card = document.createElement('div');
            card.className = 'pokemon-card';
            card.onclick = () => showPokemonDetails(pokemon.name);
            
            const types = pokemon.types.map(t => 
                `<span class="type-badge" style="background-color: ${typeColors[t.type.name]}">${t.type.name}</span>`
            ).join('');
            
            card.innerHTML = `
                <img class="pokemon-img" src="${pokemon.sprites.front_default}" alt="${pokemon.name}">
                <div class="pokemon-id">#${String(pokemon.id).padStart(3, '0')}</div>
                <div class="pokemon-name">${pokemon.name}</div>
                <div class="pokemon-types">${types}</div>
            `;
            
            grid.appendChild(card);
        }

        async function showPokemonDetails(name) {
            const response = await fetch(`/api/pokemon/${name}/details`);
            const pokemon = await response.json();
            
            const modal = document.getElementById('pokemonModal');
            const content = document.getElementById('modalContent');
            
            const types = pokemon.types.map(t => 
                `<span class="type-badge" style="background-color: ${typeColors[t.type.name]}">${t.type.name}</span>`
            ).join('');
            
            const stats = pokemon.stats.map(s => `
                <div class="stat-bar">
                    <div class="stat-name">${s.stat.name}: ${s.base_stat}</div>
                    <div class="stat-value" style="width: ${(s.base_stat / 255) * 100}%">${s.base_stat}</div>
                </div>
            `).join('');
            
            const abilities = pokemon.abilities.map(a => 
                `<span class="ability-tag">${a.ability.name}</span>`
            ).join('');
            
            const moves = pokemon.moves.slice(0, 15).map(m => 
                `<span class="move-tag">${m.move.name}</span>`
            ).join('');
            
            content.innerHTML = `
                <div class="detail-header">
                    <img class="detail-img" src="${pokemon.sprites.front_default}" alt="${pokemon.name}">
                    <h2 style="text-transform: capitalize; margin-top: 10px;">${pokemon.name}</h2>
                    <div style="color: #999;">#${String(pokemon.id).padStart(3, '0')}</div>
                    <div class="pokemon-types" style="margin-top: 10px;">${types}</div>
                    <div style="margin-top: 15px;">
                        <strong>Taille:</strong> ${pokemon.height / 10}m | 
                        <strong>Poids:</strong> ${pokemon.weight / 10}kg
                    </div>
                </div>
                
                <div class="section-title">Statistiques</div>
                <div class="stats-container">${stats}</div>
                
                <div class="abilities">
                    <div class="section-title">Capacités</div>
                    ${abilities}
                </div>
                
                <div class="moves">
                    <div class="section-title">Attaques (15 premières)</div>
                    ${moves}
                </div>
            `;
            
            modal.style.display = 'block';
        }

        document.querySelector('.close').onclick = function() {
            document.getElementById('pokemonModal').style.display = 'none';
        }

        window.onclick = function(event) {
            const modal = document.getElementById('pokemonModal');
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }

        document.getElementById('loadMore').onclick = loadPokemon;

        document.getElementById('searchInput').addEventListener('input', async (e) => {
            const search = e.target.value.toLowerCase().trim();
            if (search.length < 2) return;
            
            try {
                const response = await fetch(`/api/pokemon/${search}/details`);
                if (response.ok) {
                    const pokemon = await response.json();
                    document.getElementById('pokemonGrid').innerHTML = '';
                    displayPokemonCard(pokemon);
                }
            } catch (error) {
                console.log('Pokémon non trouvé');
            }
        });

        // Charger les premiers Pokémon au démarrage
        loadPokemon();
    </script>
</body>
</html>
    """


@app.get("/api/pokemon")
async def get_pokemon_list(offset: int = 0, limit: int = 20):
    """Récupère une liste de Pokémon avec pagination"""
    try:
        response = await client.get(f"{POKEAPI_BASE}/pokemon?offset={offset}&limit={limit}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des Pokémon: {str(e)}")


@app.get("/api/pokemon/{name_or_id}")
async def get_pokemon(name_or_id: str):
    """Récupère les informations basiques d'un Pokémon par nom ou ID"""
    try:
        response = await client.get(f"{POKEAPI_BASE}/pokemon/{name_or_id.lower()}")
        response.raise_for_status()
        data = response.json()
        
        return {
            "id": data["id"],
            "name": data["name"],
            "height": data["height"],
            "weight": data["weight"],
            "types": data["types"],
            "sprites": data["sprites"]
        }
    except httpx.HTTPError:
        raise HTTPException(status_code=404, detail=f"Pokémon '{name_or_id}' non trouvé")


@app.get("/api/pokemon/{name_or_id}/details")
async def get_pokemon_details(name_or_id: str):
    """Récupère toutes les informations détaillées d'un Pokémon"""
    try:
        response = await client.get(f"{POKEAPI_BASE}/pokemon/{name_or_id.lower()}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError:
        raise HTTPException(status_code=404, detail=f"Pokémon '{name_or_id}' non trouvé")


@app.get("/api/pokemon/{name_or_id}/species")
async def get_pokemon_species(name_or_id: str):
    """Récupère les informations d'espèce d'un Pokémon (descriptions, évolutions, etc.)"""
    try:
        # D'abord récupérer le Pokémon pour avoir l'URL de l'espèce
        pokemon_response = await client.get(f"{POKEAPI_BASE}/pokemon/{name_or_id.lower()}")
        pokemon_response.raise_for_status()
        pokemon_data = pokemon_response.json()
        
        # Ensuite récupérer les infos d'espèce
        species_response = await client.get(pokemon_data["species"]["url"])
        species_response.raise_for_status()
        return species_response.json()
    except httpx.HTTPError:
        raise HTTPException(status_code=404, detail=f"Espèce du Pokémon '{name_or_id}' non trouvée")


@app.get("/api/pokemon/{name_or_id}/evolution")
async def get_pokemon_evolution(name_or_id: str):
    """Récupère la chaîne d'évolution d'un Pokémon"""
    try:
        # Récupérer l'espèce
        pokemon_response = await client.get(f"{POKEAPI_BASE}/pokemon/{name_or_id.lower()}")
        pokemon_response.raise_for_status()
        pokemon_data = pokemon_response.json()
        
        species_response = await client.get(pokemon_data["species"]["url"])
        species_response.raise_for_status()
        species_data = species_response.json()
        
        # Récupérer la chaîne d'évolution
        evolution_response = await client.get(species_data["evolution_chain"]["url"])
        evolution_response.raise_for_status()
        return evolution_response.json()
    except httpx.HTTPError:
        raise HTTPException(status_code=404, detail=f"Chaîne d'évolution du Pokémon '{name_or_id}' non trouvée")


@app.get("/api/types")
async def get_types():
    """Récupère tous les types de Pokémon"""
    try:
        response = await client.get(f"{POKEAPI_BASE}/type")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des types: {str(e)}")


@app.get("/api/type/{type_name}")
async def get_type_details(type_name: str):
    """Récupère les détails d'un type spécifique (forces, faiblesses, Pokémon de ce type)"""
    try:
        response = await client.get(f"{POKEAPI_BASE}/type/{type_name.lower()}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError:
        raise HTTPException(status_code=404, detail=f"Type '{type_name}' non trouvé")


@app.on_event("shutdown")
async def shutdown():
    """Ferme le client HTTP à l'arrêt de l'application"""
    await client.aclose()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8377, reload=True)
    