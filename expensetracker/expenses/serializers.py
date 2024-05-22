from rest_framework import serializers
from expenses.models import IncomeSource,ExpenseCategory,Transaction


class IncomeSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model= IncomeSource
        fields = ['title','total_amount','user']



