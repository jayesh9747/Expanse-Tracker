from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TransactionAPI, BudgetGoalAPI
from .utils import send_email_gmail
from django.db.models import Sum

@receiver(post_save, sender=TransactionAPI)
def notify_budget_overrun(sender, instance, **kwargs):
    user = instance.user
    goals = BudgetGoalAPI.objects.filter(user=user)
    notifications = []
    
    for goal in goals:
        total_expenses = TransactionAPI.objects.filter(user=user, expense_category=goal.category, date__range=[goal.start_date, goal.end_date]).aggregate(Sum('amount'))['amount__sum'] or 0
        remaining = goal.amount - total_expenses
        if remaining < 0:
            notifications.append(goal.category.title)
    
    if notifications:
        categories = ", ".join(notifications)
        subject = "Budget Overrun Notification"
        to_email = user.email
        html_content = f"<p>You have exceeded your budget for the following categories: {categories}.</p>"
        send_email_gmail(subject, to_email, html_content)