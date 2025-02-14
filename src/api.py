import enum
import logging
from typing import Annotated, Any, Dict, Optional

from livekit.agents import llm

from db import DB_queries
from models.student import Student

logger = logging.getLogger("student-assistant")
logger.setLevel(logging.INFO)

db = DB_queries()


class StudentDetails(enum.Enum):
    first_name = "first_name"
    last_name = "last_name"
    date_of_birth = "date_of_birth"
    knowledge_level = "knowledge_level"
    score = "score"
    test_taken = "test_taken"


class AssistantFunction(llm.FunctionContext):
    """Function to call the assistant"""

    def __init__(self):
        super().__init__()
        self._student_details = {
            StudentDetails.first_name: None,
            StudentDetails.last_name: None,
            StudentDetails.date_of_birth: None,
            StudentDetails.knowledge_level: None,
            StudentDetails.score: None,
            StudentDetails.test_taken: None,
        }

    def _get_query_str(self, query_dict: Dict[str, Any]) -> str:
        """return a string with the query"""
        str_result = ""
        for key, val in query_dict.items():
            if val is None:
                str_result += f"{key} n'existe pas\n"
                continue
            str_result += f"{key}: {val}\n"
        return str_result

    @llm.ai_callable(
        description="trouver un etudiant a partir de son nom et de son prenom"
    )
    async def find_student(
        self,
        first_name: Annotated[str, llm.TypeInfo(description="le nom de l'etudiant")],
        last_name: Optional[
            Annotated[str, llm.TypeInfo(description="le prenom de l'etudiant")]
        ],
    ) -> Student:
        try:
            """trouver un etudiant a partir de son nom et de son prenom"""
            logger.info(
                "recherche un etudiant a partir de son nom et de son prenom %s %s",
                first_name,
                last_name,
            )
            student = await db.get_student(first_name, last_name)
            if not student:
                logger.info("etudiant %s %s not found", first_name, last_name)
                return "impossible de trouver un etudiant avec ce nom et ce prenom"
            student_detail = self._get_query_str(self._student_details)

            return f" les informations sur l'etudiant {first_name} {last_name} sont \n{student_detail}"
        except Exception as e:
            logger.info("error impossible de trouver le compte de l'etudiant: %s", e)
            return "impossible de trouver le compte de l'etudiant"

    @llm.ai_callable(
        description="creer un nouvel etudiant dans la base de données au debut de la conversation"
    )
    async def create_student(
        self,
        first_name: Annotated[str, llm.TypeInfo(description="le nom de l'etudiant")],
        last_name: Annotated[str, llm.TypeInfo(description="le prenom de l'etudiant")],
        date_of_birth: Annotated[
            str, llm.TypeInfo(description="la date de naissance de l'etudiant")
        ],
    ) -> str:
        """Appelle cette fonction pour creer un nouvel etudiant dans la base de données au debut de la conversation, apres que l'etudiant ait dit son nom et son prenom
        cette fonction retourne les informations sur l'etudiant qui va etre creer
        """
        try:
            try:
                is_student_exist = await db.get_student(first_name, last_name)
            except Exception as e:
                logger.info(
                    "error impossible de trouver le compte de l'etudiant: %s", e
                )
            print("is_student_exist", is_student_exist)
            if is_student_exist:
                logger.info("l'etudiant %s %s existe déja", first_name, last_name)
                self._student_details = {
                    StudentDetails.first_name: is_student_exist.first_name,
                    StudentDetails.last_name: is_student_exist.last_name,
                    StudentDetails.date_of_birth: is_student_exist.date_of_birth,
                    StudentDetails.knowledge_level: is_student_exist.knowledge_level,
                    StudentDetails.score: is_student_exist.score,
                    StudentDetails.test_taken: is_student_exist.test_taken,
                }
                return f"l'etudiant {first_name} {last_name} existe déja, voici ses informations \n {self._get_query_str(self._student_details)}"
            logger.info(
                "creer un etudiant %s %s %s",
                first_name,
                last_name,
                date_of_birth,
            )
            stutent = await db.create_student(
                first_name,
                last_name,
                date_of_birth,
            )
            self._student_details = {
                StudentDetails.first_name: stutent.first_name,
                StudentDetails.last_name: stutent.last_name,
                StudentDetails.date_of_birth: stutent.date_of_birth,
                StudentDetails.knowledge_level: stutent.knowledge_level,
                StudentDetails.score: stutent.score,
                StudentDetails.test_taken: stutent.test_taken,
            }
            student_detail = self._get_query_str(self._student_details)

            return f" les informations sauvegarder de l'etudiant {first_name} {last_name} sont \n{student_detail}"
        except Exception as e:
            logger.info("error impossible de creer le compte de l'etudiant: %s", e)
            return "impossible de creer le compte de l'etudiant"

    @llm.ai_callable(description="met a jour un etudiant")
    async def update_student(
        self,
        first_name: Annotated[str, llm.TypeInfo(description="le nom de l'etudiant")],
        knowledge_level: Annotated[
            str, llm.TypeInfo(description="niveau de connaissance de l'etudiant")
        ],
        score: Annotated[int, llm.TypeInfo(description="le score de l'etudiant")],
        test_taken: Annotated[
            bool, llm.TypeInfo(description="si l'etudiant a pris l'examen")
        ],
    ) -> Student:
        """met a jour un etudiant"""
        logger.info(
            "met a jour un etudiant %s avec %s %s %s",
            first_name,
            knowledge_level,
            score,
            test_taken,
        )
        student = await db.update_student(
            first_name,
            knowledge_level,
            score,
            test_taken,
        )
        if not student:
            logger.info("etudiant %s not found", first_name)
            return "impossible de trouver un etudiant avec ce nom"
        student_detail = self._get_query_str(self._student_details)

        return f" les informations sur l'etudiant {first_name} sont \n{student_detail}"
