import sys
import os
import string

from PIL import Image
import Picklable

sys.path.append( os.path.expanduser( "~/lib/boto-1.8d" ) )

bucket = "drzeus"
public_key = "AKIAJXDENFTNNMLDD6XQ"
secret_fname = os.path.expanduser("~/etc/s3pwd.txt")
if not os.path.exists(secret_fname):
	secret_fname = "C:\\Documents and Settings\\poskanze\\My Documents\\s3pwd.txt"
	

class Thumbnailer(Picklable.Picklable):
	
	def __init__(self, max_dim, local_only=True):
		Picklable.Picklable.__init__(self)
		self.max_dim = max_dim
		self.local_only = local_only
		self.secret = None
		self.conn = None
		self.bucket = None
		
		
	def __getstate__(self):
		d = Picklable.Picklable.__getstate__(self)
		del d['secret']
		del d['conn']
		del d['bucket']
		return d
	
	def __setstate__(self, d):
		Picklable.Picklable.__setstate__(self, d)
		self.secret = None
		self.conn = None
		self.bucket = None
		
		
	def getURL(self, abspath):
		return self.loc.toAbsoluteURL(abspath, self.local_only)
	
		
	def makeThumb(self, img, fpath):
		self.writeThumb(img, fpath)
		try:
			return self.uploadThumb(fpath)
		except:
			os.remove(fpath)
			raise
		
		
	def writeThumb(self, img, fpath):
		self.logger.debug("Creating thumbnail %s..." % (fpath))
		dims = [self.max_dim] * 2
		thumb = img.copy()
		thumb.thumbnail(dims, Image.ANTIALIAS)
		thumb.save(fpath)
		
		
	def uploadThumb(self, abspath):
		if self.local_only:
			return
		# abspath is absolute.  We must also have a path relative to the project dir.
		relpath = self.loc.toRelativePath(abspath)
		# Importing late so we can run on Python 2.3 at work...
		from boto.s3.key import Key
		self.loadSecret()
		self.connect()
		key = Key(self.bucket, "%s/%s" % (self.loc.project_name, self.loc.toRelativeURL(relpath)))
		self.logger.debug("Uploading %s to %s..." % (abspath, key))
		key.set_contents_from_filename(abspath, policy='public-read')
		return self.getURL(abspath)


	def loadSecret(self):
		if not self.secret:
			f = open(secret_fname)
			self.secret = string.strip(f.read())
			f.close()

	
	def connect( self ):
		if (self.conn == None):
			# Importing late so we can run on Python 2.3 at work...
			from boto.s3.connection import S3Connection
			self.conn = S3Connection(public_key, self.secret)
			self.logger.debug("Connected to %s." % (self.conn.host))
		if (self.bucket == None):
			self.bucket = self.conn.get_bucket(bucket)
