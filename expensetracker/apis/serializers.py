from django.utils import timezone
from datetime import date
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import IncomeSourceAPI,TransactionAPI,BudgetGoalAPI,TransactionSplitAPI,ExpenseCategoryAPI,Profile




from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'profile_picture', 'location', 'birth_date', 'phone_number']

    def validate_birth_date(self, value):
        """
        Ensure that the birth date is not in the future.
        """
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Birth date cannot be in the future.")
        return value

    def validate_phone_number(self, value):
        """
        Ensure that the phone number is exactly 10 digits long.
        """
        if value and not isinstance(value, int):
            raise serializers.ValidationError("Phone number must be an integer.")
        if value < 1000000000 or value > 9999999999:
            raise serializers.ValidationError("Phone number must be a 10-digit integer.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']



class IncomeSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSourceAPI
        fields = ['id', 'title', 'total_amount','date']



class ExpenseCategoryAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategoryAPI
        fields = ['id', 'title']


class TransactionAPISerializer(serializers.ModelSerializer):
    expense_category = ExpenseCategoryAPISerializer(read_only=True)
    expense_category_id = serializers.PrimaryKeyRelatedField(
        queryset=ExpenseCategoryAPI.objects.all(), source='expense_category', write_only=True)
   

    class Meta:
        model = TransactionAPI
        fields = ['id', 'amount', 'user', 'description', 'expense_category', 'expense_category_id', 'date', 'remaining_amount', 'transaction_receipt_picture']
        read_only_fields = ['id', 'remaining_amount', 'user']    

    def validate_date(self, value):
        """
        Ensure that the date is not in the future.
        """
        if value > timezone.now().date():
            raise serializers.ValidationError("Date cannot be set to a future date.")
        return value


class TransactionSplitAPISerializer(serializers.ModelSerializer):
    transaction = TransactionAPISerializer(read_only=True)
    transaction_amount = serializers.DecimalField(source='transaction.amount', max_digits=10, decimal_places=2, read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = TransactionSplitAPI
        fields = ['id', 'user', 'amount_owed', 'transaction', 'transaction_amount']
        read_only_fields = ['transaction', 'transaction_amount']

    def validate_amount_owed(self, value):
        if value <= 0:
            raise serializers.ValidationError("The amount owed must be greater than zero.")
        return value

    def validate(self, data):
        transaction = self.context['transaction']
        amount_owed = data['amount_owed']

        if amount_owed > transaction.amount:
            raise serializers.ValidationError("The amount owed cannot be more than the transaction amount.")

        total_splits = sum(split.amount_owed for split in transaction.splits.all())
        if self.instance:
            total_splits -= self.instance.amount_owed

        if total_splits + amount_owed > transaction.amount:
            raise serializers.ValidationError("The total amount owed cannot exceed the transaction amount.")

        return data






class BudgetGoalSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source='category.title', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=ExpenseCategoryAPI.objects.all())

    class Meta:
        model = BudgetGoalAPI
        fields = ['id', 'category', 'category_title', 'amount', 'start_date', 'end_date']

    def validate(self, data):
        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data

