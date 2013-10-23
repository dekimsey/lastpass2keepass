import sys
import xml.etree.ElementTree as ElementTree
import base64
print sys.argv
old, new = sys.argv[1:3]

keepass = ElementTree.parse(old)
lastpass = ElementTree.parse(new)
keepass_groups = dict((x.find("Name").text, x) for x in keepass.findall(".//Group"))
kp_parent_map = dict((c, p) for p in keepass.getiterator() for c in p)
lp_parent_map = dict((c, p) for p in lastpass.getiterator() for c in p)

def get_string(node, name):
	return [x.find("Value").text for x in node.findall("./String") if x.find("Key").text == name].pop()

def search(entry, group, show=False):
	possibles = []
	needle_uuid = entry.find("UUID").text
	needle_title = get_string(entry, "Title")
	needle_username = get_string(entry, "UserName")
	needle_url = get_string(entry, "URL")
	if needle_url == "http://" or needle_url == "https://":
		needle_url = None
	for e in group.findall("Entry"):
		try:
			uuid = e.find("UUID").text
			title = get_string(e, "Title")
			username = get_string(e, "UserName")
			url = get_string(e, "URL")
			if show and title == "amazon":
				print needle_title, needle_username, needle_url, needle_uuid
				print title, username, url, uuid
			if needle_uuid == uuid:
				return e
			if needle_title == title and needle_username == username and (needle_url == url or (url and (needle_url == "http://" + url or needle_url == "https://" + url))):
				if show:
					print "Got it"
				possibles.append(entry)
		except IndexError:
			# Ignoring
			pass
	if len(possibles) > 1:
		print "wtf? Node entry isn't unique"
		for k in possibles:
			print get_string(k, "Title"), get_string(k, "URL"), k.find("UUID").text
	if len(possibles) >= 1:
		return possibles.pop()
	return None

import itertools
def sync(lastpass_grp, keepass_grp):
	for lp_entry in lastpass_grp.findall("Entry"):#), sorted(keepass_grp.findall("Entry"))):
		show = False
		if lastpass_grp.find("Name").text == "Shopping":
			show = True
			
		match = search(lp_entry, keepass_grp, show)
		if match is None:
			lp_parent_map[lp_entry].remove(lp_entry)
			keepass_grp.append(lp_entry)
		else:
			if get_string(lp_entry, "Password") == get_string(match, "Password") and get_string(lp_entry, "Notes") == get_string(match, "Notes"):
				pass
			else:
				lp_parent_map[lp_entry].remove(lp_entry)
				keepass_grp.append(lp_entry)
				
for group in lastpass.findall(".//Group"):
	group_name = group.find("Name").text
	if group_name in keepass_groups:
		print "Matching group for", group_name
		group.find("UUID").text = keepass_groups[group_name].find("UUID").text
		sync(group, keepass_groups[group_name])
	else:
		print "No match for group, moving", group_name
		lp_parent_map[group].remove(group)
		keepass.find("./Root/Group").append(group)

keepass_groups = dict((x.find("Name").text, x) for x in keepass.findall(".//Group"))
kp_parent_map = dict((c, p) for p in keepass.getiterator() for c in p)
lp_parent_map = dict((c, p) for p in lastpass.getiterator() for c in p)

uniq={}
parent_map = dict((c, p) for p in lastpass.getiterator() for c in p)

print [x.find("Name").text for x in keepass.findall("./Root/Group/Group")]

with open("/cygdrive/f/merge.xml", "wb") as fh:
	keepass.write(fh, encoding='utf-8')
