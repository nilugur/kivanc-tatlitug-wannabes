from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q

from ..models.logs import ExerciseLog
from ..forms import ExerciseLogForm, ExerciseProgramForm, ExerciseProgramItemForm
from ..models.programs import ExerciseProgram


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


class ExerciseProgramListView(LoginRequiredMixin, View):
    def get(self, request):
        programs = ExerciseProgram.objects.filter(
            Q(created_by=None) | Q(created_by=request.user)
        )
        return render(
            request, "tracker/exercise_programs.html", {"programs": programs}
        )


class CreateExerciseProgramView(LoginRequiredMixin, View):
    def get(self, request):
        exercise_program_form = ExerciseProgramForm()
        return render(
            request,
            "tracker/create_exercise_program.html",
            {"exercise_program_form": exercise_program_form},
        )

    def post(self, request):
        exercise_program_form = ExerciseProgramForm(request.POST)
        if exercise_program_form.is_valid():
            new_program = exercise_program_form.save(commit=False)
            new_program.created_by = request.user
            new_program.save()
            return redirect("tracker:add_exercise_program_item", program_id=new_program.id)

        else:
            return render(
                request,
                "tracker/create_exercise_program.html",
                {"exercise_program_form": exercise_program_form},
            )


class AddExerciseProgramItemView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.program = get_object_or_404(ExerciseProgram, pk=kwargs["program_id"])
        self.items = self.program.exerciseprogramitem_set.all()

    def get(self, request, program_id):
        exercise_program_item_form = ExerciseProgramItemForm()
        return render(
            request,
            "tracker/add_exercise_program_item.html",
            {"exercise_program_item_form": exercise_program_item_form,
             "program": self.program,
             "items": self.items
            }

        )

    def post(self, request, program_id):
        exercise_program_item_form = ExerciseProgramItemForm(request.POST)
        if exercise_program_item_form.is_valid():
            new_program_item = exercise_program_item_form.save(commit=False)
            new_program_item.program = self.program
            new_program_item.save()
            return redirect("tracker:add_exercise_program_item", program_id=self.program.id)

        else:
            return render(
                request,
                "tracker/add_exercise_program_item.html",
                {"exercise_program_item_form": exercise_program_item_form,
                    "program": self.program,
                    "items": self.items
                }
            )





