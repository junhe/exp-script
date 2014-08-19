import os, sys, time
import pprint
import math



def load_commits():
    f = open('./commits-forlinus2..mmc-merge', 'r')
    commitlist = f.readlines()
    f.close()

    commitlist = [x.strip()[:13] for x in commitlist]
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

    step = (end_index - start_index + 1) / float(npartitions)
    step = int(math.ceil(step))
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

def assign_job(clusters, testlist, distr_image):
    ntests = len(testlist)
    nclusters = len(clusters)
    if ntests % nclusters != 0:
        print 'Sorry we only handle aligned cases'
        exit(1)
    avgtests = ntests / nclusters
    for clusteri in range(nclusters):
        clustersuffix = clusters[clusteri]
        print '############ Cluster', clustersuffix
        thisstart = clusteri * avgtests
        clustertests = testlist[thisstart:thisstart+avgtests]
        script = gen_shell_script(clustersuffix, clustertests, do_dist_img=distr_image)
        print script
            

def gen_shell_script(version, patches, jobtag, clustersuffix, do_dist_img):
    base_str = ""\
        "python ~/workdir/exp-script/lazy-build-from-ops.py"\
        " {version} {patches} {jobtag} 0-7 {clustersuffix} notusefinished {distr_image}download,"\
        "patch,make_oldconfig,make_kernel,tar_src,pull_src_tar,"\
        "untar_src,install_kernel,set_default_kernel,reboot,wait_for_alive,"\
        "never_writeback,check_current_version,clean,run_exp"

    if do_dist_img == True:
        distr_image = 'distribute_images,'
    else:
        distr_image = ''

    cmd = base_str.format(
            version = version,
            patches = patches,
            jobtag  = jobtag,
            clustersuffix = clustersuffix,
            distr_image   = distr_image)
    return cmd

def get_result_filename(version, jobtag):
    filename = "agga.fixedimg-{version}.txt-{jobtag}"
    filename = filename.format(version=version,
                               jobtag = jobtag)
    return filename


def gen_analysis_cmd(aggafiles, nodestr, clustersuffix):
    "nodestr example: 0-7"
    base_str = "python ~/workdir/exp-script/analyze_agga.py "\
                    "{aggafiles} {nodenums} {clustersuffix}"

    cmd = base_str.format(aggafiles=aggafiles,
                          nodenums=nodestr,
                          clustersuffix=clustersuffix)
    return cmd

def gen_analysis_cmd2(version, jobtag, nodestr, clustersuffix):
    filename = get_result_filename(version, jobtag)
    cmd = gen_analysis_cmd(filename, nodestr, clustersuffix)
    return cmd


def gen_agga_check_cmd(version, jobtag):
    filename = get_result_filename(version, jobtag)
    base_str = "cd ~/workdir/metawalker/src/ && wc -l {aggafiles} && cd -"
    cmd = base_str.format(aggafiles=filename)
    return cmd


def gen_plot_strings(version, jobtag):
    "nodestr example: 0-7"
    base_str = "ext4.1.auto-fixedimage-agga.fixedimg-{version}.txt-{jobtag}.Rdata"
    filename = base_str.format(version=version, jobtag=jobtag)

    # generate scp command to execute on mac to download
    print '################ cmd for download'
    ssh_str = "scp jhe@marmot-ops.pdl.cmu.edu:"\
                "./workdir/sensitivity-analysis/{rdatafile} "\
                "/Users/junhe/workdir/curstage/analysis-scripts/datafiles ; "
    downloadstr = ""
    for file in [filename]:
        cmd = ssh_str.format(rdatafile=file)
        downloadstr += cmd
    print downloadstr

    files4r = '",\n"'.join([filename])
    files4r = '"'+files4r+'"'
    print '################ file string for R plot'
    print files4r


def main():
    clusters = ['noloop003.plfs']
    jobtags  = ['paperspace']

    analysiscluster = 'anacluster'
    analysisnodes = '0-3'

    version = '3.12.5'
    patches = 'nopatches'
    do_dist_img = True

    for clustersuffix, jobtag in zip(clusters, jobtags): 
        print gen_shell_script(version, patches, jobtag, clustersuffix, do_dist_img)
    
    for clustersuffix, jobtag in zip(clusters, jobtags): 
        print gen_analysis_cmd2(version, jobtag, analysisnodes, analysiscluster)
    for clustersuffix, jobtag in zip(clusters, jobtags): 
        print gen_agga_check_cmd(version, jobtag)
    for clustersuffix, jobtag in zip(clusters, jobtags): 
        gen_plot_strings(version, jobtag)


if __name__ == '__main__':
    main()


