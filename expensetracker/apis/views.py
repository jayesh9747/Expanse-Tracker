from rest_framework import viewsets , permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied ,ValidationError

from django.db.models import Sum
from datetime import datetime
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
from .utils import send_email_gmail
from django.http import JsonResponse
from cloudinary.uploader import upload

from .models import Profile, IncomeSourceAPI , TransactionAPI , BudgetGoalAPI , TransactionSplitAPI 
from .serializers import  ProfileSerializer, IncomeSourceSerializer , BudgetGoalSerializer , TransactionSplitAPISerializer , TransactionAPISerializer,UserSerializer
from .permissions import IsOwner


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if Profile.objects.filter(user=self.request.user).exists():
            raise ValidationError("You can only create a profile once.")
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if Profile.objects.filter(user=request.user).exists():
            return Response({"detail": "You can only create a profile once."}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.user != request.user:
            return Response({"detail": "You can only modify your own profile."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.user != request.user:
            return Response({"detail": "You can only modify your own profile."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)


def upload_image_to_cloudinary(image_path):
    return upload(image_path)


class IncomeSourceAPIViewSet(viewsets.ModelViewSet):
    queryset = IncomeSourceAPI.objects.all()
    serializer_class = IncomeSourceSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return IncomeSourceAPI.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)


class TransactionAPIViewSet(viewsets.ModelViewSet):
    queryset = TransactionAPI.objects.all()
    serializer_class = TransactionAPISerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return TransactionAPI.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
     
    @action(detail=False, methods=['get'], url_path='report/(?P<year>\d+)/(?P<month>\d+)')
    def monthly_report(self, request, year, month):
        start_date = datetime(int(year), int(month), 1)
        end_date = start_date + relativedelta(months=1, days=-1)

        print(start_date,end_date)

        # Calculate total income for the specified month
        total_income = IncomeSourceAPI.objects.filter(user=request.user, date__range=[start_date, end_date]).aggregate(total_amount_sum=Sum('total_amount'))['total_amount_sum'] or 0

        print(total_income)


        # Calculate total expenses for the specified month
        total_expenses = TransactionAPI.objects.filter(user=request.user, date__range=[start_date, end_date]).aggregate(Sum('amount'))['amount__sum'] or 0

        print(total_expenses)

        report_data = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': total_income - total_expenses,
        }

        return Response(report_data)
    



class TransactionSplitAPIViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSplitAPISerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        transaction_id = self.kwargs['transaction_pk']
        return TransactionSplitAPI.objects.filter(transaction__id=transaction_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        transaction_id = self.kwargs['transaction_pk']
        context['transaction'] = TransactionAPI.objects.get(pk=transaction_id)
        return context

    def perform_create(self, serializer):
        transaction = self.get_serializer_context()['transaction']
        amount_owed = serializer.validated_data['amount_owed']
        user = serializer.validated_data['user']

        if transaction.user != self.request.user and self.request.user not in transaction.splits.values_list('user', flat=True):
            raise PermissionDenied("You do not have permission to split this transaction.")

        self.validate_split(transaction, amount_owed, user)

        serializer.save(transaction=transaction)
        self.update_remaining_amount(transaction)

    def perform_update(self, serializer):
        transaction = self.get_serializer_context()['transaction']
        amount_owed = serializer.validated_data['amount_owed']
        user = serializer.instance.user

        if transaction.user != self.request.user and user != self.request.user:
            raise PermissionDenied("You do not have permission to modify this split.")

        self.validate_split(transaction, amount_owed, user, exclude_instance=serializer.instance)

        serializer.save()
        self.update_remaining_amount(transaction)

    def perform_destroy(self, instance):
        transaction = instance.transaction
        if transaction.user != self.request.user and instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this split.")

        instance.delete()
        self.update_remaining_amount(transaction)

    def validate_split(self, transaction, amount_owed, user, exclude_instance=None):
        if user == transaction.user:
            raise ValidationError("A user cannot owe themselves.")

        if amount_owed > transaction.amount:
            raise ValidationError("The amount owed cannot be more than the transaction amount.")

        total_splits = sum(split.amount_owed for split in transaction.splits.all())
        if exclude_instance:
            total_splits -= exclude_instance.amount_owed

        if total_splits + amount_owed > transaction.amount:
            raise ValidationError("The total amount owed cannot exceed the transaction amount.")

    def update_remaining_amount(self, transaction):
        total_splits = sum(split.amount_owed for split in transaction.splits.all())
        transaction.remaining_amount = transaction.amount - total_splits
        transaction.save()    




class BudgetGoalAPIViewSet(viewsets.ModelViewSet):
    queryset = BudgetGoalAPI.objects.all()
    serializer_class = BudgetGoalSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return BudgetGoalAPI.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.user != self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='progress')
    def track_progress(self, request):
        goals = BudgetGoalAPI.objects.filter(user=request.user)
        expenses = TransactionAPI.objects.filter(user=request.user)
        progress = []
        notifications = []
        
        for goal in goals:
            total_expenses = expenses.filter(expense_category=goal.category, date__range=[goal.start_date, goal.end_date]).aggregate(Sum('amount'))['amount__sum'] or 0
            remaining = goal.amount - total_expenses
            progress.append({
                'goal': goal,
                'total_expenses': total_expenses,
                'remaining': remaining
            })
            if remaining < 0:
                print(request.user.email)
                notifications.append(goal.category.title)

        # Send notification if there are budget overruns
        if notifications:
            print("notification is sended",  request.user.email)
            categories = ", ".join(notifications)
            subject = "Budget Overrun Notification"
            to_email = request.user.email
            html_content = f"You have exceeded your budget for the following categories: {categories}."
            send_email_gmail(subject, to_email, html_content)

        progress_data = [
            {
                'category': item['goal'].category.title,
                'budgeted_amount': item['goal'].amount,
                'total_expenses': item['total_expenses'],
                'remaining_amount': item['remaining']
            }
            for item in progress
        ]
        return Response(progress_data)
    

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


def custom_404_view(request, exception):
    return JsonResponse({'detail': 'This path does not exist.'}, status=404)

