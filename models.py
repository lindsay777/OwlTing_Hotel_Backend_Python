from django.db import models

# Create your models here.
class Order(models.Model):
	key = models.CharField(max_length=10)
	user_id = models.CharField(max_length=20)
	date = models.DateField(auto_now=False, auto_now_add=False)
	room_type = models.IntegerField()
	order_id = models.CharField(max_length=50)

	def __str__(self):
		return 'key:' + self.key

class Room(models.Model):
	key = models.CharField(max_length=10)
	total = models.IntegerField()
	soldout = models.IntegerField()

	def __str__(self):
		return 'key' + self.key