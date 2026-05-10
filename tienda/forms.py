from django import forms
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

class UserRegisterForm(forms.ModelForm):
    """
    Formulario para el registro de nuevos usuarios con validación de correo avanzada.
    """
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator(message="Por favor, introduce una dirección de correo electrónico válida.")],
        widget=forms.EmailInput(attrs={'style': 'flex-grow:1; border:none; background:transparent; padding:10px 0; font-size:1em; color:#212529; outline:none;', 'placeholder': 'correo@ejemplo.com'})
    )
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'style': 'flex-grow:1; border:none; background:transparent; padding:10px 0; font-size:1em; color:#212529; outline:none;', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(label='Repetir Contraseña', widget=forms.PasswordInput(attrs={'style': 'flex-grow:1; border:none; background:transparent; padding:10px 0; font-size:1em; color:#212529; outline:none;', 'placeholder': 'Confirmar contraseña'}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'style': 'flex-grow:1; border:none; background:transparent; padding:10px 0; font-size:1em; color:#212529; outline:none;', 'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'style': 'flex-grow:1; border:none; background:transparent; padding:10px 0; font-size:1em; color:#212529; outline:none;', 'placeholder': 'Nombre(s)'}),
        }
        help_texts = {
            'username': None,
        }
        error_messages = {
            'username': {
                'unique': "Este nombre de usuario ya existe.",
            },
        }

    def clean_email(self):
        """
        Validación personalizada para el campo de correo electrónico.
        - Comprueba la unicidad del correo en la base de datos.
        - Bloquea dominios de correo electrónico temporales conocidos.
        """
        email = self.cleaned_data.get('email')

        # Validación de unicidad: asegura que el correo no esté ya registrado.
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado. Por favor, utiliza otro.")

        # Restricción de dominios temporales para evitar cuentas falsas.
        temporary_domains = [
            'temp-mail.org', '10minutemail.com', 'guerrillamail.com', 
            'yopmail.com', 'throwawaymail.com'
        ]
        domain = email.split('@')[1]
        if domain in temporary_domains:
            raise ValidationError("No se permiten registros desde dominios de correo temporal.")

        return email

    def clean_password2(self):
        """
        Verifica que las dos contraseñas introducidas coincidan.
        """
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd.get('password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
