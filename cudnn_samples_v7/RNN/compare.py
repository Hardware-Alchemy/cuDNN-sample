#This script can compare the result files with the golden files and report the status: pass or failed\
#Usage: python compare_result.py results.txt golden.txt
import os, sys, re

patterns = ['{key1}\s+checksum\s+([.eE+0-9]+)\s+{key2}\s+checksum\s+([.eE+0-9]+)\s+{key3}\s+checksum\s+([.eE+0-9]+)', #3 similar keys as below each line
            '{key1}\s+checksum\s+([.eE+0-9]+)\s+{key2}\s+checksum\s+([.eE+0-9]+)', #2 similar keys as below each line
            '{key}\s+checksum\s+([.eE+0-9]+)',   #one key each line: di checksum 6.676003E+01
            '{key}[: ]+([0-9]+)\s+GFLOPS[, ]+\\(([0-9]+)\s+GFLOPS\\)[, ]+\\(([0-9]+)\s+GFLOPS\\)', #1 key each line with more returns
            '{key}[: ]+([0-9]+)\s+GFLOPS']       #one key each line: Forward: 673 GFLOPS
#keys = [('i', 'c', 'h'), ('di', 'dc', 'dh'), ('i', 'h'), ('di', 'dh'), 'dw', 'Backward', 'Forward']
keys = [('i', 'c', 'h'), ('di', 'dc', 'dh'), ('i', 'h'), ('di', 'dh'), 'dw'] # skip the last 2 targets
pats = [0,0,1,1,2,3,4]
datnum = [len(k) if isinstance(k, tuple) else (3 if k == 'Backward' else 1) for k in keys]
#tol = 1.0e-3
def compare_results(ftarget, fgolden):
    assert ftarget and fgolden, 'No enough input files given!'
    print ftarget, fgolden
    targ, _ = get_results_from_file(ftarget)
    golden, tol = get_results_from_file(fgolden, golden=True)

    ret = 0
    assert targ and golden, 'targets or golen results not generated!'
    for k, vals in golden.iteritems():
        if not isinstance(vals, list):
            vals = [vals]
            targ[k] = [targ[k]]
        for idx, v in enumerate(vals):
            tval = float(targ[k][idx])
            gval = float(v)
            err = None
            if tol[k]['type'] == 'rel':
                err = abs((tval-gval)/max(gval,tval)) # clamp rel_err <= 1
            elif tol[k]['type'] == 'abs':
                err = abs(tval-gval)
            assert err is not None, 'Error is Empty!'
            tol_i = tol[k]['val']
            #print 'k,t,g,err',k,tval, gval, err
            if err > tol_i:
                print 'FAILED %s=%s Error: %.2e vs. golden (%s) with tol (%.2e)'%(k, targ[k][idx], err, v, tol_i)
                ret = 1
            else:
                print 'PASSED %s=%s Error: %.2e vs. golden (%s) with tol (%.2e)'%(k, targ[k][idx], err, v, tol_i)
    if ret == 0:
        print 'ALL PASSED'
    return ret

def _get_tolerance_line(line):
    """get a data item for a tolerance line with format (each line only one item):
    i: type=rel, 1e-3
    """
    assert line, 'Empty line!'
    line = line.strip().replace(' ','')
    stmp = line.split(':')
    key = stmp[0]
    _type, _val = stmp[1].split(',')
    _type = _type.split('=')[-1]
    tol={key:{'type':_type, 'val':float(_val)}}
    return tol

def get_results_from_file(fname, golden=False):
    assert fname, 'No file name given!'
    ret = {}
    tol = {}
    is_tolerance = False
    with open(fname, 'r') as fin:
        lines = fin.readlines()
    if len(lines) == 1:
        lines = lines[0].split('\r')
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        val = get_valpat_line(line)
        if val:
            ret = dict(ret, **val)
        if golden:
            if 'TOLERANCE' in line: # the next line is the tol value
                is_tolerance = True
            elif is_tolerance:
                _tol = _get_tolerance_line(line)
                tol = dict(tol, **_tol)

    return ret, tol

def get_valpat_line(line):
    for idx, key in enumerate(keys):
        Ndat = datnum[idx]
        if isinstance(key, tuple):
            format_expr = {}
            for j in range(Ndat):
                format_expr['key%d'%(j+1)] = keys[idx][j]
            ret = re.search(patterns[pats[idx]].format(**format_expr), line)
            if ret:
                vals = {}
                for j in range(Ndat):
                    vals[key[j]] = ret.group(j+1)
                return vals
        else:
            ret = re.search(patterns[pats[idx]].format(key=key), line)
            if ret:
                if Ndat >1:
                    #print Ndat, key, datnum, idx
                    return {key:[ret.group(j+1) for j in range(Ndat)]}
                else:
                    return {key:ret.group(1)}
    return None

def str_test():
    s='Forward: 673 GFLOPS'
    s1='Backward: 835 GFLOPS, (654 GFLOPS), (1155 GFLOPS)'
    s2='i checksum 1.315793E+06 h checksum 1.315212E+05'
    s3='di checksum 6.676003E+01 dh checksum 6.425050E+01'
    s4='dw checksum 1.453750E+09'
    print get_valpat_line(s1)
    print get_valpat_line(s)
    print get_valpat_line(s2)
    print get_valpat_line(s3)
    print get_valpat_line(s4)
if __name__ == '__main__':
    #str_test()
    #print get_results_from_file('results.txt')
    #print get_results_from_file('golden.txt', golden=True)
    sys.exit(compare_results(sys.argv[1], sys.argv[2]))


