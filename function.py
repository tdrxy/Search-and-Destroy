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
##########

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

def checksum_md5(filename):
	try:
		md5 = hashlib.md5()
		with open(filename, 'rb') as f:
			for chunk in iter(lambda: f.read(128*md5.block_size), b''):
				md5.update(chunk)
		return md5.digest()
	except:
		return -1
###########################
def delete_duplicate(original, path, name):
	
	deleted = 0
	duplicate = path+name
	next = False
	while not next:
		answer = raw_input("DUPLICATE of ["+ original+"] - DELETE [" + name + "]?(y/n) ")
		if answer == "y":
			deleted = os.path.getsize(duplicate)
			#files.remove(name)
			os.remove(duplicate)
			next = True
		elif answer == "n":
			next = True
		else:
			next = False
	return deleted


def status_bar(status, goal):
	sys.stdout.write(progress(status, goal) + '\r')
	sys.stdout.flush()

def make_hashtable(files):

	hashtable = {}
	print "Making hashtable.."
	status_bar(len(hashtable), len(files)-1)
	for f in files:
		hashtable[f] = checksum_md5(path+f)
		status_bar(len(hashtable)-1, len(files)-1)
	sys.stdout.write('\n')

	return hashtable



def search_and_destroy(files, hashtable):
	deleted_bytes = 0
	for original in files:
		#print files
		try:
			
			a_filepath = path+original
			a_md5 = hashtable.get(original)

			for other_name in files:
				
				b_filepath = path+other_name
				b_md5 = hashtable.get(other_name)

				if a_filepath != b_filepath and a_md5 == b_md5 and a_md5 != -1 and b_md5 != -1:
					deleted_bytes += delete_duplicate(original, path, other_name)
					

		except IOError as exc:
			print exc
			#pass
		except:
			pass

		files.remove(original)
	return deleted_bytes


COLS = struct.unpack('hh',  fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, '1234'))[1]
path = '/Users/thomasdierckx/Documents/scripts/'   
print "___________________________________________________________"
print "Working dir: "+ path

files = os.listdir(path)
hashtable = make_hashtable(files)
deleted_bytes = search_and_destroy(files, hashtable)

if deleted_bytes == 0:
	print bold("No Duplicates.")
else:
	print bold("Freed "+str(deleted_bytes/1024)+"Kb of "+ str(os.path.getsize(path)) +"Kb.")


print "___________________________________________________________"

