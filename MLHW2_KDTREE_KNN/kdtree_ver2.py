import csv
import numpy as np
import os
import pprint
import math
class kd_node:
    def __init__(self ,point = None, split = None, left_child_init = None, right_child_init = None, knn_traversed_init = False): #default constructor of the class
        self.point = point #dat a point
        self.split = split
        self.left_child = left_child_init
        self.right_child = right_child_init
        self.knn_traversed = knn_traversed_init

def fileparsing():
    with open('train.csv','r') as opened_file : #use r for reading a file
        parsed_data = csv.reader(opened_file)
        all_data_list = list(parsed_data)

    for i in range(1,len(all_data_list)):
        for j in range(2,11):
            all_data_list[i][j]=float(all_data_list[i][j])

    return all_data_list

def append_knnquery_boolean(all_data_list):
    for i in range(0,len(all_data_list)):
        all_data_list[i].append('false')

def create_kd_tree(root,node_data_set,split_attribute):
    node_data_len = len(node_data_set)
    median_index = int(len(node_data_set)/2)
    node_data_set.sort(key=lambda x:x[split_attribute])
    point = node_data_set[median_index]
    root =  kd_node(point,split_attribute)

    if node_data_len ==1: #build over
        print("Leaf ",root.point[0], " split ",root.split)
        return root

    if split_attribute == 10:
        split_attribute = 2
    else:
        split_attribute += 1

    if median_index > 0:
        root.left_child = create_kd_tree(root.left_child, node_data_set[:median_index],split_attribute)
    if median_index < len(node_data_set)-1:
        root.right_child = create_kd_tree(root.right_child, node_data_set[median_index+1:],split_attribute)

    return root

def tree_traverse_check(current_kd_node,cnt):
    current_kd_node.knn_traversed = False
    #print("traversed ID ",current_kd_node.point[0]," split ",current_kd_node.split)
    if current_kd_node.left_child:
        tree_traverse_check(current_kd_node.left_child,cnt+1)
    if current_kd_node.right_child:
        tree_traverse_check(current_kd_node.right_child,cnt+1)

def validate(root,training_set):
    validation_set = []
    for i in range(0,36):
        validation_set.append(training_set[i])
    #what to output
    output_file = open('result.txt','w') #Write mode
    #integer declaration
    predicted_correct = 0
    #string class declaration
    original_class = None
    final_predicted_class = None
    #hashmap declaration for voting system
    knn_result_hash = {'cp':0,'im':0,'pp':0,'imU':0,'om':0,'omL':0,'imL':0,'imS':0}
    classname_set = ['cp','im','pp','imU','om','omL','imL','imS']
    #KNN main core
    first_three_output = [[] for i in range(3)]
    for knn_query in [1,5]:
        first_three_output = [[] for i in range(3)]
        predicted_correct += 1
        for query_index in range(0,3):
            query_point = validation_set[query_index] #take the point for querying
            original_class = query_point[11]
            for search_hash in range(len(classname_set)): #clear the hash map for the query from each point for voting
                knn_result_hash[classname_set[search_hash]] = 0

            tree_traverse_check(root,0) #clear all traversed mark to false first,which symbolized non traversed
            for individual_knn_query in range(0,knn_query):
                print("query_point ",query_point[0]," knn now " ,individual_knn_query)
                NN,predicted_class = KNN_core(root,query_point)
                knn_result_hash[predicted_class] += 1
                if(query_index >=0 and query_index<3): #outputresult
                    first_three_output[query_index].append(NN)
            #input()
            max_voted_class = 0
            for search_hash in range(len(classname_set)): #voting for the best result
                if knn_result_hash[classname_set[search_hash]] > max_voted_class:
                    max_voted_class = knn_result_hash[classname_set[search_hash]]
                    final_predicted_class = classname_set[search_hash]
            print("Original ",original_class," predicted class",final_predicted_class)
            if(original_class == final_predicted_class):
                print("Predicted correct ")
                predicted_correct+=1
            ###input
        print("A KNN Is end ",query_index,"Acc is ",float(predicted_correct)/36.0)
        print('\n'+'\n'+'\n'+'\n'+'\n')
        output_file.write('KNN accuracy: '+str(float(predicted_correct)/36.0)+'\n')
        for output_index in range(len(first_three_output[0])):
            output_file.write(first_three_output[0][output_index]+' ')
        output_file.write('\n')
        for output_index in range(len(first_three_output[1])):
            output_file.write(first_three_output[1][output_index]+' ')
        output_file.write('\n')
        for output_index in range(len(first_three_output[2])):
            output_file.write(first_three_output[2][output_index]+' ')
        output_file.write('\n')

        output_file.write('\n')

    output_file.close()

