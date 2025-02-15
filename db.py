"""Initialize the database connection and index."""

import asyncio
import os
from typing import Optional
from urllib.parse import urlparse

from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from models.student import Student

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")


class DB_queries:


    async def initialize(self) -> None:
        """Initialize database connection"""
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
            return client

        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            raise Exception("Failed to connect to MongoDB") from e


    async def create_student(
        self,
        full_name: str,
        date_of_birth: Optional[str] = None,
        knowledge_level: Optional[str] = None,
        score: Optional[int] = 0,
        test_taken: Optional[bool] = False,
    ) -> Student:
        try:
            # Ensure Beanie is ready before any operation
            
            print(f"[DEBUG] Creating student: {full_name} ")
            student = await Student.find_one({"full_name": full_name})
            if student:
                print(f"[DEBUG] Updating existing student: {student.id}")
                student.date_of_birth = date_of_birth
                await student.save()
            else:
                print("[DEBUG] Creating new student")
                student = Student(
                    full_name=full_name,
                    date_of_birth=date_of_birth,
                    knowledge_level=knowledge_level or "debutant",
                    score=score,
                    test_taken=test_taken,
                )
                await student.save()
            return student
        except Exception as e:
            print(f"[ERROR]❌ Failed to create/update student: {str(e)}")
            raise Exception("Failed to create/update student") from e

    async def get_student(self, full_name: str) -> Student:
        try:
            
            student = await Student.find_one({"full_name": full_name})
            return student
        except Exception as e:
            print(f"[ERROR]❌ Failed to get student: {str(e)}")
            raise Exception("Failed to get student") from e

    async def update_student(
        self,
        full_name: str,
        knowledge_level: Optional[str] = None,
        score: Optional[int] = 0,
        test_taken: Optional[bool] = None,
    ):
        try:
            
            student = await Student.find_one({"full_name": full_name})
            if knowledge_level is not None:
                student.knowledge_level = knowledge_level
            if score is not None:
                student.score = score
            if test_taken is not None:
                student.test_taken = test_taken
            await student.save()
            return student
        except Exception as e:
            print(f"[ERROR]❌ Failed to update student: {str(e)}")
            raise Exception("Failed to update student") from e

