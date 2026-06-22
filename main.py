# main.py
from fastapi import FastAPI, HTTPException, Query
from bson import ObjectId
from bson.errors import InvalidId
from database import products_collection
from models import Product, ProductUpdate, product_helper

app = FastAPI(
    title="E-Commerce Products API",
    description="REST API déployée dans le cloud, adossée à MongoDB Atlas",
    version="1.0.0"
)


# ── Helper : valider qu'une chaîne est un ObjectId MongoDB valide ─────────────
def to_object_id(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except (InvalidId, Exception):
        raise HTTPException(
            status_code=400,
            detail=f"'{id}' n'est pas un ID de produit valide. "
                   f"Les IDs ressemblent à : 507f1f77bcf86cd799439011"
        )


# ── GET / ─────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    count = await products_collection.count_documents({})
    return {
        "message":        "L'API e-commerce est en cours d'exécution",
        "total_products": count,
        "docs_url":       "/docs",
        "version":        "1.0.0"
    }


# ── GET /products ─────────────────────────────────────────────────────────────
@app.get("/products")
async def list_products(
    category: str  = Query(default=None, description="Filtrer par nom de catégorie"),
    in_stock: bool = Query(default=None, description="Filtrer par disponibilité en stock")
):
    query = {}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if in_stock is not None:
        query["in_stock"] = in_stock

    cursor   = products_collection.find(query)
    products = [product_helper(p) async for p in cursor]
    return {"count": len(products), "products": products}


# ── GET /products/search ──────────────────────────────────────────────────────
# IMPORTANT : Cette route doit être définie AVANT /products/{id}.
@app.get("/products/search")
async def search_products(
    q: str = Query(..., description="Mot-clé à rechercher dans le nom et la description")
):
    pattern = {"$regex": q, "$options": "i"}
    cursor  = products_collection.find({
        "$or": [{"name": pattern}, {"description": pattern}]
    })
    results = [product_helper(p) async for p in cursor]
    return {"query": q, "count": len(results), "products": results}


# ── GET /products/categories ──────────────────────────────────────────────────
@app.get("/products/categories")
async def list_categories():
    categories = await products_collection.distinct("category")
    return {"count": len(categories), "categories": sorted(categories)}


# ── GET /products/low-stock ──────────────────────────────────────────────────
@app.get("/products/low-stock")
async def low_stock_products(
    threshold: int = Query(default=10, description="Stock max pour être considéré faible")
):
    cursor  = products_collection.find({"stock_count": {"$lte": threshold}, "in_stock": True})
    results = [product_helper(p) async for p in cursor]
    return {"threshold": threshold, "count": len(results), "products": results}


# ── GET /products/{id} ────────────────────────────────────────────────────────
@app.get("/products/{product_id}")
async def get_product(product_id: str):
    product = await products_collection.find_one({"_id": to_object_id(product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail=f"Produit {product_id} introuvable")
    return product_helper(product)


# ── POST /products ────────────────────────────────────────────────────────────
@app.post("/products", status_code=201)
async def create_product(product: Product):
    result  = await products_collection.insert_one(product.dict())
    created = await products_collection.find_one({"_id": result.inserted_id})
    return product_helper(created)


# ── PUT /products/{id} ────────────────────────────────────────────────────────
@app.put("/products/{product_id}")
async def update_product(product_id: str, updates: ProductUpdate):
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Aucun champ à mettre à jour. Envoyez au moins un champ dans le corps de la requête."
        )
    result = await products_collection.update_one(
        {"_id": to_object_id(product_id)}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Produit {product_id} introuvable")
    updated = await products_collection.find_one({"_id": to_object_id(product_id)})
    return product_helper(updated)


# ── DELETE /products/{id} ─────────────────────────────────────────────────────
@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    product = await products_collection.find_one({"_id": to_object_id(product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail=f"Produit {product_id} introuvable")
    await products_collection.delete_one({"_id": to_object_id(product_id)})
    return {"message": f"Produit '{product['name']}' supprimé avec succès."}