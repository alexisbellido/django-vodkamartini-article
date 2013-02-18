from django import forms
from vodkamartiniarticle.models import Article

class ArticleForm(forms.Form):
    def __init__(self, author, article_id=0, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.author = author
        self.article_id = article_id

    error_css_class = 'error'
    required_css_class = 'required'

    title = forms.CharField()
    teaser = forms.CharField(widget=forms.Textarea, label='Enter teaser', required=False)
    body = forms.CharField(widget=forms.Textarea, label='Enter article body')
    image = forms.ImageField(required=False)

    # examples of validating functions
    #def clean_body(self):
    #    body = self.cleaned_data['body']
    #    num_words = len(body.split())
    #    if num_words < 4:
    #        raise forms.ValidationError("Not enough words for the article!")
    #    return body

    #def clean_image(self):
    #    image = self.cleaned_data['image']
    #    print "image", image

    def clean(self):
        """
        Require image uploaded if this is a new article.
        """
        cleaned_data = super(ArticleForm, self).clean()
        image = cleaned_data.get('image')

        if not self.article_id and not image:
            raise forms.ValidationError("Please choose an image to upload.")

        return cleaned_data

    def save(self):
        # TODO what to do about status?, it's live by default now
        if self.article_id:
            """ existing article, no need to change author or status and image will change only if a new one uploaded """
            article = Article.objects.get(pk=self.article_id)
            article.title = self.cleaned_data['title']
            article.teaser = self.cleaned_data['teaser']
            article.body = self.cleaned_data['body']
            if self.cleaned_data['image']:
                article.image = self.cleaned_data['image']
            article.save()
        else:
            """ new article """
            article = Article(title=self.cleaned_data['title'], 
                              teaser=self.cleaned_data['teaser'], 
                              body=self.cleaned_data['body'],
                              author=self.author,
                              image=self.cleaned_data['image'],
                              status=Article.LIVE_STATUS,
                             )
            article.save()
            # if categories need to be exposed in form
            #categories = self.cleaned_data['categories']
            #for category in categories:
            #    article.categories.add(category)
        return article
