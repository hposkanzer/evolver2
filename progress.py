#                      -*- Mode: Python ; tab-width: 4 -*- 

# Classes for printing progress bars

import sys
import string
import time
import threading
import copy


OutOfBoundsException = "Progress bar out of bounds"


#####################################################################################
# A progress bar for a single thread.
class ProgressBar:

	progress_width = 60
	timeout = 1

	# The callback is called once for each item in items.
	def __init__( self, items, callback=None, newlines=0 ):
		self.items = items
		self.item_count = len(items)
		self.callback = callback
		self.i = 0
		self.t0 = 0
		self.last = time.time()
		self.newlines = newlines


	# Begin calling the callback with each item.
	# Return when all items are processed.
	def start( self ):
		# Print the initial bar before we callback.
		self.initializeBar()
		if self.item_count:
			while self.hasMore():
				self.progress()
		else:
			# No items!  Print the final bar.
			self.printBar( self.progress_width, 1.0, 0 )

	# Deprecated.
	def loop( self ):
		self.start()


	def hasMore( self ):
		return (self.i < self.item_count)


	def progress( self ):
		# Callback.
		if self.callback:
			ret = self.callback( self.items[self.i] )
		else:
			ret = self.items[self.i]
		# Update the bar
		self.updateBar()
		# Return the results
		return ret


	def updateBar( self ):
		# Post-callback progress bar.
		if ((self.i == self.item_count-1)  # Last one
			or not (self.i % self.progress_stride)  # Every n objects
			or ((time.time() - self.last) > self.timeout)):  # Every n seconds
			# Percent done
			pct_done = float(self.i + 1) / float(self.item_count)
			# Progress bar
			done_width = int( round( pct_done * self.progress_width ) )
			# Estimated time remaining
			dt = time.time() - self.t0
			secs = (self.item_count * dt / float(self.i + 1)) - dt
			# Output string
			self.printBar( done_width, pct_done, secs )
			# Update the status
			self.last = time.time()
		self.i = self.i + 1


	def initializeBar( self ):
		self.t0 = time.time()
		self.progress_stride = max( self.item_count / 100, 1 )
		self.printBar( 0, 0.0, 0 )


	def printBar( self, done_width, pct_done, remain_secs ):
		if (self.i >= self.item_count-1):
			remain_secs = time.time() - self.t0  # Last one, print elapsed time.
		etr = "%02d:%02d:%02d" % (remain_secs/3600, (remain_secs % 3600)/60, round(remain_secs) % 60)
		s = "\r|" + ("=" * done_width) + ("-" * (self.progress_width - done_width)) + "| %3.0f%%  %s"  % (pct_done * 100, etr)
		sys.stdout.write( s )
		if (self.newlines  # Debug is on
			or ((self.i >= self.item_count-1)  # Last one
				and (pct_done > 0))):  # Not the initial bar
			sys.stdout.write( "\n" )
		sys.stdout.flush()


#####################################################################################
# A progress bar for multiple threads.
class ThreadedProgressBar( ProgressBar ):

	lock = threading.Lock()

	# workers is a list of ProgressBarWorker subclasses.
	# Each worker thread is started and then lets us know when it's completed an item.
	def __init__( self, workers, item_count, newlines=0 ):
		ProgressBar.__init__( self, workers, newlines=newlines )
		self.item_count = item_count
		if not workers:
			raise RuntimeError, "No workers provided"
		# Let's double-check that the workers are really workers.
		for worker in workers:
			if not isinstance(worker, ProgressBarWorker):
				raise RuntimeError, "%s is not a ProgressBarWorker" % (worker)


	# Start each worker working.  Return when all are complete.
	def start( self, block=1 ):
		self.initializeBar()
		if self.item_count:
			for worker in self.items:
				worker.setProgressBar( self )
				worker.start()
			if block:
				for worker in self.items:
					worker.join()
		else:
			# No items!  Print the final bar.
			self.printBar( self.progress_width, 1.0, 0 )


	def updateProgress( self ):
		self.lock.acquire()
		try:
			self.updateBar()
		finally:
			self.lock.release()


#####################################################################################
# A worker thread for a ThreadedProgressBar.
class ProgressBarWorker( threading.Thread ):

	def __init__ ( self ):
		threading.Thread.__init__( self )
		self.bar = None

	def setProgressBar( self, bar ):
		self.bar = bar

	def run( self ):
		item = self.getNextItem()
		while (item is not None):  # NOTE: this means None is not a valid item.
			self.processItem( item )
			self.bar.updateProgress()
			item = self.getNextItem()

	def getNextItem( self ):
		raise NotImplementedError, "getNextItem"

	def processItem( self ):
		raise NotImplementedError, "processItem"


#####################################################################################
# Testing
#####################################################################################
import random

class Tester:

	def __init__( self, persistent_arg ):
		self.persistent_arg = persistent_arg

	def __call__( self, item ):
		# Do something interesting with item, using persistent_arg.
		time.sleep( random.uniform(0.0, 0.3) )


class TestWorker( ProgressBarWorker ):

	# items is a queue that will be destroyed as we progress.
	def __init__( self, items ):
		ProgressBarWorker.__init__( self )
		self.items = items

	def getNextItem( self ):
		# Pop an item off the queue.
		try:
			return self.items.pop()
		except IndexError:
			return None

	def processItem( self, item ):
		# Do something interesting with item.
		time.sleep( random.uniform(0.0, 1.0) )
		

def test():

	# The set of items to iterate over.  A bunch of letters & numbers in this case.
	items = ["a", "b", "c", "d"] + range(50)

	newlines = 0

	print "Testing single-threaded progress bar..."

	print "%d items..." % (len(items))
	t = Tester( "foo" )
	p = ProgressBar( items, t, newlines=newlines )
	p.start()

	print "0 items..."
	t = Tester( "foo" )
	p = ProgressBar( [], t, newlines=newlines )
	p.start()


	print "Testing multi-threaded progress bar..."
	threads = 5

	print "%d workers, %d items..." % (threads, len(items))
	workers = []
	queue = copy.copy( items ) # Make a copy so we don't consume the original.
	for i in range( threads ):
		worker = TestWorker( queue )
		workers.append( worker )
	p = ThreadedProgressBar( workers, len(queue), newlines=newlines )
	p.start()
	
	print "%d workers, 0 items..." % (threads)
	workers = []
	for i in range( threads ):
		worker = TestWorker( [] )
		workers.append( worker )
	p = ThreadedProgressBar( workers, 0, newlines=newlines )
	p.start()


	print "Testing broken progress bars (tracebacks expected)..."
	threads = 2

	print "Abstract worker..."
	workers = []
	for i in range( threads ):
		worker = ProgressBarWorker()
		workers.append( worker )
	p = ThreadedProgressBar( workers, len(items) )
	p.start()

	print "Non-worker..."
	workers = []
	for i in range( threads ):
		worker = Tester( items )
		workers.append( worker )
	try:
		p = ThreadedProgressBar( workers, len(items) )
		raise "Expected RuntimeError not encountered"
	except RuntimeError, e:
		print e

	print "No workers..."
	try:
		p = ThreadedProgressBar( [], len(items) )
		raise "Expected RuntimeError not encountered"
	except RuntimeError, e:
		print e


if __name__ == "__main__":
	test()
