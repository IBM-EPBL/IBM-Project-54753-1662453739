from locust import HttpUser, between, task
import time
import random

data =( {'email':'vijayit2023@gmail.com', 'password':'12345'},{'email':'tharunkumarit2023@gmail.com' , 'password':'12345'},{'email':'vijay8870605473@gmail.com', 'password':'12345'} )
post_headers={'content-Type':'application/x-www-form-urlencoded'}

class WebsiteUser(HttpUser):
    wait_time = between(5,15)

    @task
    def index(self):
        self.client.get("/")

    @task
    def home(self):
        self.client.get("/login",
                    data=data[random.randint(0,3)], headers=post_headers)
    
    @task
    def home(self):
        self.client.get("/signup",
                    data=data[random.randint(0,3)], headers=post_headers)

    @task
    def home1(self):
        self.client.get("/home")
    
    
    @task
    def contact(self):
         self.client.get("/contact")
    
    @task
    def prediction(self):
         self.client.get("/prediction")

    @task
    def images(self):
         self.client.get("/images")

    @task
    def explore(self):
         self.client.get("/explore")