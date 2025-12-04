from django.http import Http404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.functions import TruncDay


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "app/dashboard.html"
    login_url = '/login/'

    def get_context_data(self, **kwargs):

        owner = self.request.user

        if owner.is_anonymous:
            raise Http404()

        context = super().get_context_data(**kwargs)
        context["owner"] = owner
        shop = owner.shop
        context["shop"] = shop
        condition = {'is_used': True}
        if shop:
            stubs = shop.stub.filter(**condition)
            day_stubs = stubs.annotate(
                    day=TruncDay('updated_at')
                ).values('day').annotate(
                    total=Count('day')
                )
            if day_stubs:
                cul_stubs = []
                # print(day_stubs)
                day_stub = day_stubs[0]
                [year,month,day] = day_stub["day"].strftime('%y-%m-%d').split("-")
                cul_stubs.append({"kind":2, "year":year, "month":month, "day":day, "month_stub":day_stub["total"], "day_stub":day_stub["total"]})
                [_last_year, _last_month] = [year, [month, 0]]
                count = {'year': {year: 1},'year_month': {year: 1},'month': {month: 1}}
                for day_stub in day_stubs[1:]:
                    [year,month,day] = day_stub["day"].strftime('%y-%m-%d').split("-")
                    cul_stub = {"kind": 0, "year": -1, "month": -1, "day": day, "month_stub": -1, "day_stub": day_stub["total"]}
                    if not _last_month[0] == month:  # 前の月と違う場合
                        cul_stub["month"] = month
                        cul_stub["kind"] += 1
                        count["month"][month] = 1
                        cul_stub["month_stub"] = day_stub["total"]
                        _last_month = [month, len(cul_stubs)]
                        count["year_month"][year] = 1
                        if not _last_year == year:
                            cul_stub["year"] = year
                            cul_stub["kind"] += 1
                            count["year"][year] = 1
                            _last_year = year
                        else:
                            count["year"][year] += 1
                    else:
                        count["month"][month] += 1
                        count["year"][year] += 1
                        cul_stubs[_last_month[1]]["month_stub"] += day_stub["total"]
                        count["year_month"][year] += 1
                    cul_stubs.append(cul_stub)
                context['stubs_days'] = list(day_stubs)
                context['cul_stubs'] = cul_stubs
                context['stub_count'] = count

            context['stubs'] = stubs
        print(context)
        return context


class HomeDetailView(LoginRequiredMixin, TemplateView):
    template_name = "app/dashboard_detail.html"
    login_url = '/login/'

    def get_context_data(self, **kwargs):

        owner = self.request.user

        if owner.is_anonymous:
            raise Http404()

        context = super().get_context_data(**kwargs)
        context["name"] = owner.username
        context["shop"] = owner.shop
        return context
