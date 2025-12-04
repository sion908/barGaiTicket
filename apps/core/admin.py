from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms

from .models import Shop, User, Owner, Ticket, Stub

# class SettingAdmin(admin.ModelAdmin):
#     def has_add_permission(self, request):
#         # 設定を1つだけしか登録できないようにする
#         count = Setting.objects.all().count()
#         if count == 0:
#             return True
#         return False

#     def has_delete_permission(self, request, obj=None):
#         # 設定を削除できないようにする
#         return False

# class TicketForm(forms.ModelForm):
#     class Meta:
#         model = Ticket
#         fields = ('kind', 'session_id', 'situation')


class TicketInline(admin.TabularInline):
# class TicketInline(admin.StackedInline):
    model = Ticket
    fk_name = "owner"
    # formset = forms.modelformset_factory(Ticket, fields=('kind', 'session_id', 'situation'))

# class OwnerAdmin(UserAdmin):
#     fields = (
#         "username",
#         "is_staff",
#         "is_active",
#         "shop",
#         "user"
#     )
#     exclude = ('date_joined')
#     list_display = (
#         "username",
#         "is_staff",
#         "is_active",
#         "shop",
#         "user"
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2')}
#         ),
#     )
#     ordering = ("is_staff", "is_active",) 


class MyUserAdmin(admin.ModelAdmin):
    fields = (
        "lineUserID",
        "username",
        "email",
        "is_followed"
    )
    inlines = [ TicketInline, ]


class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', "is_active", 'id')
    # list_editable = ("is_active")
    ordering = ("-is_active",) 

admin.site.register(Owner) # , OwnerAdmin)
admin.site.register(User, MyUserAdmin)
admin.site.register(Shop, ShopAdmin)
# admin.site.register(Setting, SettingAdmin)
