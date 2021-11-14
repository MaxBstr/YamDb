from import_export import resources

from .models import Comment, Review


class ReviewResource(resources.ModelResource):
    class Meta:
        model = Review
        fields = ('text', 'author', 'score', 'pub_date', 'title')


class CommentResource(resources.ModelResource):
    class Meta:
        model = Comment
        fields = ('author', 'review', 'text', 'pub_date')
