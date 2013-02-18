from django.core.management.base import BaseCommand, CommandError
from vodkamartiniarticle.models import Article
from optparse import make_option

class Command(BaseCommand):
    args = '<article_id article_id ...>'
    option_list = BaseCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
    )
    help = 'Delete articles.'

    def handle(self, *args, **options):
        interactive = options.get('interactive')
        articles = Article.objects.filter(id__in=args)
        for article in articles:
            input_msg = "Are you sure you want to delete article with id %d and title '%s'? (type 'y' to confirm)" % (article.id, article.title)
            if interactive:
                delete = raw_input(input_msg + ': ')
            else:
                delete = 'y'
            if delete == 'y':
                id = article.id
                title = article.title
                article.delete()
                self.stdout.write("%d: '%s' deleted.\n" % (id, title))

        if not articles.count():
            self.stdout.write("No articles found, please verify the ids used.\n")
