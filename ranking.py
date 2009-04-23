import twokenize,util,re,bigrams


#norm_re = re.compile(r'[^a-zA-Z0-9_@]')
#norm_re = re.compile(r'^[^a-zA-Z0-9_@]+')
#def tok_norm(tok):
#  s = norm_re.subn('',tok)[0]
#  if len(s)>=1: return s
#  return tok

def rank_and_filter(linkedcorpus, background_model, q, type='bigram'):
  #q_toks = [tok_norm(t) for t in twokenize.tokenize(q)]
  q_toks = bigrams.tokenize_and_clean(q, alignments=False)
  q_toks_set = set(q_toks)
  stopwords = bigrams.stopwords - q_toks_set
  for ratio,ngram in bigrams.compare_models(linkedcorpus.model, background_model,type,3):
    norm_ngram = [tok_norm(t) for t in ngram]
    if set(norm_ngram) <= bigrams.stopwords:
      print "reject stopwords", norm_ngram
      continue
    if set(norm_ngram) <= q_toks_set:
      print "reject query-subsumed", norm_ngram
      continue
    #if len(linkedcorpus.index[ngram]) <= 2: continue
    if len(norm_ngram)>1 and norm_ngram[-1] in stopwords: 
      print "reject effective n-1gram", norm_ngram
      continue
    topic_label = " ".join(ngram)
    tweets = linkedcorpus.index[ngram]
    yield ngram, topic_label, tweets

def prebaked_iter(filename):
  for line in util.counter(open(filename)):
    yield simplejson.loads(line)

if __name__=='__main__':
  import simplejson
  import sys
  import linkedcorpus
  import util; util.fix_stdio()

  q = sys.argv[1]         # coachella
  prebaked = sys.argv[2]  # data/c500

  lc = linkedcorpus.LinkedCorpus()
  for tweet in prebaked_iter(prebaked):
    lc.add_tweet(tweet)

  import lang_model, ansi
  #background_model = lang_model.MemcacheLM()
  background_model = lang_model.TokyoLM(readonly=True)
  for topic_ngram, topic_label, tweets in rank_and_filter(lc, background_model, q, type='bigram'):
    print ansi.color(topic_label,'bold','blue'), "(%s)" % len(tweets)
    #for tweet in tweets: print "",tweet['text']

