from django.utils import timezone
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied ,ValidationError




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.BigIntegerField(null=True, blank=True)  # Change to BigIntegerField

    def __str__(self):
        return f"{self.user.username}'s Profile"
    


class IncomeSourceAPI(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=date.today())

    def __str__(self) -> str:
        return f"{self.user}-{self.title}-{self.total_amount}"
    
    def save(self, *args, **kwargs):
        if self.date > timezone.now().date():
            raise ValidationError("Date cannot be set to a future date.")
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['title']


class ExpenseCategoryAPI(models.Model):
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


class TransactionAPI(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today())
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    expense_category = models.ForeignKey(ExpenseCategoryAPI, null=True, blank=True, on_delete=models.SET_NULL)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_receipt_picture = models.ImageField(upload_to='transaction_receipts/', null=True, blank=True)


    def save(self, *args, **kwargs):
        # Initialize remaining amount to the total amount when the transaction is created
        if not self.pk:
            self.remaining_amount = self.amount
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['date']    
    

    def __str__(self):
        category = self.expense_category.title if self.expense_category else "No Category"
        user_owed = ", ".join(split.user.username for split in self.splits.all())
        return f"{self.date} - {category} - {self.amount} - {self.description} - Owed by: {user_owed}"




class TransactionSplitAPI(models.Model):
    transaction = models.ForeignKey(TransactionAPI, related_name='splits', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)


    def save(self, *args, **kwargs):
        if self.pk:
            # Check if the user ID has been changed
            original_split = TransactionSplitAPI.objects.get(pk=self.pk)
            if original_split.user != self.user:
                raise ValidationError("You cannot change the owed user's ID.")
        super().save(*args, **kwargs)

    def transaction_amount(self):
        return self.transaction.amount

    def transaction_description(self):
        return self.transaction.description

    def transaction_owner(self):
        return self.transaction.user.username

    def __str__(self):
        return f"{self.user.username} owes {self.amount_owed} from {self.transaction.user} for {self.transaction.description}"

class BudgetGoalAPI(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategoryAPI, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.category.title} - {self.amount}"



