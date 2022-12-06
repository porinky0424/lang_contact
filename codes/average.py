import argparse
import matplotlib.pyplot as plt
import numpy as np
import glob
import re
from organize_data import extract_one_model_data

def ngram_averaged_entropy(ids):
    L_data = [
        # L_1
        { "unigram": [], "bigram": [] },
        # L_2
        { "unigram": [], "bigram": [] },
        # L_3
        { "unigram": [], "bigram": [] },
        # L_4
        { "unigram": [], "bigram": [] },
    ]
    for id in ids:
        files = glob.glob(f"result_md/{id}*.md")
        f = open(files[0], 'r')
        md_text = f.read()
        f.close()

        match = re.search(r'### N-gram entropy\n\n\|\| unigram \| bigram \|\n\|-----\|-----\|-----\|\n\| \$L_1\$ \| (.*?) \| (.*?) \|\n\| \$L_2\$ \| (.*?) \| (.*?) \|\n\|\n\| \$L_3\$ \| (.*?) \| (.*?) \|\n\| \$L_4\$ \| (.*?) \| (.*?) \|\n', md_text)

        L_data[0]["unigram"].append(float(match.group(1)))
        L_data[0]["bigram"].append(float(match.group(2)))
        L_data[1]["unigram"].append(float(match.group(3)))
        L_data[1]["bigram"].append(float(match.group(4)))
        L_data[2]["unigram"].append(float(match.group(5)))
        L_data[2]["bigram"].append(float(match.group(6)))
        L_data[3]["unigram"].append(float(match.group(7)))
        L_data[3]["bigram"].append(float(match.group(8)))
    
    plt.figure(facecolor='lightgray')
    plt.title("Unigram entropy")
    plt.ylabel("entropy")
    plt.bar(
        ["L_1", "L_2", "L_3", "L_4"],
        [np.average(L_data[i]["unigram"]) for i in range(4)],
        yerr=[np.std(L_data[i]["unigram"]) / np.sqrt(len(ids)) for i in range(4)],
        capsize=10,
    )
    plt.savefig(f"averaged_result/{ids[0]}~{ids[-1]}/unigram_entropy.png")

    plt.figure(facecolor='lightgray')
    plt.title("Bigram entropy")
    plt.ylabel("entropy")
    plt.bar(
        ["L_1", "L_2", "L_3", "L_4"],
        [np.average(L_data[i]["bigram"]) for i in range(4)],
        yerr=[np.std(L_data[i]["bigram"]) / np.sqrt(len(ids)) for i in range(4)],
        capsize=10,
    )
    plt.savefig(f"averaged_result/{ids[0]}~{ids[-1]}/bigram_entropy.png")

def topsim_averaged_topsim(ids):
    L_data = [
        # L_1
        { "topsim": [] },
        # L_2
        { "topsim": [] },
        # L_3
        { "topsim": [] },
        # L_4
        { "topsim": [] },
    ]
    for id in ids:
        files = glob.glob(f"result_md/{id}*.md")
        f = open(files[0], 'r')
        md_text = f.read()
        f.close()

        match = re.search(r'### Topsim\n\n\|\| Spearman Correlation \|\n\|-----\|-----\|\n\| \$L_1\$ \| (.*?) \|\n\| \$L_2\$ \| (.*?) \|\n\|\n\| \$L_3\$ \| (.*?) \|\n\| \$L_4\$ \| (.*?) \|\n', md_text)

        L_data[0]["topsim"].append(float(match.group(1)))
        L_data[1]["topsim"].append(float(match.group(2)))
        L_data[2]["topsim"].append(float(match.group(3)))
        L_data[3]["topsim"].append(float(match.group(4)))
    
    plt.figure(facecolor='lightgray')
    plt.title("Topsim")
    plt.ylabel("topsim")
    plt.bar(
        ["L_1", "L_2", "L_3", "L_4"],
        [np.average(L_data[i]["topsim"]) for i in range(4)],
        yerr=[np.std(L_data[i]["topsim"]) / np.sqrt(len(ids)) for i in range(4)],
        capsize=10,
    )
    plt.savefig(f"averaged_result/{ids[0]}~{ids[-1]}/topsim.png")

def extract_L_data(ids):
    L_datas = []
    for id in ids:
        L_data = [
            {
                "test": [],
                "generalization": [],
            } for _ in range(12)
        ]
        files = glob.glob(f"result/{id}*.txt")
        f = open(files[0], 'r')
        raw_text = f.read()
        f.close()

        for i in range(12):
            extract_one_model_data(
                re.compile(r"--------------------L_{0} training start--------------------((.|\s)*?)--------------------L_{0} training end--------------------".format(i+1)),
                raw_text,
                L_data[i],
            )
        L_datas.append(L_data)
    return L_datas

def averaged_change_of_acc(ids, L_datas):
    plt.figure(facecolor='lightgray')
    plt.title("Change of Acc")
    plt.xlabel("epochs")
    plt.ylabel("acc")
    max_epochs = [max([len(L_datas[i][j]["test"]) for i in range(len(L_datas))]) for j in range(4)] # L_1 ~ L_4の最大epochを取得
    plots = []
    for j in range(4): # L_1 ~ L_4
        acc = [0 for _ in range(max_epochs[j])]
        count = [0 for _ in range(max_epochs[j])]
        for i in range(len(L_datas)): # 実行回数
            for k, data in enumerate(L_datas[i][j]["test"]):
                acc[k] += float(data["acc"])
                count[k] += 1
        acc = [a / c for a, c in zip(acc, count)]
        plots.append(plt.plot(np.array([i+1 for i in range(max_epochs[j])]), np.array(acc)))
    plt.legend((plot[0] for plot in plots), (f"L_{i}" for i in range(1, 4+1)), loc=2)
    plt.savefig(f"averaged_result/{ids[0]}~{ids[-1]}/change_of_acc.png")

