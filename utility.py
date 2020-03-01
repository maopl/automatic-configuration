

def GetAllSubset(items):
    #generate all combination of N items
    N = len(items)
    #enumerate the 2**N possible combinations
    set_all=[]
    for i in range(2**N):
        combo = []
        for j in range(N):
            if(i >> j ) % 2 == 1:
                combo.append(items[j])

        set_all.append(combo)
    return set_all