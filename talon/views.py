from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
from datetime import timedelta, date

from main.services.authentication import ClientTokenAuthentication
from main.services.permissions import IsOperator, IsRegistrator
from main.services import constants
from stats.models import Actions
from base.models import Service
from eqs.models import EQS

from . serializers import TalonSerializer, TalonCreateSerializer
from . models import Talon


class TalonView(APIView):
    authentication_classes = [ClientTokenAuthentication]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        else:
            return [AllowAny()]

    def get(self, request:Request):
        talon = Talon.objects.all()
        serializer = TalonSerializer(talon, many=True)
        return Response(serializer.data)

    def post(self, request:Request):
        serializer = TalonCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            qr_code_image = serializer.data['qr_code']

            response_data = serializer.data
            response_data['qr_code'] = qr_code_image

            return Response(response_data)


class RegistratorTalonView(APIView):
    permission_classes = [IsRegistrator]

    def post(self, request:Request):
        request.data['branch'] = request.user.branch.id
        serializer = TalonCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            qr_code_image = serializer.data['qr_code']

            response_data = serializer.data
            response_data['qr_code'] = qr_code_image

            return Response(response_data)

class TalonToEndView(APIView):
    permission_classes = [IsOperator]

    def get(self, request:Request, pk:str):
        if not request.user.status == constants.EMPLOYEE_STATUS_ACTIVE:
            return Response(
            'Не верный статус оператора',
        )

        talon = Talon.objects.filter(token=pk, appointment_date__date=date.today()).first()
        if talon:
            talon.delete()
            talon.appointment_date = None
            talon.save()

            Actions.objects.create(
                employee=request.user,
                action=f'talon {talon} moved to end',
                branch=request.user.branch
                )
        else:
            return Response(
            'Такого талона нет',
            status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            'Талон отправлен в конец очереди успешно',
            status=status.HTTP_200_OK
        )


class RegistratorTalonRemoveView(APIView):
    permission_classes = [IsRegistrator]

    def get(self, request:Request, pk:str):
        if not request.user.status == constants.EMPLOYEE_STATUS_ACTIVE:
            return Response(
            'Не верный статус оператора',
        )

        talon = Talon.objects.filter(id=pk).first()
        if talon:
            talon.status = constants.TALON_STATUS_CANCELED
            talon.save()

            Actions.objects.create(
                employee=request.user,
                action=f'talon {talon} canceled',
                branch=request.user.branch
                )
        else:
            return Response(
            'Такого талона нет',
            status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            'Талон  успешно удален',
            status=status.HTTP_204_NO_CONTENT
        )


class TalonRemoveView(APIView):
    permission_classes = [IsOperator]

    def get(self, request:Request, pk:str):
        if not request.user.status == constants.EMPLOYEE_STATUS_ACTIVE:
            return Response(
            'Не верный статус оператора',
        )

        talon = Talon.objects.filter(token=pk, appointment_date__date=date.today()).first()
        if talon:
            talon.status = constants.TALON_STATUS_CANCELED
            talon.service_end = timezone.now()
            talon.operators.add(request.user)
            talon.save()

            Actions.objects.create(
                employee=request.user,
                action=f'talon {talon} canceled',
                branch=request.user.branch
                )
        else:
            return Response(
            'Такого талона нет',
            status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            'Талон  успешно удален',
            status=status.HTTP_204_NO_CONTENT
        )


class TalonTransferToAnotherQueueView(APIView):
    permission_classes = [IsOperator]

    def get(self, request:Request, token:str,service_id:int):
        if not request.user.status == constants.EMPLOYEE_STATUS_ACTIVE:
            return Response(
            'Не верный статус оператора',
        )

        talon = Talon.objects.filter(token=token, appointment_date__date=date.today()).first()
        if talon:
            talon.delete()
            service = talon.service
            talon.service = Service.objects.get(id=service_id)
            talon.save()

            Actions.objects.create(
                employee=request.user,
                action=f'talon {talon} transfered from {service} to {talon.service}',
                branch=request.user.branch
                )
        else:
            return Response(
            'Такого талона нет',
            status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            'Талон перемешен успешно',
            status=status.HTTP_200_OK
        )


class TalonToStartView(APIView):
    permission_classes = [IsOperator]

    def get(self, request:Request,pk:str):
        if not request.user.status == constants.EMPLOYEE_STATUS_ACTIVE:
            return Response(
            'Не верный статус оператора',
        )

        talon = Talon.objects.filter(token=pk, appointment_date__date=date.today()).first()
        first_talon_time = Talon.objects.filter(
            branch=talon.branch,
            appointment_date__date=date.today(),
            service=talon.service,
            status=constants.TALON_STATUS_WAITING
            ).first().appointment_date
        if talon:
            talon.appointment_date = first_talon_time - timedelta(minutes=talon.service.average_time)
            talon.save()

            Actions.objects.create(
                employee=request.user,
                action=f'talon {talon} moved to start',
                branch=request.user.branch
                )
        
            return Response(
            'Талон перемешен успешно',
            status=status.HTTP_200_OK
        )
        else:
            return Response(
            'Такого талона нет',
            status=status.HTTP_404_NOT_FOUND
            )


class TalonServeStartView(APIView):
    permission_classes = [IsOperator]

    def get(self, request:Request, pk:str):
        if not request.user.status == constants.EMPLOYEE_STATUS_ACTIVE:
            return Response(
            'Не верный статус оператора',
        )

        talon = Talon.objects.filter(token=pk, appointment_date__date=date.today()).first()
        if talon:
            talon.status = constants.TALON_STATUS_INSERVICE
            talon.service_start = timezone.now()
            talon.operators.add(request.user)
            talon.save()

            Actions.objects.create(
                employee=request.user,
                action=f'talon {talon} start service',
                branch=request.user.branch
                )
        else:
            return Response(
            'Такого талона нет',
            status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            'Начало обслуживания',
            status=status.HTTP_202_ACCEPTED
        )


class TalonServeEndView(APIView):
    permission_classes = [IsOperator]

    def get(self, request:Request, pk:int):
        if not request.user.status == constants.EMPLOYEE_STATUS_ACTIVE:
            return Response(
            'Не верный статус оператора',
        )

        talon = Talon.objects.filter(token=pk, appointment_date__date=date.today()).first()
        if talon:
            EQS.objects.filter(service=talon.service,branch=talon.branch).first().talon_count -= 1
            talon.service_end = timezone.now()
            if talon.service.auto_transport:
                talon.service = talon.service.service_to_auto_transport
                talon.status = constants.TALON_STATUS_WAITING
            else:
                talon.status = constants.TALON_STATUS_COMPLETED
            talon.save()

            Actions.objects.create(
                employee=request.user,
                action=f'talon {talon} service end',
                branch=request.user.branch
                )
        else:
            return Response(
            'Такого талона нет',
            status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            'Окончание обслуживания',
            status=status.HTTP_202_ACCEPTED
        )