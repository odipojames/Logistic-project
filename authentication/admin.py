from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from  django.contrib.auth.forms import ReadOnlyPasswordHashField

from authentication.models import User, Role

class UserCreationForm(forms.ModelForm):
    """A form creating new users. Include all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone','is_verified', 'is_active', 'is_staff', 'role')
    
    def clean_password2(self):
        # Ensure that the two password entries match
        password1 = self.cleaned_data.get("password2")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the field on the user,
    but replaces the password field with admin's password has display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone', 'password','is_verified', 'is_active', 'is_staff', 'role')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
    
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User
    list_display = ('email', 'full_name', 'phone', 'date_joined')
    list_filter = ('full_name',)
    fieldsets = (
        (None, {"fields": ('full_name', 'password')}),
        ('Contact info', {'fields' : ('phone', 'email')}),
        ('Other info', {'fields' : ('role',)}),
        ('Permissions', {'fields' : ('is_staff', 'is_active', 'is_verified', 'is_superuser')})
    )
    add_fieldsets = (
        (None, {
            'classes' : ('wide',),
            'fields' : ('email', 'full_name', 'phone', 'role','is_active', 'is_staff', 'is_superuser', 'is_verified','password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(Role)