def averaged_ease_of_learning_freezed_receiver(ids, L_datas):
    plt.figure(facecolor='lightgray')
    plt.title("Ease of Learning (freezed receiver)")
    plt.xlabel("epochs")
    plt.ylabel("acc")
    max_epochs = [max([len(L_datas[i][j]["test"]) for i in range(len(L_datas))]) for j in [4, 6, 8, 10]]
    plots = []
    for j, max_epoch in zip([4, 6, 8, 10], max_epochs):
        acc = [0 for _ in range(max_epoch)]
        count = [0 for _ in range(max_epoch)]
        for i in range(len(L_datas)): # 実行回数
            for k, data in enumerate(L_datas[i][j]["test"]):
                acc[k] += float(data["acc"])
                count[k] += 1
        acc = [a / c for a, c in zip(acc, count)]
        plots.append(plt.plot(np.array([i+1 for i in range(max_epoch)]), np.array(acc)))
    plt.legend((plot[0] for plot in plots), (f"L_{i}" for i in [5, 7, 9, 11]), loc=2)
    plt.savefig(f"averaged_result/{ids[0]}~{ids[-1]}/ease_of_learning_freezed_receiver.png")

def averaged_ease_of_learning_freezed_sender(ids, L_datas):
    plt.figure(facecolor='lightgray')
    plt.title("Ease of Learning (freezed sender)")
    plt.xlabel("epochs")
    plt.ylabel("acc")
    max_epochs = [max([len(L_datas[i][j]["test"]) for i in range(len(L_datas))]) for j in [5, 7, 9, 11]]
    plots = []
    for j, max_epoch in zip([5, 7, 9, 11], max_epochs):
        acc = [0 for _ in range(max_epoch)]
        count = [0 for _ in range(max_epoch)]
        for i in range(len(L_datas)): # 実行回数
            for k, data in enumerate(L_datas[i][j]["test"]):
                acc[k] += float(data["acc"])
                count[k] += 1
        acc = [a / c for a, c in zip(acc, count)]
        plots.append(plt.plot(np.array([i+1 for i in range(max_epoch)]), np.array(acc)))
    plt.legend((plot[0] for plot in plots), (f"L_{i}" for i in [6, 8, 10, 12]), loc=2)
    plt.savefig(f"averaged_result/{ids[0]}~{ids[-1]}/ease_of_learning_freezed_sender.png")

def averaged_entropy(ids, L_datas):
    plt.figure(facecolor='lightgray')
    plt.title("Sender Entropy")
    plt.xlabel("epochs")
    plt.ylabel("entropy value")
    max_epochs = [max([len(L_datas[i][j]["test"]) for i in range(len(L_datas))]) for j in range(4)] # L_1 ~ L_4の最大epochを取得
    plots = []
    for j in range(4): # L_1 ~ L_4
        sender_entropy = [0 for _ in range(max_epochs[j])]
        count = [0 for _ in range(max_epochs[j])]
        for i in range(len(L_datas)): # 実行回数
            for k, data in enumerate(L_datas[i][j]["test"]):
                sender_entropy[k] += float(data["sender_entropy"])
                count[k] += 1
        sender_entropy = [a / c for a, c in zip(sender_entropy, count)]
        plots.append(plt.plot(np.array([i+1 for i in range(max_epochs[j])]), np.array(sender_entropy)))
    plt.legend((plot[0] for plot in plots), (f"L_{i}" for i in range(1, 4+1)), loc=1)
    plt.savefig(f"averaged_result/{ids[0]}~{ids[-1]}/entropy.png")

def averaged_generalizability(ids, L_datas):
    plt.figure(facecolor='lightgray')
    plt.title("Generalizability")
    plt.xlabel("epochs")
    plt.ylabel("acc")
    max_epochs = [max([len(L_datas[i][j]["generalization"]) for i in range(len(L_datas))]) for j in range(4)] # L_1 ~ L_4の最大epochを取得
    plots = []
    for j in range(4): # L_1 ~ L_4
        acc = [0 for _ in range(max_epochs[j])]
        count = [0 for _ in range(max_epochs[j])]
        for i in range(len(L_datas)): # 実行回数
            for k, data in enumerate(L_datas[i][j]["generalization"]):
                acc[k] += float(data["acc"])
                count[k] += 1
        acc = [a / c for a, c in zip(acc, count)]
        plots.append(plt.plot(np.array([i+1 for i in range(max_epochs[j])]), np.array(acc)))
    plt.legend((plot[0] for plot in plots), (f"L_{i}" for i in range(1, 4+1)), loc=2)
    plt.savefig(f"averaged_result/{ids[0]}~{ids[-1]}/generalizability.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', required=True, nargs="*", type=str)
    args = parser.parse_args()

    import os
    try:
        os.mkdir(f"averaged_result/{args.ids[0]}~{args.ids[-1]}")
    except FileExistsError:
        pass

    ngram_averaged_entropy(args.ids)
    topsim_averaged_topsim(args.ids)

    L_datas = extract_L_data(args.ids)
    averaged_change_of_acc(args.ids, L_datas)
    averaged_ease_of_learning_freezed_receiver(args.ids, L_datas)
    averaged_ease_of_learning_freezed_sender(args.ids, L_datas)
    averaged_entropy(args.ids, L_datas)
    averaged_generalizability(args.ids, L_datas)