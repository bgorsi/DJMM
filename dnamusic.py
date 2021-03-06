#!/usr/bin/env python3

#filename: dnamusic_pca.py
#owner: Bushra Gorsi & Stella Paffenholz
#output: Generate a PCA plot from a dictionary containing counts of amino acids and DNA bases from a dna string generated from a song of a specific genre



#========================================================================
#                       Part1: count aa and nt
#=========================================================================

#open fasta file and create dictionaries to count aa and nt

DNA_fasta_sequences = open ("sequences.fa" , "r")
nucleotide_dict = {}
nucleotide_comp = {}
amino_acid_comp ={}
seq_id = ''
final_dict ={}

#create dictionary of sequence ID and sequence
for line in DNA_fasta_sequences:
    line = line.rstrip()
    if line.startswith('>'):
        for (seq_id, year, genre) in re.findall(r'>(\S+)\s\w+=(\d+)\s\w+=(\w+)', line):
            nucleotide_dict[seq_id] = ''
    else:
        if seq_id in nucleotide_dict:
            nucleotide_dict[seq_id] += line
        else:
            nucleotide_dict[seq_id] = line

#create a dictioary with nucleotide count
for seq_id in nucleotide_dict:
    sequence = nucleotide_dict[seq_id]
    a_count = sequence.count('A')
    c_count = sequence.count('C')
    g_count = sequence.count('G')
    t_count = sequence.count('T')
    nucleotide_comp[seq_id] = {'nucA':a_count,'nucC':c_count,'nucG':g_count,'nucT':t_count}


#Calculate amino acid composition and store them in a dictionary
from Bio.Seq import Seq
from Bio.SeqUtils.ProtParam import ProteinAnalysis

for seq_id in nucleotide_dict:
    sequence = nucleotide_dict[seq_id]
    seqobj = Seq(sequence)
    seq_str=str(seqobj)
    protein = seqobj.translate()
    prot_str = str(protein)
    amino_acid_comp[seq_id] = prot_str

for seq_id in amino_acid_comp:
    prot_str = amino_acid_comp[seq_id]
    prot_obj = ProteinAnalysis(prot_str)
    count_aa = prot_obj.count_amino_acids()
    amino_acid_comp[seq_id] = count_aa

print(amino_acid_comp)

#extract genre and store it in a dictionary
import re
DNA_fasta_sequences = open ("sequences.fa" , "r")

genre_dict = {}

for line in DNA_fasta_sequences:
    line = line.rstrip()
    if line.startswith('>'):
        for (seq_id, year, genre) in re.findall(r'>(\S+)\s\w+=(\d+)\s\w+=(\w+)', line):
            genre_dict[seq_id] = genre

#========================================================================
#                           Part2: create a PCA
#=========================================================================

#Generate a dataframe from the dictionary containing the amino acid, nucleotide composition and genre
import pandas as pd
import numpy as np

aa_df = pd.DataFrame.from_dict(amino_acid_comp)
nt_df = pd.DataFrame.from_dict(nucleotide_comp)
genre_df = pd.Series(genre_dict).to_frame().transpose()
genre_df = genre_df.rename({0: 'genre'}, axis='index')

seq_df = pd.concat([aa_df, nt_df, genre_df]).transpose()
print(seq_df)

#Standardize the data onto unit scale (mean = 0 and variance = 1)
from sklearn.preprocessing import StandardScaler

#seperating out the counts of amino acid and DNA bases (= column headers, without genre)
features = list(seq_df)
print(features)
features.remove('genre')

x = seq_df.loc[:, features].values
print(x)

#separating out the genres
y = seq_df.loc[:,['genre']].values
print(y)

#standardizing the features
x2 = StandardScaler().fit_transform(x)
print(x2)


# calculate principal components and create dataframe of genre with PC1 and PC2 values
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
pca_components = pca.fit_transform(x2)
print(pca_components)


principal_df = pd.DataFrame(data = pca_components
             , columns = ['PC1', 'PC2'], index = seq_df.index)
print(principal_df)

final_df = pd.concat([principal_df, seq_df[['genre']]], axis = 'columns')
print(final_df)

#PCA plotting
import matplotlib.pyplot as plt

fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1)
ax.set_xlabel('PC1', fontsize = 15)
ax.set_ylabel('PC2', fontsize = 15)
ax.set_title('PCA', fontsize = 20)

targets = ['rock', 'classic', 'dance']
colors = ['r', 'g', 'b']

for genre, color in zip(targets,colors):
    indicesToKeep = final_df['genre'] == genre
    ax.scatter(final_df.loc[indicesToKeep, 'PC1']
               , final_df.loc[indicesToKeep, 'PC2']
               , c = color
               , s = 50)
ax.legend(targets)
ax.grid()
