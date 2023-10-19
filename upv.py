#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 11:52:43 2022

@author: hagar
"""

from pipelines.generalPipeline import general_pipe
from viruses.flu import flu
from pipelines.deNovo import de_novo
from viruses.polio import polio
from viruses.hiv import hiv
from viruses.hsv import hsv
from utils import utils, parse_gb_file, parse_input
from mutations import signatures
import os


SCRIPT_PATH = os.path.dirname(__file__) +'/'

if __name__ == "__main__":
    
    DEBUG = False
    
    reference, fastq, treads, flu_flag, de_novo_flag, polio_flag, cmv_flag, hiv_flag, \
        hsv_flag, gb_file, regions_file, mutations_flag, mini, \
            skip_spades, vcf, cnsThresh, multi_ref_flag = parse_input.parser()
    
    dirs=['BAM','QC','CNS','CNS_5','QC/depth', 'alignment'] if not hiv_flag else ['BAM','QC','CNS','QC/depth', 'alignment']
    
    if not mini:      
        utils.create_dirs(dirs) 
        if hiv_flag:
            reference = SCRIPT_PATH + "viruses/refs/K03455.1_HIV.fasta"
            vcf = True
        elif not reference:
            raise ValueError("reference sequence is required.")
        
        
            
        if not cnsThresh:
            cnsThresh = 0.6
        
        multi_ref_flag = True if multi_ref_flag or flu_flag else False
    
        if fastq and reference and not mini:
            if not fastq.endswith("/"):
                fastq = fastq+"/"
        
            
            if flu_flag:
                pipe = flu(reference,fastq)
            
            elif de_novo_flag:
                pipe = de_novo(reference,fastq) #temp comment
                if not skip_spades:
                    pipe.run_spades()
                pipe.run_blast()
                sample_ref = pipe.choose_reference_filter_contigs()
                pipe.import_references(sample_ref)
            
            elif polio_flag:
                pipe = polio(reference,fastq)
            
            elif hiv_flag:
                pipe = hiv(reference,fastq)
                
            elif hsv_flag:
                pipe = hsv(reference,fastq)
    
            else:
                pipe = general_pipe(reference,fastq)
            
            if polio_flag:
                # filter reads - keep only polio read 
                pipe.filter_not_polio()
                pipe.fastq = pipe.fastq + "polio_reads/"
                
                #run spades
                if not skip_spades:
                    pipe.run_spades()
        
            #mapping 
            pipe.bam(treads)
            
            
            if multi_ref_flag:    
                utils.split_bam("BAM/")
            
    
            if vcf:
                utils.create_dirs(["VCF"])
                pipe.variant_calling()
                
            pipe.cns_depth("BAM/","QC/depth/","CNS/","CNS_5/", cnsThresh) #temp comment
            
            
            if flu_flag:
                pipe.concat_samples()
                pipe.concat_segments()
            
            
            pipe.mafft(reference, "alignment/all_not_aligned.fasta", "alignment/all_aligned.fasta")
       
            if hiv_flag:
                pipe.excel_fasta("CNS/",hiv_flag)

            
            pipe.qc_report("BAM/", "QC/depth/", 'QC/QC_report') #temp comment
        

    if gb_file:
        parse_gb_file.parse(gb_file)
        regions_file = gb_file.replace(".gb", "_regions.csv")

    if mutations_flag or mini:
        if not gb_file and not regions_file:
            raise ValueError("gene bank file or regions file is required.")
        utils.create_dirs(["reports"])
        aligned = fastq if mini else "alignment/all_aligned.fasta" # if mini flag is on, user must insert an alignment file instead of fastq.
        signatures.run(aligned, regions_file, "reports/mutations.xlsx")
    
    