import json
with open('storiesJson.txt', 'r') as f:
	data = f.read()

stories = json.loads(data)

chosen = []

import unicodedata
i = 0
for story in stories:
	i += 1
	if i < 572:
		continue
	print str(i) + ') ',
	classification = max(story['classification'], key=story['classification'].get)
	print '---------------'
	print classification.encode('utf-8')
	print str(story['links'].encode('utf-8'))
	s = story['text']
	s = unicodedata.normalize('NFD', s)
	print str(s.encode('ascii', 'ignore'))

	c = raw_input()
	if c == 'y':
		story['classification'] = { classification: 1 }
		continue
	if c == 'q':
		break
	classesList = {
		'p': "Politica / Economia", 
		'a': "Propaganda", 
		'f': "Filme", 
		'h': "Humor", 
		'c': "Celebridade", 
		's': "Esporte", 
		'pes': "Pessoal",
		't': "Turismo",
		'ct': "Ciencia / Tecnologia",
		'min': "Minorias",
		'e': "Educacao",
		'n': "Noticias",
		'b': "Bebes / Animais",
		'm': "Medicina",
		'o': "Outros"
	}
	if c in classesList:
		story['classification'] = { classesList[c]: 1 }


with open('storiesJsonParsed.txt', 'w') as f:
	f.write(json.dumps(stories))

