import logging
from copy import deepcopy
from scipy.sparse import csgraph
from sklearn.metrics import accuracy_score
from sklearn.metrics.pairwise import euclidean_distances
import numpy as np
from C07_label_spreading_comp import load_data


def kernel(X, y=None, gamma=None):
    if gamma is None:
        gamma = 1.0 / X.shape[1]
    K = euclidean_distances(X, y, squared=True)
    K *= -gamma
    np.exp(K, K)  # <==> K = np.exp(K)
    return K


class LabelSpreading():
    """Base class for label propagation module.
    """

    def __init__(self, gamma=20, alpha=0.2,
                 max_iter=30, tol=1e-3):
        self.max_iter = max_iter
        self.tol = tol
        self.gamma = gamma
        self.alpha = alpha

    def _get_kernel(self, X, y=None):
        return kernel(X, y, gamma=self.gamma)

    def _build_graph(self):
        # 计算标准化后的拉普拉斯矩阵
        n_samples = self.X_.shape[0]
        affinity_matrix = self._get_kernel(self.X_)
        # D^{-1/2}WD^{-1/2}
        laplacian = -csgraph.laplacian(affinity_matrix, normed=True)
        laplacian.flat[::n_samples + 1] = 0.0  # 设置对角线原始全为0
        return laplacian

    def fit(self, X, y):
        """
        模型拟合
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            A matrix of shape (n_samples, n_samples) will be created from this.

        y : array-like of shape (n_samples,)
            `n_labeled_samples` (unlabeled points are marked as -1)
            All unlabeled samples will be transductively assigned labels.
        """
        self.X_ = X
        self.graph_matrix = self._build_graph()
        classes = np.unique(y)
        self.classes_ = (classes[classes != -1])

        n_samples, n_classes = len(y), len(self.classes_)

        alpha = self.alpha
        if alpha is None or alpha <= 0.0 or alpha >= 1.0:
            raise ValueError("alpha必须大于0小于1")
        self.label_distributions_ = np.zeros((n_samples, n_classes))
        for label in self.classes_:
            self.label_distributions_[y == label, self.classes_ == label] = 1

        y_static = np.copy(self.label_distributions_)
        y_static *= 1 - alpha
        l_previous = np.zeros((self.X_.shape[0], n_classes))

        for self.n_iter_ in range(self.max_iter):
            if np.abs(self.label_distributions_ - l_previous).sum() < self.tol:
                break
            l_previous = self.label_distributions_
            label_distributions_ = np.matmul(self.graph_matrix, self.label_distributions_)
            self.label_distributions_ = alpha * label_distributions_ + y_static
        else:
            logging.warning(
                'max_iter=%d was reached without convergence.' % self.max_iter)
            self.n_iter_ += 1

        normalizer = np.sum(self.label_distributions_, axis=1, keepdims=True)
        normalizer[normalizer == 0] = 1
        self.label_distributions_ /= normalizer
        self.transduction_ = self.classes_[np.argmax(self.label_distributions_, axis=1)]
        return self

    def predict(self, X):
        """
        预测
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data matrix.
        Returns
        -------
        y : ndarray of shape (n_samples,)
            Predictions for input data.
        """
        probas = self.predict_proba(X)
        return self.classes_[np.argmax(probas, axis=1)].ravel()

    def predict_proba(self, X):
        """
        概率预测
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data matrix.
        Returns
        -------
        probabilities : shape (n_samples, n_classes)
        """
        weight_matrices = self._get_kernel(self.X_, X)
        weight_matrices = weight_matrices.T
        probabilities = np.matmul(weight_matrices, self.label_distributions_)
        normalizer = np.sum(probabilities, axis=1, keepdims=True)
        normalizer[normalizer == 0] = 1  # 平滑处理
        probabilities /= normalizer
        return probabilities

    def score(self, X, y):
        return accuracy_score(self.predict(X), y)


def test_label_spreading():
    x_train, x_test, y_train, y_test, y_mixed = load_data(noise_rate=0.1)
    model = LabelSpreading()
    model.fit(x_train, y_mixed)

    logging.info(f"模型在训练集上的准确率为: {model.score(x_train, y_train)}")
    logging.info(f"模型在测试集上的准确率为: {model.score(x_test, y_test)}")


if __name__ == '__main__':
    formatter = '[%(asctime)s] - %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG,  # 如果需要查看详细信息可将该参数改为logging.DEBUG
                        format=formatter,  # 关于Logging模块的详细使用可参加文章https://www.ylkz.life/tools/p10958151/
                        datefmt='%Y-%m-%d %H:%M:%S', )
    test_label_spreading()
