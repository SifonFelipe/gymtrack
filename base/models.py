from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

class Topic(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Group(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()

    def __str__(self):
        return self.user.username

# Create profile when new user signs up
@receiver(post_save, sender=User)
def createProfile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

#post_save.connect(createProfile, sender=User)

class Message(models.Model):
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)

class Exercise(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class ExerciseByPerson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    series = models.PositiveIntegerField(default=1)
    reps = models.PositiveIntegerField()
    date = models.DateField(default=datetime.date.today)
    routine = models.ForeignKey('Routine', on_delete=models.CASCADE, default=None)

class Routine(models.Model):
    title = models.CharField(max_length=30, default=0)
    date = models.DateField(default=datetime.date.today)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Article(models.Model):
    group = models.ForeignKey(Group, related_name='articles', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']

class ArticleComment(models.Model):
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']