import requests
import os
import spacy
from itertools import product
from bs4 import BeautifulSoup


SV = "ROOT(nsubj)"
SVO = "ROOT(nsubj+obj)"
SVOO = "ROOT(nsubj+obj+obl)"
COP = "ROOT(nsubj+cop)"

nlp = spacy.load("pl_core_news_lg")

def process_rule(rule):
  head = ""
  tail = None
  ind = 0
  while ind < len(rule) and rule[ind] != "(":
    head += rule[ind]
    ind += 1
  tail = rule[ind:]
  tail = tail.strip("()")
  return head, tail

def prune_dep(dep, strict):
  if strict:
    return dep
  else:
    return dep.split(":", 1)[0]

def process_tree(toks, rule, strict = False):
  rule_head, rule_tail = process_rule(rule)
  rule_head = prune_dep(rule_head, strict)
  tail_deps = [prune_dep(dep, strict) for dep in rule_tail.split("+")]
  matches = []
  for tok in toks:
    if prune_dep(tok.dep_, strict) == rule_head:
      match = (tok, tok.dep_)
      match_dic = {dep: [] for dep in tail_deps}
      children = tok.children
      for child in children:
        if prune_dep(child.dep_, strict) in match_dic:
          match_dic[prune_dep(child.dep_, strict)].append((child, child.dep_))
      combinations = list(product([match], *[v for k, v in match_dic.items()]))
      sorted_combinations = [sorted(c, key = lambda c:c[0].i) for c in combinations]
      matches.extend(sorted_combinations)
  return matches

def lemmatize_matches(sent_matches):
  lemmatized_matches = []
  for match in sent_matches:
    lemmatized_match = [] 
    for tok in match:
      lemmatized_match.append((tok[0].lemma_, tok[1]))
    lemmatized_matches.append(tuple(lemmatized_match))
  return lemmatized_matches

url = "https://pl.wikipedia.org/wiki/Lew_afrykański"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
paragraphs = soup.find_all("p")
paragraph_texts = [p.text for p in paragraphs if p.text != ""]
full_text = "\n".join(paragraph_texts)
doc = nlp(full_text)

for s in doc.sents:
  matches = process_tree(s, COP)
  lemmatized = lemmatize_matches(matches)
  if lemmatized != []:
    for match in lemmatized:
      if ("lew", "nsubj") in match:
        print(match)

for s in doc.sents:
  matches = process_tree(s, SVO)
  lemmatized = lemmatize_matches(matches)
  if lemmatized != []:
    for match in lemmatized:
      if ("lew", "nsubj") in match:
        print(match)


