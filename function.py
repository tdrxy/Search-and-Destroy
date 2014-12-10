#!/usr/bin/python 

import hashlib
import sys
import errno
import os
import fcntl
import termios
import struct
import time


######
#
#
#	Finding duplicates /w md5 
#
#
#####

#pretty progress bar
################################
def bold(msg):
	return u'\033[1m%s\033[0m' % msg

def progress(current, total):
	prefix = '%d / %d' % (current, total)
	bar_start = ' ['
	bar_end = '] '

	bar_size = COLS - len(prefix + bar_start + bar_end)
	amount = int(current / (total / float(bar_size)))
	remain = bar_size - amount

	bar = 'X' * amount + ' ' * remain
	return bold(prefix) + bar_start + bar + bar_end

def status_bar(status, goal):
	sys.stdout.write(progress(status, goal) + '\r')
	sys.stdout.flush()

################################
def checksum_md5(filename):
	try:
		md5 = hashlib.md5()
		with open(filename, 'rb') as f:
			for chunk in iter(lambda: f.read(128*md5.block_size), b''):
				md5.update(chunk)
		return md5.digest()
	except Exception as a:
		return -1

def delete_duplicate(original, name, prompt):
	
	deleted = 0
	duplicate = name
	if prompt:
		next = False
		while not next:
			answer = raw_input("DUPLICATE of ["+ original+"] - DELETE [" + name + "]?(y/n) ")
			if answer == "y":
				deleted = os.path.getsize(duplicate)
				os.remove(duplicate)
				next = True
			elif answer == "n":
				next = True
			else:
				next = False
	else:
		deleted = os.path.getsize(duplicate)
		os.remove(duplicate)
		print "DUPLICATE of ["+ original+"] - [" + name + "] - DELETED "

	return deleted


def make_hashtable(files):

	hashtable = {}
	print "Making hashtable.."
	status_bar(len(hashtable), len(files))
	for f in files:
		hashtable[f] = checksum_md5(f)
		status_bar(len(hashtable), len(files))
	sys.stdout.write('\n')

	return hashtable

def get_filename(path):
	return path.split('/')[-1]

def search_and_destroy(filepaths, hashtable):
	
	deleted_bytes = 0
	
	for original_path in filepaths:

		try:
		 	a_md5 = hashtable.get(original_path)

		 	for other_path in filepaths:
		 		b_md5 = hashtable.get(other_path)

		 		if original_path != other_path and a_md5 == b_md5 and a_md5 != -1 and b_md5 != -1:
		 			
		 			#Are the names equal but the paths different? -> Duplicate, no prompt.
		 			if(get_filename(original_path) == get_filename(other_path)):
		 				deleted_bytes += delete_duplicate(original_path, other_path, prompt=False)
		 			#Are you sure they are duplicate? Uncertainty requires prompt = True
		 			else:
		 				deleted_bytes += delete_duplicate(original_path, other_path, prompt=False)

		except IOError as exc:
		 	pass
		except Exception as a:
		 	pass

	return deleted_bytes


##############
#   PATH
path = '/Users/thomasdierckx/Desktop/'
extensions = ["jpg", "jpeg", "png", "img", "img", "wav", "mp3", "mov", "vid", "m4a"]
#
###############

COLS = struct.unpack('hh',  fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, '1234'))[1]
   
print "___________________________________________________________"
print "Working dir: "+ path

#Get subdirectories
directories = []
for directory in [x[0] for x in os.walk(path)]:
	if directory[-1] != "/":
		directory = directory +"/"
		directories.append(directory)
	else:
		directories.append(directory)

#Get all files in all directories/subdirectories
files = []
for directory in directories:
	names = os.listdir(directory)
	files += [directory+name for name in names]

files = [f for f in files if f.split('.')[-1].lower() in extensions]
hashtable = make_hashtable(files)
deleted_bytes = search_and_destroy(files, hashtable)



if deleted_bytes == 0:
	print bold("No Duplicates.")
else:
	print bold("Freed "+str(deleted_bytes/(1024*1024))+"Mb.")


print "___________________________________________________________"

