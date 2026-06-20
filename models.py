# models.py
from pydantic import BaseModel, Field
from typing import Optional


# ── Utilisé pour POST — créer un nouveau produit ─────────────────────────────
class Product(BaseModel):
    name:        str   = Field(..., min_length=1, max_length=200)
    description: str   = Field(..., min_length=1)
    price:       float = Field(..., gt=0, description="Doit être supérieur à 0")
    category:    str   = Field(..., min_length=1)
    brand:       str   = Field(default="Unknown")
    sku:         str   = Field(default="")
    in_stock:    bool  = True
    stock_count: int   = Field(default=0, ge=0)
    rating:      float = Field(default=0.0, ge=0.0, le=5.0)
    tags:        list  = Field(default=[])


# ── Utilisé pour PUT — mettre à jour un produit existant ─────────────────────
# Chaque champ est Optional — vous n'envoyez que les champs à modifier.
class ProductUpdate(BaseModel):
    name:        Optional[str]   = None
    description: Optional[str]  = None
    price:       Optional[float] = Field(default=None, gt=0)
    category:    Optional[str]  = None
    brand:       Optional[str]  = None
    in_stock:    Optional[bool] = None
    stock_count: Optional[int]  = Field(default=None, ge=0)
    rating:      Optional[float] = Field(default=None, ge=0.0, le=5.0)
    tags:        Optional[list] = None


# ── Convertit un document MongoDB en dict compatible JSON ─────────────────────
def product_helper(product: dict) -> dict:
    """
    MongoDB stocke l'ID de chaque document comme un ObjectId — un type spécial
    de 12 octets qui ne peut pas être sérialisé en JSON directement.
    Cette fonction le convertit en chaîne de caractères pour que FastAPI puisse le retourner.
    """
    return {
        "id":          str(product["_id"]),
        "name":        product.get("name", ""),
        "description": product.get("description", ""),
        "price":       product.get("price", 0.0),
        "category":    product.get("category", ""),
        "brand":       product.get("brand", "Unknown"),
        "sku":         product.get("sku", ""),
        "in_stock":    product.get("in_stock", True),
        "stock_count": product.get("stock_count", 0),
        "rating":      product.get("rating", 0.0),
        "tags":        product.get("tags", []),
    }