from app.database.database import get_db
from bson import ObjectId

class JobRepository:
    @property
    def collection(self):
        """Garante que sempre pegamos a instância ativa do banco"""
        return get_db().jobs

    async def insert_one(self, data: dict) -> str:
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    async def find_one(self, filter_query: dict) -> dict | None:
        # Converte automaticamente '_id' de string para ObjectId se necessário
        if "_id" in filter_query and isinstance(filter_query["_id"], str) and "x_architect_id" in filter_query:
            if ObjectId.is_valid(filter_query["_id"]):
                filter_query["_id"] = ObjectId(filter_query["_id"])
        return await self.collection.find_one(filter_query)

    async def count_documents(self, filter_query: dict) -> int:
        return await self.collection.count_documents(filter_query)

    async def find(self, filter_query: dict, skip: int = 0, limit: int = 100) -> list:
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def update_one(self, filter_query: dict, update_data: dict) -> bool:
        # Converte automaticamente o '_id'
        if "_id" in filter_query and isinstance(filter_query["_id"], str) and "x_architect_id" in filter_query:
            if ObjectId.is_valid(filter_query["_id"]):
                filter_query["_id"] = ObjectId(filter_query["_id"])
        
        # Encapsulamos o "$set" para facilitar para quem chama a função
        result = await self.collection.update_one(
            filter_query, 
            {"$set": update_data}
        )
        return result.modified_count > 0