from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from vodkamartiniarticle.models import Article
from vodkamartinicategory.models import Category
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class Command(BaseCommand):
    args = '<article_title article_title ...>'
    option_list = BaseCommand.option_list + (
        make_option('--category_id', dest='category_id', default=None,
            help='Specifies the category id to use for new articles.'),
        make_option('--user_id', dest='user_id', default=None,
            help='Specifies the user id to assign as author of the articles.'),
    )
    help = 'Creates articles.'

    def handle(self, *args, **options):
        try:
            c = Category.objects.get(pk=options['category_id'])
        except Category.DoesNotExist:
            raise CommandError('Category with id "%s" does not exist' % options['category_id'])

        for title in args:
            self.create_article(title, c, options['user_id'])

    def create_article(self, title, c, user_id):
        teaser = 'teaser for %s' % (title,)
        body = 'body for %s' % (title,)
        u = User.objects.get(pk=user_id)
        slug = slugify(title)
        status = Article.DRAFT_STATUS
        a = Article(title=title, teaser=teaser, body=body, slug=slug, author=u, status=status)
        a.save()
        a.categories.add(c)
        a.save()
        self.stdout.write("Created article %d:'%s' for category '%s', owned by %d:'%s'.\n" % (a.id, a.title, c.title, u.id, u.username))
