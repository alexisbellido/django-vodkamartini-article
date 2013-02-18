from django.test import TestCase
from django.contrib.auth.models import User
from vodkamartiniarticle.models import Article
from vodkamartinicategory.models import Category
from django.core import  management
from StringIO import StringIO
import re

class ArticleCommandsTest(TestCase):
    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()

    def tearDown(self):
        self.stdout.close()
        self.stderr.close()

    def testArticleCreate(self):
        """
        Runs: ./manage.py vmarticle_create "The First Article", "The Second Article" --category_id=1 --user_id=1
        And then confirms the output of the command contains the titles, which indicates success, and
        to be sure counts the articles at the end.
        """
        author = User.objects.create_user(username='joe', password='qwerty')
        category_title = "The Category"
        category = Category.objects.create(title=category_title)
        titles = ("The First Article", "The Second Article")
        management.call_command('vmarticle_create', titles[0], titles[1], category_id = category.id, user_id=author.id, verbosity=0, interactive=False, stdout=self.stdout)
        command_output = self.stdout.getvalue().strip()
        for title, line in zip(titles, command_output.split('\n')):
            match = re.search(r'\b%s\b' % title, line)
            self.assertEqual(match.group(0), title)
        self.assertEqual(Article.objects.all().count(), 2)

    def testArticleDelete(self):
        """
        Runs: ./manage.py vmarticle_delete <article_id>
        And then confirms the output of the command contains the title, which indicates success, and
        to confirm there are zero articles.
        """
        title = "First Article"
        teaser = "the teaser"
        body = "the body"
        slug = "first-article"
        author = User.objects.create_user(username='joe', password='qwerty')
        status = Article.LIVE_STATUS
        article = Article.objects.create(title=title, teaser=teaser, body=body, slug=slug, author=author, status=status)
        management.call_command('vmarticle_delete', article.id, verbosity=0, interactive=False, stdout=self.stdout)
        command_output = self.stdout.getvalue().strip()
        match = re.search(r'\b%s\b' % title, command_output)
        self.assertEqual(match.group(0), title)
        self.assertEqual(Article.objects.all().count(), 0)
