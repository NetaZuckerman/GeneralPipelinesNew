import pandas as pd

def parse(file, ds=True):
    '''
    This script generates a region.csv file.
    
    Parameters
    ----------
    file : gene bank file. 
    ds : bool, optional
        is double stranded genome. The default is False.

    Returns
    -------
    None.

    '''
    df = pd.DataFrame(columns=["GENE","START","END","STRAND"])
    
    with open(file, 'r') as  f:
        lines = f.readlines()
        
        
    
    f = open(file)
    while True:
        line = f.readline().strip()
        if not line:
            break
    
        if line.startswith("CDS"):
            pos_list = []
            strand = "-" if "complement" in line else '+'
        
            if "join" in line:
               
                pos_list.extend(line.split("join(")[1].split(",")) 
                while not line.endswith(")"):
                    line = f.readline().strip()
                    pos_list.extend(line.split(")")[0].split(","))
                pos_list = [x for x in pos_list if not x=='']
            
            else:
                
                if strand == '-':
                    pos_list = [line.split("complement(")[1].strip().split(")")[0]]
                
                else:
                    pos_list = [line.split("CDS")[1].strip()]
            
            gene = f.readline().strip().split('"')[1].split('"')[0]
            for position in pos_list:
                position = position.split("..")
                df = df.append({"GENE": gene,
                            "START": position[0],
                            "END": position[1].split(")")[0],
                            "STRAND": strand}, ignore_index=True)
            
            
    f.close()
    
    if ds:
        df.to_csv(file.replace(".gb", "_regions.csv"), index = False)
    else:
        df.iloc[: , :-1].to_csv(file.replace(".gb", "_regions.csv"), index = False)
