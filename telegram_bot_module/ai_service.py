from enum import Enum
from Free_API_Load_balancer import generate
from .utils_handlers_groups import UtilsHandlersGroups


class SenderList(Enum):
    JOBS_AND_INTERNSHIPS = "jobs_and_internships_updates"
    JOBS_AND_INTERNSHIPS_1 = "jobs_and_internships_updates1"
    INTERN_FREAK = "internfreak"
    TECH_UPRISE = "TechUprise_Updates"
    DOT_AWARE = "dot_aware"
    GO_CAREERS = "gocareers"
    JOIN_DAILY_JOBS_PLACEMENT_UPDATE = "join_Daily_Jobs_Placement_Update"
    TORCHBEARER = "TorchBearerr"
    OFF_CAMPUS_JOBS_AND_INTERNSHIPS = "off_campus_jobs_and_internships"
    TECH_JOBS_DAILY = "TechJobUpdatesDaily"
    INTERNSHIP_TO_JOBS = "internshiptojobs"
    GET_JOBS = "getjobss"


class AIService:

    def __init__(self):
        pass

    def refine_posts(self, posts):
        refined = []
        handler = UtilsHandlersGroups()

        for post in posts:
            if not post:
                continue

            source = post.source

            if source == SenderList.JOBS_AND_INTERNSHIPS.value:
                post.text = handler.handle_source_1(post.text)
                if not post.text:
                    continue

            elif source == SenderList.INTERN_FREAK.value:
                post.text = handler.handle_source_2(post.text)

            elif source == SenderList.TORCHBEARER.value:
                post.text = handler.handle_source_3(post.text)

            elif source == SenderList.DOT_AWARE.value:
                post.text = handler.handle_source_4(post.text)

            elif source == SenderList.OFF_CAMPUS_JOBS_AND_INTERNSHIPS.value:
                post.text = handler.handle_source_5(post.text)

            elif source == SenderList.JOIN_DAILY_JOBS_PLACEMENT_UPDATE.value:
                post.text = handler.handle_source_6(post.text)

            elif source == SenderList.TECH_UPRISE.value:
                post.text = handler.handle_source_7(post.text)

            elif source == SenderList.TECH_JOBS_DAILY.value:
                post.text = handler.handle_source_8(post.text)

            elif source == SenderList.GET_JOBS.value:
                post.text = handler.handle_source_9(post.text)

            # Sources that need no special handling
            elif source in {
                SenderList.GO_CAREERS.value,
                SenderList.JOBS_AND_INTERNSHIPS_1.value,
                SenderList.INTERNSHIP_TO_JOBS.value,
            }:
                post.text = post.text

            refined.append(post)

        return refined
