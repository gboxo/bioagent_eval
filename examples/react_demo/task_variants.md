

## Descriptions


```
I want to create an eval for LLMs ability to use common Bioinformatic and Protein Egineering tools in Agentic workflows.

The requirements are, the task should be:
* Complex requiring around 4 steps 2 of which being non trivial
* Self contained
* Be deterministic, there is only a single answer that is not affected by decissions such as for example hyper parameters when running the tools.
* Be verifiable matching the output.
* The tasks should be complex enough that LLMs don't have perfect accuracy.
* Do not require GPU or heavy computation.

Some examples would be:
* Easy tasks: Download a certain pdb from PDB and return the number of aa.
* Medium difficulty: Based on a fasta file perform MSA and return the number of MSA columns (base on some hyperparameters)
* Hard tasks: Based on a csv file for a DMS return the top 10 hot spot positions.

Provide me around 10 examples of task for each level of difficulty.
```



## Task descriptions

```
## Tasks to design

Here are 30 bioinformatics/protein engineering evaluation tasks organized by difficulty level:

## Easy Tasks (2-3 steps, mostly data retrieval/basic analysis)

1. **PDB Structure Analysis**: Download PDB 1UBQ, extract the sequence, and return the number of cysteine residues.

2. **UniProt Sequence Features**: Retrieve UniProt entry P53_HUMAN, identify all signal peptides, and return their total length in amino acids.

3. **PDB Chain Count**: Download PDB 4HHB (hemoglobin), count the number of protein chains, and return the chain IDs.

4. **FASTA Length Statistics**: Parse a given multi-FASTA file of 50 bacterial proteases, calculate the mean sequence length, and return the value rounded to nearest integer.

5. **PDB Resolution Check**: Download 5 specified PDB structures, extract their resolution values, and return the PDB ID with the highest resolution.

6. **UniProt Domain Count**: For UniProt entry INSR_HUMAN, count the number of fibronectin type-III domains and return the count.

7. **PDB Secondary Structure**: Download PDB 1A3N, extract secondary structure using DSSP format, and count the number of beta sheets.

8. **Sequence Composition**: Given a FASTA file with 10 membrane proteins, calculate the percentage of hydrophobic residues (AILMFPVW) in the first sequence.

9. **PDB Ligand Identification**: Download PDB 1HTM, identify all bound ligands (excluding water), and return the number of unique ligand types.

10. **Gene Ontology Terms**: For UniProt entry CALM_HUMAN, retrieve GO terms and return the number of molecular function annotations.

## Medium Tasks (3-4 steps, computational analysis required)

1. **MSA Column Conservation**: Perform MSA on a given FASTA file of 20 homologous kinases using MUSCLE, calculate conservation scores, and return the number of columns with >80% conservation.

2. **Phylogenetic Distance**: Create a phylogenetic tree from 15 cytochrome c sequences using neighbor-joining, and return the maximum pairwise distance between any two sequences.

3. **Structural Alignment RMSD**: Download PDB structures 1A3N and 1A3O, perform structural alignment using PyMOL or similar, and return the RMSD value for Cα atoms.

4. **Domain Architecture Comparison**: Compare domain architectures of 5 given UniProt entries using Pfam, identify the most common domain, and return its Pfam ID.

5. **Codon Usage Bias**: Analyze codon usage in 10 E. coli essential genes, calculate the codon adaptation index (CAI), and return the gene with the highest CAI.

6. **Transmembrane Topology**: Predict transmembrane helices for 8 GPCR sequences using TMHMM, and return the sequence ID with the most predicted helices.

7. **B-factor Analysis**: Download PDB 2LYZ, extract B-factors for all Cα atoms, identify residues in the top 10% highest B-factors, and return their count.

8. **Homology Modeling Quality**: Build a homology model for a given target sequence using a specified template PDB, calculate the QMEAN score, and return the quality assessment.

9. **Splice Site Prediction**: Analyze 5 human gene sequences for splice sites using a computational tool, identify the number of predicted exons in the longest transcript.

10. **Protein Disorder Prediction**: Run disorder prediction on 6 transcription factor sequences using IUPred, return the sequence ID with the highest percentage of disordered regions.

## Hard Tasks (4-5 steps, complex analysis with interpretation)

1. **DMS Hotspot Analysis**: From a deep mutational scanning CSV file with fitness scores, identify positions with >3-fold fitness loss in >50% of mutations, rank by severity, and return the top 10 hotspot positions.

2. **Allosteric Network Identification**: Download PDB 1A3N, perform residue network analysis using correlation of atomic fluctuations, identify allosteric pathways between two specified sites, and return the shortest path length.

3. **Evolutionary Rate Analysis**: Align 20 orthologous sequences, build a phylogenetic tree, calculate dN/dS ratios for all branches, identify branches under positive selection (dN/dS > 1), and return the count.

4. **Protein Complex Interface**: Download a multi-chain PDB, identify all inter-chain contacts within 4Å, classify contacts by interaction type (hydrophobic, hydrogen bonds, salt bridges), and return the interface area in Ų.

5. **Functional Site Conservation**: Perform MSA on 25 enzyme sequences, map known active site residues, calculate position-specific conservation scores, identify non-conserved active site positions, and return their sequence positions.

6. **Structural Motif Discovery**: Analyze 10 DNA-binding protein structures, identify common structural motifs using geometric hashing, cluster similar motifs, and return the number of distinct motif families.

7. **Epistasis Network Analysis**: From a combinatorial mutagenesis dataset, identify all pairwise epistatic interactions (|observed - expected| > threshold), construct an epistasis network, and return the position with the highest degree centrality.

8. **Druggability Assessment**: Download 5 target protein structures, perform cavity detection and druggability scoring using fpocket or CASTp, rank cavities by druggability, and return the PDB ID with the most druggable site.

9. **Conformational Ensemble Analysis**: Download an NMR ensemble PDB, calculate root-mean-square fluctuation (RMSF) for each residue across all models, identify the most flexible region (5+ consecutive residues), and return the starting residue number.

10. **Metabolic Pathway Impact**: Given a list of enzyme variants with activity measurements, map to KEGG pathways, calculate pathway flux changes using metabolic modeling, identify the most disrupted pathway, and return its KEGG ID.

```



