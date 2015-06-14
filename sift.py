#!/usr/bin/python
#-*- coding:utf-8 -*-
import numpy as np
import cv2
from matplotlib import pyplot as plt
import glob
import os
import commands

class Match_count:
    def __init__(self):
        self.match_count = 0
        self.id = 0
    def __init__(self,_match_count,_id):
        self.match_count = _match_count
        self.id = _id
    def __lt__(self,other):
        if self.match_count == other.match_count:
            return self.id < other.id
        return self.match_count > other.match_count

def get_only_image_name(image_filename):
    return image_filename.split('/')[-1].split('.')[0]

def create_directory(directory_name):
    if not os.path.exists(directory_name):
        command = 'mkdir %s' % directory_name
        ret = commands.getoutput(command)

def get_feature(image_filename):
    base_path = 'feature/'
    if not os.path.exists('feature'):
        create_directory('feature')
    only_image_name = get_only_image_name(image_filename)
    numpy_saved_name = base_path+only_image_name+'.npy'
    if os.path.exists(numpy_saved_name):
        return np.load(numpy_saved_name)
    image = cv2.imread(image_filename,0)
    sift = cv2.SIFT()
    kp1, des1 = sift.detectAndCompute(image,None)
    np.save(numpy_saved_name,des1)
    print numpy_saved_name + ' is created'
    return des1

def get_match_count(des1,des2):
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)

    cnt = 0
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            cnt = cnt + 1
    return cnt

if __name__ == '__main__':
    path = 'FERET_subset/'
    fa_filenames = glob.glob(path+'fa/*.jpg')
    fb_filenames = glob.glob(path+'fb/*.jpg')
    qr_filenames = glob.glob(path+'qr/*.jpg')
    ql_filenames = glob.glob(path+'ql/*.jpg')
    fan = len(fa_filenames)
    fbn = len(fb_filenames)
    qrn = len(qr_filenames)
    qln = len(ql_filenames)

    fa_features = []
    fb_features = []
    qr_features = []
    ql_features = []
    for filename in fa_filenames:
        fa_features.append(get_feature(filename))
    for filename in fb_filenames:
        fb_features.append(get_feature(filename))
    for filename in qr_filenames:
        qr_features.append(get_feature(filename))
    for filename in ql_filenames:
        ql_features.append(get_feature(filename))

    if not os.path.exists('out'):
        create_directory('out')
    if not os.path.exists('out/fb.out'):
        rank_k = [ 0 for i in xrange(fan) ]
        for i in xrange(fbn):
            print 'fb_'+str(i)+' is testing : ',
            match_count = []
            for j in xrange(fan):
                cur_match_count = get_match_count(fb_features[i],fa_features[j])
                match_count.append(Match_count(cur_match_count,j))
            match_count.sort()
            for j in xrange(len(match_count)):
                is_find = False
                for k in xrange(0,j+1):
                    if match_count[k].id == i:
                        is_find = True
                if is_find:
                    rank_k[j] = rank_k[j] + 1
            print rank_k
        with open('out/fb.out','w') as fp:
            for rank in rank_k:
                fp.write(str(rank)+' ')

    if not os.path.exists('out/qr.out'):
        rank_k = [ 0 for i in xrange(fan) ]
        for i in xrange(qrn):
            print 'qr_'+str(i)+' is testing : ',
            match_count = []
            for j in xrange(fan):
                cur_match_count = get_match_count(qr_features[i],fa_features[j])
                match_count.append(Match_count(cur_match_count,j))
            match_count.sort()
            for j in xrange(len(match_count)):
                is_find = False
                for k in xrange(0,j+1):
                    if match_count[k].id == i:
                        is_find = True
                if is_find:
                    rank_k[j] = rank_k[j] + 1
            print rank_k
        with open('out/qr.out','w') as fp:
            for rank in rank_k:
                fp.write(str(rank)+' ')

    if not os.path.exists('out/ql.out'):
        rank_k = [ 0 for i in xrange(fan) ]
        for i in xrange(qln):
            print 'ql_'+str(i)+' is testing : ',
            match_count = []
            for j in xrange(fan):
                cur_match_count = get_match_count(ql_features[i],fa_features[j])
                match_count.append(Match_count(cur_match_count,j))
            match_count.sort()
            for j in xrange(len(match_count)):
                is_find = False
                for k in xrange(0,j+1):
                    if match_count[k].id == i:
                        is_find = True
                if is_find:
                    rank_k[j] = rank_k[j] + 1
            print rank_k
        with open('out/ql.out','w') as fp:
            for rank in rank_k:
                fp.write(str(rank)+' ')

    x = [ i+1 for i in xrange(fan) ]
    with open('out/fb.out','r') as fp:
        fby = fp.read().rstrip().split(' ')
    for fbc in fby:
        fbc = (float(fbc)/fan)*100
    with open('out/qr.out','r') as fp:
        qry = fp.read().rstrip().split(' ')
    for qrc in qry:
        qrc = (float(qrc)/fan)*100
    with open('out/ql.out','r') as fp:
        qly = fp.read().rstrip().split(' ')
    for qlc in qly:
        qlc = (float(qlc)/fan)*100
    plt.title('CMC curve')
    plt.xlabel('k')
    plt.ylabel('rank-k percentage')
    plt.axis([0,fan,0,fan+1])
    s = 'fb rank-1 : %s%%\nqr rank-1 : %s%%\nql rank-1 : %s%%'%(fby[0],qry[0],qly[0])
    plt.text(((fan-1+1)/3.0)*2.2,(fan+1+1)/13.0,s)
    plt.plot(x,fby,x,qry,x,qly,lw=2)
    plt.show()
