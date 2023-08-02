# tasks.py
from datetime import datetime
from django.conf import settings
import subprocess
from config.celery import app
import os

@app.task
def perform_backup():
    # Create the backup name based on the current date and time
    current_datetime = datetime.now()
    backup_name = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = f"/db/backups/{backup_name}.backup"

    try:
        # Set the PGPASSWORD environment variable with the database password
        os.environ['PGPASSWORD'] = settings.DATABASES['default']['PASSWORD']

        # Execute pg_dump with the -Fc option to create a custom-format binary backup
        command = [
            'pg_dump',
            '-d', settings.DATABASES['default']['NAME'],
            '-Fc',  # Use custom-format binary backup
            '-f', backup_path,
            '-U', settings.DATABASES['default']['USER'],
            '-h', settings.DATABASES['default']['HOST'],
            '-p', settings.DATABASES['default']['PORT']
        ]

        process = subprocess.run(command, capture_output=True, text=True)

        # Print the standard output and standard error of the pg_dump command
        print("Standard Output:")
        print(process.stdout)

        print("Standard Error:")
        print(process.stderr)
        print('ppppp',process.returncode)
        if process.returncode == 0:
            print(f"Резервное копирование выполнено успешно. Имя резервной копии: {backup_name}")
        else:
            print(f"Ошибка при резервном копировании. Код возврата: {process.returncode}")
    except Exception as e:
        print(f"Ошибка при резервном копировании: {str(e)}")
    finally:
        # Remove the PGPASSWORD environment variable after executing pg_dump
        os.environ.pop('PGPASSWORD', None)

@app.task
def perform_restore(backup_data):
    try:
        # Set the PGPASSWORD environment variable with the database password
        os.environ['PGPASSWORD'] = settings.DATABASES['default']['PASSWORD']

        # Specify the path of the backup file to restore
        backup_file = os.path.join('/db/backups', backup_data)

        # Check if the backup file exists
        if not os.path.isfile(backup_file):
            raise Exception("Backup file not found.")

        # Execute pg_restore with the -Fc option to restore from custom-format binary backup
        command = [
            'pg_restore',
            '--dbname', settings.DATABASES['default']['NAME'],
            backup_file,
            '-U', settings.DATABASES['default']['USER'],
            '-h', settings.DATABASES['default']['HOST'],
            '-p', settings.DATABASES['default']['PORT']
        ]

        subprocess.run(command, capture_output=True, text=True, check=True)

        print("Restore completed successfully.")
    except Exception as e:
        print(f"Error during restore: {str(e)}")
    finally:
        # Remove the PGPASSWORD environment variable after executing pg_restore
        os.environ.pop('PGPASSWORD', None)