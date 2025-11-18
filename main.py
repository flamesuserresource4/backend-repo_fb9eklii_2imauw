import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Customer as CustomerSchema, Payment as PaymentSchema

app = FastAPI(title="BluePay API", description="Lightweight payments API demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helpers
class IdModel(BaseModel):
    id: str


def serialize_doc(doc: dict):
    d = {**doc}
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    # convert datetimes to isoformat
    for k, v in list(d.items()):
        try:
            if hasattr(v, "isoformat"):
                d[k] = v.isoformat()
        except Exception:
            pass
    return d


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Payments API
@app.post("/api/customers", response_model=IdModel)
def create_customer(payload: CustomerSchema):
    try:
        new_id = create_document("customer", payload)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers")
def list_customers(limit: int = 25):
    try:
        docs = get_documents("customer", {}, limit=limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/payments", response_model=IdModel)
def authorize_payment(payload: PaymentSchema):
    try:
        data = payload.model_dump()
        # ensure status starts as authorized
        data["status"] = "authorized"
        new_id = create_document("payment", data)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/payments/{payment_id}/capture")
def capture_payment(payment_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        oid = ObjectId(payment_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payment id")

    doc = db["payment"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Payment not found")
    if doc.get("status") == "captured":
        return serialize_doc(doc)

    db["payment"].update_one({"_id": oid}, {"$set": {"status": "captured"}})
    updated = db["payment"].find_one({"_id": oid})
    return serialize_doc(updated)


@app.get("/api/payments")
def list_payments(limit: int = 50, status: Optional[str] = None):
    try:
        filt = {}
        if status:
            filt["status"] = status
        docs = get_documents("payment", filt, limit=limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