def KNN_core(root,query_point):

    nearest = None #just want the data in it
    min_dist = 9999.9999 #calculaue_distance (query_point,nearest.point)
    traversed_point = []
    cur_point = root #has to be the all node
    #binary search in k-dimensional space
    #print("query datapt",query_point)
    print('\n')
    while cur_point != None:
        traversed_point.append(cur_point)
        print("traversed to",cur_point.point[0], "split via ",cur_point.split," tvsed ",cur_point.knn_traversed)
        cur_dist = calculaue_distance(query_point,cur_point.point)
        cur_split =  cur_point.split
        if cur_dist < min_dist and cur_point.knn_traversed == False:
            nearest = cur_point
            min_dist = cur_dist
            print("smaller")

        print("min dst ",min_dist)
        if( query_point[cur_split] < cur_point.point[cur_split]):
            cur_point = cur_point.left_child
        else:
            cur_point = cur_point.right_child
    #backtrace

    while traversed_point:
        back_point = traversed_point.pop()
        cur_split = back_point.split
        #do i need to enter parent's space for searching
        print("BACK TRACK TO ",back_point.point[0], "split via ",back_point.split," tvsed ",back_point.knn_traversed)
        print("min dist ",min_dist," with hyprectl dist ",abs(float(query_point[cur_split]) - float(back_point.point[cur_split])))
        # input
        if back_point.left_child == None and back_point.right_child == None:
            if calculaue_distance(query_point,back_point.point) < min_dist and back_point.knn_traversed == False:
                nearest = back_point
                min_dist = calculaue_distance(query_point,back_point.point)
                print("LEAF NODE ID ",back_point.point[0])
        else:
            if abs(float(query_point[cur_split]) - float(back_point.point[cur_split])) < min_dist:
                if(query_point[cur_split] < back_point.point[cur_split]): #the other side
                    cur_point = back_point.right_child
                else:
                    cur_point = back_point.left_child
                if cur_point != None: #is the retraversed one
                    traversed_point.append(cur_point)
                    print("NON LEAF NODE")
                    back_trace_distance = calculaue_distance(query_point,cur_point.point)
                    if back_trace_distance < min_dist and cur_point.knn_traversed == False:
                        print("BETTER!!!!!! \n")
                        nearest = cur_point
                        min_dist = back_trace_distance

    if nearest:
        nearest.knn_traversed = True
        nearest_id = nearest.point[0]
        nearest_class = nearest.point[11]
        print("nearest point ",nearest.point," spt ",nearest.split," knn retraversed ", nearest.knn_traversed)
        return nearest_id,nearest_class

    return query_point[0],query_point[11]
def calculaue_distance(point1,point2):
    dist=0.0
    for i in range(2,11):
        dist+=(float(point1[i])-float(point2[i]))*(float(point1[i])-float(point2[i]))

    dist2=dist
    print(point1[0],"<--------------->",point2[0],"dist ",math.sqrt(dist2),)
    return math.sqrt(dist)

if __name__ == "__main__":
    training_set = fileparsing()
    original_training_set = fileparsing()

    training_set = training_set[1:len(training_set)] #remove the first one
    original_training_set = original_training_set[1:len(original_training_set)]
    #print("ts0",training_set[0])
    append_knnquery_boolean(training_set)
    root = None
    root = create_kd_tree(root,training_set,2)
    tree_traverse_check(root,1)
    #print("Root is ",root.point, "split via ",root.split ," 69 is ",original_training_set[69])
    #print("163 num and 193 num ",original_training_set[163][0],"     ",original_training_set[193][0])
    print("min dst 2 ",calculaue_distance(original_training_set[1],original_training_set[2]))
    print("min dst 213 ",calculaue_distance(original_training_set[1],original_training_set[213]))
    print("min dst 23 ",calculaue_distance(original_training_set[0],original_training_set[23]))
    #first_tree_traverse_check(root)
    validate(root,original_training_set)
    #total_cnt=0
    #tree_traverse_check(root,total_cnt)
    #print(total_cnt)
