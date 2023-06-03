#!/usr/bin/python
# =======================================================
# Alignment scoring 
# 
# For the MGB Challenge  http://www.mgb-challenge.org/
# 
# Develpped as part of the EPSRC programme in Natural 
# Speech technology 
# =======================================================
# (c) Thomas Hain (2015) http://www.dcs.shef.ac.uk/~th

# =======================================================
# IMPORTS 
# =======================================================

import os, sys , re

import argparse , difflib , textwrap

# =======================================================
# INFO 
# =======================================================

__version__ = "0.3"

# =======================================================
# Label files
# =======================================================
class TimedWordLabelFile:

    # -------------------------------------------------------------------------------------  
    def __init__(self, name = None):
        self.labels = []
        self.name = name
        self.script = []

    # -------------------------------------------------------------------------------------  
    def addentry(self , x ):
        # 0 - start time 
        # 1 - end time (in frames) 
        # 2 -  word 
        # 3 - conf  
        # 4 - inScript  (true / false)  
        # 5 - do not score (true , false)
        if len(x) == 3:
            self.labels.append( x + [ 1.0 , True,False] )
        elif len(x) == 4:
            self.labels.append( x + [ True,False] )
        else:
            raise

    def sort(self):
        self.labels.sort( key = lambda x : x[0] )

    # ------------------------------------------------------------------------------------- ALIGN SCRIPT 
    def alignscript(self):
        # align the script with the reference labels (with timing info) 
        # assume sorted labels , collect words in manual reference
        words = [ x[2] for x in self.labels ]	

        nins  = 0  # num words inserted in relation to reference	
        ndel  = 0  # num words deleted from the script 
        ncorr = 0 

        # align script with manual reference 
        # with difflib there are no substitution errors / hence successive del/ins pairs 
        # shoudl be considered as substitutions
        si = ri = 0
        for x in difflib.ndiff( self.script , words ):
            if x.startswith("+") :
                # word in reference. not script  
                #print "%40s %-20s %s" % ("",x,str(self.labels[ri]) )
                self.labels[ri][4] = False
                nins += 1
                ri += 1
            elif x.startswith("-") :
                # word in script , but not in reference , we ignore
                #print x
                ndel += 1
                si += 1
            elif x.startswith("?") :
                # these give only further detail if a 
                # a successive del/ins is based on a slight change in graphme
                continue
            else:
                # word in both script and reference
                self.labels[ri][4] = True
                ncorr += 1
                #print "%20s %-20s %20s%s " % ( "" ,x, "", str(self.labels[ri]) )
                si += 1
                ri += 1 
        verboseprint(1,"script corr %d ins %d del %d" % (ncorr , nins, ndel ) )
        self.scriptcounts = [ncorr , nins , ndel]

    # -------------------------------------------------------------------
    def alignscript_print(self):
        words = [ x[2] for x in self.labels ]	

        l1 = 'REF:' ; l2 = 'SYS:' 
        si = ri = 0
        for x in difflib.ndiff( self.script , words ):
            if x.startswith("+"):
                y = x.split()[1]
                l1 += ' ' + y
                l2 += ' *' + ' ' * (len(y)-1)
                ri += 1
            elif x.startswith("-") :
                y = x.split()[1]
                l1 += ' *' + ' ' * (len(y)-1)
                l2 += ' ' + y
                si += 1
            elif x.startswith("?") :
                continue
            else:
                l1 += ' ' + x.strip()
                l2 += ' ' + x.strip()			
                si += 1
                ri += 1 

            if len(l1) > 80 or len(l2)>80:
                print(l1)
                print(l2)
                #print
                #l1 = 'R>  ' ; l2 = 'S>  ' 

    # -------------------------------------------------------------------
    # check if any labels overlap 
    def hasoverlap(self):
        for i in range(1,len(self.labels)):
            if self.labels[i-1][1] > self.labels[i][0]: 
                return True
        return False

    # -------------------------------------------------------------------
    # ignore a time interval in scoring 
    def setignore_byinterval(self , st , et , flag = True):
        # assumes time sorted label list
        p = False
        for x in self.labels:
            if x[1] > st and x[0] < et:
                p = True
                x[5] = flag 
            elif p:
                break

    # -------------------------------------------------------------------
    def count( self , func ):
        ct = 0 
        for x in self.labels:
            if func(x[4],x[5]):
                ct+= 1
        return [ len(self.labels) , ct ] 

    def count_or( self , inscript , dontscore ):
        f = lambda x,y: (x == inscript) or (y == dontscore)
        return self.count(f)

    def count_and( self , inscript , dontscore ):
        f = lambda x,y: (x == inscript) and (y == dontscore)
        return self.count(f)

    # -------------------------------------------------------------------
    def match( self , match , hyp ):
        matched = {} 	# hyp -> ref 
        imatched = {} 	# ref -> hyp
        nref   = len( self.labels )
        nhyp   = len( hyp.labels )

        # fast match 
        ri = 0
        hi = 0
        while 1:
            r = self.labels[ri] 
            h = hyp.labels[hi] 
            if r[1] < h[0]:
                ri += 1
            elif h[1] < r[0]:
                hi += 1
            else:
                #print(ri , hi , r , " == " , h)
                if match.match( r , h ):
                    matched[ hi ] = ri 
                ri += 1 ; hi += 1
            if ri >= nref or hi >= nhyp:
                break

        # refinement 
        hl = 0 ; rl = 0 
        for i in sorted( matched.keys() ):	
            hu = i ; ru = matched[i]
            #print "old chunk start" , hl , hu , rl , ru   

            hi = hl
            while hi < hu:
                # loop over all ref words in this chunk
                ri = rl
                while ri < ru:
                    #print "hyp (%d -> %d) ref (%d -> %d)" % ( hl , hu , rl , ru )
                    #print hi , ri  
                    r = self.labels[ri] 
                    h = hyp.labels[hi] 
                    if match.match( r , h ):	
                        # matched so now we have a new chunk
                        print(">>>>>>>>>>>>>>>>match" , hi , ri)
                        matched[ hi ] = ri 
                        hl = hi+1 ; 
                        ri = rl = ri+1
                        break
                    ri += 1
                # done with the ref part 
                hi += 1
            hl = hu+1 ; rl = ru+1

        matched[-1] = -1
        matched[nhyp] = nref
        return matched

    def print_match(self , matched , hyp , out = sys.stdout ): 
        out.write( "=" * 100 + "\n" )
        out.write( "File: %s\n" % (self.name) )
        out.write( "=" * 100 + "\n" )

        # print the matchin patter 
        for hi in sorted( matched.keys() ):
            #print hi,matched[hi]
            if hi == -1:
                hl = rl = 0
                continue
            if matched[hi] - rl > 0:
                #out.write( "DEL>>> skipping %d reference words\n" % (matched[hi] - rl) )
                for x in self.labels[rl:matched[hi]]:
                    l = "[%.3f,%.3f] %s" % ( x[0] / float(1000) , x[1] / float(1000) , x[2] ) 	
                    r = "- -"
                    out.write( "%-48s D %-50s\n" % (l,r) )
            if hi- hl> 0:
                for x in hyp.labels[hl:hi]:
                    r = "[%.3f,%.3f] %s" % ( x[0] / float(1000) , x[1] / float(1000) , x[2] ) 	
                    l = "- -"
                    out.write( "%-48s I %-50s\n" % (l,r) )
            if hi == len(hyp.labels):
                break
            r = self.labels[matched[hi]] 
            h = hyp.labels[hi] 
    
            l = "[%.3f,%.3f] %s" % ( r[0] / float(1000) , r[1] / float(1000) , r[2] ) 	
            r = "[%.3f,%.3f] %s" % ( h[0] / float(1000) , h[1] / float(1000) , h[2] ) 	
            out.write( "%-48s = %-50s\n" % (l,r) )
            hl = hi+1 ; rl = matched[hi]+1

