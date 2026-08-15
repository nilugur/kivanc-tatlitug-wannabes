from django.db import models
from .catalog import Exercise
from django.conf import settings


class ExerciseProgram(models.Model):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class ExerciseProgramItem(models.Model):
    program = models.ForeignKey(ExerciseProgram, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.program.name} - {self.exercise.exercise_name if self.exercise else 'Deleted Exercise'} - {self.duration_minutes} minutes"