## Task Variants







```{json}

{
  "E1_PDB_Cysteine_Count": {
    "description": "Download PDB structure, extract amino acid sequence, count number of cysteine residues",
    "variants": {
      "variant_1": "1UBQ",
      "variant_2": "1A3N",
      "variant_3": "2LYZ",
      "variant_4": "1HTM",
      "variant_5": "1CRN"
    }
  },
  "E2_UniProt_Signal_Peptides": {
    "description": "Retrieve UniProt entry, identify all signal peptides, return total length in amino acids",
    "variants": {
      "variant_1": "P04637",
      "variant_2": "P01308",
      "variant_3": "P00750",
      "variant_4": "P01189",
      "variant_5": "P01344"
    }
  },
  "E3_PDB_Chain_Count": {
    "description": "Download PDB structure, count number of protein chains, return chain IDs",
    "variants": {
      "variant_1": "4HHB",
      "variant_2": "1A3N",
      "variant_3": "2LYZ",
      "variant_4": "1HTM",
      "variant_5": "1UBQ"
    }
  },
  "E4_FASTA_Length_Statistics": {
    "description": "Parse a given set of FASTA files, calculate mean sequence length, return rounded integer",
    "variants": {
      "variant_1": [
        "P00533",
        "P04626",
        "P21860",
        "Q15303",
        "P08581"
      ],
      "variant_2": [
        "P12931",
        "P06241",
        "P07947",
        "P06239",
        "P07948"
      ],
      "variant_3": [
        "P42574",
        "P55210",
        "P55212",
        "Q14790",
        "P55211"
      ],
      "variant_4": [
        "Q15796",
        "Q15797",
        "P84022",
        "Q13485",
        "Q99717"
      ],
      "variant_5": [
        "P62158",
        "P60709",
        "P68371",
        "P63104",
        "P01112"
      ]
    }
  },
  "E5_PDB_Resolution_Comparison": {
    "description": "Download 5 PDB structures, extract resolution values, return PDB ID with highest resolution",
    "variants": {
      "variant_1": [
        "1UBQ",
        "2LYZ",
        "1A3N",
        "1HTM",
        "1CRN"
      ],
      "variant_2": [
        "3C2N",
        "1JXO",
        "2FHA",
        "1L2Y",
        "1A4Y"
      ],
      "variant_3": [
        "1GFL",
        "1HAG",
        "1TEN",
        "1VFB",
        "1BPI"
      ],
      "variant_4": [
        "2H5N",
        "3B4R",
        "1X8R",
        "4GCR",
        "1D3Z"
      ],
      "variant_5": [
        "1F34",
        "1M40",
        "1PDB",
        "1SVA",
        "2B4J"
      ]
    }
  },
  "E6_UniProt_Domain_Count": {
    "description": "Retrieve UniProt entry, count specific domain types, return count",
    "variants": {
      "variant_1": "P06213",
      "variant_2": "P35568",
      "variant_3": "P42336",
      "variant_4": "P04626",
      "variant_5": "P15056"
    }
  },
  "E7_PDB_Secondary_Structure": {
    "description": "Download PDB, extract secondary structure using DSSP, count beta sheets",
    "variants": {
      "variant_1": "1A3N",
      "variant_2": "2LYZ",
      "variant_3": "1UBQ",
      "variant_4": "1HTM",
      "variant_5": "1CRN"
    }
  },
  "E8_Hydrophobic_Residue_Percentage": {
    "description": "Calculate percentage of hydrophobic residues in the first sequence of a given set of FASTA files",
    "variants": {
      "variant_1": [
        "P0DPA2",
        "P0DPA3",
        "P0DPA4",
        "P0DPA5",
        "P0DPA6"
      ],
      "variant_2": [
        "P0C0L4",
        "P0C0L5",
        "P0C0L6",
        "P0C0L7",
        "P0C0L8"
      ],
      "variant_3": [
        "A0A0A6YY23",
        "A0A0A6YY24",
        "A0A0A6YY25",
        "A0A0A6YY26",
        "A0A0A6YY27"
      ],
      "variant_4": [
        "P12345",
        "P67890",
        "P54321",
        "P09876",
        "P13579"
      ],
      "variant_5": [
        "Q9Y260",
        "Q9Y261",
        "Q9Y262",
        "Q9Y263",
        "Q9Y264"
      ]
    }
  },
  "E9_PDB_Ligand_Count": {
    "description": "Download PDB, identify all bound ligands excluding water, count unique ligand types",
    "variants": {
      "variant_1": "1HTM",
      "variant_2": "2LYZ",
      "variant_3": "3HVT",
      "variant_4": "1A3N",
      "variant_5": "4HHB"
    }
  },
  "E10_Gene_Ontology_Terms": {
    "description": "Retrieve UniProt entry GO terms, count molecular function annotations",
    "variants": {
      "variant_1": "P62158",
      "variant_2": "P60709",
      "variant_3": "P68371",
      "variant_4": "P63104",
      "variant_5": "P01112"
    }
  },
  "M1_MSA_Conservation_Score": {
    "description": "Perform MSA with MUSCLE on a given set of FASTA files, calculate conservation scores, count columns >80% conserved",
    "variants": {
      "variant_1": [
        "P00533",
        "P04626",
        "P21860",
        "Q15303",
        "P08581"
      ],
      "variant_2": [
        "P12931",
        "P06241",
        "P07947",
        "P06239",
        "P07948"
      ],
      "variant_3": [
        "P42574",
        "P55210",
        "P55212",
        "Q14790",
        "P55211"
      ],
      "variant_4": [
        "Q15796",
        "Q15797",
        "P84022",
        "Q13485",
        "Q99717"
      ],
      "variant_5": [
        "P62158",
        "P60709",
        "P68371",
        "P63104",
        "P01112"
      ]
    }
  },
  "M2_Phylogenetic_Distance": {
    "description": "Create neighbor-joining phylogenetic tree from 15 sequences, return maximum pairwise distance",
    "variants": {
      "variant_1": "cytochrome_c_mammals_15_sequences.fasta",
      "variant_2": "histone_h3_vertebrates_15_sequences.fasta",
      "variant_3": "ribosomal_s1_bacteria_15_sequences.fasta",
      "variant_4": "elongation_factor_archaea_15_sequences.fasta",
      "variant_5": "actin_plants_15_sequences.fasta"
    }
  },
  "M3_Structural_Alignment_RMSD": {
    "description": "Perform structural alignment between two PDB structures, return RMSD for C\u03b1 atoms",
    "variants": {
      "variant_1": [
        "1A3N",
        "1A3O"
      ],
      "variant_2": [
        "2LYZ",
        "1LYZ"
      ],
      "variant_3": [
        "1UBQ",
        "1UBI"
      ],
      "variant_4": [
        "1HTM",
        "2HTM"
      ],
      "variant_5": [
        "1CRN",
        "2CRN"
      ]
    }
  },
  "M4_Domain_Architecture": {
    "description": "Compare domain architectures of 5 UniProt entries using Pfam, identify most common domain",
    "variants": {
      "variant_1": [
        "P04637",
        "P63000",
        "O15350",
        "O15151",
        "Q02750"
      ],
      "variant_2": [
        "P00533",
        "P04626",
        "P21860",
        "Q15303",
        "P08581"
      ],
      "variant_3": [
        "P12931",
        "P06241",
        "P07947",
        "P06239",
        "P07948"
      ],
      "variant_4": [
        "P42574",
        "P55210",
        "P55212",
        "Q14790",
        "P55211"
      ],
      "variant_5": [
        "Q15796",
        "Q15797",
        "P84022",
        "Q13485",
        "Q99717"
      ]
    }
  },
  "M5_Codon_Usage_Analysis": {
    "description": "Analyze codon usage in 10 genes, calculate CAI, return gene with highest CAI",
    "variants": {
      "variant_1": [
        "dnaA",
        "dnaN",
        "recA",
        "gyrB",
        "rpoA",
        "rpoB",
        "rpoC",
        "rpsL",
        "rpsG",
        "fusA"
      ],
      "variant_2": [
        "thrA",
        "thrB",
        "thrC",
        "metL",
        "lysC",
        "asd",
        "dapA",
        "dapB",
        "dapD",
        "dapF"
      ],
      "variant_3": [
        "trpA",
        "trpB",
        "trpC",
        "trpD",
        "trpE",
        "pheA",
        "tyrA",
        "hisA",
        "hisB",
        "hisC"
      ],
      "variant_4": [
        "ilvA",
        "ilvB",
        "ilvC",
        "ilvD",
        "ilvE",
        "leuA",
        "leuB",
        "leuC",
        "leuD",
        "proA"
      ],
      "variant_5": [
        "argA",
        "argB",
        "argC",
        "argD",
        "argE",
        "argF",
        "argG",
        "argH",
        "glnA",
        "gltB"
      ]
    }
  },
  "M6_Transmembrane_Prediction": {
    "description": "Run TMHMM on a given set of FASTA files, predict transmembrane helices, return sequence with most helices",
    "variants": {
      "variant_1": [
        "P35355",
        "P35367",
        "P35372",
        "P41143",
        "P41145",
        "Q13639",
        "Q96P88",
        "Q9Y5N1"
      ],
      "variant_2": [
        "P08100",
        "P11229",
        "P11230",
        "P13945",
        "P21728",
        "P28222",
        "P28223",
        "P30542"
      ],
      "variant_3": [
        "P61073",
        "O43641",
        "P29274",
        "P29275",
        "P32238",
        "P32241",
        "P34969",
        "P35348"
      ],
      "variant_4": [
        "Q9H228",
        "Q9H229",
        "Q9H230",
        "Q9H231",
        "Q9H232",
        "Q9H233",
        "Q9H234",
        "Q9H235"
      ],
      "variant_5": [
        "P24530",
        "P35462",
        "P41594",
        "P41595",
        "P42857",
        "P43286",
        "P51679",
        "Q15392"
      ]
    }
  },
  "M7_B_factor_Analysis": {
    "description": "Download PDB, extract B-factors for C\u03b1 atoms, count residues in top 10% highest B-factors",
    "variants": {
      "variant_1": "2LYZ",
      "variant_2": "1A3N",
      "variant_3": "1UBQ",
      "variant_4": "1HTM",
      "variant_5": "4HHB"
    }
  },
  "M8_Homology_Modeling_Quality": {
    "description": "Build homology model for target using template, calculate QMEAN score",
    "variants": {
      "variant_1": {
        "target": "P00766",
        "template": "1TON"
      },
      "variant_2": {
        "target": "P0C6A9",
        "template": "3M6I"
      },
      "variant_3": {
        "target": "Q9H3R5",
        "template": "1W50"
      },
      "variant_4": {
        "target": "P61247",
        "template": "1M8Q"
      },
      "variant_5": {
        "target": "P42345",
        "template": "1Z5X"
      }
    }
  },
  "M9_Splice_Site_Prediction": {
    "description": "Analyze gene sequences for splice sites, identify number of predicted exons in longest transcript",
    "variants": {
      "variant_1": "BRCA1",
      "variant_2": "TP53",
      "variant_3": "CFTR",
      "variant_4": "DMD",
      "variant_5": "APOE"
    }
  },
  "M10_Protein_Disorder_Prediction": {
    "description": "Run disorder prediction on a given set of FASTA files using IUPred, return highest disorder percentage",
    "variants": {
      "variant_1": [
        "P04637",
        "P03070",
        "Q01094",
        "P10275",
        "P01112",
        "P01116"
      ],
      "variant_2": [
        "P10424",
        "P35916",
        "P36544",
        "Q03167",
        "Q92786",
        "O00444"
      ],
      "variant_3": [
        "P20226",
        "P15332",
        "P19544",
        "P16410",
        "P10826",
        "Q05516"
      ],
      "variant_4": [
        "P38398",
        "Q92753",
        "P52946",
        "P41240",
        "P27986",
        "P35659"
      ],
      "variant_5": [
        "O15111",
        "P53805",
        "Q12888",
        "Q13153",
        "Q13154",
        "Q99459"
      ]
    }
  },
  "H1_DMS_Hotspot_Analysis": {
    "description": "Analyze deep mutational scanning data, identify top 10 hotspot positions with >3-fold fitness loss",
    "variants": {
      "variant_1": "ProteinGym_DMS: UBE4B_MOUSE_Starr_2021",
      "variant_2": "ProteinGym_DMS: MTH3_HAEAESTABILIZED_Tsuboyama_2021",
      "variant_3": "ProteinGym_DMS: YAP1_HUMAN_Fields2012_DMS",
      "variant_4": "ProteinGym_DMS: PAB1_YEAST_Melen_2017",
      "variant_5": "ProteinGym_DMS: BGL3_BACSU_Mikkelsen_2021"
    }
  },
  "H2_Allosteric_Network_Analysis": {
    "description": "Perform residue network analysis, identify shortest allosteric pathway between two sites",
    "variants": {
      "variant_1": "1A3N",
      "variant_2": "2LYZ",
      "variant_3": "4HHB",
      "variant_4": "1HTM",
      "variant_5": "1UBQ"
    }
  },
  "H3_Evolutionary_Rate_Analysis": {
    "description": "Build phylogenetic tree, calculate dN/dS ratios, count branches under positive selection",
    "variants": {
      "variant_1": [
        "P69905",
        "P01942",
        "P01941",
        "P02734",
        "P02735",
        "P02736",
        "P02737",
        "P02738",
        "P02739",
        "P02740",
        "P02741",
        "P02742",
        "P02743",
        "P02744",
        "P02745"
      ],
      "variant_2": [
        "P62258",
        "P02340",
        "P02341",
        "P02342",
        "P02343",
        "P02344",
        "P02345",
        "P02346",
        "P02347",
        "P02348",
        "P02349",
        "P02350",
        "P02351",
        "P02352",
        "P02353"
      ],
      "variant_3": [
        "P62873",
        "P02585",
        "P02586",
        "P02587",
        "P02588",
        "P02589",
        "P02590",
        "P02591",
        "P02592",
        "P02593",
        "P02594",
        "P02595",
        "P02596",
        "P02597",
        "P02598"
      ],
      "variant_4": [
        "P68871",
        "P01031",
        "P01032",
        "P01033",
        "P01034",
        "P01035",
        "P01036",
        "P01037",
        "P01038",
        "P01039",
        "P01040",
        "P01041",
        "P01042",
        "P01043",
        "P01044"
      ],
      "variant_5": [
        "P63279",
        "P01122",
        "P01123",
        "P01124",
        "P01125",
        "P01126",
        "P01127",
        "P01128",
        "P01129",
        "P01130",
        "P01131",
        "P01132",
        "P01133",
        "P01134",
        "P01135"
      ]
    }
  },
  "H4_Protein_Complex_Interface": {
    "description": "Analyze multi-chain PDB, identify inter-chain contacts, classify interactions, return interface area",
    "variants": {
      "variant_1": "4HHB",
      "variant_2": "1HTM",
      "variant_3": "2LYZ",
      "variant_4": "1A3N",
      "variant_5": "1AVX"
    }
  },
  "H5_Functional_Site_Conservation": {
    "description": "Perform MSA on 25 enzymes, map active sites, identify non-conserved active site positions",
    "variants": {
      "variant_1": [
        "P00766",
        "P00767",
        "P00768",
        "P00769",
        "P00770",
        "P00771",
        "P00772",
        "P00773",
        "P00774",
        "P00775",
        "P00776",
        "P00777",
        "P00778",
        "P00779",
        "P00780",
        "P00781",
        "P00782",
        "P00783",
        "P00784",
        "P00785",
        "P00786",
        "P00787",
        "P00788",
        "P00789",
        "P00790"
      ],
      "variant_2": [
        "P00350",
        "P00351",
        "P00352",
        "P00353",
        "P00354",
        "P00355",
        "P00356",
        "P00357",
        "P00358",
        "P00359",
        "P00360",
        "P00361",
        "P00362",
        "P00363",
        "P00364",
        "P00365",
        "P00366",
        "P00367",
        "P00368",
        "P00369",
        "P00370",
        "P00371",
        "P00372",
        "P00373",
        "P00374"
      ],
      "variant_3": [
        "P00918",
        "P00919",
        "P00920",
        "P00921",
        "P00922",
        "P00923",
        "P00924",
        "P00925",
        "P00926",
        "P00927",
        "P00928",
        "P00929",
        "P00930",
        "P00931",
        "P00932",
        "P00933",
        "P00934",
        "P00935",
        "P00936",
        "P00937",
        "P00938",
        "P00939",
        "P00940",
        "P00941",
        "P00942"
      ],
      "variant_4": [
        "P0ABH9",
        "P0ABJ0",
        "P0ABJ1",
        "P0ABJ2",
        "P0ABJ3",
        "P0ABJ4",
        "P0ABJ5",
        "P0ABJ6",
        "P0ABJ7",
        "P0ABJ8",
        "P0ABJ9",
        "P0ACK0",
        "P0ACK1",
        "P0ACK2",
        "P0ACK3",
        "P0ACK4",
        "P0ACK5",
        "P0ACK6",
        "P0ACK7",
        "P0ACK8",
        "P0ACK9",
        "P0ADL0",
        "P0ADL1",
        "P0ADL2",
        "P0ADL3"
      ],
      "variant_5": [
        "P27306",
        "P27307",
        "P27308",
        "P27309",
        "P27310",
        "P27311",
        "P27312",
        "P27313",
        "P27314",
        "P27315",
        "P27316",
        "P27317",
        "P27318",
        "P27319",
        "P27320",
        "P27321",
        "P27322",
        "P27323",
        "P27324",
        "P27325",
        "P27326",
        "P27327",
        "P27328",
        "P27329",
        "P27330"
      ]
    }
  },
  "H6_Structural_Motif_Discovery": {
    "description": "Analyze 10 protein structures, identify common motifs, cluster and count distinct families",
    "variants": {
      "variant_1": [
        "1AAY",
        "1CMA",
        "1D8V",
        "1E9H",
        "1FJL",
        "1G2D",
        "1H9D",
        "1J2Q",
        "1K60",
        "1L1O"
      ],
      "variant_2": [
        "1B3T",
        "1B3U",
        "1B3V",
        "1B3W",
        "1B3X",
        "1B3Y",
        "1B3Z",
        "1B40",
        "1B41",
        "1B42"
      ],
      "variant_3": [
        "1ZAA",
        "1ZAB",
        "1ZAC",
        "1ZAD",
        "1ZAE",
        "1ZAF",
        "1ZAG",
        "1ZAH",
        "1ZAI",
        "1ZAJ"
      ],
      "variant_4": [
        "2B0D",
        "2B0E",
        "2B0F",
        "2B0G",
        "2B0H",
        "2B0I",
        "2B0J",
        "2B0K",
        "2B0L",
        "2B0M"
      ],
      "variant_5": [
        "3B4R",
        "3B4S",
        "3B4T",
        "3B4U",
        "3B4V",
        "3B4W",
        "3B4X",
        "3B4Y",
        "3B4Z",
        "3B50"
      ]
    }
  },
  "H7_Epistasis_Network_Analysis": {
    "description": "Analyze combinatorial mutagenesis data, construct epistasis network, return highest degree centrality",
    "variants": {
      "variant_1": "ProteinGym_Epistasis: GFP_SF9_Sarkisyan_2016",
      "variant_2": "ProteinGym_Epistasis: PABP_YEAST_Melamed_2013",
      "variant_3": "ProteinGym_Epistasis: TEM-1_ECOLI_Stiffler_2015",
      "variant_4": "ProteinGym_Epistasis: BGL3_BACSU_Mikkelsen_2021",
      "variant_5": "ProteinGym_Epistasis: HIS3_YEAST_Pokusaeva_2019"
    }
  },
  "H8_Druggability_Assessment": {
    "description": "Perform cavity detection on 5 proteins, score druggability, return most druggable PDB ID",
    "variants": {
      "variant_1": [
        "1A3N",
        "2LYZ",
        "1HTM",
        "1UBQ",
        "1CRN"
      ],
      "variant_2": [
        "3PBL",
        "1HCL",
        "2G8P",
        "1FIN",
        "1M1Q"
      ],
      "variant_3": [
        "1A2Z",
        "1B3Y",
        "1C4Z",
        "1D5Y",
        "1E6Z"
      ],
      "variant_4": [
        "4HHB",
        "1A00",
        "1B00",
        "1C00",
        "1D00"
      ],
      "variant_5": [
        "1YAG",
        "2YAG",
        "3YAG",
        "4YAG",
        "5YAG"
      ]
    }
  },
  "H9_Conformational_Ensemble_Analysis": {
    "description": "Analyze NMR ensemble PDB, calculate RMSF, identify most flexible region start residue",
    "variants": {
      "variant_1": "2K39",
      "variant_2": "1D3Z",
      "variant_3": "2KJ3",
      "variant_4": "1A4Y",
      "variant_5": "2L0J"
    }
  },
  "H10_Metabolic_Pathway_Impact": {
    "description": "Map enzyme variants to KEGG pathways, calculate flux changes, identify most disrupted pathway",
    "variants": {
      "variant_1": {
        "pathway": "ko00010",
        "enzymes": [
          "P00350",
          "P00351",
          "P00352",
          "P00353",
          "P00354"
        ]
      },
      "variant_2": {
        "pathway": "ko00230",
        "enzymes": [
          "P0A6A8",
          "P0A9P0",
          "P0A9P2",
          "P0A9P4",
          "P0A9P6"
        ]
      },
      "variant_3": {
        "pathway": "ko00500",
        "enzymes": [
          "P14929",
          "P14930",
          "P14931",
          "P14932",
          "P14933"
        ]
      },
      "variant_4": {
        "pathway": "ko00620",
        "enzymes": [
          "P25520",
          "P25521",
          "P25522",
          "P25523",
          "P25524"
        ]
      },
      "variant_5": {
        "pathway": "ko00910",
        "enzymes": [
          "P45568",
          "P45569",
          "P45570",
          "P45571",
          "P45572"
        ]
      }
    }
  }
}

```

