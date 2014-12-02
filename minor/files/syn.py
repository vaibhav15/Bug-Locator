from wordnik import *
apiUrl = 'http://api.wordnik.com/v4'
apiKey = 'a9a16fe4bb2083d1c62019295ce0cad333beca48d6e22aa2e'
client = swagger.ApiClient(apiKey, apiUrl)


wordApi = WordApi.WordApi(client)
res = wordApi.getRelatedWords('first',relationshipTypes='synonym')
syn = res[0].words
for s in syn:
	print s

