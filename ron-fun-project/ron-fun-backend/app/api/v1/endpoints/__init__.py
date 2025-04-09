# API端点包 
__all__ = ["auth", "users", "products", "lottery", "points", "applications", "banners", "files", "home", "admin"] 

from app.api.v1.endpoints import (
    auth,
    users,
    products,
    lottery,
    points,
    applications,
    banners,
    files,
    home,
    admin,
    health
) 