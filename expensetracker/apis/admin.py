from django.contrib import admin
from .models import IncomeSourceAPI, ExpenseCategoryAPI, TransactionAPI, TransactionSplitAPI, BudgetGoalAPI,Profile

class IncomeSourceAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'total_amount', 'date')
    search_fields = ('user__username', 'title')
    list_filter = ('date', 'user')
    

class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    list_filter = ('title',)

class TransactionSplitInline(admin.TabularInline):
    model = TransactionSplitAPI
    extra = 1
    min_num = 1

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount', 'description', 'expense_category', 'remaining_amount')
    search_fields = ('user__username', 'description', 'expense_category__title')
    list_filter = ('date', 'user', 'expense_category')
    inlines = [TransactionSplitInline]

class TransactionSplitAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_owner', 'transaction_amount', 'transaction_description', 'amount_owed')
    search_fields = ('transaction__description', 'user__username')
    list_filter = ('transaction__date', 'user')
    list_editable = ('amount_owed',)
    list_display_links = ('user', 'transaction_owner', 'transaction_amount', 'transaction_description')
    list_per_page = 20

class BudgetGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'start_date', 'end_date')
    search_fields = ('user__username', 'category__title')
    list_filter = ('start_date', 'end_date', 'user', 'category')

class ProfileAdmin(admin.ModelAdmin):
    pass    

admin.site.register(IncomeSourceAPI, IncomeSourceAdmin)
admin.site.register(ExpenseCategoryAPI, ExpenseCategoryAdmin)
admin.site.register(TransactionAPI, TransactionAdmin)
admin.site.register(TransactionSplitAPI, TransactionSplitAdmin)
admin.site.register(BudgetGoalAPI, BudgetGoalAdmin)
admin.site.register(Profile, ProfileAdmin)
