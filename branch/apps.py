from django.apps import AppConfig


class BranchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'branch'



# server {
#     listen 80;
#     server_name 34.159.243.132;

#     location = /favicon.ico { access_log off; log_not_found off; }
#     location /static/ {
#         root /home/sammy/RSK;
#     }

#     location / {
#         include proxy_params;
#         proxy_pass http://unix:/home/kasim_kasim2509/RSK-CEO/RSK.sock;
#     }
# }



# Description=gunicorn daemon
# After=network.target

# [Service]
# User=kasim_kasim2509
# Group=www-data
# WorkingDirectory=/home/kasim_kasim2509/RSK-CEO
# ExecStart=/home/kasim_kasim2509/RSK-CEO/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/kasim_kasim2509/RSK-CEO/RSK-CEO.sock main.wsgi:application

# [Install]
# WantedBy=multi-user.target