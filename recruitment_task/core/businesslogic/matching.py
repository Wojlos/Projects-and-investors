from django.db.models import Q

from core.models import Investor, Project

def match_investors_to_project(project):

    queryset = Investor.objects.filter( 
            project_delivery_deadline__gt = project.delivery_date,
            remaining_amount__gt = project.amount,
            individual_amount__gt = project.amount,
            )
            
    return queryset
 
def matching_projects_to_investor(investor):
    queryset = Project.objects.filter(
                Q(delivery_date__lt = investor.project_delivery_deadline),
                Q(amount__lt = investor.remaining_amount),        
                Q(amount__lt = investor.individual_amount),    
                Q(funded = False)  
        )
    return queryset