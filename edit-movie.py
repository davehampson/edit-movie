
import json, os, shutil, socket, subprocess, sys

def Main():
	scriptDir = os.path.dirname(os.path.realpath(__file__))
	
	if len(sys.argv) < 2:
		print('SYNTAX: {0} [JSON edit list]'.format(sys.argv[0]))
		return 1
	
	file = open(sys.argv[1])
	jsonData = json.load(file)
	file.close()
	
	ffmpeg = os.path.join(scriptDir, 'ffmpeg.exe')
	inputMovie = jsonData.get('inputMovie')
	inputStub = os.path.splitext(os.path.basename(inputMovie))[0].lower()
	tmpDir = jsonData.get('tmpDir')
	clips = jsonData.get('clips')
	
	try:
		os.makedirs(tmpDir)
	except OSError:
		pass
	
	version = 11
	tmpNameList = []
	for clip in clips:
		start = StampToSeconds(clip.get('start'))
		end   = StampToSeconds(clip.get('end'))
		clipLength = end - start
		if clipLength <= 0.0:
			print('ERROR: Clip length is {0}'.format(clipLength))
			return 1
			
		comment = clip.get('comment')
		print('Clip: {0}, {1}, "{2}"'.format(start, end, comment))
		
		clipName = 'clip-' + inputStub + '-v{0}-s{1:04d}-e{2:04d}'.format(version, int(start), int(end))
		clipName += '.mp4'
		clipName = os.path.join(tmpDir, clipName)

		approx = start - 1.0
		if approx < 0.0:
			approx = 0.0
		
		seek = start - approx
			
		done = os.path.isfile(clipName)
		
		if done:
			print('"' + clipName + '" already exists')
		
		if not done:
			args = [ffmpeg]
			args += ['-ss', str(approx)] # Approximate seek
			args += ['-i', inputMovie]
			args += ['-ss', str(seek)] # More accurate seek
			args += ['-t', str(clipLength)]
			args += ['-c:v', 'libx264',      '-b:v', '1000k']
			args += ['-c:a', 'libvo_aacenc', '-b:a', '192k']
			args += ['-y', clipName]
			retcode = RunCommand(args)
			if retcode != 0:
				os.unlink(clipName)
				return 1
		
		tmpNameList.append(clipName)
	
	listName = 'mylist.txt'
	list = open(listName, 'w')
	for clip in tmpNameList:
		list.write("file '" + clip + "'\n")
	list.close()
	
	name = socket.gethostname().lower()
	# Encode to a temporary file:
	tempMovieName = 'temp-' + name + '.mp4'
	args = [ffmpeg, '-f', 'concat', '-i', listName]
	args += ['-c', 'copy']
	args += ['-y', tempMovieName]
	RunCommand(args)
	
	# Copy to real filename:
	outName = 'output-' + name + '.mp4'
	try:
		os.unlink(outName)
	except OSError:
		pass
	shutil.move(tempMovieName, outName)
	
def StampToSeconds(stamp):
	hours, minutes, seconds = (['0', '0'] + stamp.split(':'))[-3:]
	h = int(hours)
	m = int(minutes)
	s = float(seconds)
	total = float(h) * 3600.0 + float(m) * 60.0 + s
	return total

def RunCommand(args, cwd = None):
	if cwd != None:
		print('RunCommand: ' + subprocess.list2cmdline(args) + ' in ' + cwd)
	else:
		print('RunCommand: ' + subprocess.list2cmdline(args))
	return subprocess.Popen(args, cwd = cwd).wait()
	
if __name__ == '__main__':
	exit(Main())
