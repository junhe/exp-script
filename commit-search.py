import os, sys, time
import pprint



def load_commits():
    f = open('./commits-hashonly-first-parent-v3.5..v3.6-rc1', 'r')
    commitlist = f.readlines()
    f.close()

    commitlist = [x.strip() for x in commitlist]
    return commitlist

def test_what(start_index, end_index, commitlist, npartitions):
    """
    start and end are index numbers in commitlist
    npartitions is the number of partitions of the search,
    if it is 2, it is a binary search. you need npartitions-1
    runs to finish one level of search.

    return:
    this function return the commit name and its index number
    for example: if npartitions=2, it will return 1 commit in the middle
    """
    print 'start_index',start_index,\
            'end_index',end_index,\
            'npartitions',npartitions

    step = (end_index - start_index + 1) / npartitions
    print 'step', step

    pick_indices = []
    for i in range(npartitions-1):
        # pick npartitions-1 indices
        pick_indices.append(start_index+(i+1)*step)
    
    ret_list = []
    for i in pick_indices:
        dic = {}
        dic['index'] = i
        dic['commithash'] = commitlist[i]
        ret_list.append(dic)

    return ret_list

def assign_job(clusters, testlist):
    ntests = len(testlist)
    nclusters = len(clusters)
    if ntests % nclusters != 0:
        print 'Sorry we only handle aligned cases'
        exit(1)
    avgtests = ntests / nclusters
    for clusteri in range(nclusters):
        clustersuffix = clusters[clusteri]
        print '************** Cluster', clustersuffix
        thisstart = clusteri * avgtests
        clustertests = testlist[thisstart:thisstart+avgtests]
        script = gen_shell_script(clustersuffix, clustertests, do_dist_img=True)
        print script
            

def gen_shell_script(clustersuffix, testlist, do_dist_img):
    base_str = "python ~/workdir/exp-script/lazy-build-from-ops.py"\
        " git nopatches {commit} 0-7 {clustersuffix} notusefinished {distr_image}download,checkout,"\
        "patch,make_oldconfig,make_kernel,tar_src,pull_src_tar,"\
        "untar_src,install_kernel,set_default_kernel,reboot,wait_for_alive,"\
        "never_writeback,check_current_version,clean,run_exp"
    script = ""
    for i,test in enumerate(testlist):
        print test
        commit = test['commithash']
        if i == 0 and do_dist_img == True:
            distr_image = 'distribute_images,'
        else:
            distr_image = ''
        mystr = base_str.format(commit         =commit,
                                clustersuffix  =clustersuffix,
                                distr_image    =distr_image)
        script += mystr + '; '

    return script

def gen_analysis_cmd(nodestr, clustersuffix, testlist):
    "nodestr example: 0-7"
    base_str = "python ~/workdir/exp-script/analyze_agga.py "\
                    "{aggafiles} {nodenums} {clustersuffix}"
    fileprefix = "agga.fixedimg-git.txt-"
    files = [fileprefix+test['commithash'] for test in testlist]
    files = ','.join(files)

    cmd = base_str.format(aggafiles=files,
                          nodenums=nodestr,
                          clustersuffix=clustersuffix)
    return cmd

def gen_agga_check_cmd(testlist):
    "nodestr example: 0-7"
    base_str = "cd ~/workdir/metawalker/src/ && wc -l {aggafiles} && cd -"
    fileprefix = "agga.fixedimg-git.txt-"
    files = [fileprefix+test['commithash'] for test in testlist]
    files = ' '.join(files)

    cmd = base_str.format(aggafiles=files)
    return cmd


def gen_plot_strings(testlist):
    "nodestr example: 0-7"
    base_str = "ext4.1.auto-fixedimage-agga.fixedimg-git.txt-{commithash}.Rdata"
    files = [base_str.format(commithash=test['commithash']) for test in testlist]

    # generate scp command to execute on mac to download
    print '################ cmd for download'
    ssh_str = "scp jhe@marmot-ops.pdl.cmu.edu:"\
                "./workdir/sensitivity-analysis/{rdatafile} "\
                "/Users/junhe/workdir/curstage/analysis-scripts/datafiles && "
    downloadstr = ""
    for file in files:
        cmd = ssh_str.format(rdatafile=file)
        downloadstr += cmd
    print downloadstr

    files4r = '",\n"'.join(files)
    files4r = '"'+files4r+'"'
    print '################ file string for R plot'
    print files4r


def main():
    commitlist = load_commits()
    testlist = test_what(150, 153, commitlist, 4) 
    pprint.pprint(testlist)
    #assign_job([
        #'noloop001.plfs',
        #'noloop002.plfs',
        #'noloop003.plfs'], testlist)
    #print gen_agga_check_cmd(testlist)
    #print gen_analysis_cmd('0-7', 'noloop001.plfs', testlist)
    print gen_plot_strings(testlist)


if __name__ == '__main__':
    main()


