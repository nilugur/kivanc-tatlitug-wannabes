from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models.profiles import ClientProfile, DietitianProfile
from ..forms import ClientProfileForm, DietitianProfileForm


class ProfileView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if ClientProfile.objects.filter(user=request.user).exists():
            self.profile = ClientProfile.objects.get(user=request.user)
            self.profile_form = ClientProfileForm
            self.profile_template = "tracker/profile_client.html"
        else:
            self.profile = DietitianProfile.objects.get(user=request.user)
            self.profile_form = DietitianProfileForm
            self.profile_template = "tracker/profile_dietitian.html"

    def get(self, request):
        # instance=profile diyerek Django'ya "yeni bir kayıt oluşturma,
        # kullanıcının zaten var olan profilini güncelle" diyoruz.
        # instance= olmasaydı, her kaydette veritabanına ikinci bir
        # ClientProfile/DietitianProfile satırı daha eklenirdi.
        form = self.profile_form(instance=self.profile)
        return render(request, self.profile_template, {"profile_form": form})

    def post(self, request):
        form = self.profile_form(request.POST, instance=self.profile)
        if form.is_valid():
            form.save()
            return redirect("tracker:profile")
        else:
            return render(request, self.profile_template, {"profile_form": form})
