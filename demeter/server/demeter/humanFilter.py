import json
with open('storiesJson.txt', 'r') as f:
	data = f.read()

stories = json.loads(data)

chosen = []

for story in stories:
	classification = max(story['classification'], key=story['classification'].get)
	print '---------------'
	print classification.encode('utf-8')
	print str(story['text'].encode('utf-8'))
	c = raw_input()
	if c == 'y':
		chosen.append(story)
	elif c == 'q':
		break


with open('storiesJsonParsed.txt', 'w') as f:
	f.write(json.dumps(chosen))

