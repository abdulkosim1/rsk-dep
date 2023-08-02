# views.py
import os
from rest_framework.permissions import IsAdminUser
from django.http import JsonResponse
from rest_framework import views, status
from rest_framework.response import Response
from .task import perform_backup, perform_restore


class BackupView(views.APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        try:
            perform_backup.delay()
            return Response({"message": "Запущено резервное копирование."},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BackupListView(views.APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        backup_folder = '/db/backups'
        backup_files = [f for f in os.listdir(backup_folder) if os.path.isfile(os.path.join(backup_folder, f))]
        return JsonResponse({"backups": backup_files}, status=status.HTTP_200_OK)


class RestoreView(views.APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        try:
            backup_data = request.data.get('data')
            backup_file = os.path.join('/db/backups', backup_data)

            # Check if the backup file exists
            if not os.path.isfile(backup_file):
                return Response({"error": "Backup file not found."}, status=status.HTTP_404_NOT_FOUND)

            # Perform the restore asynchronously
            perform_restore.apply_async(args=[backup_data])

            return Response({"message": "Restore has been initiated."},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)