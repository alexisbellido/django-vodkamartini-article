from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import User
from vodkamartiniarticle.models import Article
from vodkamartinicategory.models import Category
from django.template.defaultfilters import slugify


class ArticleModelTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='joe', password='qwerty')
        self.teaser = "this is a teaser"
        self.body = "and this is the body"

    def testCreateArticleLive(self):
        """
        Verify creation is correct when providing all fields with LIVE_STATUS.
        """
        title = "First Live Article"
        slug = "first-live-article"
        status = Article.LIVE_STATUS
        article = Article(title=title, teaser=self.teaser, body=self.body, slug=slug, author=self.author, status=status)
        article.save()
        c1 = Category.objects.create(title='Programming', slug='programming')
        c2 = Category.objects.create(title='Science', slug='science')
        article.categories.add(c1, c2)
        self.assertEqual(Article.objects.filter(status=Article.LIVE_STATUS).count(), 1)
        self.assertEqual(Article.objects.get(slug=slug).categories.count(), 2)

    def testCreateArticleDraft(self):
        """
        Verify creation is correct when providing all fields with DRAFT_STATUS.
        """
        title = "First Draft Article"
        teaser = "this is a teaser"
        body = "and this is the body"
        slug = "first-draft-article"
        status = Article.DRAFT_STATUS
        article = Article(title=title, teaser=self.teaser, body=self.body, slug=slug, author=self.author, status=status)
        article.save()
        c1 = Category.objects.create(title='Programming', slug='programming')
        c2 = Category.objects.create(title='Science', slug='science')
        article.categories.add(c1, c2)
        self.assertEqual(Article.objects.filter(status=Article.DRAFT_STATUS).count(), 1)
        self.assertEqual(Article.objects.get(slug=slug).categories.count(), 2)

    def testCreateArticleHidden(self):
        """
        Verify creation is correct when providing all fields with HIDDEN_STATUS.
        """
        title = "First Hidden Article"
        teaser = "this is a teaser"
        body = "and this is the body"
        slug = "first-hidden-article"
        status = Article.HIDDEN_STATUS
        article = Article(title=title, teaser=self.teaser, body=self.body, slug=slug, author=self.author, status=status)
        article.save()
        c1 = Category.objects.create(title='Programming', slug='programming')
        c2 = Category.objects.create(title='Science', slug='science')
        article.categories.add(c1, c2)
        self.assertEqual(Article.objects.filter(status=Article.HIDDEN_STATUS).count(), 1)
        self.assertEqual(Article.objects.get(slug=slug).categories.count(), 2)

    def testCreateArticleAutoSlug(self):
        """
        Verify automatic slug is created if not provided.
        """
        title = "Article With Slug"
        status = Article.LIVE_STATUS
        article = Article(title=title, teaser=self.teaser, body=self.body, author=self.author, status=status)
        article.save()
        self.assertEqual(article.slug, slugify(title))

    def testCreateArticleNoSlug(self):
        """
        Verify error when slug is None.
        """
        title = "Article With No Slug"
        slug = ""
        status = Article.LIVE_STATUS
        article = Article.objects.create(title=title, teaser=self.teaser, body=self.body, slug=slug, author=self.author, status=status)
        article.slug = None
        self.assertRaises(IntegrityError, article.save)


#class LiveArticleManagerTest(TestCase):
#    def setUp(self):
#        """
#        Create articles with different statuses to try the manager that gets only the live ones.
#        """
#        pass
