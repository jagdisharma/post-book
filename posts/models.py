from django.db import models

from accounts.models import User


class Post(models.Model):
    title = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/',blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)  # If user is deleted than delete this product also

    def __str__(self):
        return self.title[:100]

    def shortTitle(self):
        return self.title[:200]

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} likes {}'.format(self.user, self.post)