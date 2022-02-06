from rest_framework import serializers

from core.businesslogic.matching import match_investors_to_project, matching_projects_to_investor
from core.models import Project, Investor


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_field = ["funded", "funded_by"]


class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = "__all__"
        read_only_fields = ["remaining_amount"]


class ProjectDetailsSerializer(serializers.ModelSerializer):
    matching_investors = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["funded", "funded_by", "matching_investors"]

    def get_matching_investors(self, project):
        
        match_investors_to_project(project)        
        return(list(
                match_investors_to_project(project)
                .values_list('id',flat = True)
                ))

class InvestorDetailsSerializer(serializers.ModelSerializer):
    matching_projects = serializers.SerializerMethodField()
    
    class Meta:
        model = Investor
        fields = "__all__"
        read_only_fields = ["remaining_amount", "matching_projects"]


    def get_matching_projects(self, investor):
            
            matching_projects_to_investor(investor)        
            return(list(
                    matching_projects_to_investor(investor)
                    .values_list('id',flat = True)
                    ))