# =======================================================
# Label file Sets
# =======================================================
class TimedWordLabelFileset:	
    # init 
    def __init__(self):
        self.lf = {}

    def read(self,fname ):
        self.__readctm(fname)
        for lf in self.lf.values():
            lf.sort()

    def readstm(self,fname ):
        self.__readstm( fname )

    def alignscript(self ):
        for lf in self.lf.values():
            lf.alignscript()
            #print lf.name , lf.scriptcounts

    def filter_uem(self , uemfname ):
        self.__read_uem( uemfname , True )

    def check_for_overlap(self):
        for lf in self.lf.values():
            if lf.hasoverlap():
                raise ValueError("found overlap between words in file %s" % fname)
        verboseprint("%s no overlap detected" % lf.name) 

    ## match the complete set 
    def match( self , mo , hyp , res , matchprint = None):
        fi = {}
        # loop over all files in the Hypothesis set
        for fn in hyp.lf:
            print(fn)
            if fn in self.lf:
                # match hyp with ref 
                m = self.lf[fn].match( mo , hyp.lf[fn] )
                nmatch = len(m) - 2 # number of matches 

                # 
                # 3 counts needed 
                #  
                # cs:   nhyp - #(hyp words not in script) - #(words from hyp excluded by time)
                # cr:	nref - #(ref words not in script)- #(ref words excluded by time)
                # m:    nmatch - #(matched ref words exclued by time) 
                #              - #(matched ref words not in script)
                #  			   - #(matched hyp words not in script)

                nref     = len(self.lf[fn].labels)
                act_nref = self.lf[fn].count_and( True , False )[1]

                nhyp     = len(hyp.lf[fn].labels)
                act_nhyp = hyp.lf[fn].count_and( True , False )[1]

                fi["nref"] = nref
                fi["nhyp"] = nhyp
                fi["act_nref"] = act_nref
                fi["act_nhyp"] = act_nhyp

                #print len(self.lf[fn].labels), act_nref
                #print len(hyp.lf[fn].labels), act_nhyp

                # now go through match
                act_nmatch = 0 
                for hi in sorted( m.keys() ):
                    ri = m[hi]
                    if hi < 0 or ri == nref:
                        continue
                    #print hi, ri , nmatch 

                    rl = self.lf[fn].labels[ri]
                    hl = hyp.lf[fn].labels[hi]

                    # ref is in script and not excluded:
                    if rl[4] and not rl[5]:
                        # hyp is in script and not excluded:
                        if hl[4] and not hl[5]:
                            act_nmatch += 1
                    #print hi, ri , nmatch 

                fi["nmatch"]     = nmatch
                fi["act_nmatch"] = act_nmatch

                res.addfileinfo( fn , fi )

                if matchprint:
                    self.lf[fn].print_match( m ,  hyp.lf[fn] , matchprint )
            else:
                raise ValueError("Unknown data element %s" % fn )

    # --------------------------------------------------------
    def __read_uem( self, fname , flag):
        print("... reading uem file - %s" % fname)
        f = open(fname)
        for l in f:
            l = l.strip()
            if l.startswith('#') or len(l)==0:
                continue
            x = l.split()
            if len(x) == 4:
                lname = x[0]
                chan  = x[1]
                if chan != "0":
                    raise
                st = int( float(x[2]) * 1000 + .5 ) 
                en = int( float(x[3]) * 1000 + .5 ) 
            else:
                raise
            if not lname in self.lf: # file not known 
                raise
            self.lf[lname].setignore_byinterval( st , en , flag )

    # --------------------------------------------------------
    def __readstm(self,fname):
        f = open(fname)
        for l in f:
            l = l.strip()
            if l.startswith('#'):
                continue
            x = l.split()
            if not x[0] in self.lf:
                raise # the file needs to be there ! 
            self.lf[x[0]].script = x[6:] 		

    # --------------------------------------------------------
    def __readctm(self , fname ):
        """ read a CTM file """
        verboseprint(0,"reading ctm file")
        f = open(fname)
        for l in f:
            l = l.strip()
            if l.startswith('#'):
                continue
            x = l.split()
            #print(x)
            # only works with single channel at this point
            if not x[0] in self.lf:
                self.lf[ x[0]] = TimedWordLabelFile( x[0] )

            x[2] = int( float(x[2]) * 1000 + .5 )
            x[3] = x[2] + int( float(x[3]) * 1000 + .5 )
            self.lf[ x[0] ].addentry( x[2:] )

