from tokenizer import extract_tokens_from_story
from naive_bayes import NaiveBayes, Document
from collections import defaultdict
from random import shuffle
import math
import json

class Story:
    pass

def mock_stories(data):
    stories = []
    for d in data:
        st = Story()
        st.id = d['id']
        st.classification = d['classification']
        st.text = d['text']
        st.links = d['links']
        st.shareType = d['shareType']
        st.hasTaggedFriends = d['hasTaggedFriends']
        st.hasLocation = d['hasLocation']
        st.timestamp = d['timestamp']
        st.text = st.text.encode('utf-8')
        stories.append(st)
    return stories

data = raw_input()

stories = mock_stories(json.loads(data))
INITIAL_DOCUMENTS_SIZE = 50
DOCUMENTS_INCREASE_STEP = 50
N_TRIES_PER_STEP = 1

for n_stories in range(INITIAL_DOCUMENTS_SIZE,len(stories), DOCUMENTS_INCREASE_STEP):
    global_precision = defaultdict(lambda: 0)
    global_recall = defaultdict(lambda: 0)
    global_accuracy = 0
    global_count = 0
    global_kappa = 0
    for tries in range(0, N_TRIES_PER_STEP):
        confusion_matrix = defaultdict(lambda: defaultdict(lambda: 0))
        accuracy = 0
        shuffle(stories)

        documents = []
        test_data = []
        count_links = 0
        count_total = 0
        i = 0
        for story in stories:
            if i > n_stories:
                break
            i += 1
            story_tokens = extract_tokens_from_story(story)
            if len(story_tokens) < 5:
                continue
            best_count = max(story.classification.values())
            tag = max(story.classification, key=story.classification.get)
            count_total += 1
            if len(story.links):
                count_links += 1
            if len(documents) < n_stories*2.0/4:
                documents.append(Document(story_tokens, tag))
            else:
                test_data.append(Document(story_tokens, tag))
                test_data[len(test_data)-1].texto_completo = story.text

        naive_bayes = NaiveBayes()
        naive_bayes.train(documents)

        true_positives = defaultdict(lambda: 0)
        true_negatives = defaultdict(lambda: 0)
        false_positives = defaultdict(lambda: 0)
        false_negatives = defaultdict(lambda: 0)

        for document in test_data:
            chosen = [naive_bayes.classify(document.tokens)]
            confusion_matrix[document.tag][chosen[0]] += 1
            #print '<divisor>'
            #print chosen
            #print document.textoCompleto
            #print '</divisor>'
            if document.tag in chosen:
                accuracy += 1
            #else:
                #print '[WRONG] Deveria ser ' +  document.tag + ' mas foi ' + str(chosen)
            for tag in naive_bayes.tags:
                if document.tag == tag and tag in chosen:
                    true_positives[tag] += 1
                elif document.tag == tag and not tag in chosen:
                    false_negatives[tag] += 1
                elif document.tag != tag and not tag in chosen:
                    true_negatives[tag] += 1
                elif document.tag != tag and tag in chosen:
                    false_positives[tag] += 1
            
        n_test_documents = 1.0*len(test_data)
        global_count += 1
        for tag in naive_bayes.tags:
            if true_positives[tag] + false_positives[tag] == 0:
                precision = 1 # check corner cases
            else:
                precision = (true_positives[tag]) * 1.0 / (true_positives[tag] + false_positives[tag])
            if true_positives[tag] + false_negatives[tag] == 0:
                recall = 1 # check corner cases
            else:
                recall = (true_positives[tag]) * 1.0 / (true_positives[tag] + false_negatives[tag])
            if precision + recall != 0:
                f1 = 2 * precision * recall / (precision + recall)
            else:
                f1 = 0

            global_precision[tag] += precision
            global_recall[tag] += recall
            
            #print tag + ' TP: ' + str(true_positives[tag]) + ' / ' + str(total[tag]) + ' TN: ' + str(true_negatives[tag]) + ' / '  + str(nDocs - total[tag]) 
            #print tag + ': Precision: ' + str(precision),
            #print ' # Recall: ' + str(recall),   
            #print ' # F1: ' + str(2 * precision * recall / (precision + recall)) 
    
        accuracy = accuracy * 1.0/ n_test_documents
        global_accuracy += accuracy
        #print str(accuracy * 100)
        #print str(n_stories) + ' - Accuracy: ' + str(accuracy*100)
       
        expected_accuracy = 0
        total = 0
        for line in confusion_matrix:
            #for column in confusion_matrix:
            #    print '%5d' % confusion_matrix[line][column],
            #print
            sum_column = sum([confusion_matrix[l][line] for l in confusion_matrix])
            sum_line = sum(confusion_matrix[line].values())
            expected_accuracy += sum_column*sum_line
            total += sum_line
        
        expected_accuracy = expected_accuracy * 1.0 / (total ** 2)
        #print str(expected_accuracy * 100)

        kappa = (accuracy - expected_accuracy) / (1 - expected_accuracy)
        global_kappa += kappa
        #print kappa
    
    #print str(global_accuracay * 1.0 / global_count)
    print str(global_kappa * 1.0 / global_count)