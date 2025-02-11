"""Initialize the database connection and index."""

import os
from contextlib import contextmanager
from typing import Optional
from urllib.parse import urlparse

from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from models.student import Student

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
print("mongo_uri", mongo_uri)


class DB_queries:
    def __init__(self):
        pass

    @contextmanager
    async def _get_connection(self) -> AsyncIOMotorClient:
        """Initialize the database connection and index."""
        try:
            if not mongo_uri:
                raise ValueError("MONGO_URI environment variable is not set.")

            parsed_uri = urlparse(mongo_uri)
            database_name = parsed_uri.path.lstrip("/")
            if not database_name:
                raise ValueError("Database name is missing in MONGO_URI.")

            client = AsyncIOMotorClient(mongo_uri)
            await init_beanie(
                database=client[database_name],
                document_models=[Student],
            )
            yield client
        finally:
            client.close()

    async def create_student(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: str,
        knowledge_level: Optional[str] = None,
        score: Optional[int] = 0,
        test_taken: Optional[bool] = False,
    ):
        try:
            student = Student.find_one({"first_name": first_name}).update(
                {
                    "$set": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "date_of_birth": date_of_birth,
                        "knowledge_level": knowledge_level or "debutant",
                        "score": score,
                        "test_taken": test_taken,
                    }
                },
                upsert=True,
            )
            return student
        except Exception as e:
            print("Failed to create student", e)
            raise Exception("Failed to create student") from e

    async def get_student(self, first_name: str, last_name: Optional[str]) -> Student:
        try:
            query_filter = {"first_name": first_name}
            if last_name:
                query_filter["last_name"] = last_name

            student = await Student.find_one(query_filter)
            return student
        except Exception as e:
            print(e)
            raise Exception("Failed to get student") from e

    async def update_student(
        self,
        first_name: str,
        knowledge_level: Optional[str] = None,
        score: Optional[int] = None,
        test_taken: Optional[bool] = None,
    ):
        try:
            student = await Student.find_one({"first_name": first_name})
            if knowledge_level is not None:
                student.knowledge_level = knowledge_level
            if score is not None:
                student.score = score
            if test_taken is not None:
                student.test_taken = test_taken
            await student.save()
            return student
        except Exception as e:
            print(e)
            raise Exception("Failed to update student") from e
