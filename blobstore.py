import os
import urllib
import webapp2
import cgi
import jinja2
import cgi
import datetime

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
                                       loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class UserMusic(db.Model):
    user = db.StringProperty()
    blob_key = blobstore.BlobReferenceProperty()


def usermusic_key(usermusic_key=None):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainHandler(webapp2.RequestHandler):
    def get(self):
      
        user_nickname = ""
        
        if users.get_current_user():
            login_logout_url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            #self.response.headers['Content-Type'] = 'text/html'
            user_nickname = users.get_current_user().nickname()
        else:
            self.redirect(users.create_login_url(self.request.uri))
            login_logout_url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
    
        upload_url = blobstore.create_upload_url('/upload')
      
        userMusic_query = UserMusic.all()
        songs = userMusic_query.fetch(10)
        
        if os.environ.get('HTTP_HOST'): 
            url = os.environ['HTTP_HOST'] 
        else: 
            url = os.environ['SERVER_NAME'] 
        

#self.response.out.write('<b>%s</b> wrote:' % userMusic.blob_key)
        template_values = {
            'songs': songs,
            'url': url,
            'url_linktext': url_linktext,
            'login_logout_url': login_logout_url,
            'upload_url': upload_url,
            'user_nickname': user_nickname
        }
                    
        template = jinja_environment.get_template('cantata.html')
        self.response.out.write(template.render(template_values))


class SearchNewHandler(webapp2.RequestHandler):
    def get(self):
        
        user_nickname = ""
        
        if users.get_current_user():
            login_logout_url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            #self.response.headers['Content-Type'] = 'text/html'
            user_nickname = users.get_current_user().nickname()
        else:
            # self.redirect(users.create_login_url(self.request.uri))
            login_logout_url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        upload_url = blobstore.create_upload_url('/upload')
        
        userMusic_query = UserMusic.all()
        songs = userMusic_query.fetch(30)
        
        if os.environ.get('HTTP_HOST'): 
            url = os.environ['HTTP_HOST'] 
        else: 
            url = os.environ['SERVER_NAME'] 
        
        
        #self.response.out.write('<b>%s</b> wrote:' % userMusic.blob_key)
        template_values = {
            'songs': songs,
            'url': url,
            'url_linktext': url_linktext,
            'login_logout_url': login_logout_url,
            'upload_url': upload_url,
            'user_nickname': user_nickname
        }
        
        template = jinja_environment.get_template('search.html')
        self.response.out.write(template.render(template_values))



class SearchHandler(webapp2.RequestHandler):
    def get(self):
        music=self.request.get('music')
        user = users.get_current_user()
        
        if user:
            #self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write('Hello, ' + user.nickname())
        
                #upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write('<html><body>')
                # self.response.out.write('')
        self.response.out.write("""<form action="/search?%s" method="get"> Search: <input type="text" name="music"><br> <input type="submit" name="submit" value="Submit"> </form></body></html>""" % (urllib.urlencode({'music': music})))
        
        
        userMusic_query = UserMusic.all()
        
        songs = userMusic_query.fetch(30)
        
        if os.environ.get('HTTP_HOST'): 
            url = os.environ['HTTP_HOST'] 
        else: 
            url = os.environ['SERVER_NAME'] 
        
        
        for userMusic in songs:
            if userMusic.blob_key:
                self.response.out.write('<div><video controls="" width="600" height="50" name="media"><source src="http://'+url+'/serve/%s" type="audio/mp3"></video></div>' % userMusic.blob_key.key())
                self.response.out.write('size : %d ' % userMusic.blob_key.size)
                self.response.out.write('File Name : %s ' % userMusic.blob_key.filename)
                self.response.out.write('Uploaded : %s ' % userMusic.blob_key.creation)
            #self.response.out.write('Blob Properties : %s ' % userMusic.properites())
            else:
                self.response.out.write('There is songs at this point of time')


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        
        user_music = UserMusic(user=users.get_current_user().user_id(),blob_key=blob_info.key())
        db.put(user_music)
        self.response.out.write('Blobkey  %s' % blob_info.key())
        if users.get_current_user().nickname() == "teskkkt@example.com": 
            self.response.out.write('user is found ')
        else:
            self.response.out.write('user is not found ....')
        #self.response.out.write('users.get_current_user().nickname() : %s ' % users.get_current_user().nickname())
# self.redirect('/serve/%s' % blob_info.key())
        self.redirect('/')

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
            #if users.get_current_user().nickname() == "teskkkt@example.com": 
        self.send_blob(blob_info)


app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/search',SearchNewHandler),
                               ('/upload', UploadHandler),
                               ('/serve/([^/]+)?', ServeHandler),
                               ], debug=True)