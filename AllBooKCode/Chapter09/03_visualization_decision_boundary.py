import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_blobs


def decision_boundary():
    # 构造数据
    X, y = make_blobs(n_samples=80, centers=2, cluster_std=1.2, random_state=6)
    xlim = [np.min(X[:, 0]), np.max(X[:, 0])]
    ylim = [np.min(X[:, 1]), np.max(X[:, 1])]
    # create grid to evaluate model
    xx = np.linspace(xlim[0], xlim[1], 500)
    yy = np.linspace(ylim[0], ylim[1], 500)
    YY, XX = np.meshgrid(yy, xx)
    xy = np.vstack([XX.ravel(), YY.ravel()]).T

    data = []
    for i in range(len(X)):
        index = np.where(y == i)[0]
        data.append(X[index, :])

    plt.figure(figsize=(8, 4), dpi=80)
    plt.rcParams['ytick.direction'] = 'in'  # 刻度向内
    plt.rcParams['xtick.direction'] = 'in'  # 刻度向内
    plt.subplot(1, 2, 1)
    # plt.scatter(X[:, 0], X[:, 1], c=y, s=40, cmap=plt.cm.Paired)
    plt.scatter(data[0][:, 0], data[0][:, 1], marker='o', s=40, cmap=plt.cm.Paired)
    plt.scatter(data[1][:, 0], data[1][:, 1], marker='s', s=40, cmap=plt.cm.Paired)
    clf = LogisticRegression()
    clf.fit(X, y)
    Z1 = clf.decision_function(xy).reshape(XX.shape)
    plt.contour(XX, YY, Z1, colors='black', levels=[-2.2, 0, 1.8], alpha=0.8, linestyles=['--', '-', '--'])
    plt.xlabel('(a)', fontsize=15)

    plt.subplot(1, 2, 2)
    plt.rcParams['ytick.direction'] = 'in'  # 刻度向内
    plt.rcParams['xtick.direction'] = 'in'  # 刻度向内
    # plt.scatter(X[:, 0], X[:, 1], c=y, s=40, cmap=plt.cm.Paired)
    plt.scatter(data[0][:, 0], data[0][:, 1], marker='o', s=40, cmap=plt.cm.Paired)
    plt.scatter(data[1][:, 0], data[1][:, 1], marker='s', s=40, cmap=plt.cm.Paired)
    clf = svm.SVC(kernel='linear', C=1000)
    clf.fit(X, y)
    Z4 = clf.decision_function(xy).reshape(XX.shape)
    plt.contour(XX, YY, Z4, colors='black', levels=[-1, 0, 1], alpha=0.8, linestyles=['--', '-', '--'])
    plt.xlabel('(d)', fontsize=15)

    # plot support vectors
    plt.scatter(clf.support_vectors_[:, 0], clf.support_vectors_[:, 1], s=130,
                linewidth=1, facecolors='none', edgecolors='k')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    decision_boundary()
