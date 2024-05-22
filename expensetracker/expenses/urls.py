from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns= [
    path('', TemplateView.as_view(template_name='dashboard/home.html'), name='home'),
    path('expenses/',views.get_expenses),
    path('income_source/', TemplateView.as_view(template_name='dashboard/incomesource.html'), name='income_sources_list'),
    path('income_source/edit/<int:id>', TemplateView.as_view(template_name='dashboard/edit_incomesource.html'), name='edit_income_sources_list'),
    path('income_source/add/', TemplateView.as_view(template_name='dashboard/add_incomesource.html'), name='add_income_source'),
    path('transaction/',TemplateView.as_view(template_name='dashboard/transaction.html'), name='transaction'),
    path('transaction/add/',TemplateView.as_view(template_name='dashboard/add_transaction.html'), name='transaction_add'),
    path('budget/',TemplateView.as_view(template_name='dashboard/budget_goal.html'), name='budget_goal'),
    path('budget/add/',TemplateView.as_view(template_name='dashboard/budget_goaladd.html'), name='budget_goal_add'),
    path('profile/',TemplateView.as_view(template_name='dashboard/profile.html'), name='profile'),
    path('transaction/edit/<int:transaction_id>/', TemplateView.as_view(template_name='dashboard/edit_transaction.html'), name='edit_transaction'),
    path('transaction/<int:transaction_id>/splits/',TemplateView.as_view(template_name='dashboard/split_transaction.html'), name='transaction_split'),
    path('report/',TemplateView.as_view(template_name='dashboard/report.html'), name='report'),   
]

