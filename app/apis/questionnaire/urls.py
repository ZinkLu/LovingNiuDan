from . import questionnaire_bp
from .views import QuestionnaireResource, QuestionnairePrintResource

questionnaire_bp.add_route(QuestionnaireResource.as_view(), '/questionnaire')
questionnaire_bp.add_route(QuestionnairePrintResource.as_view(), '/questionnaire/print_task')
