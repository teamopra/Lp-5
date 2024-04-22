import random, time, sys
from multiprocessing import Pool, Process, Pipe
from itertools import chain

#Dependencies defined below main()

def main():
    """
    This is the main method, where we:
    -generate a random list.
    -time a sequential quicksort on the list.
    -time a parallel quicksort on the list.
    -time Python's built-in sorted on the list.
    """
    N = 500000
    if len(sys.argv) > 1:  #the user input a list size.
        N = int(sys.argv[1])

    #We want to sort the same list, so make a backup.
    lystbck = [random.random() for x in range(N)]

    #Sequential quicksort a copy of the list.
    lyst = list(lystbck)            #copy the list
    start = time.time()             #start time
    lyst = quicksort(lyst)          #quicksort the list
    elapsed = time.time() - start   #stop time
    
    if not isSorted(lyst):
        print('quicksort did not sort the lyst. oops.')
        
    print('Sequential quicksort: %f sec' % (elapsed))

    #So that cpu usage shows a lull.
    time.sleep(3)
    
    #Parallel quicksort.
    lyst = list(lystbck)
    
    start = time.time()
    n = 3 #2**(n+1) - 1 processes will be instantiated.
    #I set the number of processes to be high since, with
    #a random choice of pivot, it is unlikely the work
    #will distribute evenly.

    lyst = quicksortParallel(lyst, n)
    
    elapsed = time.time() - start

    if not isSorted(lyst):
        print('quicksortParallel did not sort the lyst. oops.')

    print('Parallel quicksort: %f sec' % (elapsed))


    time.sleep(3)
    
    #Built-in test.
    #The underlying c code is obviously the fastest, but then
    #using a calculator is usually faster too.  That isn't the
    #point here obviously.
    lyst = list(lystbck)
    start = time.time()
    lyst = sorted(lyst)
    elapsed = time.time() - start
    print('Built-in sorted: %f sec' % (elapsed))

    
def quicksort(lyst):
    """
    quicksort implementation, return a new sorted version
    of the input list.
    Faster quicksort in that it relies on built-in list
    comprehensions and concatenation.
    Inspired from Vitalii Vanovschi:
    http://www.parallelpython.com/component/option,com_smf/Itemid,1/action,printpage/topic,105.0
    """
    if len(lyst) <= 1:
        return lyst
    pivot = lyst.pop(random.randint(0, len(lyst)-1))
    
    return quicksort([x for x in lyst if x < pivot]) \
           + [pivot] \
           + quicksort([x for x in lyst if x >= pivot])

def swap(a,i,j):
    temp = a[i]
    a[i] = a[j]
    a[j] = temp

def partition(a, lo, hi):
    rnd = random.randint(lo, hi)
    pivot = a[rnd]
    swap(a,hi,rnd)
    b = lo
    for i in range(lo, hi):
        if a[i] < pivot:
            swap(a, i, b)
            b += 1
    swap(a, hi, b)
    return b

def partitionWrap(i_lyst):
    """
    Takes a tuple of the index, and a lyst.  The index
    is useless here, but when the map returns we'll need
    know where this lyst argument is in the overal lyst, 
    and therefore what pivot can be set in its place.
    """
    ind, lyst = i_lyst
    if len(lyst) <= 1:
        return [lyst]
    b = partition(lyst, 0, len(lyst)-1)
    return (ind, [lyst[:b], [lyst[b]], lyst[b+1:]])

def quicksortParallel(lyst, n):
    numproc = 2**n
    #Basically, we're going to partition the list until it's all
    #singletons. We'll store each singleton in the master list.
    ml = list(lyst)
    
    pool = Pool(processes = numproc)
    results = [(0, lyst)] 
	#the one initial argument to partitionWrap
    
    while len(results) > 0:
        #debug: print(str(results) + '\n\n\n')
        temp = pool.map(partitionWrap, results)
        #Each element of temp is a list of up to three lists.
        results = []
        for i, plist in temp:
            for ll in plist: #for each little list in the partition output
                if len(ll) == 1:
                    ml[i] = ll[0]
                    i += 1
                elif len(ll) > 1:
                    results.append((i, ll))
                    i += len(ll)

    return ml

def isSorted(lyst):
    """
    Return whether the argument lyst is in non-decreasing order.
    """
    for i in range(1, len(lyst)):
        if lyst[i] < lyst[i-1]:
            return False
    return True


#Call the main method if run from the command line.
if __name__ == '__main__':
    main()
    
    
"""
don't try this, it's kind of slow.
def partitionWrap(lyst):
    if len(lyst) <= 1:
        return [lyst]
    b = partition(lyst, 0, len(lyst)-1)
    temp = [lyst[:b], [lyst[b]], lyst[b+1:]]
    return [x for x in temp if len(x) > 0]

def quicksortParallel(lyst, n):  crazy slow.
    numproc = 2**n
    #Basically, we're going to partition the list until it's all
    #singletons. 
    
    pool = Pool(processes = numproc)
    results = [lyst] #list containing the list of elements.

    while len(results) < len(lyst):
        temp = pool.map(partitionWrap, results)
        results = [item for sublist in temp for item in sublist]

    return [item for sublist in results for item in sublist]
"""
