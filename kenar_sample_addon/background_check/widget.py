import datetime
import re

from django.forms import MultiWidget, Select, Widget, SelectDateWidget
from persiantools.jdatetime import JalaliDateTime

persian_months = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند"
}


class PersianSelectDateWidget(SelectDateWidget):
    """
    A widget that splits date input into three <select> boxes.

    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    """

    none_value = ("", "---")
    month_field = "%s_month"
    day_field = "%s_day"
    year_field = "%s_year"
    input_type = "select"
    select_widget = Select
    use_fieldset = True

    date_re = re.compile(r"(\d{4})/(\d\d?)/(\d\d?)$")

    def __init__(self, attrs=None, years=None, months=None, empty_label=None, input_format="%Y/%m/%d"):
        if months is None:
            months = persian_months
        super().__init__(attrs=attrs, years=years, months=months, empty_label=empty_label)

        self.input_format = input_format

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        date_context = {}
        year_choices = [(i, str(i)) for i in self.years]
        if not self.is_required:
            year_choices.insert(0, self.year_none_value)
        year_name = self.year_field % name
        date_context["year"] = self.select_widget(
            attrs, choices=year_choices
        ).get_context(
            name=year_name,
            value=context["widget"]["value"]["year"],
            attrs={**context["widget"]["attrs"], "id": "id_%s" % year_name},
        )
        month_choices = list(self.months.items())
        if not self.is_required:
            month_choices.insert(0, self.month_none_value)
        month_name = self.month_field % name
        date_context["month"] = self.select_widget(
            attrs, choices=month_choices
        ).get_context(
            name=month_name,
            value=context["widget"]["value"]["month"],
            attrs={**context["widget"]["attrs"], "id": "id_%s" % month_name},
        )
        day_choices = [(i, i) for i in range(1, 32)]
        if not self.is_required:
            day_choices.insert(0, self.day_none_value)
        day_name = self.day_field % name
        date_context["day"] = self.select_widget(
            attrs,
            choices=day_choices,
        ).get_context(
            name=day_name,
            value=context["widget"]["value"]["day"],
            attrs={**context["widget"]["attrs"], "id": "id_%s" % day_name},
        )
        subwidgets = []
        for field in self._parse_date_fmt():
            subwidgets.append(date_context[field]["widget"])
        context["widget"]["subwidgets"] = subwidgets
        return context

    def format_value(self, value):
        """
        Return a dict containing the year, month, and day of the current value.
        Use dict instead of a datetime to allow invalid dates such as February
        31 to display correctly.
        """
        year, month, day = None, None, None
        if isinstance(value, (datetime.date, datetime.datetime)):
            jalali = JalaliDateTime(value)
            year, month, day = jalali.year, jalali.month, jalali.day
        elif isinstance(value, str):
            match = self.date_re.match(value)
            if match:
                # Convert any zeros in the date to empty strings to match the
                # empty option value.
                year, month, day = [int(val) or "" for val in match.groups()]
            else:
                try:
                    d = JalaliDateTime.strptime(value, self.input_format)
                except ValueError:
                    pass
                else:
                    year, month, day = d.year, d.month, d.day

        return {"year": year, "month": month, "day": day}

    def _parse_date_fmt(self):
        fmt = self.input_format
        escaped = False
        for char in fmt:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char in "Yy":
                yield "year"
            elif char in "bEFMmNn":
                yield "month"
            elif char in "dj":
                yield "day"

    def id_for_label(self, id_):
        for first_select in self._parse_date_fmt():
            return "%s_%s" % (id_, first_select)
        return "%s_month" % id_

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)
        if y == m == d == "":
            return None
        if y is not None and m is not None and d is not None:
            try:
                date_value = JalaliDateTime(int(y), int(m), int(d))
            except ValueError:
                # Return pseudo-ISO dates with zeros for any unselected values,
                # e.g. '2017-0-23'.
                return "%s-%s-%s" % (y or 0, m or 0, d or 0)
            return date_value.strftime(self.input_format)
        return data.get(name)

    def value_omitted_from_data(self, data, files, name):
        return not any(
            ("{}_{}".format(name, interval) in data)
            for interval in ("year", "month", "day")
        )
