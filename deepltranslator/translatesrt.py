import sys
arguments = sys.argv
srt_original = '' #origninal  file
srt_target = '' #file to write output to
source_lang = '' #original language
target_lang = '' #output language

#get variables from command line
for i in range(len(arguments)):
    if arguments[i] == '-in':
        srt_original = arguments[i + 1]
    elif arguments[i] == '-out':
        srt_target = arguments[i + 1]
    elif arguments[i] == '-source':
        source_lang = arguments[i + 1]
    elif arguments[i] == '-target':
        target_lang = arguments[ i + 1]


#for testing purposes gave the variables values
srt_original = 'Dunkirk.2017.720p.BluRay.x264-SPARKS.srt'
srt_target = 'fullTranslationInSpanish.srt'
source_lang = 'EN'
target_lang = 'ES'


import pysrt
subs = pysrt.open(srt_original) #holds the srt inpur file

import deepl

words_per_screen = [] #holds number of words on that frame of the srt file before translation
for i in range(len(subs)): # fills words per screen with the number of words per frame
    words = subs[i].text.split(' ')
    for word in range(len(words)):
        words[word] = words[word].replace('\n', ' ')
        split = words[word].split(' ')
        if len(split) > 1:
            words[word] = split[0]
            words.insert(word + 1, split[1])
    words_per_screen.append(len(words))

# in order to always pass complete sentences into deepl I iterate through the text of each frame until the
# frames text ends with a period. Cases with question marks and exclaimation points are just includes in the blocks and not treated
#by the program as individual sentences. This doesn't matter because deepl will still translate them and it will end up the same as if they
# were considered individual sentences.

class senetnce_to_be_translated(): #wrapper for sentences to be translated
    def __init__(self, text, startFrame, endFrame):
        self.text = text #the text of the complete sentence
        self.startFrame = startFrame #the frame on which the sentence started
        self.endFrame = endFrame # the frame in which the senetence ended



sentences = [] #holds sentence_to_be_translated objects
sub = 1

sentences.append(senetnce_to_be_translated(subs[0].text, 0, 0)) #do first and last seprately since they seem to hold a different type of information

while sub < len(subs) - 1: #chunks sentences from period to period
    is_sentence = False # becomes true when the subtitle is a whole sentence
    to_be_translated = ''
    i = 0
    while not is_sentence:
        print(subs[sub])
        print(len(subs))
        print(sub + i)
        print(' ')
        if subs[sub + i].text[len(subs[sub + i].text) - 1] != '.' and ' ': #add a space to the end of the line if it does not already have one or end in a period
            subs[sub + i].text += ' '
        to_be_translated += subs[sub + i].text #add the newline to the text we had before
        broken_into_sentences = to_be_translated.split('.')
        if broken_into_sentences[- 1] == '': # if it ended with a period
            sentences.append(senetnce_to_be_translated(to_be_translated, sub, sub + i)) #save the text that makes a complete sentence and the line where it starts and ends
            is_sentence = True
            sub = sub + i + 1
        i += 1

sentences.append(senetnce_to_be_translated(subs[len(subs) - 1].text, len(subs) - 1, len(subs) - 1)) #last frame

for sentence in sentences:#for each complete sentence
    sentence.text = sentence.text.split(' ')
    for word in range(len(sentence.text)):
        sentence.text[word] = sentence.text[word].replace('\n', ' ')
    xyz = ''
    for word in sentence.text:
        xyz += word
        xyz += ' '
    sentence.text = xyz
    if sentence.startFrame == sentence.endFrame: # if it exists on one frame translate it and save the translated text
        translated, extra_info = deepl.translate(sentence.text, source=source_lang, target=target_lang)
        print(len(translated))
        subs[sentence.startFrame].text = translated
    else:
        before_translated_size = len(sentence.text.split(' ')) #the number of words in the complete sentence
        translated, extra_info = deepl.translate(sentence.text, source=source_lang, target=target_lang)
        sentence.text = translated #translate the text
        #next chunk of code changes the amount of words we will have on ech frame after if the translation has a differnet number of words than the original text
        difference = len(sentence.text.split(' ')) - before_translated_size
        print(sentence.text.split(' '))
        print(len(sentence.text.split(' ')), before_translated_size, difference)
        frame_counter = sentence.startFrame
        for qwer in range(sentence.endFrame - sentence.startFrame + 1):
            print(words_per_screen[qwer + sentence.startFrame])
        print(' ')
        while difference != 0:
            if difference > 0:
                words_per_screen[frame_counter] += 1
                difference -= 1
            elif difference < 0:
                words_per_screen[frame_counter] -= 1
                difference +=1
            frame_counter += 1
            if frame_counter > sentence.endFrame:
                frame_counter = sentence.startFrame

        for qwer in range(sentence.endFrame - sentence.startFrame + 1):
            print(words_per_screen[qwer + sentence.startFrame])


        sentence.text = sentence.text.split(' ') #split the text into words

        j = 0 #counter since the wifi is down at the moment and I cannot search up a method for returning the index of a list item
        for i in sentence.text: # if the word has a newline character replace it with a space
            x = i
            i = i.replace('\n', ' ')
            if x != i:
                new_words = i.split(' ')
                sentence.text[j] = new_words[0]
                sentence.text.insert(j +1, new_words[1])
            j += 1


        #go back through and put the transated complete sentnce back into the frames of the srt fil, it puts the number
        # of words on each frame based on the variable words_per_screen which had just been adjusted for differences in the length of the translation
        previous_mark = 0
        for i in range(sentence.endFrame - sentence.startFrame + 1):
            if i + sentence.startFrame == sentence.endFrame:
                subs[sentence.startFrame + i].text = sentence.text[previous_mark: 1 + previous_mark + words_per_screen[
                    sentence.startFrame + i]]
            else:
                subs[sentence.startFrame + i].text = sentence.text[previous_mark: previous_mark + words_per_screen[sentence.startFrame + i]]
            text_put_back_together = ''
            for word in subs[sentence.startFrame + i].text: # puts back together the separated words
                text_put_back_together += word
                text_put_back_together += ' '
            subs[sentence.startFrame + i].text = text_put_back_together
            previous_mark += words_per_screen[sentence.startFrame + i]



subs.save(srt_target, encoding='utf-8') #save the new srt file

