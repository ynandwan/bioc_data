
import sys 
sys.path.append('../PyBioC/src')
import copy
import pickle
from bioc import BioCReader
from bioc import BioCWriter
from os import curdir, sep 
from nltk.tokenize import wordpunct_tokenize
from nltk import PorterStemmer

from bioc import BioCAnnotation
import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--input_file',
                    help="xml data path ", type=str)

parser.add_argument('--dtd_file',
                    help="DTD file", type=str, default  = 'BioC.dtd')

parser.add_argument('--output_file',
                    help="output file name", type=str, default  = 'output.pkl')



args = parser.parse_args()    
#test_file = '../../biocreative-v-cdr/original-data/devel/CDR_DevelopmentSet.BioC.xml'
#dtd_file = '../../jointRN/data/bioc/BioC.dtd'


def annotate_passage(passage,ID = 'yatin'):
    poff = int(passage.offset)
    text = passage.text
    info_list =[]
    for annot in passage.annotations:
        atype = annot.infons['type']
        amesh = annot.infons['MESH']
        for location in annot.locations:
            info_list.append((int(annot.locations[0].offset)-poff, int(annot.locations[0].length),atype,amesh, annot.text))
    #
    s = copy.deepcopy(text)
    info_list.sort(key=lambda x: x[0], reverse=True)
    for (i,info) in enumerate(info_list):
        s = s[:info[0]] + ' ' + ID+str(i) + ' ' +s[info[0]+info[1]:]
    #
    tokens = wordpunct_tokenize(s)
    type_tags = [['O']]*len(tokens)
    mesh_tags = [['O']] * len(tokens)
    for i,token in enumerate(tokens):
        if ID in token:
            ind = int(token[len(ID):])
            info = info_list[ind]
            this_tokens = wordpunct_tokenize(info[4])
            this_type = ['I-'+info[2]]*len(this_tokens)
            this_mesh = ['I-'+info[3]]*len(this_tokens)
            this_type[0] = 'B-'+info[2]
            this_mesh[0] = 'B-'+info[3]
            type_tags[i] = this_type
            mesh_tags[i] = this_mesh
            tokens[i] = this_tokens 
        else:
            tokens[i] = [token]
    #
    #now we have a list of list that we need to flatten
    flat_tokens = [item for sublist in tokens for item in sublist]
    flat_types = [item for sublist in type_tags  for item in sublist]
    flat_mesh = [item for sublist in mesh_tags for item in sublist]
    return list(map(list,zip(flat_tokens,flat_types,flat_mesh)))


bioc_reader = BioCReader(args.input_file, dtd_valid_file=args.dtd_file)
bioc_reader.read()

documents = bioc_reader.collection.documents

annotated_sentences = []
for document in documents:
    for passage in document:
        annotated_sentences.append(annotate_passage(passage))


pickle.dump(annotated_sentences,file=open(args.output_file,'wb'))
fh = open(args.output_file+'_.txt','w')
yaml.dump(annotated_sentences,stream=fh)
fh.close()




""""
import pickle
import yaml
train_data = pickle.load(open('../data/CDR_TrainingSet.BioC.pkl','rb'))
train_data[0]
type2mesh = {}
anamoly = []
for sen in train_data:
    for token, ttype,mesh in sen:
        if ttype in type2mesh:
            type2mesh[ttype].add(mesh)
        else:
            type2mesh[ttype] = set([mesh])
        #
        if mesh in ['D','0','2','3','6','I','-']:
            anamoly.append((token,ttype,mesh))

type2mesh
type2mesh.keys()
map(len,type2mesh)
list(map(len,type2mesh))
type2mesh['B-Chemical']
""""
