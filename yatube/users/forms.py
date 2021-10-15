from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    PasswordChangeForm, SetPasswordForm, UserCreationForm,
)

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class SetPassword(SetPasswordForm):
    class Meta(PasswordChangeForm):
        fields = ('old_password', 'new_password1', 'new_password2')
