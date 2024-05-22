from django.contrib import admin

# Register your models here.

from expenses.models import IncomeSource,ExpenseCategory,Transaction


class IncomeSourceAdmin(admin.ModelAdmin):
    pass

class ExpenseCategoryAdmin(admin.ModelAdmin):
    pass

class TransactionAdmin(admin.ModelAdmin):
    pass


admin.site.register(IncomeSource, IncomeSourceAdmin)
admin.site.register(ExpenseCategory, ExpenseCategoryAdmin)
admin.site.register(Transaction,TransactionAdmin)

