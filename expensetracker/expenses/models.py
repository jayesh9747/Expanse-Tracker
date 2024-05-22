from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class IncomeSource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self)-> str:
        return f"{self.title}"
    
    class Meta:
        ordering = ['title']



class ExpenseCategory(models.Model):
    HOUSING = 'Housing'
    FOOD = 'Food'
    TRANSPORTATION = 'Transportation'
    ENTERTAINMENT = 'Entertainment'
    HEALTHCARE = 'Healthcare'

    CATEGORY_CHOICES = [
        (HOUSING, 'Housing'),
        (FOOD, 'Food'),
        (TRANSPORTATION, 'Transportation'),
        (ENTERTAINMENT, 'Entertainment'),
        (HEALTHCARE, 'Healthcare'),
    ]

    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    # total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
       return f"{self.title}"
    
    class Meta:
        ordering = ['title']


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    expense_category = models.ForeignKey(ExpenseCategory, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        category = self.expense_category.__getattribute__("title") if self.expense_category else "No Category"
        return f"{self.date} - {category} - {self.amount} - {self.description}"

    