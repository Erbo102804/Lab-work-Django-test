from django.test import TestCase
from django.urls import reverse

from .models import Blog


class BlogListDetailTests(TestCase):
    """Задание 1: тесты страниц списка (List) и детального просмотра (Detail)."""

    @classmethod
    def setUpTestData(cls):
        cls.blog = Blog.objects.create(
            title='Первая статья',
            content='Содержимое первой статьи',
        )
        cls.second_blog = Blog.objects.create(
            title='Вторая статья',
            content='Содержимое второй статьи',
        )

    # 1. Список открывается и использует нужный шаблон
    def test_list_view_status_and_template(self):
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_list.html')

    # 2. В списке есть контент всех статей
    def test_list_view_contains_content(self):
        response = self.client.get(reverse('blog_list'))
        self.assertContains(response, 'Первая статья')
        self.assertContains(response, 'Вторая статья')
        self.assertEqual(len(response.context['blogs']), 2)

    # 3. Пустой список показывает сообщение, а не статьи
    def test_list_view_empty(self):
        Blog.objects.all().delete()
        response = self.client.get(reverse('blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Статей пока нет.')
        self.assertQuerySetEqual(response.context['blogs'], [])

    # 4. Ссылки в списке ведут на детальные страницы, и по ним можно перейти
    def test_list_links_lead_to_detail(self):
        response = self.client.get(reverse('blog_list'))
        for blog in (self.blog, self.second_blog):
            url = blog.get_absolute_url()
            self.assertContains(response, f'href="{url}"')
            detail = self.client.get(url)
            self.assertEqual(detail.status_code, 200)
            self.assertContains(detail, blog.title)

    # 5. Детальная страница получает правильный id и контент
    def test_detail_view_returns_correct_object(self):
        response = self.client.get(reverse('blog_detail', kwargs={'pk': self.blog.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_detail.html')
        self.assertEqual(response.context['blog'].pk, self.blog.pk)
        self.assertContains(response, 'Содержимое первой статьи')
        self.assertNotContains(response, 'Содержимое второй статьи')

    # 6. Несуществующий id даёт 404
    def test_detail_view_404_for_missing_id(self):
        response = self.client.get(reverse('blog_detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)

    # 7. URL без числового id не совпадает с маршрутом
    def test_detail_view_non_numeric_id(self):
        response = self.client.get('/blog/abc/')
        self.assertEqual(response.status_code, 404)

    # 8. Ссылка «Назад к списку» на детальной странице работает
    def test_detail_back_link_to_list(self):
        response = self.client.get(self.blog.get_absolute_url())
        list_url = reverse('blog_list')
        self.assertContains(response, f'href="{list_url}"')
        self.assertEqual(self.client.get(list_url).status_code, 200)

    # 9. get_absolute_url строит правильный адрес
    def test_get_absolute_url(self):
        self.assertEqual(self.blog.get_absolute_url(), f'/blog/{self.blog.pk}/')
