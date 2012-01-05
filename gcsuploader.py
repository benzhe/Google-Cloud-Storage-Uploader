from __future__ import with_statement

import cgi
import urllib
import os
import sys
import json
from time import gmtime, strftime, time
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.template import render

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import files

#Change this to your bucket name, and make sure your gae appkey has been added to the gcs console.
#more detail: http://code.google.com/appengine/docs/python/googlestorage/overview.html#Prerequisites
BUCKET = 'your-bucketname'

try:
    files.gs
except AttributeError:
    import gs
    files.gs = gs
    
class QueryLine():
    pass

    Results = []

    def add(self,filename,result,url):
        pass
        self.Results.append({'filename':filename, 'result':result, 'url':url})
        

QL = QueryLine()
    
class MainPage(webapp.RequestHandler):
    def  get(self):
        pass
        
        template_values = {
        }
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

class UploadPage(webapp.RequestHandler):
    
    def post(self):
        
        QL.Results = []          
        for key, value in self.request.params.items():
            if isinstance(value, cgi.FieldStorage):
                upload = value
                if upload.type:
                    mimetype = upload.type
                else:
                    mimetype = 'application/octet-stream'
                if upload.filename:
                    pass
                    filename = urllib.quote(str(upload.filename.encode('utf8')))
                else:
                    filename = "no-name-" + str(time())[-6:]
                    
                try:     
                    title = strftime("%Y%m%d",gmtime()) + '/' + filename
                    filepath = '/gs/%s/%s' % (BUCKET,title)             
                    
                    real_filepath = files.gs.create(filename=filepath,
                                    acl='bucket-owner-full-control',
                                    mime_type= mimetype,
                                    cache_control='no-cache')
                             
                    with files.open(real_filepath,'a') as fp:
                        pass
                        fp.write(upload.value)
                    
                    files.finalize(real_filepath)
                    
                    template_values = {
                        'message':'Upload Success!',
                        'origin_url':"http://commondatastorage.googleapis.com/" + filepath[4:]    
                    }
                    
#                    origin_url = "http://commondatastorage.googleapis.com/" + filepath[4:]
                    origin_url = 'http://'+self.request.host + '/view/' + filepath[4:]
                    
                    QL.add(str(upload.filename.encode('utf8')), 'Success', origin_url)
                    #print str(QL.Results)
                    #self.response.write(str(QL.Results))
                    #self.out(template_values)           
                    

                except BaseException, e:
                    pass
                    #raise(e)
#                    template_values = {
#                        'message':'Upload Failed!'               
#                    }
                    #self.out(template_values)                    
                    QL.add(str(upload.filename.encode('utf8')), 'Failed', 'None')
                    
        res = QL.Results           
        self.response.write(json.dumps(dict(zip(range(len(res)),res))))
        
        
        
    def get(self):
        template_values = {
            'message':'Please Upload Something By POST!'               
        }
        self.out(template_values)        
#        path = os.path.join(os.path.dirname(__file__), 'result.html')
#        self.response.out.write(template.render(path, template_values))
        
    def out(self,template_values):
        path = os.path.join(os.path.dirname(__file__), 'result.html')
        self.response.out.write(template.render(path, template_values))
        
class ViewPage(webapp.RequestHandler):
    def get(self, filename):
        #self.response.write(self.request.url)
        pass
        path = '/gs/%s' % (urllib.quote(filename))
        fp = files.BufferedFile(path)
        data = fp.read(1000*1024*1024*2)
        self.response.content_type= 'application/octet-stream';
        #self.response.write(self.response.content_type)
        self.response.write(data)
#        if isinstance(data,cgi.FieldStorage):
#            self.response.write(data.type)
#        else:
#            self.response.write('lol')


app = webapp.WSGIApplication(
    [
        ('/view/(.*)', ViewPage),
        ('/upload',UploadPage),
        ('/.*', MainPage),
    ], debug=True)
