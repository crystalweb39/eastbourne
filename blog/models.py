'''
@author: chaol
'''

from django.db import models
from tagging.fields import TagField





class PublishStatus(models.Model):
    status = models.CharField(max_length=60, unique=True)
    display_to_user = models.BooleanField(default=True)
    def __unicode__(self):
        return self.status
    class Meta:
        verbose_name_plural = "Publish Status"

class CommentStatus(models.Model):
    status = models.CharField(max_length=60, unique=True)
    display_to_user = models.BooleanField(default=True)
    def __unicode__(self):
        return self.status
    class Meta:
        verbose_name_plural = "Comment Status"

class BlogPost(models.Model):
    title = models.CharField(max_length=40)
    slug = models.SlugField("Unique ID", help_text="This should be automatically generated", unique=True)
    #content = models.TextField()
    content = models.TextField()
    tags = TagField(editable=False)
    publishdate = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(PublishStatus)
    homepage_image = models.ImageField(upload_to="images/", blank=True, null=True)
    def getURL(self):
        return "/blog/%s.html" % self.slug
    def getCommentsCount(self):
        return self.getComments().count()
    def getComments(self):
        return self.comment_set.filter(status__display_to_user=True).order_by("created")
    def get_previous_entry(self):
        try:
            return self.get_previous_by_created(status__display_to_user=True)
        except:
            return None
    def get_next_entry(self):
        try:
            return self.get_next_by_created(status__display_to_user=True)
        except:
            return None

    def __unicode__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(BlogPost)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    comment = models.TextField()#max_length=600 no such thing for textareas...
    created = models.DateTimeField("Date Posted", auto_now_add=True)
    status = models.ForeignKey(CommentStatus)
    def __unicode__(self):
        return "Comment by "+self.name+" on "+self.post.title