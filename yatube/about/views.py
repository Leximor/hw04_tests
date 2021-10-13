
from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['just_title'] = 'Страница об авторе'
        context['just_text'] = ('На самом деле мне нравилась только ты, '
                                'мой идеал и моё мерило.')
        return context


class AboutTechView (TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['just_title'] = 'Страница о науке и технологиях '
        context['just_text'] = ('В 2026 году, в пустыне Невада, археологи '
                                'обнаружили объект через который человек мог '
                                'теелпортироваться в древний город '
                                'на планете Марс. '
                                'Они назвали этот телепорт - "Ковчег"'
                                'Прошло уже двадцать лет, '
                                'но мы до сих пор пытаемся '
                                'понять: Зачем этот телепорт был построен, '
                                'и что произлошло с цивилизацией '
                                'его создавшей...')
        return context
