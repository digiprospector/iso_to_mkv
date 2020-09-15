#!/usr/bin/python3

import os

def conv(iso_file, mkv_file):
	cmd = "ffmpeg -y -analyzeduration 1000M -probesize 1000M -i {} -c:v libx265 -preset fast -crf 20 -deinterlace -c:a copy -map 0:v:0 -map 0:a:0 -map 0:a:1 {}".format(iso_file, mkv_file)
	print(cmd)
	os.system(cmd)

def time_str2ms(time_str):
	hms, ms = time_str.split('.')
	h, m, s = hms.split(':')
	#print('h:{} m:{} s:{} ms:{}'.format(h, m, s, ms))
	return 1000*(3600*int(h) + 60*int(m) + int(s)) + int(ms)

def time_ms2str(time_ms):
	ms = time_ms % 1000
	hms = int(time_ms / 1000)
	s = hms % 60
	hm = int(hms / 60)
	m = hm % 60
	h = int(hm / 60)
	return "{:02d}:{:02d}:{:02d}.{:03d}".format(h, m, s, ms)

def cut(iso_file, mkv_file):
	#get chapter information
	cmd = "mount -t iso9660 -o loop {} dvd".format(iso_file)
	print(cmd)
	os.system(cmd)

	cmd = "mplayer -vo null -ao null -frames 0 -identify dvd/video_ts/video_ts.ifo "
	print(cmd)
	stream = os.popen(cmd)
	output = stream.read()
	for line in output.split('\n'):
		#print(line)
		if line.startswith("CHAPTERS"):
			chapters_start_time_str = line[len("CHAPTERS: "):-1].split(',')
			print(chapters_start_time_str)
			for i, t in enumerate(chapters_start_time_str):
				#add 20s to skip the head
				nt = time_ms2str(time_str2ms(t)+20000)
				print("{}+20s={}".format(t, nt))
				if 0 == i:
					chapter_start = nt
				else:
					chapter_end = nt
					duration = time_ms2str(time_str2ms(chapter_end) - time_str2ms(chapter_start))
					cmd = "ffmpeg -ss {} -i {} -to {} -c copy {}".format(chapter_start, mkv_file, duration, mkv_file[:-3] + '{}'.format(i) + ".mkv")
					print(cmd)
					os.system(cmd)
					chapter_start = chapter_end
			cmd = "ffmpeg -ss {} -i {} -c copy {}".format(chapter_start, mkv_file, mkv_file[:-3] + '{}'.format(i+1) + ".mkv")
			print(cmd)
			os.system(cmd)

	cmd = "umount dvd"
	print(cmd)
	os.system(cmd)

def main():
	for i in range(1,19):
		iso_file = "爱探险的朵拉{:02d}.iso".format(i)
		mkv_file = iso_file.replace('.iso', '.mkv')
		conv(iso_file, mkv_file)
	for i in range(1,19):
		iso_file = "爱探险的朵拉{:02d}.iso".format(i)
		mkv_file = iso_file.replace('.iso', '.mkv')
		cut(iso_file, mkv_file)

if __name__ == "__main__":
	main()
