import datetime

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import SelectDateWidget, DateField
from django.forms.fields import BaseTemporalField
from persiantools.jdatetime import JalaliDateTime

from kenar_sample_addon.background_check.widget import PersianSelectDateWidget
from kenar_sample_addon.kenar.utils import persian


class PersianDateField(DateField):
    widget = PersianSelectDateWidget
    default_error_messages = {
        "invalid": "تاریخ وارد شده صحیح نمی‌باشد.",
    }

    def __init__(self, input_formats=('%Y/%m/%d',), **kwargs):
        super().__init__(input_formats=input_formats, **kwargs)

    def to_python(self, value):
        """
        Validate that the input can be converted to a date. Return a Python
        datetime.date object.
        """
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return JalaliDateTime(value.date())
        if isinstance(value, datetime.date):
            return JalaliDateTime(value)
        return super().to_python(value)

    def strptime(self, value, format):
        return JalaliDateTime.strptime(value, format).date()


class BackgroundCheckForm(forms.Form):
    name = forms.CharField(
        label="نام", required=False,
        widget=forms.TextInput(attrs={}))
    family_name = forms.CharField(
        label="نام خانوادگی", required=False,
        widget=forms.TextInput(attrs={}))
    father_name = forms.CharField(
        label="نام پدر", required=False,
        widget=forms.TextInput(attrs={}))
    birth_date = PersianDateField(label="تاریخ تولد",
                                  widget=PersianSelectDateWidget(
                                      years=range(1300, 1402),
                                      empty_label=(1380, 1, 1)
                                  ))
    national_id = forms.CharField(
        label="کد‌ملی", required=False,
        widget=forms.TextInput(attrs={"class": "numberic", 'placeholder': "مثال: ۱۲۳۴۵۶۷۸۹۰",
                                      "inputmode": "numeric"}))
    identity_id = forms.CharField(
        label="شماره شناسنامه", required=False,
        widget=forms.TextInput(attrs={"class": "numberic", 'placeholder': "مثال: ۱۲۳۴۵۶۷۸۹۰",
                                      "inputmode": "numeric"}))

    def clean(self):
        cleaned_data = super().clean()
        res_cleaned_data = {}
        for key, value in cleaned_data.items():
            if type(value) == str and len(value.strip()) == 0:
                self.add_error(key, f"{getattr(self, value).label} اجباری می باشد")
            if type(value) == str:
                res_cleaned_data[key] = value.strip().translate(persian.AR_EN_NUMBER_MAPPING) \
                    .translate(persian.FA_EN_NUMBER_MAPPING).translate(persian.AR_FA_CHAR_MAPPING)
            else:
                res_cleaned_data[key] = value
        return res_cleaned_data


    def clean_national_id(self):
        national_id: str = self.cleaned_data.get('national_id')
        if len(national_id) != 10:
            raise ValidationError("کد ملی یک عدد ۱۰ رقمی می‌باشد")

        if not national_id.isdigit():
            raise ValidationError("کد ملی فقط باید شامل رقم باشد.")

        return national_id

    def clean_identity_id(self):
        identity_id: str = self.cleaned_data.get('identity_id')
        if not identity_id.isdigit():
            raise ValidationError("شماره شناسنامه فقط باید شامل رقم باشد.")

        return identity_id
