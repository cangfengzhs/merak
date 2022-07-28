#!/usr/bin/env python3
from transformers import AlbertModel, BertTokenizer
import numpy as np
import os
from multiprocessing import Process, Queue
from tqdm import tqdm
import torch


# download from http://thuctc.thunlp.org/message
dataset_path = "THUCNews/"

text_queue = Queue(maxsize=10000)

embedding_queue = Queue(maxsize=10000)

process_count = 2

total_count = 0

def read_text():
    global total_count, text_queue
    with tqdm(desc="read", total=total_count, position=1) as pbar:
        for t in os.listdir(dataset_path):
            for file in os.listdir(dataset_path+t):
                with open(dataset_path+t+"/"+file) as f:
                    text = f.read()
                    text = text.replace("\n", " ")
                    text_queue.put(text)
                    pbar.update(1)
    text_queue.put("###finish###")


def embedding():
    global text_queue, embedding_queue
    with torch.no_grad():
        tokenizer = BertTokenizer.from_pretrained("clue/albert_chinese_tiny")
        model = AlbertModel.from_pretrained("clue/albert_chinese_tiny")
        while True:
            text = text_queue.get()
            if text == "###finish###":
                text_queue.put("###finish###")
                break
            inputs = tokenizer([text], return_tensors="pt",
                               padding=True, truncation=True, max_length=512)
            outputs = model(**inputs)
            embedding_queue.put((text, outputs.pooler_output[0].numpy()))
        embedding_queue.put(())


def save():
    global embedding_queue, process_count, total_count
    count = 0
    vector_list = []
    text_list = []
    part = 1
    with tqdm(desc="save", total=total_count, position=2) as pbar:
        while count < process_count:
            embedding = embedding_queue.get()
            if len(embedding) == 0:
                count += 1
                continue
            vector_list.append(embedding[1])
            text_list.append(embedding[0])
            pbar.update(1)
            if len(vector_list) == 1000:
                vector_arr = np.array(vector_list)
                text_arr = np.array(text_list)
                np.savez_compressed("nlp_vector/part{}".format(part),
                                    vector=vector_arr, text=text_arr)
                vector_list = []
                text_list = []
                part += 1
        if len(vector_list)!=0:
            vector_arr = np.array(vector_list)
            text_arr = np.array(text_list)
            np.savez_compressed("nlp_vector/part{}".format(part),
                                vector=vector_arr, text=text_arr)


def main():
    global total_count
    for t in os.listdir(dataset_path):
        total_count = total_count + len(os.listdir(dataset_path+t))
    read_p = Process(target=read_text, args=())
    embedding_p_list = []
    for _ in range(process_count):
        embedding_p = Process(target=embedding, args=())
        embedding_p_list.append(embedding_p)
    save_p = Process(target=save, args=())
    read_p.start()
    for p in embedding_p_list:
        p.start()
    save_p.start()
    read_p.join()
    for p in embedding_p_list:
        p.join()
    save_p.join()

if __name__=="__main__":
    main()