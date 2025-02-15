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
    full_name = "full_name"
    date_of_birth = "date_of_birth"
    knowledge_level = "knowledge_level"
    score = "score"
    test_taken = "test_taken"


class AssistantFunction(llm.FunctionContext):
    """Functions qui gerent differents requestes"""

    def __init__(self):
        super().__init__()
        self._student_details = {
            StudentDetails.full_name: None,
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

    @llm.ai_callable(description="trouver un etudiant a partir de son nom complet")
    async def find_student(
        self,
        full_name: Annotated[str, llm.TypeInfo(description="le nom de l'etudiant")],
    ) -> Student:
        try:
            """trouver un etudiant a partir de son nom complet"""
            logger.info(
                "recherche un etudiant a partir de son nom complet %s",
                full_name,
            )
            student = await db.get_student(full_name)
            if not student:
                logger.info("etudiant %s not found", full_name)
                return "impossible de trouver un etudiant avec ce nom et ce prenom"
            student_detail = self._get_query_str(self._student_details)

            return (
                f" les informations sur l'etudiant {full_name}  sont \n{student_detail}"
            )
        except Exception as e:
            logger.info("error impossible de trouver le compte de l'etudiant: %s", e)
            return "impossible de trouver le compte de l'etudiant"

    @llm.ai_callable(
        description="Excecute cette fonction pour creer le compte d'un etudiant apres avoir eu son nom et prenom"
    )
    async def create_student(
        self,
        full_name: Annotated[
            str, llm.TypeInfo(description="le nom complet de l'etudiant")
        ],
    ) -> str:
        """Appelle cette function une fois que l'interlocuteur ait donne sont nom"""
        try:
            is_student_exist = None
            try:
                is_student_exist = await db.get_student(full_name)
            except Exception as e:
                logger.info(
                    "error impossible de trouver le compte de l'etudiant: %s", e
                )
            if is_student_exist:
                logger.info("l'etudiant %s existe déja", full_name)
                self._student_details = {
                    StudentDetails.full_name: is_student_exist.full_name,
                    StudentDetails.date_of_birth: is_student_exist.date_of_birth,
                    StudentDetails.knowledge_level: is_student_exist.knowledge_level,
                    StudentDetails.score: is_student_exist.score,
                    StudentDetails.test_taken: is_student_exist.test_taken,
                }
                logger.info(
                    "✅ etudiant trouver %s",
                    self._get_query_str(self._student_details),
                )
                return """ tu peux poursuivre la conversation, l'etudiant
                 {student_detail} est existe deja dans la base de donnee""".format(
                    student_detail=self._get_query_str(self._student_details)
                )
                
            logger.info(
                "creer un etudiant %s ",
                full_name,
            )
            stutent = await db.create_student(full_name=full_name)
            self._student_details = {
                StudentDetails.full_name: stutent.full_name,
                StudentDetails.date_of_birth: stutent.date_of_birth,
                StudentDetails.knowledge_level: stutent.knowledge_level,
                StudentDetails.score: stutent.score,
                StudentDetails.test_taken: stutent.test_taken,
            }
            student_detail = self._get_query_str(self._student_details)
            print("✅student_detail", student_detail)
            return f" les informations sauvegarder de l'etudiant {full_name}  sont \n{student_detail}"
        except Exception as e:
            logger.info("❌error impossible de creer le compte de l'etudiant: %s", e)
            return "impossible de creer le compte de l'etudiant"

    @llm.ai_callable(
        description="update the student in the database only if they ask you to update their information"
    )
    async def update_student(
        self,
        full_name: Annotated[
            str, llm.TypeInfo(description="le nom complet de l'etudiant")
        ],
        knowledge_level: Optional[
            Annotated[
                str, llm.TypeInfo(description="niveau de connaissance de l'etudiant")
            ]
        ],
        score: Optional[
            Annotated[int, llm.TypeInfo(description="le score de l'etudiant")]
        ],
        test_taken: Optional[
            Annotated[bool, llm.TypeInfo(description="si l'etudiant a pris l'examen")]
        ],
    ) -> Student:
        """met a jour un etudiant"""
        logger.info(
            "met a jour un etudiant %s avec %s %s %s",
            full_name,
            knowledge_level,
            score,
            test_taken,
        )
        student = await db.update_student(
            full_name,
            knowledge_level,
            score,
            test_taken,
        )
        if not student:
            logger.info("etudiant %s not found", full_name)
            return "impossible de trouver un etudiant avec ce nom"
        student_detail = self._get_query_str(self._student_details)

        return f" les informations sur l'etudiant {full_name} sont \n{student_detail}"