# =======================================================
# RESULTS display
# =======================================================
class Results:
    def __init__( self , confdict , out = sys.stdout ):
        self.cfg = confdict
        self.out = out
        self.finfo = {}

    def addfileinfo( self , fname , finfodict ):
        if fname in self.finfo:
            self.finfo[fname].update( finfodict )
        else:
            self.finfo[fname] = dict(finfodict)

    def header(self):
        import datetime 
        self.__sep(True)
        print("Alignment scoring results")
        self.__sep(True)
        self.__ne("Date",datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p") )
        self.__ne("Scoring script version", "v" + __version__ )
        self.__sep(False)
        if "script" in self.cfg:
            if self.cfg["script"]:
                self.__ne("Reference script",self.cfg["script"])
            else:
                self.__ne("Reference script","none given")
        if "refctm" in self.cfg:
            self.__ne("Reference alignment",self.cfg["refctm"])
        if "sysctm" in self.cfg:
            self.__ne("System output",self.cfg["sysctm"])
        if "uem" in self.cfg:
            if self.cfg["uem"]:
                self.__ne("Filtering UEM",self.cfg["uem"])
        self.__sep()

    def interim(self):
        self.__sep()
    
        for fn in self.finfo:
            fi = self.finfo[fn]

            anr = fi["act_nref"] 
            nr  = fi["nref"]
            anh = fi["act_nhyp"]
            nh  = fi["nhyp"] 
            m = fi["nmatch"]
            am  = fi["act_nmatch"] 

            print(fn ,"#ref %d/%d #hyp %d/%d match %d/%d" % ( anr, nr , anh , nh , anh , nh ))

            prec     = am / float(anh)
            rec      = am / float(anr)
            if prec + rec > 0:
                fmeasure = 2 * prec * rec / ( prec + rec )
            else:
                fmeasure = 0.0
            print("prec %.4f rec %.4f f %.4f" % ( prec , rec , fmeasure))

    def total(self):
        self.__sep()
        print( "Final results" )
        self.__sep()

        anr = anh = am = 0
        for fn in self.finfo:
            fi = self.finfo[fn]
            anr += fi["act_nref"] 
            anh += fi["act_nhyp"]
            am  += fi["act_nmatch"] 

        prec     = am / float(anh)
        rec      = am / float(anr)
        if prec + rec > 0:
            fmeasure = 2 * prec * rec / ( prec + rec )
        else:
            fmeasure = 0.0

    
        self.__ne("Effective #words in reference", str(anr) )
        self.__ne("Effective #words in hypothesis", str(anh) )
        self.__ne("Match count", str(am) )
        self.__sep()
        self.__ne("Precision", "%.4f" % prec )
        self.__ne("Recall", "%.4f" % rec )
        self.__ne("F", "%.4f" % fmeasure )
        self.__sep(True)

    # ----------------------------------------------------
    def __sep(self,emph=False):
        if emph:
            self.out.write( "=" * 90  + '\n' )
        else:
            self.out.write( "-" * 90  + '\n' )
    def __ne(self,l,r):
        print( "%-30s : %s" % (l,r))

# =======================================================
# Word matchin object 
# =======================================================
class WordMatch:
    def __init__(self , mtype , confdict ):
        if mtype == "paddedtime":
            self.match = self.__timematch
            self.__timematch__init(confdict)
        elif mtype == "overlap":
            self.match = self.__overlap
            self.__overlap__init(confdict)
        elif mtype == "snfe":
            self.match = self.__snfe
            self.__snfe__init(confdict)
        else:
            raise ValueError

    # ---------------------------------------------------------------- SNFE
    def __snfe__init(self,confdict):
        self.overlap_thresh = confdict['threshold']
    
    def __snfe(self,ref,hyp):
        if hyp[2] == ref[2]:
            v = self.overlap_thresh
            o =  min( ref[1] , hyp[1] ) - max( ref[0] , hyp[0] )
            dr = float( ref[1] - ref[0] )
            dh = float( hyp[1] - hyp[0] )
            if (dh - o) / min(dr,dh) <= v:
                #print (dh - o) / min(dr,dh) , o , dr , dh 
                return True
        return False

    # ---------------------------------------------------------------- OVERLAP 
    def __overlap__init( self , confdict ):
        self.overlap_thresh = confdict['threshold']

    def __overlap( self , ref , hyp ):
        v = self.overlap_thresh
        if hyp[2] == ref[2]:
            o =  min( ref[1] , hyp[1] ) - max( ref[0] , hyp[0] )
            d = max(float( ref[1] - ref[0] ), 0.001)
            if o/d >= v:
               return True
        return False

    # --------------------------------------------------------------- BOUNDARY 
    def __timematch__init(self,confdict):
        self.timematch_padding = confdict['padding']

    def __timematch(self, ref , hyp ):
        v = self.timematch_padding
        if hyp[0] >= ref[0] - v and hyp[0] <= ref[0] + v and hyp[2] == ref[2]: #hyp[1] >= ref[1] - v and hyp[1] <= ref[1] + v and hyp[2] == ref[2]: 
            return True
        return False

# =======================================================
# MAIN
# =======================================================
def main():
    global verbose, verboseprint

    # command line parsing
    p = argparse.ArgumentParser(
        usage='%(prog)s [options] RefCTM SysCTM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        --------------------------------------------------------------------
        Scorring of scripted word alignment.

        Developed for use in the MGB Challenge.
    
        Full description available at 

        http://mini.dcs.shef.ac.uk/resources/sw/alignscoring
        --------------------------------------------------------------------
        '''),
        epilog=textwrap.dedent('''\
        --------------------------------------------------------------------
        (c) 2015 Thomas Hain, University of Sheffield
        --------------------------------------------------------------------
        ''')
        )
    p.add_argument('--version', action='version', version= '%(prog)s ' + __version__ )

    p.add_argument("refctm" , metavar = "RefCTM" ,
                    help = "reference timses and words in CTM format")
    p.add_argument("sysctm" , metavar = "SysCTM" ,
                    help = "system output times and words in CTM format")
    p.add_argument("--verbose","-v",action="count")

    # script 
    p.add_argument("--script",metavar = "ScriptSTM" )

    # uem filtering 
    p.add_argument("--ignoreintervals",metavar = "ignoreUEM",
                   help="Ignore words in specified time intervals")

    # matching options
    group = p.add_mutually_exclusive_group(required=True)	
    group.add_argument("--match_bound",action="store",nargs=1,type=int,
                        metavar="FRAMES",
                        help = "boundary frames counted in 10ms units")
    group.add_argument("--match_overlap",action="store", type = float,
                        metavar="THRESHOLD",
                        help = "minimum percentage of overlap")
    group.add_argument("--match_snfe",action="store", type = float,
                        metavar="THRESHOLD",
                        help = "minimum percentage of overlap")
    group.add_argument("--match_reloverlap",action="store",nargs=1,
                        metavar="THRESHOLD")

    # outional match output 
    p.add_argument("--matchres",metavar = "FILE",
                   help="write result of word match to file")

    try:
        arg = p.parse_args(sys.argv[1:])
    except:
        #p.print_help()
        sys.exit(1)

    # results object
    res = Results( {"refctm":arg.refctm,
                    "sysctm":arg.sysctm,
                    "script":arg.script,
                    "uem"   :arg.ignoreintervals,
                   }) 
    res.header()

    # verbosity
    verbose = arg.verbose
    if arg.verbose:
        def verboseprint(level,*args):
            global verbose
            if level < verbose:
                for arg in args:
                    print(arg)
    else:   
        verboseprint = lambda *a: None      # do-nothing function

    # reference processing 
    # - loading 
    # - aligning 
    # - filtering 

    print("... reading reference")
    ref = TimedWordLabelFileset()
    if arg.refctm:
        ref.read(arg.refctm)

    if arg.script:
        print( "... aligning script to reference ")
        ref.readstm( arg.script )	
        ref.alignscript() 

    if arg.ignoreintervals:
        ref.filter_uem( arg.ignoreintervals ) 

    # system output processing 
    # - loading 
    # - aligning 
    # - filtering 
    print("... reading system output")
    hyp = TimedWordLabelFileset()
    if arg.sysctm:
        hyp.read(arg.sysctm)

    if arg.script:
        print("... aligning script to system output")
        hyp.readstm( arg.script )	
        hyp.alignscript() 

        for lf in hyp.lf.itervalues():
            if lf.scriptcounts[1] > 0:
                print(lf.name , lf.scriptcounts)
                lf.alignscript_print()

    if arg.ignoreintervals:
        hyp.filter_uem( arg.ignoreintervals ) 

    # cerate match metric
    if arg.match_bound:
        wm = WordMatch( "paddedtime" , {"padding":arg.match_bound[0] * 10 } )
    elif arg.match_overlap:
        wm = WordMatch( "overlap" , {"threshold":arg.match_overlap} )
    elif arg.match_snfe:
        wm = WordMatch( "snfe" , {"threshold":arg.match_snfe} )
    else:
        raise

    # perform match
    print("... matching ")
    if arg.matchres:
        f = open(arg.matchres,"w")
        ref.match( wm , hyp , res ,f)
        f.close()
    else:
        ref.match( wm , hyp , res )

    res.interim()
    res.total()

# =======================================================
# script handling 
# =======================================================
if __name__ == "__main__":
    #main()
    try:
        main()
    except ValueError:
        print( "VALUE ERROR:" , sys.exc_info()[1])
    except SystemExit:
        print ("... premature exit")
    except:
        print ("Unexpected error:", sys.exc_info()[0])
        raise
