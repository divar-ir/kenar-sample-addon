from django import forms
from django.core.exceptions import ValidationError

from kenar_sample_addon.kenar.utils import persian


class VerificationForm(forms.Form):
    national_id = forms.CharField(
        label="کد ملی", required=False, help_text="توجه: کد ملی شما به کاربران نمایش داده نمی‌شود.",
        widget=forms.TextInput(attrs={"class": "numberic", 'placeholder': "مثال: ۱۲۳۴۵۶۷۸۹۰",
                                      "inputmode": "numeric"}))
    postal_code = forms.CharField(
        label="کد پستی", required=False, help_text="توجه: کد پستی ملک شما به کاربران نمایش داده نمی‌شود.",
        widget=forms.TextInput(attrs={"class": "numberic", 'placeholder': "مثال: ۱۲۳۴۵۶۷۸۹۰",
                                      "inputmode": "numeric"}))

    def clean_national_id(self):
        national_id: str = self.cleaned_data.get('national_id')
        if national_id is None or len(national_id.strip()) == 0:
            raise ValidationError("کد ملی اجباری می‌باشد")

        en_national_id = national_id.translate(persian.AR_EN_NUMBER_MAPPING).translate(persian.FA_EN_NUMBER_MAPPING). \
            strip()
        if len(en_national_id) != 10:
            raise ValidationError("کد ملی یک عدد ۱۰ رقمی می‌باشد")

        if not en_national_id.isdigit():
            raise ValidationError("کد ملی فقط باید شامل رقم باشد.")

        return en_national_id

    def clean_postal_code(self):
        postal_code: str = self.cleaned_data.get('postal_code')
        if postal_code is None or len(postal_code.strip()) == 0:
            raise ValidationError("کد پستی اجباری می‌باشد")

        en_postal_code = postal_code.translate(persian.AR_EN_NUMBER_MAPPING).translate(persian.FA_EN_NUMBER_MAPPING). \
            strip()
        if len(en_postal_code) != 10:
            raise ValidationError("کد پستی یک عدد ۱۰ رقمی می‌باشد")

        if not en_postal_code.isdigit():
            raise ValidationError("کد پستی فقط باید شامل رقم باشد")

        return en_postal_code
