from django.db import models
import re
import bcrypt

#REGEX
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Create your models here.
class userManager(models.Manager):
    #validator for the registration
    def reg_validator(self, postData):
        errors = {}
        if len (postData['first_name']) < 2:
            errors ["reg_fname"] = "First name must be at least 2 characters"
        elif not NAME_REGEX.match(postData['first_name']):
            errors ["reg_fname"] = "First name can only contain letters"

        if len(postData['last_name']) < 2:
            errors ["reg_lname"] = "Last name should be at least 2 characters"
        elif not NAME_REGEX.match(postData['last_name']):
            errors ["reg_lname"] = "Last name can only contain letters"

        if len (postData['password']) < 8:
            errors ["reg_password"] = "Password should be at least 8 characters"
        if postData['password'] != postData['confirmPW']:
            errors ['reg_password'] = "Passwords should match"

        if not EMAIL_REGEX.match(postData['email']):
            errors ['reg_email'] = "you must enter a valid email address"
        for a_user in user.objects.all():
            if postData['email'] == a_user.email:
                errors [ 'unique_email'] = "This email is already in use"
        return errors

    # validator for the login
    def login_validator(self, postData):
        errors = {}
        existing = user.objects.filter(email=postData['email'])
        if len(existing) == 0:
            errors['log'] = "Invalid Email/Password"
        elif not bcrypt.checkpw(postData['password'].encode(), existing[0].password.encode()):
            errors['log'] = "Invalid Email/Password"
        return errors

class user(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=75)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = userManager()

class City(models.Model):
    city_name = models.CharField(max_length=45)
    temp = models.IntegerField()
    aqi = models.IntegerField()
    added_by = models.ForeignKey(user, related_name='cities', on_delete = models.CASCADE)
    impact = models.CharField(max_length=45, default = "Super Awesome")
    pressure = models.FloatField(default =0)
    wind = models.FloatField(default =0)
    co = models.FloatField(default =0)
