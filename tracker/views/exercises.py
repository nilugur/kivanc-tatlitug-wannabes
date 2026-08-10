from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from ..models.logs import ExerciseLog
from ..forms import ExerciseLogForm


class AddExerciseView(LoginRequiredMixin, View):

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.today = timezone.now().date()
        self.today_exercises = ExerciseLog.objects.filter(user=request.user, date__date=self.today)

    def get(self, request):
        exercise_log_form = ExerciseLogForm()

        return render(
        request,
        "tracker/add_exercise.html",
        {"exercise_log_form": exercise_log_form, "today_exercises": self.today_exercises}
        )

    def post(self, request):
        exercise_log_form = ExerciseLogForm(request.POST)
        if exercise_log_form.is_valid():
            new_exercise = exercise_log_form.save(commit=False)
            new_exercise.user = request.user
            new_exercise.save()
            return redirect("tracker:add_exercise")
        else:
            return render(
                    request,
                    "tracker/add_exercise.html",
                    {"exercise_log_form": exercise_log_form, "today_exercises": self.today_exercises}
                    )


class DeleteExerciseView(LoginRequiredMixin, View):
    def post(self, request, exercise_id):
        deleted_item = get_object_or_404(ExerciseLog, pk=exercise_id)
        if deleted_item.user != request.user:
            raise PermissionDenied
        deleted_item.delete()

        return redirect("tracker:add_exercise")


class EditExerciseView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.edited_item = get_object_or_404(ExerciseLog, pk=kwargs["exercise_id"])
        if self.edited_item.user != request.user:
            raise PermissionDenied

    def get(self, request, exercise_id):
        exercise_log_form = ExerciseLogForm(instance=self.edited_item)
        return render(request, "tracker/edit_exercise.html", {"exercise_log_form": exercise_log_form, "exercise_log": self.edited_item})

    def post(self, request, exercise_id):
        exercise_log_form = ExerciseLogForm(request.POST, instance=self.edited_item)
        if exercise_log_form.is_valid():
            exercise_log_form.save()
            return redirect("tracker:add_exercise")
        else:
            return render(request, "tracker/edit_exercise.html", {"exercise_log_form": exercise_log_form, "exercise_log": self.edited_item})