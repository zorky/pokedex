from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
from dotenv import load_dotenv
import httpx

app = FastAPI(title="Pokédex API", description="Application Pokémon utilisant PokeAPI")

# Client HTTP pour les requêtes à PokeAPI
client = httpx.AsyncClient(timeout=30.0)

load_dotenv()

POKEAPI_BASE = "https://pokeapi.co/api/v2"
BASE_APP_URL = os.getenv("BASE_APP_URL", "")

router = APIRouter(prefix=BASE_APP_URL)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "base_url": BASE_APP_URL
    })

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
    