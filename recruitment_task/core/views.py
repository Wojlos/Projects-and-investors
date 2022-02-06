from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.businesslogic.errors import CannotInvestIntoProjectException
from core.businesslogic.investing import invest_into_project
from core.businesslogic.matching import match_investors_to_project, matching_projects_to_investor
from core.models import Project, Investor
from core.serializers import ProjectSerializer, ProjectDetailsSerializer, InvestorSerializer, InvestorDetailsSerializer


class ProjectsView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProjectDetailsView(generics.RetrieveUpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailsSerializer

    def update(self, request, *args, **kwargs):
        project_to_update = self.get_object()
        if project_to_update.funded:
            return Response(data={"details": "Cannot edit funded project."}, status=status.HTTP_400_BAD_REQUEST)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(project_to_update, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class ProjectMatchesView(generics.ListAPIView):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer

    def get(self, request, pk, *args, **kwargs):
        project = Project.objects.filter(id = pk).first()
        
        if not project:
            return Response(
                    data={"details": "Project with selected id does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                    )

        if project.funded:
            return Response(
                    data={"details": "Project already funded."}, 
                    status=status.HTTP_204_NO_CONTENT
                    )

        queryset = match_investors_to_project(project)
        serializer = self.get_serializer(queryset, many = True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvestorsView(generics.ListCreateAPIView):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InvestorDetailsView(generics.RetrieveUpdateAPIView):
    queryset = Investor.objects.all()
    serializer_class = InvestorDetailsSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        investor_to_update = self.get_object()
        serializer = self.get_serializer(investor_to_update, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class InvestorMatchesView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request, pk, *args, **kwargs):
        investor = Investor.objects.filter(id = pk).first()
        
        if not investor:
            return Response(
                    data={"details": "Investor with selected id does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                    )

        queryset = matching_projects_to_investor(investor)
        serializer = self.get_serializer(queryset, many = True)        
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class InvestIntoProject(APIView):
    def post(self, request, pk, project_id):
        investor = get_object_or_404(Investor, pk=pk)
        project_to_invest_into = get_object_or_404(Project, pk=project_id)

        try:
            invest_into_project(investor, project_to_invest_into)
        except CannotInvestIntoProjectException as e:
            return Response(data={"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        investor.refresh_from_db()
        project_to_invest_into.refresh_from_db()
        return Response(
            data={
                "funded_project": ProjectSerializer(instance=project_to_invest_into).data,
                "remaining_amount": investor.remaining_amount
            }
        )
