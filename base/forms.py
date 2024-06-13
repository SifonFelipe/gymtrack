from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Group, Profile, Exercise, ExerciseByPerson, Routine

class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        exclude = ['participants', 'host']

#changed because i modified topics to be created, with forms is harder 

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']

class ExerciseForm(ModelForm):
    class Meta:
        model = ExerciseByPerson
        fields = ['exercise', 'weight', 'reps']
